# Hugging Face Hub — Troubleshooting & Diagnostics

## "Unauthenticated requests" Warning

**Symptom:** `Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.`

**Cause:** `huggingface_hub` library imported or `hf_hub_download()` called without `HF_TOKEN` in environment.

**Impact:** Lower rate limits (~100 req/hr vs 1000+), slower downloads (no CDN acceleration). If you're not hitting 429 errors, it's cosmetic.

**Fixes (pick one):**
1. `export HF_TOKEN="hf_xxxxx"` — set in shell profile or `~/.hermes/.env`
2. `huggingface-cli login` — stores token in `~/.cache/huggingface/token`
3. `hf auth login` — modern equivalent using the `hf` CLI
4. Get a free "Read" token at https://huggingface.co/settings/tokens

**When it matters:** Large model downloads, programmatic access via `hf_hub_download()`/`snapshot_download()`, hitting 429 errors.
**When it doesn't:** Occasional small file downloads, no rate limiting observed.

---

## Tracing What Was Downloaded

When something downloads from HF but you're not sure what, check these locations:

### 1. Xet download logs (most detailed)
```
ls -lt ~/.cache/huggingface/xet/logs/
cat ~/.cache/huggingface/xet/logs/xet_*.log | tail -50
```
Xet is HF's newer storage backend (replacing Git LFS). Logs contain:
- **Timestamps** of each download
- **File hashes** (SHA-256) identifying the downloaded file
- **Byte counts** and byte ranges
- **Success/failure** status codes (200 = ok, 416 = range error, 429 = rate limited)
- **Concurrency** adjustments

Example log entry to look for:
```json
{"message":"File reconstruction completed successfully","file_hash":"aaca296...","total_bytes_scheduled":66465124}
```

### 2. Hub cache (model files)
```
du -sh ~/.cache/huggingface/hub/* 2>/dev/null | sort -rh | head -10
ls ~/.cache/huggingface/hub/models--*/snapshots/*/
```
Model files (.safetensors, .bin, .gguf, .onnx) live here after download.
If empty — the download was either in-memory, temporary, or used a different cache path.

### 3. Hermes profile cache
Hermes profiles may have isolated caches:
```
~/.hermes/profiles/<name>/home/.cache/huggingface/
```

### 4. Python import-triggered downloads
Some libraries auto-download on `import`:
- `transformers` — downloads tokenizer configs, model configs
- `sentence-transformers` — downloads embedding models
- `datasets` — downloads dataset metadata

These are often small (<1MB) and won't leave large model files.

---

## Cache Management

```bash
# List cached repos
hf cache list

# Prune unused/detached revisions (frees disk)
hf cache prune

# Verify cache integrity
hf cache verify

# Nuclear option: clear everything
rm -rf ~/.cache/huggingface/hub/
```

---

## Common Pitfalls

- **`hf` vs `huggingface-cli`:** `hf` is the modern CLI. `huggingface-cli` still works but is deprecated.
- **Model not in cache after download:** If loaded via `transformers` pipeline with `device_map="auto"`, files may be in a different cache or loaded to GPU memory directly.
- **416 Range Not Satisfiable in xet logs:** Usually a retry artifact — the client adjusts byte ranges. If downloads succeed overall, ignore these errors.
- **Org/AAD accounts:** Don't use organizational Microsoft accounts for HF auth — records are tied to the account, not the person.
