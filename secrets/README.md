# secrets/

Local credential layer. **Nothing in this directory is ever committed.**

What lives here in the private repo:

- `google-sa.json` — Google Service Account credentials for Sheets access.
- `tencent-docs.env` — OAuth2 credentials for the Tencent Docs API V3 client.
- `spd-cookies.json` — Saved login state for the SPD attended browser (when applicable).
- `dida-token.txt` — TickTick / Dida API token for `warehouse-shipment-dida-task`.
- `adb-device.txt` — Pinned Android device serial for the `vendor-invoice-records` ADB session.

These never enter version control (see root `.gitignore`). They are kept out of `workspaces/` on purpose, so that the credential layer is a separate, smaller surface to audit.

## Why a dedicated `secrets/` layer

Three reasons:

1. **Smaller blast radius.** Skills that need only runtime data go to `workspaces/`. Only the few skills that need credentials reach into `secrets/`.
2. **Easier to spot leaks.** Any commit that touches `secrets/` is anomalous. A single grep on history can audit it.
3. **Easy to rotate.** When a token expires or leaks, it's one directory to wipe and re-fill — no scavenging across the repo.

## What never goes here

- Patient identifiers / surgery records — those belong in `surgery_records/` (and are also gitignored).
- Runtime captures / outputs — those belong in `workspaces/<name>/`.
- Skill scripts or rules — those belong in `skills/<name>/`.
