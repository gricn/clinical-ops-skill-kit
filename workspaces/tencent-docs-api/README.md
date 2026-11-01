# workspaces/tencent-docs-api/

Runtime workspace for the `tencent-docs-api-v3` shared backend.

Holds at runtime (all gitignored):

- `.env` — `CLIENT_ID`, `ACCESS_TOKEN`, `OPEN_ID`.
- `token_cache.json` — refreshed OAuth2 token state.
- `update_storage_status_state.json` — last hit window for `update_storage_status.py` (so the next run starts at the last stable range, not the top).
- `API_V3_MIGRATION_PLAN.md` — detailed migration evaluation (private only).
- `IMPLEMENTATION_SUMMARY.md` — implementation notes (private only).

Never committed.
