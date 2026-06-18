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
| `visual_geometry_audit.py` | Check layout-plan/native-view geometry evidence before `Verified` | `.lbssb/layout-plan.json`, optional inventory/export index | JSON audit report | expected diagrams, min sizes |
| `visual_overlap_audit.py` | Check node/edge/label overlap evidence for high-risk diagrams | `.lbssb/layout-plan.json` or native view snapshot | JSON audit report | node boxes, routed points, label boxes |
| `course_style_repair.mjs` | Native StarUML manual-style layout repair based on baseline good projects | project `.mdj`, diagram names, layout specs | saved `.mdj`, repaired PNGs, repair report | `PROJECT_FILE`, `OUT_DIR`, API ports, diagram specs |
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

## Course-Style Native Repair Script

When the parent workspace or supplied references contain good StarUML outputs for the same assignment/domain, prefer a reusable repair script over fresh generation.

Recommended file:

```text
tools/lbssb/course_style_repair.mjs
```

Required behavior:

- accept `PROJECT_ROOT`, `PROJECT_FILE`, `OUT_DIR`, and optional `LAYOUT_SPEC` through env vars or CLI args;
- open the project through StarUML MCP/API;
- locate diagrams by name/type;
- collect nodes and edges from actual diagram views;
- set element bounds with StarUML API/MCP;
- route edges with StarUML API/MCP;
- preserve existing model elements, English identifiers, and BCE stereotypes;
- delete only non-essential noisy View/dependency views when recorded;
- export repaired PNGs;
- write a repair report with changed diagrams and visual-review TODOs.

Recommended helpers:

```text
loadDiagram(name, types)
namedNodes(ctx)
endpointNodes(ctx)
setBox(view, x, y, width, height)
setEdge(edge, points, lineStyle)
routeGeneric(ctx, options)
routeWithSideCorridors(ctx, options)
reserveLabelSlots(ctx, options)
auditNodeEdgeAndLabelOverlap(layoutPlanOrSnapshot)
layoutUseCases()
layoutClassDiagram()
layoutSequenceDiagram()
layoutStateDiagram()
layoutCommunicationDiagram()
```

Parameterize stable geometry from:

```text
.lbssb/layout-specs/<diagram-name>.json
```

Do not keep many pass-specific scripts (`repair-pass2`, `repair-pass3`, etc.) as the final workflow. Once a repair works, consolidate it into `course_style_repair.mjs`.

## Forbidden Layout Script Patterns

Reject or mark `visualStatus: Unverified` when a native generation script:

- creates all diagrams before exporting and reviewing a pilot diagram;
- calls global `layout_diagram` after semantic grouping and does not perform local repair;
- uses simple row/column placement for complex use case diagrams without module zones;
- rebuilds class members from hard-coded Chinese data when a source `.mdj` has existing English identifiers;
- imports Mermaid sequence/state diagrams and accepts them as final without native visual repair;
- exports PNGs but records no visual review evidence.
- generates complex native diagrams without reading or embedding `.lbssb/layout-plan.json` or equivalent bounds/routes;
- creates use case, class, state, or sequence diagrams without explicit view bounds;
- creates sequence diagrams without explicit lifeline spacing and message y positions;
- creates sequence diagrams without visible message numbers;
- creates state diagrams without explicit state box sizing;
- creates class diagrams without restoring source inventory before sizing class boxes.
- records `visualStatus: Verified` without `visualReviewedAt`/`reviewedAt` evidence newer than exported PNGs.
- ignores an available same-assignment baseline `.mdj`/PNG set and rebuilds a visibly worse project from scratch.
- lacks any `set_view_bounds` / `set_edge_points` native repair pass for high-risk use case, class, sequence, or state diagrams.

For final native `.mdj` delivery, treat these as hard failures before production drawing:

- direct `.mdj` JSON/ZIP synthesis;
- Mermaid import accepted as final sequence/state output;
- global `layout_diagram` without local repair evidence;
- missing concrete LayoutPlan/bounds/routes for complex diagrams;
- grid-based complex use case layout;
- hard-coded translated class members when source preservation is required;
- batch creation of all diagrams before pilot export/review;
- stale visual review evidence after re-exported PNGs.
- high-risk use case/state diagrams with no node/edge/label overlap audit.
- overall use case scripts that connect every actor directly to many use cases without entry/module routing.
- state diagram scripts that keep long transition sentences on edges instead of short labels plus documentation notes.

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

## Five-Scenario Forward Test

When improving this Skill itself, validate against five distinct mini-projects rather than one copied baseline:

1. Create five project folders under the test workspace.
2. Give each folder a different business domain and vocabulary.
3. Produce at least one overall use case diagram and one state diagram per folder.
4. Reuse baseline style rules only as layout constraints; do not reuse baseline diagram names or business objects.
5. Write per-project `.lbssb/diagram-plan.json`, `.lbssb/layout-plan.json`, `diagram-manifest.json`, and visual review evidence.
6. Run script lint plus geometry/overlap audit.
7. Reject the Skill update if any scenario has actor-line braiding, line-through-node text, state label overlap, or unrequested baseline cloning.

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
  "visualStatus": "Verified | Unverified: <reason> | Failed: <reason>",
  "visualReviewedAt": "ISO-8601 timestamp when visualStatus was assigned"
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
They must also reject native `Verified` when visual review timestamps are missing or older than the exported PNG files.
