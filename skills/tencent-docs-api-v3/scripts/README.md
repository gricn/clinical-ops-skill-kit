# scripts/

Implementation scripts live in the private repository. In the private repo, this directory contains:

- `tencent-docs-api-v3.py` — Core client. `create_client_from_env()` loads OAuth2 credentials, owns token refresh, exposes `list_sheets`, `read_cells`, `batch_update`. Bounded retry with exponential backoff.
- `oauth_refresh.py` — Manual OAuth2 token refresh entry point.
- `test_smoke.py` — Smoke test against the test doc.

Access to the full source can be granted for interview review.
