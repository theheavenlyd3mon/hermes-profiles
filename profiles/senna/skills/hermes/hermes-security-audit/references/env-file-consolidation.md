# `.env` File Consolidation Methodology

When auditing or consolidating `.env` files across Hermes profiles, do NOT use `diff` to compare files — it compares byte-for-byte including comments, blank lines, and formatting, which will always show differences (e.g., 442-line root vs 370-line profile). The relevant check is **key set comparison**.

## Key Set Comparison

```bash
# Extract only key names (lines matching VARIABLE_NAME=value)
grep -E '^[A-Z_]+=' ~/.hermes/.env | cut -d= -f1 | sort > /tmp/root_keys.txt
grep -E '^[A-Z_]+=' ~/.hermes/profiles/business/.env | cut -d= -f1 | sort > /tmp/biz_keys.txt

# Check counts
echo "Root: $(wc -l < /tmp/root_keys.txt) keys"
echo "Profile: $(wc -l < /tmp/biz_keys.txt) keys"

# Keys in root NOT in profile
comm -23 /tmp/root_keys.txt /tmp/biz_keys.txt

# Keys in profile NOT in root
comm -13 /tmp/root_keys.txt /tmp/biz_keys.txt
```

If both `comm` commands return empty output, the key sets are **identical** — safe to consolidate.

## Real-World Example

A 22-profile Hermes installation had:
- Root `.env`: 442 lines, 51 keys
- Business `.env`: 370 lines, 51 keys
- `diff -q`: reported "different" (byte mismatch from whitespace)
- `comm -13/23`: zero lines (same 51 keys)

**Result:** All 16 per-profile `.env` files with identical key sets were safely renamed to `.env.bak`. The root `.env` was the canonical source. Only 3 profiles with unique keys (creative, security, maintenops) kept their per-profile `.env`.

## Consolidation Command

```bash
# Backup each duplicate, then remove
for p in business code communication cyber-blue cyber-blue-cloud \
         cyber-blue-compliance cyber-blue-forensics cyber-blue-soc \
         cyber-red finance homelab infra knowledge media mlops \
         research social; do
  f="~/.hermes/profiles/$p/.env"
  [ -f "$f" ] && mv "$f" "$f.bak"
done
```

## Verification After Consolidation

```bash
# Confirm only canonical .env files remain
find ~/.hermes -name ".env" -not -path "*/home/*" -not -name "*.bak"

# Expected survivors: root + creative + security + maintenops
```

## Pitfalls

- **macOS Terminal `***` redaction:** macOS may replace live secret values with `***` in terminal output. Use `sed -n 's/^[^#]*=[^ ]//p' .env` or `xxd .env | less` to verify actual bytes. Do not assume `***` means a placeholder.
- **Empty .env files:** A profile may have a 1-line or 0-key `.env` (like `maintenops` with only `NVIDIA_API_KEY`). These aren't duplicates — they're special-purpose. Keep them.
- **.env in home/ sandbox:** The profile sandbox home (`profiles/<name>/home/`) can contain a full nested `.hermes/profiles/` tree with 40+ additional `.env` copies. Check with `find ~/.hermes -name ".env" | wc -l` (WITHOUT the home exclusion) to see the full picture.
- **Root .env is not always comprehensive:** Before removing per-profile .env files, verify the root `.env` actually has all the keys the profiles use. Run the `comm` check above first.
