---
name: medical-inventory-tencent-import
description: Strictly convert medical-material inventory Excel (.xls/.xlsx) into the Tencent Docs import shape (fixed 10 columns), and by default continue with an attended-browser writeback into the live Tencent Docs sheet. Also handles arrival-status flip: when delivered goods reach the cath lab, batch-update existing body rows' `storage_location` from "company warehouse" to "cath lab". Stops at local `xlsx/tsv` artifacts only when the user explicitly requests file-only mode. Rule version v4: .xls → .xlsx first; conditional encoding repair; vendor-prefixed UDI content detection; abort on integrity self-check failure.
---

# Medical inventory → Tencent Docs import

This doc is responsible for:

- Reshaping medical-material inventory tables into the Tencent Docs import column order (10 columns).
- Specifying that the default completion gate in Codex / agent mode is "Tencent Docs has been updated", not "local xlsx/tsv produced".
- Specifying when to reuse a pre-built `xlsx/tsv` artifact vs re-reading the raw Excel.
- Specifying how to batch-flip `storage_location` from `company warehouse` to `cath lab` after delivery.

When to use:

- User supplies an `.xls/.xlsx` inventory file and wants it imported into Tencent Docs inventory.
- User already has a `inventory_by_tencent_order_YYYY-MM-DD.xlsx/tsv` and wants to continue with the writeback.
- User asks to fix encoding garbles, sort by `spec + lot`, or import to Tencent Docs.
- User says "today's delivery arrived at the cath lab" / "flip this batch to cath lab".

This doc is NOT responsible for:

- Logging into Tencent Docs or requesting access permissions.
- Choosing test vs prod environment on the agent's own initiative.
- Continuing the writeback when the user explicitly says "file-only / prepare-only".

Rule version: `v4`.

## Default completion semantics

- In Codex / agent mode, this skill's default endpoint is "Tencent Docs has been updated" — not "the local xlsx/tsv has been produced".
- Only stop at local artifacts when the user explicitly says "file only" / "do not write Tencent Docs yet" / "prepare-only".
- If this task has already produced `inventory_by_tencent_order_YYYY-MM-DD.xlsx` or its companion `tsv`, prefer reusing that artifact for the writeback rather than re-reading the raw Excel.
- After a thread compression / long pause / context switch, re-read this SKILL.md before resuming a live Tencent Docs operation — do not act on chat memory alone.
- After a compression / resume, restate the active write-and-validation contract in chat (target batch, arrival date, current-page acceptance bar) before any live click or paste.
- If you find yourself acting on residual chat memory rather than on `current SKILL.md + already-built xlsx/tsv + current page state`, stop, re-read, and resume.
- If the user goal is not just inventory import but "after Tencent Docs is written, continue with hospital SPD shipment", default to switching into `order-shipment` after writeback — do not stop at "Tencent Docs updated".
- If the user says "ship the goods" with an Excel / table list attached, default to a coupled task: SPD shipment **and** Tencent Docs body sync. Unless the user explicitly scopes to one side, Tencent Docs body sync is not optional.

## Codex default behavior on coupled tasks

- Default skill combo for `ship the goods`: `order-shipment` + `medical-inventory-tencent-import`, where this skill handles the inventory business rules and writeback, and the underlying API layer is provided by `tencent-docs-api-v3`.
- When the user only says "ship the goods", the Tencent Docs side defaults to "patch / sync inventory body rows", not "auto-flip storage_location to cath lab". `storage_location` stays `company warehouse` until the user explicitly says delivery arrived.
- When context is "ship today / sync inventory after shipping" and the user did not separately specify `arrival_date`, default `arrival_date` to Beijing-time next business day — do not piggyback on a same-day existing batch row.
- If the user later says "this batch has arrived at the cath lab" and asks to update inventory, upgrade the completion gate to "the corresponding body rows' `storage_location` has been updated from `company warehouse` to `cath lab` in Tencent Docs" — do not leave that step to manual follow-up.

## Tencent Docs browser policy

- Without an explicit user request to backfill historical batches, default to importing only the explicitly specified input file and arrival-date batch — do not slip in prior batches.
- For weird multi-sheet shipment / inventory workbooks, default to reading only the first sheet — do not switch to auxiliary tabs like `quote sheet` or `Sheet1` on the agent's own initiative.
- If the first sheet has a header `spec` but the column is empty while `commodity_code` or `model` has values, fall back: `spec → commodity_code → model`.
- Title + header rows in the existing Tencent Docs sheet are protected:
  1. Row 1 is the title row.
  2. Row 2 is the header row.
  3. The default append flow may write only the body — never modify, merge, undo, or reorder rows 1–2.
  4. Title edits require an exact user-provided string; never guess.
  5. Both before and after a body write, verify rows 1–2 are unchanged. Any change to those cells → failure.
- Tencent Docs flows must use a single visible browser page — no `headless`.
- If the page lands on a Tencent Docs login / permission screen and WeChat is logged in locally, default to clicking `WeChat` / `Quick Login` first. Only fall back to manual login if quick login fails.
- A `footerOverlayInGrid=true` alone, with normal `activeSheet + visibleCanvasBoard` and no `floatingSelectionGhost / 12004 / service-anomaly / loading-mask`, counts as continuable — do not misread it as a broken page.
- Do not force the browser to the front when running. Even after the script has attached to the right profile and reached the right page, do not steal foreground just to "prove the attachment".
- In Playwright `browser-profile-beta` mode, system-level `activate / System Events / foreground copy-paste` fallback is forbidden — prefer CDP keyboard events, in-page APIs, and JS-paste fallbacks only.
- Any action that pre-empts the user's current keyboard input target is a high-disturbance action. Do not run high-disturbance actions without explicit authorization.
- Before entering wait / sync / failure-closeout / success-closeout phases, park keyboard focus on a non-editable area in the page — never leave the grid in an editable state.
- High-disturbance Tencent Docs tasks must post at least 3 short heads-ups before entering live mode, each stating: whether the browser will be hijacked / selection moved / page refreshed, plus the expected duration.
- In attached mode, never repurpose a currently active page that is not this task's target Tencent Doc — open a fresh target page.
- Automation browser priority: `Google Chrome Beta` > `Chromium.app` > Playwright bundled Chromium. Never default to the user's daily Chrome stable profile.
- Project-only profile: `workspaces/medical-inventory-tencent-import/browser-profile-beta/`. The legacy `browser-profile-alt` is retired.
- With multiple `Chrome Beta` instances running, do not identify the live session by app name / window count / single window title alone — must check `profile_dir + CDP port + listener pid + page url/title`.
- `preflight / appendRow / append / verify` must happen on the same page — no headless-side probes.
- A page-state fingerprint mismatch with the user's visible page → stop, refresh, re-read tail state.
- Refresh / re-open URLs must use the core doc URL (e.g. `https://docs.qq.com/sheet/<id>`) without `_t / nlc / tab` temp params.
- Refresh policy is `on-error` only — not "always refresh once before write".
- `ready / sync` waits are 5-second-scale; abort and recover instead of waiting 20–35s.
- On `12004 / service anomaly / cannot save edited content / toolbar present but grid blank`, refresh immediately — do not keep clicking on a broken page.

## Block-level write contract (excerpt)

Writeback is `bulk-first`, not single-cell-by-default:

1. Bulk-append empty body rows first if needed.
2. Bulk-select the target range.
3. Bulk-overwrite / bulk-apply format.
4. Per-cell typing is allowed only as last-resort fallback.

In the same page:

- Build the full target model locally first: `B:K` from this batch; `A` keeps inheriting the existing formula chain.
- Submit body `B:K` once via `cellApi.setRangeValue`.
- Copy `A` column formula and format from the last good formula row into the target `A` range.
- Apply `cellApi.setFormat + setBorder` at block level — uniform font size 10, column-level alignment, four-side black border across the block.
- Border fallback may use the toolbar border button, but must structurally re-read `A:K` to confirm; toolbar-click alone is not success.
- Tencent's frontend `GridRange.endRowIndex / endColIndex` is **inclusive** — do not `+1`.

Implementation must `fail closed`:

- Helpers must never write `userEnterValue / plain numeric serial` to column `A`. Any such code path must raise, not silently degrade.

## Arrival-status flip rules (delivered → cath lab)

This is "update existing body rows", not "import a new batch".

- Default scope: column 10 `storage_location` only — do not touch other columns.
- Default target: rows written / confirmed in this task's `inventory_by_tencent_order_YYYY-MM-DD.xlsx/tsv`, or rows explicitly named by the user. Do not pull in unrelated historical batches.
- Always run a `--plan-only` pass first. Require:
  - `matchedCount == targetCount`
  - `missingCodeCount == 0`
  - `unexpectedStorageCount == 0`
- If the plan shows `needsUpdateCount == 0` and target rows are already in `alreadyDesired`, close out as "already at cath lab" — do not re-overwrite.
- For visible contiguous ranges, prefer one whole-range UI write — do not regress to per-cell trial.
- On `getMergeReference is not a function` (Tencent frontend), allow a fallback to localized writeback in column K on the same page; do not touch other columns; per-row re-read to confirm each row is now `cath lab`.

## Acceptance gate

- Right-side sync icon abnormal / offline / restore / D0005 → failure.
- "Values written" alone is not success — style consistency and border integrity must also pass.
- Newly added range column `A` must remain a formula, not a numeric.
- Style check is structural; new range `A:K` must have full four-side black borders, font size 10, expected alignment.
- `numberFormat` is a hard gate too: columns `B` arrival_date, `E/F` mfg/expiry, `I` surgery_date, `J` patient_id. Drift to `General` / `@` → failure even if the rendered text looks fine.
- If target row count is fewer than the old erroneous range, trailing rows must be physically deleted — clearing content / resetting local rowCount / removing only borders is not enough.
- Short-link retries only. One write + one refresh-and-re-read; if still failing, abort and report. "Eventually succeeded after many retries" is not an acceptable path.
- Before refresh-and-re-read or independent verify is done, the public-facing label is `attempted / pending re-read / pending verify` — never `repaired / fixed / guaranteed`.
- Each attended append/repair must drop a JSON acceptance artifact at `workspaces/medical-inventory-tencent-import/artifacts/verification/`. Status flips to `verified` only when that artifact says so.

## Free-tier and quota policy

- Tencent Docs flows must be designed to succeed on the free tier — UI automation must not rely on paid privileges or repeated retries to bridge a flaky path.
- Official API must also respect the free quota — multi-round retry is not a normal success path.
- Any approach that is stable only with a paid plan must be flagged as restricted, not adopted as default.

## Known high-risk signals (red flags)

- Right-side red cloud / exclamation / `D0005` / `please back up` / `pending sync after network restore` → stop writing.
- Plain refresh does not clear `D0005 / please back up / offline` → escalate to: clear `docs.qq.com` site data (excluding cookies) → reopen with core URL → read-only verify.
- `12004 / service anomaly / cannot save edited content` → refresh once. If not recovered within 5s, abort and report.
- Toolbar present but grid blank → page render crash. Stop, refresh, re-read.
- `View only` banner or `authInfo.attribute.canEdit=false` → wrong profile / wrong page. Abort attended write, switch profile or fall back to API with `verified_via_api` marker.

## Recovery chains, summarized

- Refresh → same-URL reopen → desktop roundtrip. Each step waits ~3s and re-reads. After step 3, allow extra `~8–10s` wait window after a same-URL reopen.
- If three same-class attempts (`refresh / same-URL reopen / new tab`) have all failed, do not try a 4th — escalate to "clear docs.qq.com site data → reopen with core URL → read-only verify".
- If a `cellApi.setRangeValue` write happened in a broken-page session, do not declare success even if API readback succeeds — frontend page must also be restored and verified.

## Output

- File name fixed: `inventory_by_tencent_order_YYYY-MM-DD.xlsx` (date = arrival_date).
- TSV name fixed: `inventory_by_tencent_order_YYYY-MM-DD.tsv`.
- The script auto-cleans files older than 7 days in the default output dir.
- Output column order (fixed):
  1. arrival_date
  2. commodity_name
  3. spec
  4. mfg_date
  5. expiry_date
  6. lot
  7. UDI
  8. surgery_date (empty by default)
  9. patient_id (empty by default)
  10. storage_location (`company warehouse` by default)

## Arrival-date rule (Beijing time)

- Default: next China-Mainland statutory work day (including holiday-swap rules) — not naive "tomorrow", not naive "skip weekend".
- The script bundles only the **current business year's** State Council holiday-swap calendar; cross-year inputs require an explicit `--arrival-date YYYY-MM-DD`.
- If the holiday calendar for the current business year is missing but State Council has published the official notice, fetch the notice and update `scripts/china_mainland_workdays.py` — do not punt the date decision to the user.
- Fixed format: `YYYY-MM-DD`.
- Explicit `--arrival-date` overrides default.
- For a same-day repeat run with a "ship today, arrive tomorrow" instruction, regenerate the batch with the new date — do not reuse yesterday's artifact.

## Hard rules baked into the script

- `.xls` is losslessly converted to `.xlsx` before reading.
- Encoding repair only runs when triggered; failed repair falls back to the original value — never overrides correct Chinese.
- `commodity_name` resolves by column-header first (`commodity_name / 名称 / 产品名称`); falls back to "most-Chinese-chars-per-row" column.
- `spec / mfg_date / expiry_date / lot` are resolved by column-header only — header-miss aborts the script.
- UDI is content-pattern only: cells beginning with `<vendor-prefix>` (lowercase / uppercase) — column header is ignored.
- `surgery_date`, `patient_id` are blank by default; `storage_location` is `company warehouse` by default.
- Sort order:
  1. Group by `spec`, in the order each `spec` first appears in the source file.
  2. Within `spec`, by `lot` ascending across the whole file.
- Pre-write integrity self-check failure (empty required column, no UDI emitted) → abort. No fake-success file is produced.

## Execution constraints

- Do not prompt the user, do not have them re-export, do not emit dependency-install prompts.
- Do not merge / split / drop raw data rows, do not replace UDI sources, do not guess field semantics.
- On script error, return the error. On success, return only the output file paths.
- In Codex / agent mode, "Tencent Docs has been updated" is the default completion gate.
- A "Tencent Docs + SPD shipment" coupled task completes only when Tencent Docs is written **and** the agent has switched into `order-shipment`.
