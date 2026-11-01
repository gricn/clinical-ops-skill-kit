---
name: spd-confirm-delivery
description: >
  Fast path: in the `<hospital>` SPD / sp.<vendor-portal>.com visible page, complete the current pending slip's
  `发货 → 确认` chain and verify success. Use when the user is already in the SPD page / pending edit page,
  or when the target pending slip / purchase order number is known, and only needs "confirm shipment of the
  current slip" / "press confirm on this slip". Reuses `order-shipment`'s session, workspace, and confirm script.
  Does NOT handle: homepage to-do `确认供货` for new orders, batch scanning, plan splitting, attachment fill,
  or Tencent Docs coupling.
---

# SPD confirm delivery

This skill is responsible for:

- Reusing the current SPD visible browser page to complete a single pending slip's confirm fast path.
- Depending on the current page state, deciding whether to click `发货` first, then walk through `0 / 1 / 2`-layer confirm dialogs.
- Acceptance: the red `取消发货` button on the order detail page.

When to use:

- User says "confirm the order in SPD" / "press confirm" / "confirm the current slip".
- Currently in the `unfilled_delivery_form.html` edit layer.
- Or `delivery slip number` / `purchase order number` is known and findable in the pending list.
- And the slip already has a user-approved shipment plan in this thread.

When NOT to use:

- Scan the entire pending list.
- Generate a shipment plan from Excel / Tencent Docs.
- Fill attachments / batch dates / clean unrelated rows.
- Post-shipment Tencent Docs inventory sync.

## Shared prerequisites

- Reuses `workspaces/order-shipment/` and `skills/order-shipment/scripts/confirm_pending_delivery.py`.
- Python via `./.venv/bin/python`.
- Attended only; attach to current `Chrome Beta` (CDP `<configured-port>`).
- Healthy edit page → don't open new tabs, don't close the current tab, don't restart SPD "for safety".

## Required rules

- Success = the red `取消发货` button on the detail page, NOT "the click went through".
- This skill cannot bypass the SPD shipment approval gate in `AGENTS.md`. Without a prior approved plan in this thread: stop, post a one-slip plan summary, wait for approval.
- Before approval: do not click `发货`, do not click confirm, do not assume "only one click left, just send it".
- `发货` may surface `0 / 1 / 2` layers of confirm dialogs; the script may handle them in one pass — no manual "save first then ship" split.
- If already parked on a confirm dialog, pass `--skip-trigger` so `发货` is not clicked twice.
- "保存成功" / dialog dismissed ≠ shipped per plan. Re-read live state once; only on plan-match record success.
- Missing attachment / abnormal field / page error / dead selector → stop, switch back to `order-shipment` for full pipeline triage.
- After thread compression / long break / context switch: re-read `order-shipment` and `references/pending-order-rules.md` (private repo) before any live click.
- Same action 3× in a row without state change → treat as bug, do not keep clicking.

## Default command

```bash
./.venv/bin/python skills/order-shipment/scripts/confirm_pending_delivery.py --order-code <slip-number>
```

Common flags:

- `--po-code <purchase-order-number>` — when slip number is unknown but the PO has only one pending slip.
- `--skip-trigger` — when already on a confirm dialog.
- `--dry-run` — probe only.
- `--slowmo-ms 220`
- `--cdp-port <configured-port>`

Default output:

- `workspaces/order-shipment/TMP/confirm_pending_delivery_result.json`

## Routing

- New PO not yet in pending list → `spd-confirm-supply`.
- Slip is fully prepared (attachment / batch / mfg / expiry) and plan approved → this skill.
- Still need to delete / add rows / fill dates / attach files / triage shortage → `order-shipment`.
- After confirmed shipment, when Tencent Docs inventory needs sync → chain to `medical-inventory-tencent-import` (only after SPD truly confirms; only then may `storage_location` flip).
