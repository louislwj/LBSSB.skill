# lbssb-staruml Tests

These are manual test scenarios for environments that may not have StarUML GUI access.

## Manifest Schema Example

```powershell
python lbssb-staruml/tools/validate_manifest.py --manifest lbssb-staruml/demo/expected-manifest.json
```

The demo manifest shows the required root fields. It may fail file existence checks unless placeholder outputs exist.

## Fallback Manifest Example

Example file:

```text
lbssb-staruml/tests/fixtures/fallback-manifest.json
```

Run:

```powershell
python lbssb-staruml/tools/validate_manifest.py --manifest lbssb-staruml/tests/fixtures/fallback-manifest.json
```

A valid PlantUML fallback manifest must use:

```json
{
  "backend": "plantuml-fallback",
  "capabilityLevel": "L0",
  "preflightStatus": "Unverified: capability L0",
  "nativeMdjVerified": false,
  "fallbackUsed": true,
  "status": "Unverified"
}
```

It must not use `nativeMdjVerified: true` or `status: Verified`.

## Fake Verified Failure Example

`verify_deliverables.py` must fail when:

- backend is `plantuml-fallback`;
- capability is below `L4`;
- `nativeMdjVerified` is true;
- status is `Verified`;
- `.mdj` starts with ZIP magic bytes `PK`.
- root `engineeringStatus`, `visualStatus`, or `sourcePreservationStatus` is missing or not `Verified`.
- a diagram record lacks `engineeringStatus: Verified` or `visualStatus: Verified`.
- a fallback or `draw_from_plan` PNG claims `consistency: native`.

Expected exit code: `1` or `2`.

Example file:

```text
lbssb-staruml/tests/fixtures/fake-verified-manifest.json
```

Run:

```powershell
python lbssb-staruml/tools/verify_deliverables.py --manifest lbssb-staruml/tests/fixtures/fake-verified-manifest.json
```

Expected result: non-zero exit code.

## Visual Status Gate

Native StarUML delivery is not `Verified` until manifest root and every diagram record contain:

```json
{
  "engineeringStatus": "Verified",
  "visualStatus": "Verified",
  "sourcePreservationStatus": "Verified"
}
```

If the `.mdj` opens and exports but the diagrams are tangled, clipped, or unreviewed, the expected final status is:

```text
Unverified: diagram quality gate failed
```

## Legitimate PlantUML Fallback Example

PlantUML fallback can pass its own file checks but remains native-StarUML `Unverified`.

Allowed files:

- `.puml`
- `.png`
- `.docx` or `.md`
- `diagram-manifest.json`
- `fallback-report.json`

Forbidden claims:

- `Verified editable StarUML .mdj`
- `StarUML native delivery complete`
- `MCP write success`
