# fixtures/

Desensitized sample inputs for the skills in this kit. Use these to read the SKILL.md and understand the input shape without touching real data.

## Files

| File | Used by | Notes |
| --- | --- | --- |
| `sample-schedule.docx` | `cathlab-schedule-ocr` | Synthetic cathlab schedule with `<patient-N>` and `<surgeon-N>` placeholders. Matches the layout (date header → cath room → numbered case rows) that the OCR skill consumes. |
| `generate_sample_schedule.py` | (the file above) | Regenerates `sample-schedule.docx`. Run as `python3 fixtures/generate_sample_schedule.py`. |

## What is NOT included

- A sample inventory `.xlsx` for `medical-inventory-tencent-import`. The real input is a vendor-supplied workbook with specific column conventions; a believable fake needs the user's spec. Not urgent for the showcase.
- A sample schedule **image**. In production the input may also be a photo of a printed schedule. Generating a believable fake image needs hand-drawing or screen-shotting the Word fake — out of scope for the auto-generated showcase.

## Why fixtures exist

Skills describe rules. Rules over what? Without a concrete input, a reader has to imagine. The fixtures give that reader a one-file anchor — open it, then re-read the SKILL.md, and the trigger conditions / workflow / column contracts all click.

All fixture data is synthetic. No real patient, surgeon, vendor, hospital, or document ID appears here.
