# scripts/

Implementation scripts for this skill live in the private repository. The desensitized public showcase keeps the SKILL.md, references and architecture, but not the executable scripts (they include credentials, doc IDs and live API access).

In the private repo, this directory contains:

- `ocr_extract.py` — OCR + structured extraction over image / Word inputs.
- `apply_decision_rules.py` — runs the rule chain from `references/decision-rules.md` over the in-memory record list.
- `writeback_gsheet.py` — calls into `gsheet-append-dedup` with the resolved row set.
- `emit_tsv.py` — strict 10-column TSV emit, no Markdown fallback.

Access to the full source can be granted for interview review.
