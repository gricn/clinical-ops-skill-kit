---
name: surgery-volume-summary
description: Strictly summarize user-supplied weekly / monthly / yearly surgery statistics into a single closed-form line. For "weekly surgery summary", "monthly surgery volume summary", "annual surgery summary" scenarios. Only sums the supplied fields (AF-family / non-AF-family / exclusions), enforces a closure check (AF + non-AF = total), and makes no medical inference or rewriting.
---

# Surgery volume standard summary

## Core goal

Generate a standardized single-line conclusion ready for department reporting from the current input. Stable wording, closed-form numbers, copy-pasteable.

## Workflow

1. Use only the data in the current message.
2. Identify mode: weekly / monthly / yearly.
3. Sum these fields:
   - surgery days
   - total surgeries
   - AF-family count
   - non-AF-family count
   - per-procedure breakdown counts
4. Handle exclusions:
   - `EPS only / ICE only / LAAC / special` go into parenthesis as exclusions.
   - Exclusions do not count toward "total of X surgeries".
5. Closure check:
   - `AF-family + non-AF-family == total`.
6. Emit a single line — no process narration.

## AF-family vs non-AF-family judgment

When data source is the sales record (Tencent Docs), not user-entered, judge by actual materials used:

1. **Has `<item-E>` → AF-family**
2. **Has `<item-A>` or `<item-B>` but no `<item-E>` → non-AF-family**
3. **No `<item-A>` / `<item-B>` → does NOT count toward surgery stats; route to exclusions:**
   - Only `<item-H>` and/or `<item-D>` → EPS only.
   - Only `<item-I>` → ICE only.

This rule explains why the same procedure label (e.g. AT, "atrial tachycardia") may fall into different categories across cases:
- AT using `<item-E>` → AF-family procedure done on AT → AF-family.
- AT not using `<item-E>` → simple-procedure AT → non-AF-family.

Note: `<item-D>`, `<item-I>`, `<item-A>`, `<item-B>` each have multiple model variants; the ones cited are the currently known set.

## Counting / wording rules

1. Sum only fields present in input — no new fields, no inferred fields.
2. If the user provides `AF-family / non-AF-family` classification directly, use it. Else apply the SKU rules above.
3. Exclusions: if input has no explicit exclusions, treat as "no exclusions".
4. Per-procedure breakdown:
   - Does not need to sum to total (compound procedures, one-stop allowed).
   - Keep original procedure names — no rewrite, no merge.
5. Output order: known procedures first in fixed order (`AF, AFL, AT, PAC, SVT, PVC, one-stop, WPW, VT`), others appended in input order.
6. EN → CN mapping (sales-record column C → weekly summary Chinese name):
   - AF → 房颤, AFL → 房扑, AT → 房速, SVT → 室上速, PVC → 室早, WPW → 预激.

## On closure failure

Single-line error, not a "normal summary":

`Validation failed: AF-family({X}) + non-AF-family({Y}) ≠ total({Z}). Source: <list inconsistent period / field>.`

## Output template

### Monthly

```
YYYY年M月（截止M月D日，如有）：手术日X天，共计X台手术（除电生理检查X台，单独超声X台，左心耳封堵X台等，如有）。房颤类X台，非房颤类X台。
X房颤，X房扑，X房速，X房早，X室上速，X室早，X一站式，X预激，X室速……
```

Constraints:
- No `（截止...）` when no cutoff.
- No exclusion parenthesis when no exclusions.
- Single line by default.
- Multi-line only when user explicitly requests.

### Weekly

`<user-given week label>：手术日X天，共计X台手术（除...，如有）。房颤类X台，非房颤类X台。[per-procedure counts]。`

Single line. Keep the user's original week label.

### Yearly

```
YYYY年年度总结：手术日X天，共计X台手术（除电生理检查X台，单独超声X台等，如有）。房颤类X台，非房颤类X台。
X房颤，X房扑，X房速……
```

Single line by default. Multi-line only when user explicitly requests.

## Output constraints (mandatory)

1. Only the final single line — no process.
2. No tables, no bullets, no explanation.
3. Consistent Chinese punctuation and units (`X天`, `X台`).
4. Do not auto-correct raw data.
5. Do not change procedure names, do not change counting scope, do not merge categories, do not infer procedure family.

## On missing data

If the user did not supply computable data, reply only:

`请提供本次周度/月度/年度手术统计数据，我将按固定口径输出单行汇总。`
