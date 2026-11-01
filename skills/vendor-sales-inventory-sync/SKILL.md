---
name: vendor-sales-inventory-sync
description: >
  When the user says "materials have arrived", "today's materials are in the cath lab", or similar, auto-trigger this skill. By default read today's Google Sheet surgery records, keep only one specified vendor's `<procedure-AF-family>` / `<procedure-non-AF-family>` cases, run OCR on package-label photos, cross-check against barcode and QR with vendor-prefixed UDIs, and run the full pipeline through sales-record / inventory writeback and closeout gates. Also handles "sync vendor-x cases after on-site work", "read today's vendor-x cases first", "OCR the material sticker photos".
---

# Vendor-x sales / inventory sync (thin entry)

This skill is shaped as:

- **Thin entry**: this file holds the goal, hard rules, default environment, and step routing.
- **Small playbooks**: each step loads its closest rule file as needed.
- **Deep references**: opened only when the current step requires them.

The goal: avoid reading the whole skill every round; cut context cost; raise speed and stability.

## Default data source

- Spreadsheet ID: `<cathlab-summary-sheet-id>`
- Tab: `<cathlab-summary-sheet-name>`
- Default credentials: `secrets/google-sa.json`
- Timezone: `Asia/Shanghai`

## Current hard rules

1. After each on-site round, read the corresponding day's Google Sheet records first.
2. If the user did not state a date, default to today.
3. If the user gave an explicit date, use that date.
4. Process only `vendor = <vendor-x>`.
5. Keep `surgery_category ∈ {<procedure-AF-family>, <procedure-non-AF-family>}`.
6. Save the filtered set locally as structured JSON for downstream reuse.
   - Pre-check today's schedule first. If after the vendor-x + category filter today is 0 cases, "today's daily / week-closeout" must not trigger by itself.
   - Weekly summary triggers only when "this week is closed". Closure is judged by China-Mainland natural week (Mon–Sun), anchored at the last vendor-x surgery day's last consumable line. If Sunday has surgery, week summary goes on the Sunday line, even if Thursday / Friday was the last real work day.
   - Before writing or moving column `K` weekly summary, walk up column `A` from the target `K` row to confirm the surgery date's natural week is closed; then walk down to the next non-blank `A` date — if it falls in the same natural week, do not write into the current `K`.
   - 0 cases today on the vendor-x filter does not by itself trigger this week's summary; only confirmed "no more vendor-x cases this week" or backfilling a previously missed prior week is allowed.
   - If a later vendor-x case is added, re-run today's chain from the latest Google Sheet; if this week's summary already exists, recompute and overwrite, migrate `K` to the latest surgery day's last consumable line, clear the old anchor.
   - Google Sheet is the live case-state source of truth. On `cancel / hold / reschedule`, write back to Google Sheet first, then re-read — never treat local `history/*.json` as truth.
   - For confirmed cancelled / held / rescheduled rows, change `surgery_category` to `其他` ("other") and append `"<procedure-AF-family> cancelled (specific reason)"` to the original `remarks`. Downstream only carries `<procedure-AF-family> / <procedure-non-AF-family>` forward.
   - Cancellation reasons must be the actual same-day reason; do not adopt a single boilerplate.
   - On explicit `surgery_type` correction, rewrite Google Sheet first, then append the original value into `remarks` as `original surgery_type: <old value>` — no silent overwrite.
7. Pre-run cleanup: `history` retained 7 days; image artifacts retained 3 days.
8. Until full sales / inventory write rules are stabilized, stop at "filtered + reported candidate cases" — do not guess sales-table / inventory-table column mappings.
9. When the user points out a wrong rule understanding, omission, or bug, the lesson must be written back into this skill or the relevant `references/` file in the same round.
10. Together with rule update, do a first-pass fix in the same round — do not respond with "got it" only.
    - On-site material photos use vendor-prefixed UDI (`<vendor-prefix>`) as the primary anchor. Pin UDI first, then the inventory's unique-match row provides `commodity_name / spec / family` ground truth.
    - Adjacent model codes, short-names, handwritten labels are OCR-corrected and human-checked, not hard gates.
    - When `<vendor-prefix>` UDI has no nearby model code: continue. When the nearby model conflicts with the UDI's inventory row: default to the inventory row, do not stop on this conflict.
    - Business output normalizes by family / short-name: `<item-A>`, `<item-B>`, `<item-D>`, `<item-E>`, `<item-F>`, `<item-G>`, `<item-H>`, `<item-I>`, `<item-J>`.
    - `<item-A>` and `<item-B>` are two distinct big-ticket subfamilies — never merge `<item-A>` back into `<item-B>` in the final output.
    - Currently only single-curve big-ticket SKUs are in scope; dual-curve appears later → confirm against physical and inventory before naming.
    - A single surgery cannot contain two big-ticket SKUs. If a parse yields `<item-A> + <item-B>`, `2 × <item-A>`, or `2 × <item-B>` — flag as a grouping error and split into at least 2 surgery candidates before continuing.
11. While a live case is not truly closed, do not switch to skill refactoring, flow optimization, or extra experiments.
12. Live tasks like `update surgery data` must run the completion gate. No gate → no "done".
    - Final closeout: re-read `references/live-acceptance-checklist.md` (private repo). This short checklist cannot be replaced by "context compression" / "I remember checking it". Any uncovered item → only `部分完成 / 未完成` is allowed.
    - For inventory `patient_id = blank` closeout filtering, follow `references/inventory-filter-playbook.md` (private repo).
    - Inventory filter range must be row 2 `A:L` (title row, not row 1 which is the sheet name).
    - Script / completion gate must verify `workbookRange.range.startRowIndex == 1`, `startColIndex == 0`, `endColIndex == 11`, and verify `A2=index / B2=arrival_date / J2=patient_id / L2=remarks`. If not satisfied: cancel the wrong filter and rebuild — do not keep stacking `J`-column conditions.
    - UI default path: `J column → by condition → content type → cell is blank → OK` — not "scroll to the bottom of the value list".

## Out of scope

- This skill does not implement the writeback details of the sales / inventory tables. Until rules stabilize, the user owns the write step.
- Cross-vendor blending is out of scope.
