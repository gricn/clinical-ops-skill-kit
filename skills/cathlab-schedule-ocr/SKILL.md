---
name: cathlab-schedule-ocr
description: Handle cathlab surgery schedule input (images, Word docs, or mixed multi-file). Run OCR, field extraction, surgery filtering, surgeon and vendor rule judgment, sorting and consistency checks. Default writes to Google Sheet via gsheet-append-dedup; outputs strict 10-column TSV only when user explicitly asks. Used for "schedule screenshot/doc to structured table" and "schedule change reconciliation" scenarios.
---

# Cathlab Schedule OCR

## Overview

Convert cathlab schedule input into table-ready data. Input may be image, Word, or both. Run full OCR + structuring first, then unified validation / filtering / sorting, then route by mode:

- **Default**: write to Google Sheet under `gsheet-append-dedup` rules and return a summary.
- **User explicitly asks for TSV**: emit strict 10-column TSV (cuts off at the remarks column); do not generate Excel.
- **User supplies actual post-op results later**: rewrite already-written records by the stated semantics; `surgery_category` may be rewritten, `remarks` is append-only.
- **Cancellation / hold / reschedule on the same day**: the canonical write surface is still Google Sheet — do not silently patch the local cache or temp JSON.

## Trigger Conditions

Trigger this skill in any of:

- User asks to handle "cathlab surgery schedule / 排台 / 台账".
- User gives a vague instruction ("analyze today's data") and uploads schedule-shaped files.
- User uploads 1+ schedule images.
- User uploads 1+ schedule Word docs (`.doc` / `.docx`).
- User uploads both Word and images and asks to merge.
- User asks to emit TSV (strict 10 columns up to remarks) or write to the cathlab summary sheet.
- User uploads files only — no text instruction — but file content is recognizably a cathlab schedule.

Do NOT trigger:

- Uploaded content is not a schedule and no surgery records can be extracted (e.g. a generic notice with no patient info).
- The user's task is unrelated to schedule OCR / structuring.

## Workflow

Run in this exact order, no skipping:

1. Check run mode.
2. Validate input files (image / Word / mixed) as a schedule.
3. Run OCR / text extraction on all inputs and produce an internal record list (do NOT emit results mid-recognition).
4. Field normalization and inheritance (date, cath room, patient ID, ocr_order).
5. Consistency and plausibility checks (date, patient ID, surgeon).
6. Surgery filtering and type / category mapping.
7. Sort (date → cath room → ocr_order).
8. Primary-key and 7-day reminder check.
9. Mode-driven output (writeback summary, or TSV + notes).

Detailed business rules: load [references/decision-rules.md](references/decision-rules.md).

## Mode Split

First determine whether the target Google Sheet is read/write accessible.

- **Has write access, user did not request TSV**: run writeback. Final summary:
  `Done: added X, updated Y, skipped Z (overrode N existing cells).`
- **User explicitly requested TSV**: do not write; emit strict 10-column TSV.
- **No write access, user did not request TSV**: emit strict 10-column TSV and note that no writeback was attempted.

## Zero-Config Behavior

Defaults aim at "smallest possible instruction":

- File count is unbounded. Single, multiple, or mixed inputs all go through the same batch.
- If output format is unspecified, default to Google Sheet writeback.
- If the user just says "analyze today's data": if files include today, prefer today; otherwise fall back to all valid records and note this in the summary.
- If the filename or the user's latest stated surgery date is newer than the in-doc `日期：` line, prefer the newer date.

Default writeback target:

- Spreadsheet ID: `<cathlab-summary-sheet-id>`
- Tab: `<cathlab-summary-sheet-name>`
- Dedup / patch / border rules: reuse `gsheet-append-dedup`.

**⚠ Pre-write history-format check**:
- Read the last 3–5 rows of the target tab to confirm whether `surgery_weekday / week_label / surgery_month` are plain text or formula.
- New records must match historical format exactly.
- See [decision-rules.md#10](references/decision-rules.md).

## Required Messages

Strict failure prompts:

- No file uploaded or input not recognizable as a schedule:
  `Please upload a clear image or Word doc of the cathlab surgery schedule (photo, screenshot, or doc/docx) before I can process.`

## Output Contract

For non-agent mode:

- `Column` = field count; `row` = record count.
- "10 columns" refers to core field width, not a row-count cap.
- Output row count must equal valid surgery record count.
- Example: 11 ablation cases recognized → at least 11 rows.
- Default: strict 10-column TSV, terminating at column 10 (remarks).
- Row count is unbounded.
- Do not auto-append columns 11+.
- TSV body goes in a code block by itself — no narrative text inside the block.
- Notes (skips / rejections / suspicions) go after the code block.
- No Markdown tables as the final paste content.

Fixed column order:

1. Surgery date
2. Surgery weekday
3. Patient ID
4. Surgery type
5. Surgery category
6. Surgeon
7. Vendor
8. Week label
9. Surgery month
10. Remarks

Columns 2 / 8 / 9 must be left blank: row 3 of the target sheet has an `ARRAYFORMULA` that fills the column — writing into them overrides the array formula.

Remarks column policy:

- Do not write vendor-rule explanations (e.g. "today AF = `<vendor-x>` else `<vendor-y>`").
- Only write when an exception or human review is needed:
  - Compound procedures (e.g. `CAG + ablation`) — write the raw type string, not judgment phrases.
  - Suspected reschedule / hold.
  - Same hospitalization-ID on a different date within 7 days.
  - Surgeon or other key field ambiguous.
  - Auto-corrected surgeon anomaly — keep original schedule text, e.g. `original schedule: <name>`.

## Guardrails

- For records that are uncertain in a way that may affect accuracy: do not guess. Ask if interactive; skip and log otherwise.
- Surgeon name correction is conservative by default. But for obvious one-char garbles or known typos that map uniquely to a stable canonical name, correct directly, keep the original in remarks, and flag the auto-correction in the summary.
- In agent mode, do not overwrite human-filled `surgery_category` or other key human fields without explicit authorization.
- When the user explicitly supplies actual post-op results, overrides on the specified columns are allowed; otherwise still treat as blank-fill-only.
- If the user did not provide vendor semantics and writeback already happened, the summary must remind that vendor is still unconfirmed; the user can patch it afterward — do not silently finish.
