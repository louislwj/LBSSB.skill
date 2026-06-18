# lint_generation_strategy.py Spec

## Purpose

Reject unsafe generated-script strategies before they are used as final native StarUML delivery.

This tool checks scripts, not diagrams. It prevents common failure modes where a script can technically generate or export files while still producing poor native StarUML work.

## CLI

```text
python lbssb-staruml/tools/lint_generation_strategy.py --native-final tools/lbssb
python lbssb-staruml/tools/lint_generation_strategy.py --native-final --source-preservation-required tools/lbssb
python lbssb-staruml/tools/lint_generation_strategy.py --native-final tools/lbssb --out .lbssb/generation-strategy-report.json
```

## Inputs

- One or more script files or directories.
- Use `--native-final` when the scripts are intended to create or repair final editable StarUML `.mdj` diagrams.
- Use `--source-preservation-required` when a source `.mdj`, source inventory, or previous English class vocabulary exists.

## Fail Patterns

- Direct `.mdj` or `project.json` synthesis instead of StarUML MCP/API authoring.
- Mermaid `generate_diagram` accepted as final sequence/state output.
- Global `layout_diagram` without local move/resize/reroute repair evidence.
- Complex use case diagrams positioned by raw row/column grid.
- Hard-coded translated class members when source identifiers must be preserved.
- Batch-create-all-then-export workflow with no pilot visual gate.
- Verified status claims without split engineering/visual/source-preservation fields.

## Outputs

JSON report:

```json
{
  "status": "Verified | Failed",
  "filesScanned": 0,
  "errors": [],
  "warnings": [],
  "nativeFinal": true,
  "sourcePreservationRequired": true
}
```

## Exit Codes

- `0`: no hard strategy errors.
- `1`: one or more hard errors found.

## Interpretation

If this tool returns `Failed`, native StarUML delivery cannot be final `Verified`. Repair or replace the generation strategy, then rerun the lint before production drawing.
