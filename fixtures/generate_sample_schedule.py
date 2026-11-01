"""
Generate a fake cathlab schedule Word document for the fixtures/ directory.

The output mirrors the shape that the real `cathlab-schedule-ocr` skill consumes
in production — date header, cath room sections, per-row patient ID + procedure +
surgeon + slot — but with **fully invented** patient IDs and surgeon placeholder
labels. No real hospital, vendor, or person is referenced.

Run:
    python3 fixtures/generate_sample_schedule.py
"""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH


HERE = Path(__file__).resolve().parent

SCHEDULE = {
    "header": "Cardiology Cathlab Surgery Schedule",
    "date": "2026-05-26 (Monday)",
    "department": "Cardiology, <hospital>",
    "rooms": [
        {
            "name": "Cath Room A",
            "cases": [
                {
                    "slot": "1",
                    "patient_id": "P000001",
                    "patient_name": "<patient-a>",
                    "procedure": "<procedure-AF>",
                    "surgeon": "<surgeon-A>",
                    "time": "09:00",
                    "notes": "",
                },
                {
                    "slot": "2",
                    "patient_id": "P000002",
                    "patient_name": "<patient-b>",
                    "procedure": "<procedure-SVT>",
                    "surgeon": "<surgeon-B>",
                    "time": "11:00",
                    "notes": "",
                },
                {
                    "slot": "3",
                    "patient_id": "P000003",
                    "patient_name": "<patient-c>",
                    "procedure": "<procedure-PVC>",
                    "surgeon": "<surgeon-C>",
                    "time": "14:00",
                    "notes": "left-side, may need <item-D>",
                },
            ],
        },
        {
            "name": "Cath Room B",
            "cases": [
                {
                    "slot": "1",
                    "patient_id": "P000004",
                    "patient_name": "<patient-d>",
                    "procedure": "<procedure-AT>",
                    "surgeon": "<surgeon-A>",
                    "time": "09:00",
                    "notes": "",
                },
                {
                    "slot": "2",
                    "patient_id": "P000005",
                    "patient_name": "<patient-e>",
                    "procedure": "<procedure-AF>+<procedure-VT>",
                    "surgeon": "<surgeon-B>",
                    "time": "13:30",
                    "notes": "compound case",
                },
            ],
        },
    ],
    "footer": "Note: schedule subject to last-minute add-ons / cancellations.",
}


def _set_default_font(document: Document) -> None:
    style = document.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)


def _add_heading(document: Document, text: str, level: int = 1) -> None:
    para = document.add_heading(text, level=level)
    para.alignment = WD_ALIGN_PARAGRAPH.LEFT


def _add_room(document: Document, room: dict) -> None:
    _add_heading(document, room["name"], level=2)
    table = document.add_table(rows=1, cols=6)
    table.style = "Light Grid Accent 1"
    hdr = table.rows[0].cells
    headers = ["#", "Patient ID", "Name", "Procedure", "Surgeon", "Time / Notes"]
    for cell, value in zip(hdr, headers):
        cell.text = value
    for case in room["cases"]:
        row = table.add_row().cells
        row[0].text = case["slot"]
        row[1].text = case["patient_id"]
        row[2].text = case["patient_name"]
        row[3].text = case["procedure"]
        row[4].text = case["surgeon"]
        time_note = case["time"] + ((" — " + case["notes"]) if case["notes"] else "")
        row[5].text = time_note


def build_document() -> Document:
    document = Document()
    _set_default_font(document)

    title = document.add_heading(SCHEDULE["header"], level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    meta = document.add_paragraph()
    meta.add_run(f"Date: {SCHEDULE['date']}\n").bold = True
    meta.add_run(f"Department: {SCHEDULE['department']}")

    for room in SCHEDULE["rooms"]:
        _add_room(document, room)

    document.add_paragraph()
    footer = document.add_paragraph(SCHEDULE["footer"])
    footer.runs[0].italic = True

    return document


def main() -> None:
    output = HERE / "sample-schedule.docx"
    document = build_document()
    document.save(str(output))
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
