# N+1 on `/tracker/games/`

Recorded from django-debug-toolbar before fixing.

---

## Before

**Header:** `11 queries including 6 similar` — 2.70ms

| # | Query | Note |
|---|---|---|
| 1 | `SELECT` | connection setup |
| 2 | `SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED` | connection setup |
| 3 | `SELECT ... FROM django_session WHERE session_key = ...` | auth overhead |
| 4 | `SELECT ... FROM auth_user WHERE id = 1` | auth overhead |
| 5 | `SELECT ... FROM tracker_game` | **the "+1"** |
| 6 | `... tracker_genre INNER JOIN tracker_game_genres ... WHERE game_id = 1` | loop A |
| 7 | `... FROM tracker_gamesession WHERE game_id = 1` | loop B |
| 8 | `... genre ... WHERE game_id = 2` | loop A |
| 9 | `... gamesession ... WHERE game_id = 2` | loop B |
| 10 | `... genre ... WHERE game_id = 3` | loop A |
| 11 | `... gamesession ... WHERE game_id = 3` | loop B |

Queries 1–4 are fixed overhead. The bug is 5–11.

### Two separate loops

**Loop A — genres.** The `genres` field on `GameSerializer` iterates the M2M
manager once per game.

```sql
SELECT `tracker_genre`.`id`, `tracker_genre`.`name`
FROM `tracker_genre`
INNER JOIN `tracker_game_genres`
  ON (`tracker_genre`.`id` = `tracker_game_genres`.`genre_id`)
WHERE `tracker_game_genres`.`game_id` = 1
```

**Loop B — total hours.** The `total_hours` `cached_property` on `Game` runs its
`SUM` aggregate once per game.

```sql
SELECT SUM(`tracker_gamesession`.`duration_hours`)
FROM `tracker_gamesession`
WHERE `tracker_gamesession`.`game_id` = 1
```

### The tell

`WHERE game_id = 1` — a single literal ID means the query was built to serve one
parent, so something has to run it again for every other parent.

- `parent_id = <literal>`, repeated → N+1
- `parent_id IN (...)` → batched, healthy

### Cost model

Not scanning — the index on `game_id` means each query touches ~3 rows.
The cost is **round trips**: send, parse, plan, execute, return, deserialize,
paid once per query regardless of row count.

- localhost: ~0.3ms per trip → invisible
- remote database: 5–30ms per trip → 100 games = 2–3 seconds of waiting

---

## Fix

In the **view**, not the serializer — the serializer only declares what it wants;
the queryset decides how it's loaded.

```python
Game.objects
    .prefetch_related('genres')          # loop A → one query with IN (...)
    .annotate(computed_hours=...)        # loop B → folded into the main query
```

Serializer field points at the annotation:

```python
total_hours = serializers.DecimalField(
    max_digits=7, decimal_places=2, read_only=True, source='computed_hours'
)
```

---

## After

**Header:** `5 queries` — 0 similar

| # | Query | Note |
|---|---|---|
| 1 | `SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED` | connection setup |
| 2 | `SELECT ... FROM django_session WHERE session_key = ...` | auth overhead |
| 3 | `SELECT ... FROM auth_user WHERE id = 1` | auth overhead |
| 4 | `SELECT ... FROM tracker_game LEFT OUTER JOIN tracker_gamesession ... GROUP BY ...` | games **+ the total, in one query** |
| 5 | `SELECT ... FROM tracker_genre INNER JOIN tracker_game_genres ... WHERE game_id IN (1, 2, 3)` | the prefetch |

**11 → 5.** Both loops gone.

### The two cure signatures

Loop B folded into the main query — no extra query at all:

```sql
FROM `tracker_game`
LEFT OUTER JOIN `tracker_gamesession` ON (`tracker_game`.`id` = `tracker_gamesession`.`game_id`)
GROUP BY `tracker_game`.`id`, COALESCE(`tracker_game`.`untracked_hours`, 0)
ORDER BY NULL
```

`LEFT OUTER JOIN`, not inner — games with no sessions must still appear.
(`ORDER BY NULL` is Django suppressing MySQL's implicit `GROUP BY` sort. Not ours.)

Loop A batched into one:

```sql
WHERE `tracker_game_genres`.`game_id` IN (1, 2, 3)
```

`IN (...)` where there used to be three separate `= 1`, `= 2`, `= 3`.

### Flat now

Add 500 games and it's still 5 queries. The `IN` list gets longer; the count
doesn't move.

### Ignore the timings

Total went **up** — 2.70ms before, 40.43ms after. Cold caches, and `auth_user`
alone took 9.79ms this run. At three rows, milliseconds are noise.

The shape was optimised, not this particular measurement. Query count is the
signal.

---

## General workflow, for next time

1. Load the endpoint in the browser, open the SQL panel
2. Read the header — "N similar" is the alarm
3. Ignore session/auth queries at the top
4. Find the repeated shape; read its `FROM` table and `WHERE` clause
5. Map the table to the serializer field or model property that touches it
6. Choose the fix:
   - many related objects → `prefetch_related`
   - one related object → `select_related`
   - a sum or count → `annotate`
7. Apply it to the queryset in the view
8. Reload, confirm the count dropped and "similar" is gone

If the culprit field isn't obvious: comment out half of `Meta.fields`, reload,
and bisect.

**Judge by query count, not milliseconds.** Local timings are meaningless —
the database is on the same machine and the dataset is tiny.
