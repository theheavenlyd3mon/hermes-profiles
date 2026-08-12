# Vault File Renumbering

When a numbered sequence of files has a gap (e.g., 01, 02, 03, 05, 06...) and you need to close it, renumbering requires coordinated changes across files, MOCs, and cross-references.

## Execution Order

### 1. Rename files (highest-to-lowest)

Always rename from the highest number down to avoid collisions:

```bash
cd <folder>
mv "14_Old_Name.md" "13_New_Name.md"
mv "13_Previous_Name.md" "12_New_Name.md"
# ... continue downward
```

Renaming low-to-high would overwrite files (e.g., renaming 05→04 then 06→05 would collide with the just-renamed 05).

### 2. Update the MOC file

Rewrite the `_MOC_*.md` with the new filenames. Don't patch — rewrite is cleaner since every link changes.

### 3. Update `episode:` frontmatter

Each renamed file needs its `episode:` value decremented. Use `patch` with the exact line from frontmatter:

```
old: episode: 5
new: episode: 4
```

### 4. Update Previous/Next wikilinks

Every file in the renamed range needs both its `← Previous` and `→ Next` links updated. The file *before* the range (the last un-renamed file) also needs its `→ Next` link updated. The last file in the renamed range has no `→ Next` to update (it already points correctly or is the chain end).

**Critical:** Don't forget the file just before the gap — its `→ Next` link still points to the old number.

### 5. Verify

Run `ls -1 *.md` to confirm contiguous numbering. Spot-check a few files' Previous/Next links with `search_files`.

## Example: Closing a gap at position 04

Original: 01, 02, 03, **(missing 04)**, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14

Renames: 14→13, 13→12, 12→11, 11→10, 10→09, 09→08, 08→07, 07→06, 06→05, 05→04

Updates needed:
- File 03: `→ Next` link 05→04
- File 04 (was 05): `episode:` 5→4, `→ Next` 06→05
- File 05 (was 06): `episode:` 6→5, `← Previous` 05→04, `→ Next` 07→06
- ... pattern continues for all files in range
- File 13 (was 14): `episode:` 14→13, `← Previous` 13→12
