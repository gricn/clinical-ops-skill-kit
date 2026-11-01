# scripts/

Implementation scripts for this skill live in the private repository. In the private repo, this directory contains:

- `convert_inventory.py` — Excel → Tencent Docs import shape converter (rule v4). Owns encoding repair, UDI detection, sort, integrity self-check, output file naming, arrival-date computation.
- `write_tencent_docs_attended.py` — Attended-browser writeback driver. Reuses existing `xlsx/tsv` when present; supports `--prepare-only`, `--open-only`, `--cdp-port`, `--skip-profile-check`, `--tsv-input`, `--xlsx-input`, `--test-doc`.
- `update_storage_status.py` — API-path arrival-status flip (`company warehouse → cath lab`) with `--dry-run`. Records last hit-window state under `workspaces/tencent-docs-api/`.
- `update_storage_status_attended.py` — UI-path arrival-status flip for cases the API cannot reach. Supports `--plan-only`, `--xlsx-input`, `--url`.
- `repair_arrival_date_format_attended.py` — Fix-in-place `B` column to true date cells (with `numberFormat`) for historical rows polluted into plain text.

Plus shared helper modules.

Access to the full source can be granted for interview review.
