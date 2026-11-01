"""
Repository documentation sync gate.

Looks at staged changes. If the commit introduces:

- a new `skills/*/SKILL.md`, the same commit must also touch:
  AGENTS.md, README.md, skills/catalog/README.md, skills/catalog/collections.yaml.

- a first-time `workspaces/<name>/` reference, the same commit must also touch:
  README.md, skills/catalog/README.md.

The check is wired into the precommit hook so an agent cannot ship a new skill
or a new workspace by editing only the SKILL.md / source while forgetting the
catalog and discoverability docs.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

SKILL_PATH_RE = re.compile(r"^skills/([^/]+)/SKILL\.md$")
WORKSPACE_PATH_RE = re.compile(r"^workspaces/([^/]+)/")
WORKSPACE_REF_RE = re.compile(r"(?<!skills/)workspaces/([A-Za-z0-9._-]+)/")

REQUIRED_SKILL_DOCS = (
    "AGENTS.md",
    "README.md",
    "skills/catalog/README.md",
    "skills/catalog/collections.yaml",
)
REQUIRED_WORKSPACE_DOCS = (
    "README.md",
    "skills/catalog/README.md",
)


def run_git(args: list[str], allow_exit_codes: set[int] | None = None) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    allowed = allow_exit_codes or {0}
    if result.returncode not in allowed:
        raise RuntimeError(
            f"git {' '.join(args)} failed with code {result.returncode}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result.stdout


def parse_name_status(text: str) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split("\t")
        status = parts[0]
        if status.startswith(("R", "C")) and len(parts) >= 3:
            entries.append((status, parts[2]))
        elif len(parts) >= 2:
            entries.append((status, parts[1]))
    return entries


def extract_new_skill_names(entries: list[tuple[str, str]]) -> set[str]:
    names: set[str] = set()
    for status, path in entries:
        if not status.startswith("A"):
            continue
        match = SKILL_PATH_RE.match(path)
        if match:
            names.add(match.group(1))
    return names


def extract_workspace_names_from_paths(paths: set[str]) -> set[str]:
    names: set[str] = set()
    for path in paths:
        match = WORKSPACE_PATH_RE.match(path)
        if match:
            names.add(match.group(1))
    return names


def extract_added_lines(patch_text: str) -> str:
    added_lines: list[str] = []
    for raw_line in patch_text.splitlines():
        if raw_line.startswith("+++") or not raw_line.startswith("+"):
            continue
        added_lines.append(raw_line[1:])
    return "\n".join(added_lines)


def extract_workspace_names_from_text(text: str) -> set[str]:
    return set(WORKSPACE_REF_RE.findall(text))


def read_known_workspace_names_from_head() -> set[str]:
    matches = run_git(
        ["grep", "-hoE", r"workspaces/[A-Za-z0-9._-]+", "HEAD", "--", "."],
        allow_exit_codes={0, 1, 128},
    )
    names: set[str] = set()
    for line in matches.splitlines():
        _, _, workspace_name = line.partition("/")
        if workspace_name:
            names.add(workspace_name)
    return names


def validate_doc_sync(
    staged_paths: set[str],
    new_skill_names: set[str],
    new_workspace_names: set[str],
) -> list[str]:
    errors: list[str] = []

    if new_skill_names:
        missing_docs = [path for path in REQUIRED_SKILL_DOCS if path not in staged_paths]
        if missing_docs:
            errors.append(
                "New skill detected: "
                f"{', '.join(sorted(new_skill_names))}. "
                "The same commit must update: "
                f"{', '.join(missing_docs)}"
            )

    if new_workspace_names:
        missing_docs = [path for path in REQUIRED_WORKSPACE_DOCS if path not in staged_paths]
        if missing_docs:
            errors.append(
                "First-time workspace introduction detected: "
                f"{', '.join(sorted(new_workspace_names))}. "
                "The same commit must update: "
                f"{', '.join(missing_docs)}"
            )

    return errors


def check_repo_docs_sync() -> list[str]:
    entries = parse_name_status(
        run_git(["diff", "--cached", "--name-status", "--find-renames", "--diff-filter=ACMR"])
    )
    if not entries:
        return []

    staged_paths = {path for _, path in entries}
    new_skill_names = extract_new_skill_names(entries)

    patch_text = run_git(["diff", "--cached", "--unified=0", "--diff-filter=ACMR", "--", "."])
    added_workspace_names = extract_workspace_names_from_text(extract_added_lines(patch_text))
    added_workspace_names |= extract_workspace_names_from_paths(staged_paths)

    known_workspace_names = read_known_workspace_names_from_head()
    new_workspace_names = added_workspace_names - known_workspace_names

    return validate_doc_sync(staged_paths, new_skill_names, new_workspace_names)


def main() -> int:
    errors = check_repo_docs_sync()
    if errors:
        print("Repository documentation sync check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Repository documentation sync OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
