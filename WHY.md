# Why this design

This document explains why the repo is shaped the way it is. It is not a tutorial.

## The setting

A single operator runs the on-site material logistics for one cardiology department in a tertiary hospital:

- Schedules arrive as Word docs or photos of paper printouts, daily.
- Inventory lives in **Tencent Docs** (the team's chosen tool) — a document format that is, in practice, hostile to AI / programmatic access.
- The hospital's **SPD system** is the only canonical place to confirm supply, allocate shipments and confirm delivery. One wrong click = a real money mistake.
- Vendor on-site reps drop off cases that must be cross-checked against barcode / QR / handwritten labels.
- The upstream warehouse needs replenishment plans by a privately configured cutoff.
- And every step has to be summarized into weekly / monthly reports.

Doing this fully by hand is feasible but eats most of the working day. Doing this fully by AI is **not** feasible — too many edge cases, too high a downside on any single mistake, and too many sources of truth that disagree with each other.

So the goal is: **AI does the structured 80%, humans intercept the ambiguous 20%, and the system makes the ambiguity loud rather than silent.**

## Five constraints that shape the architecture

### 1. The document tool fights back

Tencent Docs is the team's standard. It is *not* AI-friendly:

- The browser DOM is virtualized; scroll position breaks selectors.
- The official API V3 is rate-limited and has gaps around inline format and batch updates.
- Several flows must be done in an attended browser session — the agent cannot run headless.

Lesson encoded in this repo:
- A dedicated **shared backend skill** `tencent-docs-api-v3` isolates the API V3 client so every business skill that needs Tencent Docs can reuse the same auth, retry and value-write code path.
- Skills that must touch the live DOM (e.g. `medical-inventory-tencent-import` for status flips) declare *attended* Playwright sessions, not headless ones.
- Skills explicitly state when to drop back to the API vs when to drive the browser.

### 2. Live business systems are unforgiving

The SPD shipment page is a single source of truth for real money: each row deletion / quantity edit / attachment upload commits actual product against actual purchase orders.

Lesson encoded:
- A repo-wide **shipment approval gate** (see `AGENTS.md`) forces every agent to post a complete plan in chat *before* the first live edit.
- Approval is **batch-level**, not slip-level — the agent doesn't re-stop to ask about each click; that would drown the human in interruptions.
- Save-success / button-clicked never counts as shipment-success. After each slip, re-read the live page and verify against the approved plan.

### 3. OCR / barcode / handwriting often disagree

A single cathlab schedule row may have:
- A printed surgery type.
- A handwritten correction.
- A barcode on the package.
- A QR code from the supplier.
- A vendor-prefixed code.

Any two of them can disagree. The system must surface the disagreement, not pick a side.

Lesson encoded:
- Each recognition skill (`cathlab-schedule-ocr`, `vendor-sales-inventory-sync`) declares **cross-check rules** explicitly in its `references/`.
- When checks disagree, the skill **falls back to human review** rather than guessing.
- Exceptions land in a **TickTick task** via `warehouse-shipment-dida-task` — so the human sees them at the next phone glance, not as a buried log line.

### 4. Operators need to override mid-flow

The original schedule changes. Cases get cancelled. Add-ons appear mid-day. A vendor calls to swap a SKU. The agent must accept overrides without rebuilding from scratch.

Lesson encoded:
- `gsheet-append-dedup` performs **append + patch** semantics, not append-only.
- Surgery type and remarks have separate update rules: type may be rewritten with a clear intent; remarks are **append-only** (never overwritten) so audit history survives.
- `cathlab-schedule-ocr` accepts late-arriving corrections (cancel / change / add-on) and rewrites the canonical Google Sheet row in place, rather than producing a new conflicting record.

### 5. Runtime data is regulated data

Patient identifiers, surgery records, vendor pricing — none of this belongs in a code repository, even a private one.

Lesson encoded:
- A hard separation between **capability layer** (`skills/`, versioned) and **runtime layer** (`workspaces/`, `surgery_records/`, both gitignored).
- A **credential layer** (`secrets/`, also gitignored) holds per-task login material; no skill is allowed to reach across that boundary.
- The public privacy gate checks staged paths and common sensitive patterns; catalog and documentation checks enforce structural consistency. Manual review remains necessary for business semantics.

## Why "skill-based" rather than a single agent prompt

A single mega-prompt would work for a week and then collapse under edge cases. The chosen pattern:

- One `SKILL.md` per business flow. Trigger conditions, workflow steps, mode splits, exception handling — all in one place.
- A `skills/catalog/` layer above, declaring **which skills feed which** (entry / fast-path / shared-backend / task-sync relations) so the agent picks the right skill instead of guessing.
- A governance layer below, enforcing that adding a new skill **also** updates the catalog, the README and the AGENTS doc — otherwise precommit fails.

This is the only way an 8-month-old kit doesn't drift into a junk drawer.

## What this is *not*

- Not a generic agent framework. Skills here are domain-specific.
- Not a model fine-tune. The investment is in **workflow design, exception handling, and reusable governance**, not in training.
- Not a sales tool, not a CRM, not an EHR. Strictly the operational connective tissue between three or four existing systems.

## Reading order

1. `README.md` — what's here.
2. `skills/catalog/README.md` — how skills relate.
3. `skills/cathlab-schedule-ocr/SKILL.md` — a representative entry skill end-to-end.
4. `skills/tencent-docs-api-v3/SKILL.md` — a representative shared-backend skill.
5. `skills/task-closeout-standards/SKILL.md` — how the kit forces itself to evolve.
