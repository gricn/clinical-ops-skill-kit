---
name: gsheet-append-dedup
description: Safely write structured surgery rows (TSV / row arrays) into Google Sheet with dedup by primary key, date-correct insertion when filling earlier dates, blank-only patch semantics on existing rows, and full black borders on freshly written rows. Used for "schedule OCR result writeback" and "patch missing fields" scenarios.
---

# GSheet Append Dedup

## Overview

Default writeback semantics:

- **Primary key not found**: write into the date-correct position. If the date is older than the current tail, insert before the first later-date row — do not just append to the bottom.
- **Primary key found**: do not create a duplicate row; patch only the blank cells in the existing row.
- **Newly appended rows**: apply uniform black full borders (including innerHorizontal / innerVertical).
- **With explicit user authorization**: a specified column may overwrite existing non-blank values (used for post-op result patches). `remarks` is the exception — even with override authorization, new remarks are appended after the old, not overwritten.

Default target sheet:

- Spreadsheet ID: `<cathlab-summary-sheet-id>`
- Tab: `<cathlab-summary-sheet-name>`
- Explicit user-provided sheet / tab overrides defaults.

## Trigger Conditions

- "Append to the bottom of Google Sheet / table".
- "Skip if duplicate" or "patch only missing fields".
- "Add black border to new rows".
- User supplies TSV and asks for auto Google Sheet writeback.

## Assumption

The target is **Google Sheets**, not Google Docs. If the user says "Google Docs" but the request is row / column / border / append-to-bottom shaped, treat as Sheets.

## Workflow

1. Read the target header and build a column-name map.
2. Read existing data rows and build a primary-key index.
3. For each input row:
   - Key not found: queue into `to_append`.
   - Key found: write non-blank new values only into existing blank cells (`to_patch`).
   - With explicit column override authorization: only those columns may overwrite existing non-blank values; other columns still blank-fill only.
4. Run patches first, then appends. If a new date is earlier than the current tail, insert before the first later-date row.
5. Apply uniform black full borders to the just-written set.
6. Emit a summary.

## Default rules

- Default primary key: `surgery_date + patient_id`.
- Primary-key match ignores trailing `?` on `patient_id` (avoids re-appending tagged uncertainty markers).
- Blank-only by default.
- Override existing non-blank only when explicitly authorized per column.
- `remarks` is append-only, even with override authorization.
- `surgery_type` is a controlled English-code field: only `AF / SVT / WPW / AT / AFL / PAC / PVC / EPS / LAAC / VT` (or `+` combinations). Reject Chinese or free-form text before write.
- Multiple existing rows on the same key → skip the row and flag `needs human review`.
- Duplicates do not raise — they are routed to patch / skip.

## Border rule

For **all written rows** in this round (append + patch):

- Range: column 1 to the last output column.
- Style: black, solid, full borders (including innerHorizontal / innerVertical).
- Patch rows also get re-applied borders — historical stub rows (see below), once filled, must not look unformatted.
- Already-complete rows are not actively re-bordered (skipped rows are untouched).

## Output summary

- `append_count`
- `patch_count`
- `skip_count`
- `conflict_count` (multiple rows for one key)

## Known edge cases

### Stub rows

The sheet may carry stub rows with only `date + patient_id` (rest blank) — typically pre-filled from schedule planning.

**Past bug**: Google Sheets stores dates as integer serials (e.g. `46097` = 2026-03-16). `FORMATTED_VALUE` reads can return the integer string, breaking primary-key matching → stub row is ignored → data is appended as new → duplicate row.

**Fix**: `parse_date_to_iso` now recognizes:
- ISO text formats: `2026-03-16`, `2026/03/16`
- Google Sheets serial (int / float / numeric string in range 1–99999) → converts to ISO.

### Duplicate-row cleanup

If after a run there are multiple rows for the same key (stub + full), the script does NOT auto-delete — requires explicit human or scripted deletion via `batchUpdate -> deleteDimension`.

## Safety

- No write access → return preview stats only, no writes.
- No auto row deletion.
- No history reordering. No overrides on human-filled non-blank content (unless explicitly authorized).

## Format consistency check (mandatory before write)

### Past pitfall

Writing formulas directly produced inconsistency with history:
- weekday column: history was plain text `周一` ("Monday"); new write rendered the formula as `一` ("one")
- month column: history was plain text `2026年03月` ("March 2026"); new write rendered as serial `46082`

### Fixed-fix

Pre-write history check, using both renderings:

```python
resp_raw = svc.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID,
    range=f'{TAB}!A253:J256',
    valueRenderOption='UNFORMATTED_VALUE',
).execute()

resp_fmt = svc.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID,
    range=f'{TAB}!A253:J256',
    valueRenderOption='FORMATTED_VALUE',
).execute()

# UNFORMATTED `周一` → plain text → new row must be plain text too
# UNFORMATTED `=TEXT(...)` → formula → new row may use formula
```

Live audit discipline added:
- Do not decide format from the last 3–5 rows alone — if recent tail has already been mis-written, the error propagates.
- If the user maintains `weekday / week_label / month` as derived columns, prefer a single `ARRAYFORMULA` over per-row `INDIRECT("A"&ROW())`.
- Once detected that the first data row is `ARRAYFORMULA`-managed, treat those input columns as "in-sheet derived" — leave blank on both append and patch.
- Filters must cover open range `A:J` (or whole columns); a fixed-bottom filter range won't pick up future months in `Filter by values`.
- Check at least a short window to catch "first rows are formula, later rows became plain text" discontinuities.
- On mixed state: stop blind writing; default to formula mode as the canonical baseline; report the anomaly first, then decide whether to restore formulas or accept the human plain-text overrides.

### Next-default-path

1. Read last 3–5 rows of target.
2. Diff `UNFORMATTED_VALUE` vs `FORMATTED_VALUE`.
3. If history is plain text, new rows use plain text.
4. After write, re-read and verify format consistency.
