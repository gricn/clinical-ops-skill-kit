---
name: material-complaint-update
description: >
  Update existing rows in the formal Tencent Docs inventory sheet for live material-complaint cases based on package-label photos and same-day case context. Trigger when the user says "today's <procedure> material complaint, update the info", "material complaint", or asks to patch complaint info into the formal inventory instead of creating a new row.
---

# Material complaint update

This doc is responsible for:

- Patching complaint info onto the original material row in the formal Tencent Docs inventory — not creating a new complaint-log row.
- Reading vendor-prefixed UDI, spec, lot, mfg / expiry, handwritten complaint content from the package / label photo.
- Combining same-day case context to fill `surgeon`, then writing complaint remarks back to the formal inventory.
- Producing a ready-to-send group-chat complaint report in the team's confirmed format.
- Default order: produce the shareable complaint message first, then write the formal inventory — so the wording is locked before any sheet write.

When to use:

- "Today <procedure-AF-family> complaint, update the info" / "material complaint" / "update complaint info".
- User supplies a material / label photo and wants the formal inventory's matching row patched.
- User wants to reference existing complaint rows (chosen by the user) in the formal inventory as templates.

This doc is NOT responsible for:

- Replacing the vendor-side official complaint-submission flow.
- Modifying sales records or other ledgers on the side.
- Adding a new "complaint record" row in place of patching the original.

## Currently validated scenario

- Formal inventory: `https://docs.qq.com/sheet/<prod-inventory-doc-id>`
- Validated template: `<procedure-AF-family> / <vendor-x> / <item-B> / "synthetic device anomaly"`.
- Reference complaint rows: `references/reference-cases.md` (private repo).

## Default input

- One material photo.
- Formal Tencent Docs inventory.
- Same-day Google Sheet case context (default scope: `<vendor-x>` × `<procedure-AF-family> / <procedure-non-AF-family>`).

## Default output

- Matched original inventory row updated to complaint style:
  - Column `I`: blank by default; only fill when a complaint code is actually generated and user asks for it.
  - Column `J`: confirmed complaint number / value, e.g. `DEMO-COMPLAINT-001` (synthetic example only).
  - Column `K`: leave untouched.
  - Column `L`: `YYYY/MM/DD pending complaint, <complaint content>. Surgeon: <surgeon>`.
- If header cell `M2` aggregates current complaint count, sync the count.
- A ready-to-send group-chat complaint message in the team's confirmed format.

## Default execution path

1. Extract from the photo:
   - vendor-prefixed UDI
   - spec
   - lot
   - mfg / expiry
   - handwritten complaint content
2. Cross-check vendor-prefixed UDI against the formal inventory's body to locate the original row.
3. Fill `surgeon` from same-day case context.
4. Compose the complaint message (group-chat format, locked wording).
5. Write `J` / `L` back to the formal inventory via the `tencent-docs-api-v3` shared backend.
6. Update `M2` aggregate if applicable.
7. Acceptance: re-read the patched row; verify the message matches what was written.
