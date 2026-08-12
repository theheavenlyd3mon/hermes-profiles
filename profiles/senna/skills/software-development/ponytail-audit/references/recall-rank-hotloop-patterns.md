# Recall / Ranking hot-loop patterns (reusable recipe)

Concrete, portable fixes for the two most common recall/ranking over-engineering
and correctness bugs. Captured from a real mnemosyne `beam.py` `recall()` pass
but applies to any hybrid vector+FTS scorer with a per-candidate bonus loop.

## Pattern 1 — Batch-hoist per-candidate DB queries out of the scoring loop

**Symptom.** Inside the per-candidate scoring loop there is a query like:

```python
# BAD: leading-wildcard LIKE cannot use the index → per-candidate FULL TABLE SCAN
for memory_id in candidates:
    cursor.execute(
        "SELECT COUNT(*) FROM graph_edges WHERE source LIKE ? OR target LIKE ?",
        (f"%{memory_id}%", f"%{memory_id}%"))
    edge_count = cursor.fetchone()[0]
```

This is O(candidates x table_rows) every recall and directly contradicts any
"sub-millisecond recall" claim in the docs.

**Fix.** Before the loop, batch ALL candidate IDs into ONE indexed query, then
fold the rows into dicts and do O(1) lookups inside the loop.

```python
# ids are the EXACT stored source/target/source_msg_id values, so equality
# (not LIKE) hits the existing index (idx_edges_source / idx_edges_target).
ph = ",".join("?" * len(cand_ids))
ge_rows = conn.execute(
    f"SELECT source, target FROM graph_edges "
    f"WHERE source IN ({ph}) OR target IN ({ph})",
    (*cand_ids, *cand_ids),
).fetchall()
edge_counts: dict[str, int] = {}
for r in ge_rows:
    s, t = r["source"], r["target"]
    edge_counts[s] = edge_counts.get(s, 0) + 1
    if t != s:
        edge_counts[t] = edge_counts.get(t, 0) + 1
# ...later, inside the loop:
edge_count = edge_counts.get(memory_id, 0)
```

**Two facts that make this safe, both worth checking before you "optimize":**
- The stored `source`/`target`/`source_msg_id` values are the SAME strings as
  the candidate IDs, so equality `IN (...)` matches what the `LIKE '%id%'`
  matched. NO substring semantics are lost. (Verify with a 2-line repro if
  unsure — the schema `CREATE TABLE` + the `add_edge`/`INSERT` call site.)
- If the schema really can store *substrings* of the id (it usually can't),
  this optimization would change results — don't do it blindly in that case.

**Same pattern for the "facts" path:** one `WHERE source_msg_id IN ({ph})`,
group rows by `source_msg_id` into `{mid: [token_sets]}`, then in-loop do
set-overlap against the query tokens.

**Hoist loop-invariants too.** Anything computed once-per-candidate that never
changes across candidates is debt. Example from the same pass:

```python
# BAD: recomputed for every candidate
popcount_table = np.array([bin(i).count('1') for i in range(256)], dtype=np.uint32)
h_dist = int(np.sum(popcount_table[xor_arr]))
# GOOD: module-level, computed once at import
_POPCOUNT_TABLE = np.array([bin(i).count('1') for i in range(256)], dtype=np.uint32)
```

## Pattern 2 — Cache key must include every query-altering filter

**Symptom.** A cached recall path keys only on `query`:

```python
cached = cache.get(query)            # WRONG
cache.put(query, results)            # WRONG
```

while the `recall()` it wraps accepts `author_id`, `from_date`, `memory_type`,
`source`, `veracity`, `channel_id`, ... Different filter scopes return different
rows; keying on the query string alone **bleeds results across scopes** (a
filtered query returns someone else's unfiltered/unscoped results from cache).

**Fix.** Build a filter-aware key. Best as a small classmethod so callers can't
forget a field:

```python
@classmethod
def make_key(cls, query: str, **filters) -> str:
    parts = [str(query)]
    for field in cls._FILTER_FIELDS:      # the tuple of filter kwarg names
        v = filters.get(field)
        if v is not None:
            parts.append(f"{field}={v}")
    return "\u0001".join(parts)
# call site:
key = QueryCache.make_key(query, author_id=kwargs.get("author_id"),
                          memory_type=kwargs.get("memory_type"), ...)
cached = cache.get(key); cache.put(key, results)
```

Note: in a wrapper that forwards filters via `**kwargs`, pull them with
`kwargs.get("field")` — the filter names are NOT local variables in scope.

## Pattern 3 — Collapse a multi-tier cache when invalidate()-on-every-write

**Symptom.** A "5-tier semantic query cache" with: hashing tiers, embedding
cosine-scan tiers, a synonym tier, AND a SQLite persistence table — but the
owner calls `cache.invalidate()` on *every* `remember()`/write. Result: the
cache is empty in normal use, so the SQLite table, the cosine-scan tiers
(claims "O(1)" but loops all entries computing cosine = O(n*d)), and the TTL
machinery are all dead weight. The embedding-scan tiers also serially scan
every cached entry per `get()`, which is the opposite of O(1).

**Fix.** Collapse to ONE in-memory dict keyed by the filter-aware key
(Pattern 2). The cache is a pure read-path speedup: a miss just recomputes, so
correctness never depends on cache contents. Keep `invalidate()` (cleared on
every write -> never stale), drop the SQLite table + embedding/cosine tiers +
TTL bookkeeping. ~250 lines -> ~80.

## Verification checklist for these edits
- Import the module; run a couple of intent/query classifications to confirm
  nothing throws.
- If you touch regex (e.g. entity patterns), confirm case-handling: a pattern
  like `[a-z]+` will FAIL on an already-`.lower()`ed input that contains a
  proper name -> use `[a-zA-Z]+` (or rely on the lowered input).
- Grep the WHOLE repo before deleting any "dead" symbol. A symbol with a
  non-benchmark test importer or a facade in `core/__init__.py` /
  `memory.py` is LIVE — KEEP it. (`MemoryCompressor` looked speculative but had
  a `memory.py` facade + `core/__init__.py` export + `test_patterns.py` -> kept.)
