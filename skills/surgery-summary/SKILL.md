---
name: surgery-summary
description: Summarize daily surgery records from markdown files under `surgery_records/YYYY/MM/`.
---

# Surgery summary

## Purpose

Process daily surgery markdown files under `surgery_records/YYYY/MM/` and emit a base aggregate.

## Input

Files named `YYYY-MM-DD.md`. Each file typically contains:

- Surgery schedule (plain text or list).
- Barcode scans (code blocks).
- Notes.

## Workflow

1. **Identify target files** — all `.md` under `surgery_records/YYYY/MM/`.
2. **Extract** — per file:
   - Parse date from filename.
   - Count surgeries.
   - Pull patient ID, procedure name, consumables if present.
3. **Emit** — table or list:
   - columns: date, total surgeries, key notes.

## Usage

Run for a quick overview of surgery volume / details over a chosen period. Feed the result into `surgery-volume-summary` for the standardized single-line report.
