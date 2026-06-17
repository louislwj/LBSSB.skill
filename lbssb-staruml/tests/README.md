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
