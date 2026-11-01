# AGENTS.md

Repo-wide instructions for any agent (Claude / Codex / Qwen / Gemini / etc.) operating inside this skill kit.

> Desensitized public showcase. Hospital names, vendor names, patient identifiers, credentials and runtime data have been stripped. Sensitive constants in this document are replaced with neutral placeholders such as `<hospital>` or `<vendor-x>`.

## Skills

A skill is a set of local instructions in a `SKILL.md` file. This repo keeps skills inside the project so they can be versioned and used without copying to any global skills directory.

### Available skills

- `cathlab-schedule-ocr` — OCR and structuring for cathlab schedule files, with optional Google Sheet writeback.
- `gsheet-append-dedup` — Append/patch structured surgery rows into Google Sheet with dedup and blank-field fill rules.
- `medical-inventory-tencent-import` — Convert inventory `.xls/.xlsx` into strict Tencent Docs import order with encoding-safe repair and integrity checks (rule version v4). Also covers status flips, e.g. when delivered goods reach the cath lab and `货物存放` should change from "company warehouse" to "cath lab".
- `warehouse-shipment-planning` — Generate shipment / replenishment plans for the upstream warehouse, based on the empty-patient-id remainder rows in the formal inventory sheet.
- `warehouse-shipment-dida-task` — Sync the day's finalized shipment list into a Dida (TickTick) task using a fixed template.
- `vendor-sales-inventory-sync` — Read the day's Google Sheet cases, keep only one specified vendor's atrial-fibrillation / non-AF cases, save filtered set as local JSON, OCR case-sheet images to align handwritten labels with vendor-prefixed codes, cross-check via barcode and QR when available; runtime artifacts retained 7 days.
- `material-complaint-update` — Update existing rows in the formal Tencent Docs inventory sheet for live material complaint cases, using package-label photos and same-day case context.
- `spd-confirm-supply` — Click `确认供货` for a new purchase order in the SPD homepage to-do list, and verify it appears in `待发货订单`.
- `order-shipment` — Full pipeline for SPD shipment orders: login, scan pending shipments, match new-arrival stock, batch-level allocation, print delivery slips, strip stray fields, attach customs documents, confirm shipment.
- `spd-confirm-delivery` — Fast path: click `发货 / 确定发货` on the current shipment edit page and verify success by the red `取消发货` button. Does not handle new purchase order confirmation.
- `vendor-invoice-records` — Collect vendor invoice records from a B2B portal and safely write back to Excel.
- `surgery-summary` — Summarize daily surgery markdown records.
- `surgery-volume-summary` — Produce closed weekly / monthly / yearly surgery summary lines with cutoff wording and count validation.
- `task-closeout-standards` — Cross-task completion discipline: short retrospectives and clear new-document intros.
- `tencent-docs-api-v3` — Shared Tencent Docs official API V3 client for OAuth2 auth, bulk reads/writes, and retry-safe value updates when browser automation is unnecessary.

### How to use skills

- Trigger a skill when the user names it (e.g. `$skill-name`) or when the request clearly matches its description.
- Read the skill's `SKILL.md` first; load only the exact referenced resources for the current task.
- Keep the context small — avoid bulk-loading unrelated references or assets.
- Prefer bundled scripts over re-implementing logic in ad hoc code.
- If multiple skills apply, use the minimal set and execute them in dependency order.
- If a skill is missing or blocked, state the issue briefly and continue with best-effort fallback.
- If a commit introduces a new `skills/*/SKILL.md` or first-time `workspaces/<name>/` reference, update the repo README docs in the same commit; `scripts/check_repo_docs_sync.py` is part of pre-commit enforcement.

### Skill relationships

- Function-group directory: `skills/catalog/README.md`
- Machine-readable mapping: `skills/catalog/collections.yaml`

## Domain rule placement (all agents)

- `AGENTS.md` only holds cross-task, cross-skill, cross-agent global execution rules.
- Concrete business-side rules — short-code mappings, material grouping, case matching, surgery classification — live inside each skill and its `references/`, not in `AGENTS.md`.
- A rule may rise into `AGENTS.md` only when it actually affects multiple unrelated workflows in this repo.

## Live browser workspace hygiene (all agents)

- For live browser tasks (business system / Tencent Docs / Google Sheet), do not identify the active session by application name alone. Before any critical read/write, verify `App/bundle + profile_dir + CDP port + current tab URL/title`, and include enough of that fingerprint in checkpoints to distinguish sessions.
- When several Chrome Beta profiles, several tabs of the same doc, or a separately opened stable Chrome are present, anchor to the declared target profile/port — never let cursor focus drift to whichever window is currently frontmost.
- After a task is done or switching phase, close duplicate tabs and temporary automation windows; keep exactly one explainable target page. If multiple pages must remain, state each one's purpose.

## Business system shipment approval gate (all agents)

- Applies to any task that may touch the live SPD `待发货订单` / `编辑发货单` page: row deletions, additions, quantity edits, attachment uploads, `保存` clicks, `发货` clicks, shipment confirmation dialogs.
- Before any live modification, post a complete shipment plan in chat for user review. Read-only scanning, local planning, and dry-run artifact generation are allowed pre-approval; live edits are not.
- The shipment plan doubles as the execution checklist — save it to shipment artifacts and execute against it; do not reconstruct the slip list mid-run from chat memory.
- Minimum content of the plan:
  - current task scope / input baseline
  - number of SPD pending orders to be used
  - number of actual shipment slips
  - per slip: source `采购单号/发货单号`, `规格 + 数量`, planned keep/delete row structure, attachment status
  - current `已完成 / 待执行 / 失败` summary
- After posting the plan, if the current user instruction already explicitly says go (`执行 / 直接执行 / 发吧 / 继续`), do not ask again. Without explicit go-ahead, do not edit the live order, do not click `保存`, do not click `发货`.
- Approval is **batch-level**, not slip-level. Do not re-ask for each slip, attachment or dialog already listed in the approved checklist.
- Re-confirm only when the live page no longer matches the approved plan, scope expanded, or live facts conflict with the user's stated quantities.
- If the live page diverges from the approved plan mid-run, stop, re-list the updated plan, and wait for approval again.
- `保存成功`, pre-filled fields, or a clicked button are **not** shipment success. After each slip, re-read live state and verify it matches the approved plan before reporting done.

## Git workflow standard (all agents)

- Auto-commit by default after finishing a change and passing checks.
- Skip auto-commit only when the user explicitly says "do not commit yet".
- Before commit, run project checks (default: `./scripts/precommit_checks.sh`).
- Every commit must record an actor via `Agent:` trailer. Non-empty identifiers are accepted: `codex`, `claude`, `kimi`, `qwen`, `gemini`, `antigravity`, `human`, `human:<name>`, etc.
- Commit review is mandatory. Default path: `./scripts/reviewed_commit.sh --agent <agent> ...` — equivalent to running `./scripts/commit_review.sh --agent <agent>` first, then `COMMIT_AGENT=<agent> git commit ...`.
- Commit review cannot be skipped with `--no-verify`. The `prepare-commit-msg` hook blocks commits without a fresh review token for the staged tree.
- Agents must not self-bypass commit review by mutating hook policy, deleting review tokens, or routing through alternate commit flows — unless the user explicitly asks to modify governance itself.
- Never stage runtime data or sensitive artifacts (`workspaces/**`, Excel/backup outputs, captures, temp files). Rely on `.gitignore` and review `git status` before commit.
- Keep commits scoped to the task and use conventional-style messages (`feat(...)`, `fix(...)`, `refactor(...)`, `docs(...)`).
- On a fresh clone or repaired local config, run `./scripts/install_githooks.sh` once.
- Do not push unless the user explicitly asks.

## Task closeout standard (all agents)

A user task is only considered fully closed when both **delivery** and **engineering sedimentation** are completed.

### 1. Mandatory dual closeout

A. Task status closeout
- Status: 已完成 / 部分完成 / 未完成 / 无法继续
- Current result (what has actually been produced)
- Remaining blockers (if any)

B. Engineering sedimentation
- Skill updated (with concrete change), or
- Script updated, or
- AGENTS.md / repo rule updated, or
- Explicit justification why no update is needed.

If A is done but B is missing → task is "delivered but not closed".

### 2. No verbal-only retrospective

These are not sufficient:
- 本次踩坑 without a code/rule update
- 固定改法 only described
- 下次默认路径 only in chat

Every retrospective must produce a reusable artifact or an explicit "no-update" decision.

### 3. Mandatory retrospective structure

- 本次踩坑（1–3）
- 固定改法（1–2）
- 下次默认路径（1）

Plus identify: is any issue a repeated error? Did validation logic fail?

### 4. Forced update triggers

If any of the following occurred, default action is to update skill/script/rule unless proven unnecessary:
- Repeated error
- Validation gap (e.g. false "completed" state)
- Inefficient execution path
- Any misreport of completion

If not updating, explicitly explain why this is a one-off.

### 5. Completion integrity (anti-fake-complete)

Before marking task complete:
- Result is actually executed (not inferred)
- Result is directly verifiable
- All requirements are covered
- No obvious omissions

Otherwise downgrade to 部分完成 or 未完成.

### 6. Skills integration rule

When a task relies on a skill:
- First COMPLETE the task using the current skill
- Only AFTER completion evaluate whether the skill needs update

Never interrupt task execution to refactor a skill unless the task is completely blocked AND no fallback path exists.

### 7. Default evolution principle

Goal: increase one-pass success rate.
- Avoid repeating the same mistakes
- Prefer stable reusable paths over ad hoc fixes
- Convert useful fixes into repo-level assets (skills / scripts / rules)

### 8. Documentation requirement for new/changed docs

If you add or substantially rewrite a document, its opening must state:
- what the document is for
- when to use it
- what it does NOT cover

For operational docs, additionally include: default input, default output, shortest runnable example.

## Python environment rule (all agents)

- Do not run bare `python` / `python3` for project work. Default to the repo virtualenv (`./.venv/bin/python`).
- Applies to ad hoc Playwright attach/debug scripts as well.
- If a command needs project dependencies, assume `.venv` first rather than probing system Python.

## Public privacy review

Before publishing, review names and abbreviations, private-name mappings,
product descriptions, operational numbers, document metadata and commit identity.
Synthetic examples must be marked as synthetic. Keep production mappings and
business parameters outside this repository. Pattern scanning is not a semantic
privacy audit and does not remove previously published history.
