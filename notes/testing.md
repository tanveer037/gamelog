# Testing — reference

pytest + pytest-django + model_bakery, against the gamelog API.

---

## Setup (done once)

```bash
pipenv install --dev pytest pytest-django model_bakery
```

`pytest.ini` at the project root:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = gamelog.settings
python_files = test_*.py
```

Tests live in `tracker/tests/`, one file per area. `__init__.py` makes it a package.
`tracker/tests.py` had to go — a file and a folder of the same name collide.

Run from the project root:

```bash
pytest              # run everything
pytest -v           # list each test by name
pytest --reuse-db   # skip re-running migrations, much faster
pytest -k games     # only tests with "games" in the name
pytest -x           # stop at the first failure
```

---

## The database

- Django creates a **separate** `test_gamelog` database, runs migrations into it,
  and drops it afterwards. Your real data is never touched.
- **Every test starts empty.** No Palworld, no Steam, no genres.
- Each test runs in a transaction that is **rolled back** at the end, so tests
  can't pollute each other.
- First run is slow because migrations run from scratch — `--reuse-db` skips that.

---

## The four imports

| Import | What it's for |
|---|---|
| `pytest` | the framework — needed for the `django_db` marker |
| `decimal.Decimal` | exact decimals, so assertions compare cleanly |
| `model_bakery.baker` | creates test objects without writing them out by hand |
| `rest_framework.test.APIClient` | fake HTTP client |

**`APIClient` makes no network request.** No server, no port. It builds a request
object, hands it to Django's URL resolver, runs the view in-process, and returns the
response. That's why tests are fast and why `runserver` doesn't need to be running.

It's the programmatic version of the browsable API — same URLs, same payloads, same
responses.

```python
client = APIClient()
client.get('/tracker/games/')
client.post('/tracker/games/', {...})
client.patch('/tracker/games/5/', {...})
client.delete('/tracker/games/5/')
```

Each returns a response with `.status_code` and `.data`.

---

## `@pytest.mark.django_db`

A **marker** — metadata pytest reads off the test.

pytest-django **blocks database access by default.** Any test that touches the
database without this raises an error. Deliberate: it keeps database-free tests honest
and forces you to say which ones need one.

On a class, it applies to every method inside.

---

## AAA

**Arrange** — put the world into the state the test needs. Usually creating rows;
later also authenticating a client or building a payload.

**Act** — the one operation under test. Usually a request; sometimes a queryset call
or a model method.

**Assert** — the observable outcome. Usually the response; sometimes the database
state.

```python
def test_returns_201(self):
    platform = baker.make(Platform)                            # Arrange

    response = client.post('/tracker/games/',                  # Act
                           {'title': 'Hollow Knight', 'platform': platform.id})

    assert response.status_code == 201                         # Assert
```

Two "Act" lines usually means two tests.

---

## model_bakery

```python
baker.make(Game)                          # fills required fields, creates the FK
baker.make(Game, title='Hollow Knight')   # pin what matters, fabricate the rest
baker.make(Game, _quantity=3)             # three games (and three platforms)
baker.make(GameSession, game=game)        # pin the relationship — see below
```

**What baker fills:** required fields only. Nullable ones stay `None`, fields with
defaults use the default, M2M is left empty.

For `Game` that means it fabricates `title` and creates a `platform` — the only two
with no default and no null allowed. `status` comes out `'B'` from the model default,
`rating` and `untracked_hours` stay `None`.

**Pin relationships explicitly.**

```python
baker.make(GameSession, game=game)    # ✅ attached to that game
baker.make(GameSession)               # ❌ creates a brand-new Game
```

baker's default is to fabricate, not to reuse. Forgetting this gives a failing
assertion with a non-obvious cause.

**What you specify:** not "the non-null ones" — **the ones your test depends on.**
Pin what you assert on, let baker invent everything else.

---

## Testing the computed field

`total_playtime` is an **annotation**, not a column. `baker.make(Game).total_playtime`
raises `AttributeError` — baker creates a row, and rows don't have it.

So test it through something that annotates:

```python
# through the API — the behaviour test
response = client.get(f'/tracker/games/{game.id}/')
assert response.data['total_hours'] == '102.50'

# through the queryset — testing with_hours() directly
result = Game.objects.with_hours().get(pk=game.pk)
assert result.total_playtime == Decimal('102.50')
```

**Decimals come back from the API as strings**, not `Decimal` — DRF's default. Compare
against `'102.50'`.

**The test worth writing first:**

```python
def test_total_hours_is_zero_when_nothing_logged(self):
    game = baker.make(Game)
    response = client.get(f'/tracker/games/{game.id}/')
    assert response.data['total_hours'] == '0.00'
```

Remove the `Coalesce` guards from `with_hours()` and only this test fails. Everything
else still passes. It covers the bug that would otherwise be silent.

---

## Gotchas specific to this project

**Pagination is on**, so the list endpoint returns an envelope:

```python
assert response.data['count'] == 3          # ✅
assert len(response.data) == 3              # ❌ counts the envelope's keys
```

**DELETE needs two assertions.** A 204 alone doesn't prove the row went:

```python
assert response.status_code == 204
assert not Game.objects.filter(pk=game.id).exists()
```

**`assertNumQueries` locks in the N+1 fix.** Strictly it tests implementation, which
breaks the usual rule — justified because query count regresses silently and can't be
caught by reading a response.

---

## Test behaviours, not implementations

**Behaviour** — what a caller can observe: status codes, response bodies, whether the
row is really gone.

**Implementation** — how it happened: that `perform_create` ran, that `with_hours()`
is in the queryset, that the serializer has a `source`.

All of the implementation can be rewritten tomorrow. If behaviour is unchanged, the
tests should still pass. Tests that assert on internals break on every refactor, which
trains you to ignore them.

**The useful reframe:** every screenshot sent during this project was a manual test.
That list *is* the test suite.

```
GET  /tracker/games/                    200, paginated envelope
POST /tracker/games/  valid             201, correct fields back
POST /tracker/games/  no title          400, error keyed on "title"
POST /tracker/games/  rating 9          400, max-value message
POST /tracker/games/  platform 999      400, invalid pk
GET  /tracker/games/999/                404
PATCH /tracker/games/5/  {"rating": 4}  200, only rating changed
DELETE /tracker/games/5/                204, then GET gives 404
/games/1/sessions/                      only that game's sessions
/games/1/sessions/2/                    404 when session 2 belongs to game 6
POST journal with a smuggled "game"     lands under the URL's game
POST /games/999/journal/                404, not a 500
```
