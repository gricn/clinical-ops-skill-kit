---
name: tencent-docs-api-v3
description: Tencent Docs API V3 client wrapper. OAuth2 auth, batch read/write, bounded auto-retry. Used to replace a subset of browser-automation operations and reduce API calls. The free 100/day quota covers daily inventory and sales-record updates.
---

# Tencent Docs API V3

## Capabilities

- **OAuth2 auth**: automatic token management, caching, expiry detection.
- **Batch read/write**: wraps `batchUpdate` and `read_cells`.
- **Bounded retry**: exponential backoff, default max 2 attempts.
- **Quota-friendly**: 100/day free tier is sufficient for routine ops.

## Applicable scenarios

- Inventory read.
- Surgery-date / patient-id back-fill.
- Sales-record base writes.
- **NOT applicable**: cell merge, border, filter — still require the browser.

## Default priority

- This is the **lower-level capability** under Tencent Docs flows. It is not the user-facing entry skill for coupled tasks like "ship the goods" — those default to `medical-inventory-tencent-import`, which then dispatches into this API as needed.
- Whenever a Tencent Docs step can be done with `access_token + client_id + open_id` API, prefer this path.
- For pure-read or pure-value-write steps already covered by the official API, do not default to in-page `behaviorApi / mutationApi`.
- Browser automation is reserved for what the official API does not cover: row insert, merge, border / font / alignment, filter.
- The API path must work under the free tier — never adopt "paid quota + many retries" as a baseline success contract.
- A single request failure may retry within a short bounded chain; on persistent failure, report — do not paper over with long retries.

## Usage

### 1. Basic read

```python
from skills.tencent-docs-api-v3.scripts.tencent-docs-api-v3 import create_client_from_env

client = create_client_from_env()

sheets = client.list_sheets("<doc-id>")
data = client.read_cells("<doc-id>", sheets[0]["sheetId"], "A1:J100")
```

### 2. Batch write

```python
requests = [{
    "updateRangeRequest": {
        "sheetId": sheet_id,
        "gridData": {
            "startRow": 10,
            "startColumn": 8,  # column I
            "rows": [{"values": [{"cellValue": {"text": "2026/03/27"}}]}],
        },
    }
}]

result = client.batch_update("<doc-id>", requests)
```

Notes:
- The actually writable request name is `updateRangeRequest`, not `updateCellsRequest`.
- Single `batchUpdate` carries at most 5 requests; 6 triggers a `BatchSize Validate error`.

### 3. Tests

```bash
./.venv/bin/python skills/tencent-docs-api-v3/scripts/test_smoke.py
```

## Quota

| Item | Value |
|------|------|
| Free tier | 100/day |
| Estimated daily use | 15–25 |
| Headroom | 75–85 |

**No paid plan required.**

## Environment variables

Configured under `workspaces/tencent-docs-api/.env`:

```
CLIENT_ID=<your_client_id>
ACCESS_TOKEN=<your_access_token>
OPEN_ID=<your_open_id>
```

## Doc ID mapping

| Env | Type | Doc ID |
|-----|------|--------|
| test | inventory | `<test-inv-doc-id>` |
| test | sales | `<test-sales-doc-id>` |
| prod | inventory | `<prod-inv-doc-id>` |
| prod | sales | `<prod-sales-doc-id>` |

## Limitations

- No cell merge support.
- No border setting.
- No font / alignment style.
- No filter operations.
- If an API experiment breaks the live test / prod doc, recover via Tencent Docs revision history to a clearly known version — do not "write back to look approximately right".

These features still require browser automation.

## References

- Detailed evaluation: `workspaces/tencent-docs-api/API_V3_MIGRATION_PLAN.md` (private repo)
- Implementation summary: `workspaces/tencent-docs-api/IMPLEMENTATION_SUMMARY.md` (private repo)
