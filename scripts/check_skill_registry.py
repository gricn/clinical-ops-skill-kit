"""
Skill registry consistency gate.

Cross-checks three sources that must stay aligned:

- The actual `skills/*/SKILL.md` files on disk.
- The `### Available skills` list in AGENTS.md.
- The `name` / `path` entries in `skills/catalog/collections.yaml`.

Any mismatch (extra in one source, missing in another, mis-pointed path) is a
hard failure. Wired into the precommit hook so a new skill cannot be added
without updating AGENTS.md and the catalog in the same commit.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
AGENTS_PATH = REPO_ROOT / "AGENTS.md"
CATALOG_PATH = REPO_ROOT / "skills" / "catalog" / "collections.yaml"

AGENTS_SECTION_HEADER = "### Available skills"
AGENTS_SKILL_RE = re.compile(r"^- `(?P<name>[^`]+)`")
CATALOG_NAME_RE = re.compile(r"^\s+- name: (?P<name>.+)$")
CATALOG_PATH_RE = re.compile(r"^\s+path: (?P<path>skills/.+)$")


def discover_actual_skills(repo_root: Path = REPO_ROOT) -> dict[str, Path]:
    return {
        skill_file.parent.name: skill_file
        for skill_file in sorted(repo_root.glob("skills/*/SKILL.md"))
    }


def parse_agents_skills(text: str) -> set[str]:
    entries: set[str] = set()
    in_section = False
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line == AGENTS_SECTION_HEADER:
            in_section = True
            continue
        if in_section and line.startswith("### "):
            break
        if not in_section or not line.startswith("- "):
            continue
        match = AGENTS_SKILL_RE.match(line)
        if match is None:
            continue
        entries.add(match.group("name"))
    return entries


def parse_catalog_skills(text: str) -> dict[str, Path]:
    entries: dict[str, Path] = {}
    pending_name: str | None = None

    for raw_line in text.splitlines():
        name_match = CATALOG_NAME_RE.match(raw_line)
        if name_match:
            pending_name = name_match.group("name")
            continue
        path_match = CATALOG_PATH_RE.match(raw_line)
        if path_match and pending_name:
            entries[pending_name] = REPO_ROOT / path_match.group("path")
            pending_name = None

    return entries


def _format_skill_set(skill_names: set[str]) -> str:
    return ", ".join(sorted(skill_names)) or "<none>"


def validate_skill_registry(repo_root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []

    actual = discover_actual_skills(repo_root)
    agents = parse_agents_skills(AGENTS_PATH.read_text(encoding="utf-8"))
    catalog = parse_catalog_skills(CATALOG_PATH.read_text(encoding="utf-8"))

    actual_names = set(actual)
    catalog_names = set(catalog)

    missing_in_agents = actual_names - agents
    extra_in_agents = agents - actual_names
    if missing_in_agents or extra_in_agents:
        errors.append(
            "AGENTS.md skill list mismatch: "
            f"missing={_format_skill_set(missing_in_agents)}; "
            f"extra={_format_skill_set(extra_in_agents)}"
        )

    missing_in_catalog = actual_names - catalog_names
    extra_in_catalog = catalog_names - actual_names
    if missing_in_catalog or extra_in_catalog:
        errors.append(
            "skills/catalog/collections.yaml skill list mismatch: "
            f"missing={_format_skill_set(missing_in_catalog)}; "
            f"extra={_format_skill_set(extra_in_catalog)}"
        )

    for skill_name, skill_path in sorted(catalog.items()):
        actual_path = actual.get(skill_name)
        if actual_path is None:
            continue
        expected_dir = actual_path.parent
        if skill_path != expected_dir:
            errors.append(
                f"collections.yaml path mismatch for {skill_name}: "
                f"declared={skill_path} actual={expected_dir}"
            )
        if not (skill_path / "SKILL.md").exists():
            errors.append(
                f"collections.yaml path missing SKILL.md for {skill_name}: {skill_path}"
            )

    return errors


def main() -> int:
    errors = validate_skill_registry()
    if errors:
        print("Skill registry validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Skill registry OK ({len(discover_actual_skills())} skills)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
