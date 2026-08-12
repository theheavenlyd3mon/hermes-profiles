# Worked example — mnemosyne audit (importers/MCP/CLI + embeddings/LLM/extraction)

## PART 1 — integrations / importers / MCP / CLI

Surface: `mnemosyne/{integrations,core/importers,mcp_server,mcp_tools,
tool_schemas,cli,batch_tool}`.

### A. Over-engineering (delete / simplify)

- `mcp_tools.py:57-110` — `_SchemaProxy` (7-method lazy proxy) + `_get_schema`
  + six `_*_SCHEMA` module vars. **Dead**: repo-wide grep shows zero references
  outside their own module. Rung (1). Delete.
- `importers/{mem0,letta,zep,supermemory,cognee}.py` — five `run()` overrides
  that reproduce `BaseImporter.run()` plus a *byte-identical* identity UPDATE.
  Rung (2). Lift the delta into the base, delete ~300->~15 lines.
- `importers/base.py:170-175` — `validate()` no-op branch. Rung (5).
- `_resolve_default_scope()` duplicated verbatim in `mcp_tools.py` + `cli.py`.
  Rung (2) -> one shared helper.
- `importers/base.py:179` `_content_hash` — only referenced by a unit test.
  Rung (1) (reused to close a gap below).

### B. Missing capabilities

1. CLI can't reach the 8 provider importers -> add `--from <provider>` +
   `--list-providers`.
2. PII scan not at ingestion -> wire `core/hygiene.py` post-transform.
3. `dry_run` returns only a count -> add `preview = memories[:5]`.
4. Non-idempotent import -> wire `_content_hash` (already written, unused).

### C. Top 3

1. (M) Collapse the 5 `run()` overrides into `BaseImporter.run()`.
2. (S) Delete dead `_SchemaProxy`/`_get_schema`/`_*_SCHEMA` (verified).
3. (M) CLI `--from <provider>` + close idempotency gaps.

### Non-findings

- `mcp_server.py:69-87` SSE auth gating is correct — KEEP, not over-engineered.

---

## PART 2 — embeddings / LLM / extraction subsystem

Surface: `core/{embeddings,local_llm,llm_backends,llm_conflict_detector,
model_refresh,veracity_consolidation,streaming,token_counter,cost_log,
binary_vectors,shmr,weibull,aaak}.py`, `extraction/{client,prompts,
diagnostics,__init__}.py`, `core/extraction.py`. Read all in full, proved
reachability with repo-wide grep.

### A. Over-engineering (all grep-verified unreachable)

- `binary_vectors.py:56-372` — `BinaryVectorStore` + `FastBinarySearch` + `__main__`.
  The standalone `binary_vectors` table is documented "production never wrote
  to". `beam.py` computes Hamming inline; `hamming_distance as _hamming` import is
  set to `None` and never used. Rung (1). Keep ONLY `maximally_informative_binarization`.
- `shmr.py:1-656` — `harmonize()` + helpers + 2 own tables. `harmonize(` has
  zero callers (own def + docstring + `build/` copies). Rung (1). Delete unless
  a `mnemosyne_sleep()` hook is planned (then wire now).
- `token_counter.py:1-72` — zero importers. `extraction/client.py`+`prompts.py` —
  second divergent engine. `available_api()` (`embeddings.py:294`) — never called.
  `aaak.py:93-94` `REV_CATEGORY`/`REV_PHRASE` — no `decode()` exists. All rung (1).
  No-ops: `embeddings.py:42` alias, `:350` self-assign, `_API_CALL_COUNT`
  incremented but never read.
- `llm_conflict_detector` re-defines `_estimate_tokens` + private `MODEL_PRICING`
  duplicating `local_llm` + `cost_log`. Rung (2) -> reuse shared helpers.

### B. Missing capabilities (gaps)

1. **Doc-embedding cache** (highest value). `embed_query` is `lru_cache`d
   (`embeddings.py:309`) but `embed()` (`embeddings.py:326`) is not; identical
   content re-embedded on re-index (`beam.py:2417`), edit (`4180`), summary
   (`4341`). Mirror the query cache.
2. **Embedding observability.** Extraction has full diagnostics; embeddings make
   the real network/GGUF calls and have none. Add a mirror of the extraction-
   diagnostics pattern; fold `cost_log.get_cost_stats` (never called) in.
3. **Local->API fallback.** Transport chosen once at import; a runtime local-load
   failure -> `None` + silent recall degradation. Retry via API when configured.
4. **Single extraction source of truth.** Delete `extraction/client.py`+
   `prompts.py`; route benchmark through `core/extraction`; add a
   `CallableLLMBackend` (`llm_backends.py:50`) deterministic seam.
5. **Veracity correctness:** `unknown:0.8` outranks `inferred:0.7`/`tool:0.5`
   (must be lowest); `bayesian_update` docstring claims `1-0.7^n` but implements
   `old+(1-old)*w*0.3`; `run_consolidation_pass` ignores veracity/recency.

### C. Top 3

1. (S/M) Delete dead code — `binary_vectors` classes, `token_counter`,
   `available_api`, aaak reverse-maps, `shmr.py` (~1,100 LOC, zero risk).
2. (M) Add doc-embedding cache (`embeddings.py:326`) + expose `_API_CALL_COUNT`.
3. (M) Remove dead `shmr.py` harmonize subsystem (0 callers) unless wired now.

### Cross-cutting flag

`pyproject.toml` headline "Zero-Dependency, Sub-Millisecond, Fully Private" does
NOT hold for the embeddings/LLM layers: `numpy` is effectively required, plus
optional `fastembed`/`llama-cpp-python`/`ctransformers`/`huggingface-hub`; calls
are network/GGUF-bound (ms-seconds). Claim holds only for the FTS5 + AAAK recall
path. Scope the claim in docs or guard heavy imports behind an optional path.
