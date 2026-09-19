# Schema v2 — catalogue + per-user libraries

The MyAnimeList model, for games. A curated catalogue that admins maintain, and a
personal list each user builds from it.

**Why the change:** `rating` lived on `Game`, and `Game` belonged to one user — so two
people playing Palworld meant two unrelated rows both called "Palworld". Nothing could
be shared or compared. Splitting "the game" from "my copy of it" fixes that.

---

## Models

### `Game` — the catalogue

```
title
genres          M2M → Genre
release_year    optional
```

One row per game in the world. **Admin writes, everyone reads.**

No `platform` here — see below.

### `LibraryEntry` — my copy

```
user            FK → User
game            FK → Game
platform        FK → Platform
status          backlog / playing / finished / dropped
rating          1–5, nullable
untracked_hours nullable
added_on        auto

unique together: (user, game)
```

One row per person per game. **You write your own, everyone reads.**

### `GameSession` — private detail

```
library_entry   FK → LibraryEntry
played_on
duration_hours
```

**Yours only.** Not readable by other users.

### `Review` — public opinion

```
game            FK → Game
user            FK → User
body
written_on
updated_at

unique together: (game, user)
```

One per person per game, editable. **You write your own, everyone reads.**

Replaces `JournalEntry`. The dated running-commentary idea is dropped — add a private
journal back later if the want for one turns out to be real.

### `Genre`, `Platform`

Unchanged. **Admin writes, everyone reads.**

---

## The field test

> **Is this true of the game, or true of my copy of it?**

| Field | Belongs to |
|---|---|
| title, genres, release year | the game |
| platform, status, rating, hours | my copy |

Platform is the non-obvious one. Palworld is on Steam *and* Epic; which one you own it
on is a fact about you, not about the game.

---

## Computed fields

| On | Field | How |
|---|---|---|
| `LibraryEntry` | `total_hours` | `untracked_hours + Sum(sessions.duration_hours)` — carried over from v1 |
| `Game` | `mean_rating` | `Avg` across its library entries |
| `Game` | `owner_count` | `Count` of its library entries |

Same annotation machinery as `with_hours()`, pointed at different relations. Watch for
the fan-out problem when combining `Avg(entries__rating)` with an M2M genre filter.

---

## Permissions

| Resource | Read | Write |
|---|---|---|
| Game | any logged-in user | admin |
| Genre, Platform | any logged-in user | admin |
| LibraryEntry | any logged-in user | owner only |
| GameSession | **owner only** | owner only |
| Review | any logged-in user | owner only |

Nobody anonymous. One asymmetry that needs a real permission class — the
read-for-all / write-for-admin split on the catalogue and lookup tables.

Ownership on the rest comes free from queryset filtering: a `LibraryEntry` you don't
own isn't in your queryset, so editing it 404s rather than 403s. Same mechanism as the
nested-route scoping already built, and it doesn't leak existence.

---

## Endpoints

```
/games/                      catalogue         read all · write admin
/games/<id>/                 one game, with mean rating and owner count
/games/<id>/reviews/         reviews           read all · write own

/library/                    my entries
/library/<id>/               one of mine
/library/<id>/sessions/      my sessions       private

/users/<username>/library/   someone else's list

/genres/                     read all · write admin
/platforms/                  read all · write admin
```

`/games/` changes meaning — it becomes the shared catalogue. The personal list moves to
`/library/`.

---

## Order of work

Both the custom user model and this refactor want a fresh database, so they're cheaper
done in one pass than separately. But they're different *kinds* of change.

**1. Schema refactor first.** Models, serializers, viewsets, tests — all familiar
territory. No new concepts, just rearrangement.

**2. Then authentication.** That's where the unfamiliar material is. Adding it on top
of a settled schema means a failure has one likely cause instead of two.

The custom user model has to be created before the first migration of the new
database, so it happens at the start of step 1 even though nothing uses it until step 2.

### Data

Four games, two sessions, one journal entry. Re-enter by hand — not worth a migration
script, and the old shape doesn't map cleanly anyway.

Worth a `dumpdata` of the current state first, purely as a reference for what to
re-type.

---

## Open for later

- Private journal alongside public reviews, if the want for one turns out to be real
- `Game` → `Platform` M2M for "available on", separate from "where I own it"
- Sharing / following between users
- Steam sync — writes `LibraryEntry` rows and `GameSession` deltas
