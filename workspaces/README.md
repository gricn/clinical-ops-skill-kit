# workspaces/

Runtime data lives here, not under `skills/`. This split is deliberate:

- `skills/` is the **capability layer** — versioned, reusable, code-reviewable.
- `workspaces/` is the **runtime layer** — business inputs, outputs, captures, browser profiles. Disposable, gitignored except for the per-workspace README.

## Layout

Each workspace is owned by one skill (or one functional collection). The owning skill consults its workspace at runtime; nothing else touches it.

| Workspace | Owning skill / collection | Use |
| --- | --- | --- |
| `cathlab-schedule-ocr/` | `cathlab-schedule-ocr` | Cathlab schedule recognition runtime inputs / outputs |
| `vendor-sales-inventory-sync/` | `vendor-sales-inventory-sync` | Vendor on-site case data, images, browser profile |
| `medical-inventory-tencent-import/` | `medical-inventory-tencent-import` | Inventory conversion artifacts, Tencent Docs browser profile |
| `vendor-invoice/` | `vendor-invoice-records` | Vendor invoice cache and capture results |
| `order-shipment/` | `order-shipment` | SPD session, attachments, plans, browser profile |
| `tencent-docs-api/` | `tencent-docs-api-v3` | Tencent Docs API credentials, local evaluation, experiment notes |

## Standard subdirectory pattern

Each workspace may contain (created on demand):

```
workspaces/<name>/
├── inbox/        runtime input drop point
├── sources/      raw assets (images, PDFs, screenshots)
├── history/      execution traces / past runs
├── outputs/      generated artifacts (TSV, Excel, JSON)
├── captures/     screenshots taken during a run
├── temp/         scratch
├── processed_orders/   business-specific state
└── browser-profile-beta/   Chrome Beta profile (per-workspace, never shared)
```

All of these are gitignored. The per-workspace `README.md` and `.gitkeep` are the only things committed.

## Why this split

In the private repo, this directory holds real schedules, real patient identifiers, real surgery dates, and live browser-session cookies. None of that belongs in version control, ever. The capability / runtime split lets the agent design get reviewed without touching regulated data.
