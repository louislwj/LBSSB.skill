# verify_deliverables.py Spec

## Purpose

Check that UML deliverables are present, consistent, and visually plausible.

## CLI

```text
python lbssb-staruml/tools/verify_deliverables.py --manifest .lbssb/diagram-manifest.json --preflight .lbssb/preflight-report.json --out .lbssb/verification-report.json
python lbssb-staruml/tools/validate_manifest.py --manifest .lbssb/diagram-manifest.json
```

## Checks

- StarUML delivery preflight passed if editable `.mdj` is required.
- `.lbssb/preflight-report.json` exists.
- Capability level is `L4` for editable StarUML delivery.
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
- For editable `.mdj` delivery, reject ZIP magic bytes `PK\x03\x04`.
- For editable `.mdj` delivery, first non-whitespace byte must be `{`.
- Reject direct-script `.mdj` authoring markers such as `zipfile.ZipFile`, `writestr('project.json'`, or `writestr("project.json"` in generated helper scripts.
- Reject manifest/status contradiction: fallback backend plus native `Verified`.
- Reject final wording that claims manual StarUML open success without recorded StarUML open/export verification.
- Reject `status: Verified` when `capabilityLevel` is not `L4`.
- Reject `nativeMdjVerified: true` when `fallbackUsed` is true or backend is `plantuml-fallback`.

## Outputs

- Console summary.
- `.lbssb/verification-report.json`.

## Exit Codes

- `0`: verified.
- `1`: failed or unverified.
- `2`: invalid input or missing files.
