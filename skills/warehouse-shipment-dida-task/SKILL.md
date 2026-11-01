---
name: warehouse-shipment-dida-task
description: >
  When the day's `<hospital>` shipment plan is still pending, create an empty-body `📚Work / <hospital> shipment`
  placeholder task. When shipment quantities are finalized, update the task body with the day's shipment info on a
  fixed template. Use for "log today's shipment to TickTick", "create the <hospital> shipment task",
  "sync TickTick when shipping from the warehouse".
---

# `<hospital>` shipment TickTick task

This skill is responsible for:

- Generating a fixed-template task body from the day's confirmed shipment lines.
- When the day's shipment plan is requested but quantities are not yet confirmed, creating / updating an empty-body `<hospital> shipment` placeholder.
- Reusing the existing `dida-tasks` skill to create / update the task under project `📚Work`.
- Only when ALL three conditions hold — "this round's SPD has already partially shipped + this round's real demand minus SPD pending-receipt and pending-shipment remaining is still in deficit + the next round's new plan is not yet formed" — default to creating a next-day follow-up task `<hospital> SPD remaining goods to ship`.
- Default also creates a next-China-Mainland-business-day `<hospital> delivery` task.
- Avoid creating multiple same-title tasks on the same day.

When to use:

- "Log today's shipment to TickTick" / "Create the `<hospital>` shipment task" / "Sync TickTick when shipping from the warehouse".
- "Build a shipment plan from today's schedule and inventory" / "Estimate remaining material and build a shipment plan" — quantities not yet locked → create empty-body placeholder.
- Quantities already locked → sync to TickTick.
- Hand-off from `warehouse-shipment-planning` or `order-shipment`.

When NOT to use:

- Infer / rewrite shipment quantities.
- Replace the generic `dida-tasks` skill for unrelated TickTick items.
- Read / modify Tencent Docs inventory body.

## Default input

- Shipment date: today (Beijing time).
- Shipment lines: blank allowed when not yet locked; once locked, in the user-confirmed order as `spec=N` or `spec × N`.
- Title: `<hospital> shipment`.
- Project: `📚Work`.

## Default output

- One task under `📚Work` titled `<hospital> shipment`:
  - Task date: actual shipment day.
  - Body: blank while quantities pending; once locked, first line = actual shipment date.
- Plus, by default, one `<hospital> delivery` task:
  - Task date: next China-Mainland statutory business day (including holiday-swap).
  - Body: blank.
- Body template once locked:

```text
YYYY/MM/DD（周X）<hospital> shipment：
<item-B> × 3
<item-D> × 1
```

- Only when "this round partially shipped + remaining deficit confirmed + new plan not yet" — create / update a next-day task `<hospital> SPD remaining goods to ship`:
  - Locked specs / quantities → body lists them directly.
  - Unlocked → body blank.

## Relationship

- Upstream: `warehouse-shipment-planning` (creates the placeholder when planning starts).
- Sibling: generic `dida-tasks` (this skill orchestrates the specialized `<hospital>` shipment use case).
