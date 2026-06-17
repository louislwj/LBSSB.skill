# verify_deliverables.py Spec

## Purpose

Check that UML deliverables are present, consistent, and visually plausible.

## CLI

```text
python verify_deliverables.py --out <output-dir> --plan diagram-plan.json --manifest diagram-manifest.json
```

## Checks

- StarUML delivery preflight passed if editable `.mdj` is required.
- Expected `.mdj` exists if required.
- StarUML can open the produced `.mdj`.
- Diagram count matches `diagram-plan.json` or guide requirements.
- Each required diagram has major elements.
- Each required diagram with relationships/messages/edges has at least one such connector.
- Every required diagram can export PNG.
- PNG count matches plan/manifest.
- PNG files are non-empty and decodable.
- Image dimensions meet minimum threshold.
- Manifest has required fields for every image.
- Sources are one of `staruml-export`, `draw_from_plan`, `normalized`, `plantuml-fallback`.
- Consistency is one of `native`, `semantic-consistent`, `unverified`.
- PlantUML fallback is never accepted as editable StarUML `.mdj` delivery.
- Optional sample pixel check rejects all-black/all-transparent images.

## Outputs

- Console summary.
- Optional `verification-report.json`.

## Exit Codes

- `0`: verified.
- `1`: unverified or missing required outputs.
- `2`: failed due to unreadable input or runtime error.
