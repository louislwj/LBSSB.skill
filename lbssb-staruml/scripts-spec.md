# Scripts Spec

## Positioning

Scripts are Skill-generated or Skill-reused low-token tools. They are not user prerequisites and do not replace StarUML MCP. Use them for deterministic export, fallback rendering, validation, and inspection.

Scripts must not fake native StarUML success. If a script writes `.puml`, PNG, docs, or any non-StarUML artifact, the manifest and final summary must identify the backend honestly.

Scripts must also not fake diagram quality. If a script can create/export diagrams but does not inspect or repair exported PNGs, it can only produce `engineeringStatus: Verified`, not final diagram `visualStatus: Verified`.

## Script Generation Conditions

Generate or update `tools/lbssb/` only when at least one condition is true:

- StarUML export is unreadable, low contrast, clipped, or otherwise unsuitable.
- Batch verification/export is needed.
- Cross-session replication needs stable reusable scripts.
- The user explicitly asks for reusable scripts.

Do not generate scripts for a simple `audit` route unless the audit cannot be completed without deterministic tooling.

Scripts are internal Skill tool caches, not prerequisites the user must understand or run manually.

## Required Script Specs

| Script | Purpose | Input | Output | Reusable Parameters |
|---|---|---|---|---|
| `export_staruml_diagrams.mjs` | Export selected StarUML diagrams through API/MCP | diagram IDs, output dir, filename map | PNG, manifest draft | API base URL, IDs, names |
| `export_current_project_images.mjs` | Export all diagrams from current/opened project | project path, output dir | PNGs, image index | `PROJECT_FILE`, `OUT_DIR` |
| `draw_from_plan.py` | Render clear fallback UML PNGs | `diagram-plan.json`, `layout-theme.json` | PNG, README, manifest | fonts, theme, page size |
| `normalize_png_background.py` | Convert unreadable dark/transparent export to white background | PNG dir | normalized PNG | thresholds, root dir |
| `verify_deliverables.py` | Check `.mdj`, PNGs, manifest, image dimensions | output dir, expected plan | report JSON/text | expected counts, min size |
| `inspect_class_associations.mjs` | Inspect class relations, multiplicities, and crossings hints | project or diagram ID | console/JSON report | diagram name/ID |
| `build_diagram_plan.py` or `.mjs` | Convert requirements and source inventory into diagram/layout plan | guide text, source inventory | `diagram-plan.json`, `layout-plan.json` | project name, output dir |
| `visual_quality_check.py` | Record page/image-level visual review results | exported PNG dir, expected diagrams | visual review JSON | min sizes, manual notes |
| `tools/start_project_staruml.ps1` | Resolve and start project/system StarUML safely | project root, optional runtime config | JSON startup result | ports, wait seconds |
| `tools/check_staruml_preflight.py` | Hard preflight and capability level report | project root, optional evidence | `.lbssb/preflight-report.json` | evidence file, MCP tools JSON |
| `tools/check_staruml_preflight.ps1` | Windows wrapper for Python preflight | same as Python script | `.lbssb/preflight-report.json` | Python executable |
| `tools/validate_manifest.py` | Manifest schema and consistency checks | manifest path | console JSON | expected diagram count |
| `tools/verify_deliverables.py` | Final hard deliverable verification | manifest, preflight, mdj | `.lbssb/verification-report.json` | expected diagram count |
| `tools/lint_generation_strategy.py` | Reject unsafe native generation strategies before drawing | script files or `tools/lbssb/` | console JSON, optional report | `--native-final`, `--source-preservation-required` |

## PlantUML Fallback Scripts

Generate PlantUML fallback only when StarUML/MCP preflight fails or the user explicitly asks for PlantUML.

Allowed outputs:

- `.puml`
- PNG rendered from `.puml`
- `.docx` or `.md` documentation
- manifest with `deliveryBackend: plantuml-fallback`
- `fallback-report.json`

Forbidden:

- Do not create or claim editable StarUML `.mdj`.
- Do not mark fallback PNG as `native`.
- Do not silently replace a requested StarUML delivery with PlantUML output.
- Do not set `final_status`, `finalStatus`, or a QualityGate summary to `Verified` for editable StarUML delivery when the backend is fallback/script-only.
- Do not claim `MCP write success`.
- Do not claim `StarUML native delivery complete`.

If fallback is used, final status must be `Unverified: StarUML native delivery unavailable; provided PlantUML fallback` unless the user's requested deliverable was explicitly PlantUML.

If fallback emits any `.mdj` skeleton or JSON-like project file, it must be marked:

```text
experimental
unverified
not StarUML-native-authored
not accepted as editable delivery
```

It becomes accepted native delivery only after StarUML MCP/API opens it, saves a copy, exports PNG, and `tools/verify_deliverables.py` exits `0`.

## Forbidden MDJ Script Patterns

Scripts must not create native `.mdj` deliverables by direct file synthesis.

Reject a script as a native StarUML authoring path if it contains:

```text
zipfile.ZipFile
writestr('project.json'
writestr("project.json"
"_type": "Project"
Path(...).write_text
Path(...).write_bytes
fs.writeFile
fs.writeFileSync
```

Allowed use:

- read-only inspection of existing `.mdj`;
- creating fallback `.puml`, PNG, README, or manifest;
- calling verified StarUML MCP/API endpoints that create/save real StarUML objects.

If such a script still writes a `.mdj`, mark the delivery `Failed: invalid native StarUML authoring path`.

## Forbidden Layout Script Patterns

Reject or mark `visualStatus: Unverified` when a native generation script:

- creates all diagrams before exporting and reviewing a pilot diagram;
- calls global `layout_diagram` after semantic grouping and does not perform local repair;
- uses simple row/column placement for complex use case diagrams without module zones;
- rebuilds class members from hard-coded Chinese data when a source `.mdj` has existing English identifiers;
- imports Mermaid sequence/state diagrams and accepts them as final without native visual repair;
- exports PNGs but records no visual review evidence.

For final native `.mdj` delivery, treat these as hard failures before production drawing:

- direct `.mdj` JSON/ZIP synthesis;
- Mermaid import accepted as final sequence/state output;
- global `layout_diagram` without local repair evidence;
- grid-based complex use case layout;
- hard-coded translated class members when source preservation is required;
- batch creation of all diagrams before pilot export/review.

Run:

```powershell
python lbssb-staruml/tools/lint_generation_strategy.py --native-final --source-preservation-required tools/lbssb
```

If there is no source `.mdj` or previous class vocabulary, omit `--source-preservation-required` but still run `--native-final` for editable StarUML delivery.

Allowed pattern:

1. Read source inventory.
2. Write `diagram-plan.json`.
3. Write `layout-plan.json`.
4. Generate or repair one pilot/high-risk diagram.
5. Export and inspect.
6. Apply local move/resize/edge repair.
7. Continue batch generation only after the layout pattern passes.

## Project Directory Support

Project scripts must accept project-root parameters instead of hard-coding one user's path whenever practical:

```text
--project-root <dir>
--source-mdj <file>
--guide <file>
--output-dir <dir>
--manifest <file>
```

If a temporary script is hard-coded for one project, record that in `.lbssb/scripts-inventory.md` and do not promote it as a reusable Skill tool.

Hard-coded absolute paths are allowed only for one-off project scripts inside that project. Reusable Skill scripts must use CLI parameters or environment variables.

## Static Scan Gate

Before final acceptance, scan generated scripts and manifests for contradiction patterns:

```text
final_status = "Verified"
"finalStatus": "Verified"
"QualityGate": "Verified"
"backend": "script fallback"
"deliveryBackend": "plantuml-fallback"
"StarUML MCP not available"
"StarUML GUI not available"
```

If unavailable-StarUML or fallback markers appear together with native `Verified`, fail the gate.

## Current Project Reusable Assets

Known reusable sources from this project:

- `test/draw_clear_uml.py`: project-specific hard-coded renderer; useful as prototype for `draw_from_plan.py`.
- `test/export_staruml_diagrams.mjs`: selected diagram export prototype.
- `test/normalize_png_background.py`: background normalization prototype.
- `mcp/export-current-project-images.mjs`: all-diagram export prototype.
- `mcp/inspect-class-associations.mjs`: class relation inspection prototype.
- `tools/verify-deliverables.py`: deliverable verification prototype.
- `tools/flatten_png_backgrounds.py` and `tools/flatten_png_dir.py`: PNG normalization helpers.

## draw_from_plan.py

Inputs:

- `diagram-plan.json`
- `layout-theme.json`

Outputs:

- PNG files.
- `README.md`.
- `diagram-manifest.json`.

Supported diagram types:

- `class`
- `sequence`
- `communication`
- `activity`

Use cases:

- Fallback when StarUML PNG export is dark, unreadable, clipped, or too low contrast.
- Fast generation of clear submission screenshots.
- Visual cross-check against native StarUML diagrams.

Restriction:

- A `draw_from_plan` PNG must not be presented as native `.mdj` optimization. Mark manifest consistency as `semantic-consistent` unless it is proven native.

## diagram-plan.json

Minimum structure:

```json
{
  "project": {
    "name": "",
    "sourceMdj": "",
    "outputDir": ""
  },
  "diagrams": [
    {
      "type": "class",
      "title": "",
      "filename": "",
      "classes": [],
      "relationships": []
    }
  ]
}
```

For native StarUML work, also include:

```json
{
  "sourcePreservation": {
    "preserveExistingIdentifiers": true,
    "sourceInventory": ""
  },
  "layout": {
    "strategy": "zone-based",
    "pilotDiagram": "",
    "allowGlobalAutoLayoutAsFinal": false
  }
}
```

Sequence diagrams should use `participants` and `messages`. Communication diagrams should use `objects` and `messages`. Activity diagrams should use `nodes`, `edges`, and optional `lanes`.

## layout-theme.json

Minimum structure:

```json
{
  "page": { "background": "#ffffff", "padding": 48 },
  "font": { "family": "Microsoft YaHei", "size": 18 },
  "stroke": { "color": "#111111", "width": 2 },
  "classBox": { "width": 220, "minHeight": 90 },
  "sequence": { "lifelineGap": 210, "messageGap": 46 }
}
```

## Manifest Rule

Every PNG record must include:

```json
{
  "file": "",
  "diagramTitle": "",
  "type": "",
  "source": "staruml-export | draw_from_plan | normalized | plantuml-fallback",
  "mdjDiagram": "",
  "consistency": "native | semantic-consistent | unverified",
  "engineeringStatus": "Verified | Unverified: <reason> | Failed: <reason>",
  "visualStatus": "Verified | Unverified: <reason> | Failed: <reason>"
}
```

If PNG source is `normalized`, also record `baseFile` when possible.

The root manifest must include:

```json
{
  "engineeringStatus": "Verified | Unverified: <reason> | Failed: <reason>",
  "visualStatus": "Verified | Unverified: <reason> | Failed: <reason>",
  "sourcePreservationStatus": "Verified | Unverified: <reason> | Failed: <reason>"
}
```

`tools/validate_manifest.py` and `tools/verify_deliverables.py` must reject native `Verified` delivery when any required visual/source-preservation status is missing.
