# scripts/

Governance layer. Keeps `AGENTS.md`, `README.md`, `skills/catalog/` and the actual `skills/*/SKILL.md` set from drifting apart.

| File | Purpose |
| --- | --- |
| `check_skill_registry.py` | Hard-checks that every on-disk `SKILL.md` is listed in `AGENTS.md` and in `skills/catalog/collections.yaml`, with matching paths. |
| `check_repo_docs_sync.py` | When a commit adds a new `SKILL.md` or first-time `workspaces/<name>/` reference, requires the same commit to update the discoverability docs. |
| `precommit_checks.sh` | Wires the two checks above plus a `py_compile` syntax pass. Called by `.githooks/pre-commit`. |
| `install_githooks.sh` | One-shot setup after fresh clone — points `git config core.hooksPath` at `.githooks/`. |
| `.githooks/pre-commit` | The hook entry point — just `exec`s `precommit_checks.sh`. |

## Setup on a fresh clone

```bash
./scripts/install_githooks.sh
```

After this, every `git commit` runs the gate.

## Not included in this public showcase

The private repo additionally carries:

- `commit_review.sh` and `reviewed_commit.sh` — produce a short-lived review token for each staged tree; `prepare-commit-msg` rejects commits without a fresh matching token.
- `git_commit_guard.sh` — shared validation helpers for the agent-label / token plumbing.

That chain enforces an `Agent:` trailer on every commit and prevents the gate from being skipped with `--no-verify`. It is governance-only and adds no business value to this showcase, so it is omitted. Reach out for access if you'd like to see the full setup.

## Public privacy gate

`check_public_privacy.py` checks staged paths and common sensitive patterns. It reports locations without echoing secrets. `tests/test_public_privacy.py` covers runtime paths and credential patterns. Manual review of aliases, business parameters and document metadata is still required.

Development evidence regeneration accepts `--mapping /path/to/private/mapping.json` with `exact` and `prefixes` objects. Keep that configuration in the private repository. Without it, unmatched historical names are grouped as internal; per-skill counts may differ from the preserved published snapshot.
