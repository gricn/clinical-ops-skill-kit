# workspaces/vendor-sales-inventory-sync/

Runtime workspace for the `vendor-sales-inventory-sync` skill.

Holds at runtime (all gitignored):

- `inbox/` — on-site material photos for the day.
- `history/` — filtered case JSON, retained 7 days max.
- `outputs/` — sales-record / inventory writeback drafts.
- `captures/` — material-photo OCR intermediates, retained 3 days max.
- `browser-profile-beta/` — Chrome Beta profile for Google Sheet access.

Never committed.
