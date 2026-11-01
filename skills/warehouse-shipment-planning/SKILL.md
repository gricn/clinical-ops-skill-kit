---
name: warehouse-shipment-planning
description: >
  After each surgery day, compute a shipment / replenishment plan for the upstream warehouse, based on the
  "patient_id = blank" remainder rows in the formal Tencent Docs inventory and a target stock band per SKU.
  Trigger on: "compute today's shipment plan", "what's left in stock", "how much more do we need to ship",
  "build a replenishment plan from the inventory's blank-patient rows".
---

# Warehouse shipment planning

This doc is responsible for:

- After each surgery day, computing a shipment plan for the upstream warehouse from the un-used remainder in the formal Tencent Docs inventory.
- Aligning "target stock band" and "current remainder" into one shared view for downstream notification and SPD shipping.
- Producing the unified baseline that `order-shipment` will consume.

When to use:

- User says "compute today's shipment plan", "what's left in stock", "how much more do we need to ship".
- User wants to notify the upstream warehouse based on the inventory's `blank-patient / blank-hospitalization-id` remainder.
- User wants the chain `warehouse → me → hospital SPD` to start with planning before SPD execution.

This doc is NOT responsible for:

- Clicking shipment / supply-confirm / upload-attachment in the SPD page.
- Direct edits to the Tencent Docs body.
- Pinning every range-bounded SKU to a fixed value when the warehouse-specific rule has not been stated.

Business chain in scope:

`upstream warehouse → me (notify warehouse, fill SPD shipment system, fill Tencent Docs inventory) → hospital SPD`.

Default input:

- Formal Tencent Docs inventory: `https://docs.qq.com/sheet/<prod-inventory-doc-id>`
- Body rows with `patient_id = blank` represent "un-used remainder stock".

Default output:

- A shipment-plan text aimed at the warehouse operator, with at minimum: `current_remainder`, `target_stock`, `suggested_replenishment`.

Shortest example: "from the inventory's blank-patient remainder, give me today's warehouse shipment plan."

## Default read semantics

- Default to reading the formal (prod) Tencent Docs inventory, not the test sheet.
- `patient_id = blank` is the operational definition of un-used remainder.
- Aggregate by `spec / model`; never mix in rows that already carry a patient or surgery date.
- `cath lab on-hand stock` must satisfy both `patient_id = blank` AND `storage_location = cath lab`. If the recent target-model batch is still tagged `company warehouse`, list it separately as "not counted in cath lab on-hand", never silently exclude.
- Through-browser `SpreadsheetApp` reads must do a one-shot stability re-check on target models. Any change between `cath lab / company warehouse` counts → take the latest read and note the variance in the result.
- Local evidence artifact must save full blank-patient rows with `row1 / spec / code / patient_id / storage / remark` — not only the `cath lab` slice — so later we can trace which rows were excluded by `storage_location`.
- Read-only inventories prefer the `tencent-docs-api-v3` shared backend; do not disturb the visible browser unless explicitly required.
- If reading via browser profile and the page shows `D0005 / please back up / table error / pending sync after network restore / offline`, do not trust the read even if `SpreadsheetApp` still returns a row model. Recover the page per `medical-inventory-tencent-import`'s recovery chain first, then re-read.
- For "what do we need to ship today" questions, also read the same-day schedule (surgery type + surgeon at minimum), not stock alone.

## Schedule coupling

- For "what do we still need today" plans, default to reading today's `<vendor-x>` case count and surgery types, plus surgeons, before deciding defaults.
- Schedule source priority:
  - Already-written Google Sheet cathlab records.
  - If today's records are missing / abnormal / the user wants the originals, fall back to schedule images / Word docs.

## Configurable planning rules

Production procedure bundles, surgeon preferences, stock targets, product aliases
and packing dimensions remain in private configuration. No real operational
values are included in this public example.

For each generic item, calculate projected remainder as current stock minus
confirmed expected consumption, then compare with the configured target band.
Unknown procedure or operator rules require human review; never infer preferences.

Synthetic example only (not a real product or stock policy): item A has current
stock 4, expected consumption 1 and target 6, so suggested replenishment is 3.
Packing uses privately supplied dimensions and handling constraints.

## Default plan format

When the user asks "what do we need to ship today":

- First call `warehouse-shipment-dida-task` to create / update an empty-body `📚Work / <hospital> shipment` placeholder task for the day.
- Lead with the shipment verdict — do not preface.
- Output `min_shipment_estimate` and `max_shipment_estimate`.
- Then `current_stock`, `projected_consumption_today`, `projected_remainder_after`.
- Analysis goes last, not interleaved with the verdict.
- "Don't ship today" is also a verdict — state it first.
- An explicit "ship today: SKU × N" from the user pins that quantity as the final decision; `min/max` then becomes background-only.
- "Recent error / complaint / risk uptick on SKU X" from the user is a per-batch safety buffer, not a permanent target-stock rewrite (unless the user says so).

For fixed-target SKUs: `current_remainder`, `target`, `suggested_replenishment = target - current`.

For range-target SKUs: `current_remainder`, `target_band`, plus `distance to lower bound` and `distance to upper bound`. Do not collapse the band into a single number on the agent's own initiative.

## Default output template

```text
Verdict: ship today.

min_shipment_estimate
`<item-B> × ?`
`<item-G> × ?`

max_shipment_estimate
`<item-B> × ?`
`<item-D> × ?`
`<item-G> × ?`
`<item-J> × ?`

**current_stock**
... (full SKU list)

**projected_consumption_today**
... (today's bundle)

**projected_remainder_after**
... (full SKU list)

-----------

analysis
- stock source: prod inventory blank-patient remainder
- today's vendor-x: surgery_type × ?, surgeon ?
- min = replenish to lower bound
- max = replenish to upper bound
```

## Relationships with other skills

- Plan-only run: stop here.
- For "today's shipment plan", chain to `warehouse-shipment-dida-task` to create / update an empty-body shipment placeholder; once the user confirms the day's final list, chain again to fill the body.
- To continue with hospital SPD execution, switch to `order-shipment`.
- To later patch actual arrivals into Tencent Docs body, chain to `medical-inventory-tencent-import`.

## Open rules (not yet decided)

- Warehouse-specific shipment SLAs / cut-off times.
- Whether range-target SKUs default to lower bound or upper bound when not pinned.
- Buffer rules for back-to-back surgery days / pre-holiday stocking.
