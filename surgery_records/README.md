# surgery_records/

Raw business records layer. **Nothing in this directory is ever committed.**

Holds daily surgery markdown records keyed by date:

```
surgery_records/
├── YYYY/
│   ├── MM/
│   │   ├── YYYY-MM-DD.md
│   │   ├── YYYY-MM-DD.md
│   │   └── ...
```

Each file is a free-form markdown record of one day's cases, written either by the operator or generated as the `vendor-sales-inventory-sync` closeout artifact. Contents may include:

- Patient identifiers
- Procedure types
- Surgeon names
- Material UDIs and barcode scans
- Same-day complaint or anomaly notes

All of this is regulated and never leaves the device. Both `surgery_records/` (this directory) and the runtime `workspaces/` are gitignored at the root level.

## Why this is a separate layer

`workspaces/` and `surgery_records/` are both gitignored, but they serve different purposes and have different retention rules:

- `workspaces/` — disposable runtime data (caches, screenshots, intermediate JSON). May be wiped between runs.
- `surgery_records/` — the canonical raw daily record. Retained for the operator's business need; never auto-cleaned by skills.

The `surgery-summary` skill reads from here. The `surgery-volume-summary` skill consumes that aggregate. Nothing else writes here.
