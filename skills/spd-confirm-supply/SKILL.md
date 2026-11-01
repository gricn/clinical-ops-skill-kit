---
name: spd-confirm-supply
description: >
  On the `<hospital>` SPD / sp.<vendor-portal>.com homepage right-side to-do, handle "you have N pending-confirm
  orders": enter the pending-confirm order detail, click "确认供货", then verify the PO appears in 待发货订单.
  Use when the user says "confirm new SPD order", "press confirm on the new order", "get this PO into the
  pending-shipment list". Reuses `order-shipment`'s session and visible browser. Does NOT handle shipment edit /
  batch / attachment / Tencent Docs coupling.
---

# SPD confirm supply

This skill is responsible for:

- Entering `待确认订单` from the SPD homepage right-side to-do.
- Opening the matching PO detail and clicking `确认供货`.
- Verifying the PO now appears in `待发货订单`.

When to use:

- "Confirm new SPD order".
- Push a new PO into `待发货订单`.
- User supplies homepage-to-do / PO number / note / same-round context — not the shipment edit page.

When NOT to use:

- Shipment edit page `发货 → 确认`.
- Batch / mfg / expiry / attachment fill.
- Batch shipment planning / shortage triage / Tencent Docs coupling.

## Shared prerequisites

- Reuses `workspaces/order-shipment/` session and the visible `Chrome Beta` (CDP `<configured-port>`).
- Stay in one visible page; no second browser instance.
- After compression / long break / context switch → re-read `order-shipment` and `references/browser-login.md` (private repo) before live clicks.

## Default I/O

- Input: currently logged-in SPD homepage `home.html`.
  - If right-side to-do `待确认订单` has only 1 item → handle directly.
  - If `> 1` → match by `purchase order number / note / audit-pass time / record`. Never blindly click the first one.
- Output:
  - Confirmed `purchase order number`.
  - Whether it left `待确认订单`.
  - Whether it now appears in `待发货订单`.
  - If a `delivery slip number` already shows on the page, record it too.

Shortest example: `"confirm new SPD order"`.

## Operation order

1. Confirm currently parked on SPD `home.html`.
2. Before reading the to-do count, even if already on `home.html`, reopen / refresh the core homepage URL. New orders may arrive while parked, and the right-side iframe will keep showing stale `0`.
3. The right-side to-do lives in iframe `block_supplier_new.html` — do not scan only the main page `body`.
4. Click `马上查看` on the matching to-do: `/pages/order/purchase_order_supplier/confirm_orders.html`.
5. On `待确认订单管理`, locate the target PO:
   - Single item: enter `详情` directly.
   - Multi-item: align on `PO number / note / audit-pass time` first, then enter `详情`.
6. Detail page is `confirm_order_form.html`. Click `确认供货`.
7. Live confirm layer order:
   - `信息 → 确定可供货么` → click `确定`.
   - `信息 → 操作成功` → prefer `前往待发货订单页面`.
   - If the success layer click fails, manual switch to `待发货订单` is also acceptable.
8. Acceptance:
   - This PO disappeared from `待确认订单管理` (or list became `无数据`).
   - After refresh, `待发货订单` returns this PO by `purchase order number`.

## Required rules

- "Already in the detail page" ≠ confirmed. Must actually click `确认供货 → 确定`.
- If `待发货订单` was already open, refresh after confirm-supply before reading. Do not judge "new order not yet present" from a stale cache.
- The acceptance signal in `待发货订单` is `purchase order number`, not just to-do-count change.
- If the new PO is not visible after confirm-supply, do a few refreshes first before treating as anomaly.
- Multiple pending-confirm orders without a unique identifier from the user → pause live clicks, ask the user for matching criteria.

## Routing

- Pre-shipment scan / planning, and `待确认订单 > 0` → this skill is the required precondition. Do not keep using a stale `待发货订单` snapshot.
- "Get a new PO into pending shipment" → this skill.
- Already in shipment edit page, goal is real `发货 → 确认` → `spd-confirm-delivery`.
- New order already in pending, still need row delete / batch / attachment / final ship → `order-shipment`.
