# workspaces/order-shipment/

Runtime workspace for the `order-shipment`, `spd-confirm-supply`, and `spd-confirm-delivery` skills.

Holds at runtime (all gitignored):

- `TMP/` — per-run result JSON (e.g. `confirm_pending_delivery_result.json`).
- `processed_orders/` — record of already-shipped slips.
- `attachments/` — staged customs documents per slip.
- `plans/` — approved shipment plans (the "checklist" referenced by AGENTS.md's shipment approval gate).
- `browser-profile-beta/` — Chrome Beta profile for the SPD session (configured CDP port).

Never committed.
