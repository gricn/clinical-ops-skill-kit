# Cathlab schedule decision rules (excerpted)

> Desensitized excerpt of the in-repo rule book. The full rule set in the private repo covers ~15 sections; the headings and a few representative rules are kept here to show the shape of the decision logic.

## 1. Date inheritance

- The date in the filename, in the doc body's `日期：` line, and in the user's latest stated date may disagree. Resolution order: user latest > filename > doc body.
- If the same Word doc contains multiple `日期：` markers, treat the latest one as the date for all subsequent rows until the next `日期：`.

## 2. Cath room inheritance

- Cath room labels (`<room-A>` / `<room-B>` / ...) carry forward downward inside a Word doc.
- An image is a single cath room snapshot — do not infer multi-room layout from one image.

## 3. Patient ID validation

- Hospitalization IDs in this domain are fixed digit-width. Anomalies (too short / too long / non-digit) trigger a remarks flag, not a rejection.
- Same hospitalization ID on different dates within 7 days → remarks flag for human review.

## 4. Surgeon canonicalization

- Known canonical surgeon set: `<surgeon-A> / <surgeon-B> / <surgeon-C> / <surgeon-D> / ...`
- Soft correction: one-char garbles that map uniquely to a canonical name.
- Hard reject: stop guessing and write the original string when correction would be ambiguous.

## 5. Surgery type filtering and category mapping

- Pre-defined inclusion set (atrial fibrillation / non-AF ablation procedures) and exclusion set (diagnostic catheterization only, biopsy only, etc.).
- A compound procedure (e.g. `<procedure-X>+<procedure-Y>`) is written into `surgery_type` verbatim; do not split into two rows.
- Category mapping is a small fixed table; if a type is not in the table, the record is still emitted but the category cell is left blank.

## 6. Sorting

- Sort key: surgery date → cath room → ocr_order (the within-image / within-doc reading order).
- Equal date + room → preserve ocr_order; never alphabetize by patient name or surgeon.

## 7. Vendor judgment

- Vendor is inferred per surgery type per day, using the team's stated rule (e.g. "today AF = `<vendor-x>`, others = `<vendor-y>`").
- Vendor never goes into remarks. Unconfirmed vendor → summary reminder.

## 8. Compound procedure remarks

- For `<procedure-X>+<procedure-Y>` compound rows, write the raw type string into remarks verbatim — do not append words like "need review".

## 9. Reschedule / hold / cancel

- Same-day post-recognition changes must be applied to the canonical Google Sheet row, not the local cache or temp JSON.
- Holds and cancels become `surgery_type` overrides plus a remarks flag.

## 10. Formula vs plain-text history check

- Before writeback, read the last 3–5 rows of the target tab.
- If `surgery_weekday / week_label / surgery_month` are formulas in history, the new rows must leave those cells blank (`ARRAYFORMULA` fills them).
- If they are plain text in history, new rows must write the plain text values.
- Mixing the two breaks the column's downstream consumers.
