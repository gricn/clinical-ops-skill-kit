---
name: order-shipment
description: >
  Full pipeline for `<hospital>` SPD / sp.<vendor-portal>.com shipment orders: login, scan pending shipments,
  lock this round's scope (this batch from Excel / Tencent Docs, today's new stock, or the entire pending list),
  lot-level shipment allocation, print delivery slips, clean stray fields, attach customs documents, confirm shipment.
  Trigger on "go SPD ship", "scan pending shipment", "look at today's stock", "run the shipment",
  "continue shipment", "did shipment slip N go out", "upload customs doc", "select customs doc",
  "sp.<vendor-portal>", "<hospital> shipment", "regular shipment", "pending shipment", "next slip", "ship the goods".
  If an Excel / table list is attached, default scope is "SPD shipment + Tencent Docs inventory sync" as one coupled task.
---

# Order shipment pipeline

## Purpose

In the supply-chain coordination system (SP / MSCM), drive shipment orders end-to-end: login, scan pending, lock the round's scope, match stock, clean stray fields, all within one visible browser page.

## When to load additional references

- Login / Chrome Beta / captcha / profile / single-page attach rules → `references/browser-login.md` (private repo).
- Pending order sort / stock match / lot-level rules / attachment order → `references/pending-order-rules.md` (private repo).
- Paths, dirs, output locations, workspace migration → `references/workspace-layout.md` (private repo).

## Core constraints

- Attended flow uses a visible browser by default; no headless.
- Use `Chrome Beta` by default.
- Visible SPD session reuses the existing visible `Chrome Beta` (CDP `<configured-port>`); script exit detaches control but does not close the page.
- Stay in one page when possible — no random new tabs, tab close, or full-browser restart.
- Python / Playwright commands always use `./.venv/bin/python`.
- "Ship the goods" without scope reduction → both SPD shipment AND Tencent Docs body sync.
- "<hospital> shipment" with an Excel / table list → same coupled scope.
- Coupled-task default skill combo: `order-shipment` + `medical-inventory-tencent-import`. This skill owns SPD shipment and orchestration; Tencent Docs writes belong to the inventory skill.
- If the same batch goes through parallel agents for SPD and Tencent Docs, both must share the same baseline `shipment_plan` and the same `inventory_by_tencent_order_*.xlsx|tsv` artifact — never split into two batches.
- Parallel ≠ pre-flip state: until SPD truly confirms shipment, do not flip Tencent Docs body `storage_location` from `company warehouse` to `cath lab`.
- Login URL: `https://sp.<vendor-portal>.com/pages/login.html`.
- Home URL: `https://sp.<vendor-portal>.com/pages/home.html`.
- Captcha OCR: max 5 retries; then fall back to human input.
- Lessons confirmed in this round must be written back to `SKILL.md` / `references/*.md` in the same round — not "I'll remember it for next time".
- The SPD live shipment approval gate (`AGENTS.md`) applies: before any live row delete / add / quantity edit / attachment upload / `保存` / `发货` click, post the full plan in chat and wait for explicit approval.
- After thread compression / long break / context switch, re-read this `SKILL.md` and `references/pending-order-rules.md` before resuming any live click. Restate 1–3 active rules of the round in chat first.

## Speed discipline

- SPD live ops target: "fast close-out of a single real shipment slip" — not exploratory click-and-watch.
- Default per-slip path collapses to:
  1. Refresh pending list, lock the live order number.
  2. Enter edit page.
  3. One-pass row delete / add to target lines.
  4. One-pass fill of batch dates.
  5. One-pass attachment upload.
  6. Direct `发货 → 确认`.
  7. Verify the red `取消发货` button on the order detail.
- With baseline / gap / attachment locked, do not re-think the plan / re-read old logs / wait for the system to self-fix.
- Plan reports stay short — only this round's slips, specs, lots, attachments. Background already locked is not re-narrated.
- After the same live error twice in a row, no more chat-memory fixes — write the rule back first, then continue.

## Routing

- If the user says "confirm new SPD order" → switch to `spd-confirm-supply`. Do not jump to the pending-shipment page wondering "where is it".
- If the user says only "confirm current pending slip" and the slip's rows / dates / attachments are ready → switch to `spd-confirm-delivery`. Do not re-narrate the whole plan.

## Cross-skill relationships

- Coupled with `medical-inventory-tencent-import` for "ship the goods + sync inventory".
- Preceded by `spd-confirm-supply` when a new purchase order has not yet entered the pending list.
- Followed by `spd-confirm-delivery` for the fast close-out of an already-prepared current slip.
- Preceded by `warehouse-shipment-planning` when a plan baseline is required first.
