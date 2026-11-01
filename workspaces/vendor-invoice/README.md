# workspaces/vendor-invoice/

Runtime workspace for the `vendor-invoice-records` skill.

Holds at runtime (all gitignored):

- `<vendor>-invoice-records.xlsx` — the rolling baseline file.
- `<vendor>-invoice-records_YYYYMMDD-HHMM.xlsx` — timestamped delivery copies.
- `captures/` — screenshots from the WebView OCR pipeline.
- `history/` — past run logs.

Never committed.
