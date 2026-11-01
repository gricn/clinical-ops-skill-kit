---
name: vendor-invoice-records
description: On an Android device with the vendor B2B app, iterate orders, enter detail, click "申请开票" to open the invoice WebView, capture the commodity-fee and delivery-fee invoice amounts and issue time, and write within a user-specified date range to Excel (Sheet1). Used for invoice collection, polling, and print-table fill scenarios.
---

# Vendor invoice records v0.3.3

## Purpose

- Collect vendor-side invoice amounts from a B2B app and reshape into a user-aligned date-range billing Excel.
- Trigger when the user states a date range and asks to summarize / patch / verify invoice records over that range.
- Does NOT cover: voucher redemption, in-store consumption splits, merchant-portal re-issued invoices.

## Run params

- `invoice_start_date_bj` (required, `YYYY-MM-DD`).
- `invoice_end_date_bj` (optional, `YYYY-MM-DD`; with both → closed range `[start, end]`; Excel keeps only records in-range).
- `excel_file` (required; Sheet1, header on row 1).
- `max_orders` (optional, default 300).
- `merchant_exclusion_list` (optional, comma-separated; substring hit → skip the order, no Excel / sidecar write).
- `run_mode`: `write` / `dry_run` (default `write`; `dry_run` parses without table write).

Shortest example:

```bash
./.venv/bin/python skills/vendor-invoice-records/run.py \
  --invoice_start_date_bj 2026-04-07 \
  --invoice_end_date_bj 2026-04-19 \
  --excel_file workspaces/vendor-invoice/<vendor>-invoice-records.xlsx
```

- On delivery, also export a timestamped copy: `<vendor>-invoice-records_YYYYMMDD-HHMM.xlsx`.
- Same rule applies to manual edit / patch / migration deliveries — never deliver by overwriting only the baseline file.

## Device & ADB prereqs

- Android device with the vendor B2B app logged in; keep unlocked and screen on.
- Developer options + USB debugging on; `adb devices` shows `device`.
- `run.py` calls local `adb` directly — no extra bridge.
- Script launches the app; if already inside, attempts `Me → All orders` navigation.

## Key finding: invoice-status check

**⚠ The order-detail page's "invoice info" text is unreliable.**

- "You haven't added invoice info" on the detail page ≠ not invoiced.
- Must click "申请开票" to enter the invoice WebView before judging real status.
- The invoice WebView is a WebView — `uiautomator dump` cannot read it → must use **screenshot + OCR**.
- Supermarket / store-class orders may not have the standard `Order Completed` title; `commodity fee + paid + apply for refund / order again` is also a valid detail page — do not skip.

## Invoice WebView page shapes (screenshot recognition)

After clicking "申请开票", the WebView may show:

### State A — processed / submitted in progress

```
已处理（or 已提交，处理中）
开票总金额 ¥XX.XX

商品费用  ¥XX.XX          ← commodity-fee invoice amount (merchant-issued)
```

(Full state matrix lives in private repo's `references/`.)
