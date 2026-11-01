# workspaces/medical-inventory-tencent-import/

Runtime workspace for the `medical-inventory-tencent-import` skill.

Holds at runtime (all gitignored):

- `outputs/` — `inventory_by_tencent_order_YYYY-MM-DD.xlsx` and matching `.tsv`. Auto-cleaned after 7 days.
- `artifacts/verification/` — per-run acceptance JSON; status flips to `verified` only when this artifact says so.
- `browser-profile-beta/` — Chrome Beta profile dedicated to Tencent Docs writeback. Never shared with the user's stable Chrome.

Never committed.
