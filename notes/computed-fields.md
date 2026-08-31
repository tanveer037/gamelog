# Computed fields — the pattern

How to expose a value that isn't a database column, without creating an N+1.

---

## The rule

**If it can be expressed in SQL, annotate it. Compute in Python only for things
SQL can't do.**

A computed value on a *list* endpoint must be computed by the database, in the
same query that fetches the rows. Anything computed per-object in Python is an
N+1 by construction.

---

## The three steps

### 1. Define the expression once — a queryset method on the model

```python
class GameQuerySet(models.QuerySet):
    def with_hours(self):
        return self.annotate(
            total_playtime=Coalesce(Sum('sessions__duration_hours'), Value(Decimal(0)))
            + Coalesce(F('untracked_hours'), Value(Decimal(0)))
        )


class Game(models.Model):
    ...
    objects = GameQuerySet.as_manager()
```

`as_manager()` makes the method available on `Game.objects`, alongside `filter`,
`exclude` and the rest. It returns a queryset, so it chains in any position.

This is where the logic lives — one definition, no duplication between views and
admin.

### 2. Call it wherever the value is needed

```python
# views.py
Game.objects.with_hours().prefetch_related('genres')

# admin.py
def get_queryset(self, request):
    return super().get_queryset(request).with_hours()
```

The annotation rides along on each object for that request. Nothing is stored,
no migration, no column in the table.

### 3. Declare it on the serializer

```python
total_hours = serializers.DecimalField(
    max_digits=7, decimal_places=2, read_only=True, source='total_playtime'
)
```

and list it in `Meta.fields`.

`ModelSerializer` can't infer the type — there's no model field to introspect —
so the declaration is explicit. `source` bridges the public name (`total_hours`)
to the internal name (`total_playtime`).

Drop `source` if you're happy for the JSON key to match the annotation name.
`serializers.ReadOnlyField()` also works and takes no arguments, at the cost of
precision control.

---

## What to avoid

All three of these work and all three are N+1 on a list endpoint:

```python
# model property — one query per object
@property
def total_hours(self):
    return self.sessions.aggregate(Sum('duration_hours'))['...']

# SerializerMethodField — same, hidden behind DRF
total_hours = serializers.SerializerMethodField()

# a Python loop in the view — same, just more visible
for game in games:
    game.total = sum(s.duration_hours for s in game.sessions.all())
```

They're fine for a **single object** (`/games/1/`), where there's only one of it.
They're wrong for lists.

---

## Loading hints — which one, when

Decide by reading `Meta.fields`. For each relation that renders, add the matching
hint. Nothing else.

| Serializer renders | Add | Cost |
|---|---|---|
| M2M or reverse FK, as objects/IDs | `prefetch_related` | +1 query |
| FK/O2O, and you read its *fields* | `select_related` | JOIN, no extra query |
| FK rendered as a bare ID | nothing | `platform_id` is already loaded |
| an aggregate over a relation | `annotate` | no extra query |

The common over-application is `select_related` on a FK that only renders as an
ID — that buys a JOIN you never use.

Nested relations chain with `__`:

```python
.prefetch_related('sessions__game__platform')
```

---

## NULL handling

`SUM` over zero rows returns `NULL`, not 0. Nullable columns are `NULL`. And in
SQL, `NULL + 5` is `NULL` — one null poisons the whole expression.

So every aggregate in an annotation wants a guard:

```python
Coalesce(Sum('sessions__duration_hours'), Value(Decimal(0)))
```

The failure mode is silent: no error, a `200`, and blank values for exactly the
rows with no related records — which is usually the majority.

---

## Expression vocabulary

| Piece | Means |
|---|---|
| `Sum('sessions__duration_hours')` | aggregate across a relation (`__` traverses) |
| `F('untracked_hours')` | a column on the current row |
| `Value(Decimal(0))` | a literal, not a column name |
| `Coalesce(a, b)` | use `a`, or `b` if `a` is NULL |

Inside a function or a lookup, bare strings are field names. In standalone
arithmetic, wrap columns in `F()`.

---

## Verifying

Query count, not milliseconds. Local timings are meaningless — the database is on
the same machine with three rows in it.

Load the endpoint in the browser (DRF's browsable API is HTML, so the toolbar
attaches), open the SQL panel, and read the header:

```
6 queries including 0 similar
```

"N similar" is the alarm. The count should stay flat as rows are added.
