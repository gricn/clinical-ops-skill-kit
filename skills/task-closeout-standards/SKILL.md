---
name: task-closeout-standards
description: When the user asks to summarize pitfalls, codify lessons, tighten closeout standards, or judge whether a task is truly closed, trigger this thin entry. It does not re-state the full ruleset; the global closeout hard rules are in AGENTS.md. This skill only reminds, gives a minimal template, and points to where the lesson should be sedimented.
---

# Task closeout — thin entry

This skill is responsible for:

- Reminding agents to execute the global closeout rules when the user explicitly asks ("summarize pitfalls / codify lesson / tighten closeout").
- Providing a minimal output template so a retrospective is not verbal-only.
- Pointing to the nearest `SKILL.md`, `references/*.md`, script, or repo rule where the lesson should be sedimented.

When to use:

- The task has been delivered, and we are deciding whether it is truly closed.
- The user says "don't make the same mistake next time" / "write this experience into the rules".
- This round had a repeat error, validation gap, false "completed", fake-pass.
- This round added or substantially rewrote a doc / ops manual / rule.

This skill is NOT responsible for:

- Copying or rewriting the full closeout rules in `AGENTS.md`.
- Replacing each business skill's tests / acceptance / completion gate.
- Deciding how a specific business problem should be fixed.

## Source of truth

- Global closeout hard rules → `AGENTS.md`, section `Task closeout standard (all agents)`.
- This skill is a trigger entry; it does not maintain a second canonical copy.
- If this skill conflicts with `AGENTS.md`, `AGENTS.md` wins.

## Minimal workflow

1. Decide delivery status:
   - `已完成 / 部分完成 / 未完成 / 无法继续`
   - What was actually produced
   - What remains blocked
2. Decide whether engineering sedimentation is done:
   - Updated skill / script / repo rule
   - Or explicit justification why this round does not need sedimentation
3. Emit a short retrospective:
   - `pitfalls`
   - `fixed-fix`
   - `next-default-path`
4. If the exposure is a stable process, repeat error, validation gap, misreported completion, or fake-pass:
   - Default to updating the closest business rule file
   - Do not leave the conclusion in chat only

## Short template

```md
Status
- 已完成 / 部分完成 / 未完成 / 无法继续
- Current result: …
- Remaining blocker: …

Engineering sedimentation
- Updated: <skill / script / AGENTS.md / reference>
- Or: not updating because …

Pitfalls
- …

Fixed-fix
- …

Next-default-path
- …
```

## Persistence checklist

- Repeat error, validation gap, misreported completion, or fake-pass → must write back to the repo.
- Update the closest business file first; do not pile everything into the top-level doc.
- For new or substantially rewritten docs, the opening must state:
  - What this doc is for
  - When to use it
  - What it does NOT cover
