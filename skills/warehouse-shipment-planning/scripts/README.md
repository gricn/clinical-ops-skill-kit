# scripts/

Implementation scripts live in the private repository. In the private repo, this directory contains:

- `compute_remainder.py` — Reads the prod inventory via `tencent-docs-api-v3`, groups blank-patient rows by spec, applies `cath lab + company warehouse` storage-bucket rules.
- `consumption_estimator.py` — Cross-references today's cathlab schedule (or its writeback rows) with the per-procedure / per-surgeon default bundle table to estimate today's consumption.
- `emit_plan.py` — Composes the final report (`verdict / min / max / current / projected / analysis`) and triggers the empty-body `warehouse-shipment-dida-task` placeholder when relevant.

Access to the full source can be granted for interview review.
