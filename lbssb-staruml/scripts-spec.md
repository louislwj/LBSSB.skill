# Scripts Spec

## Positioning

Scripts are Skill-generated or Skill-reused low-token tools. They are not user prerequisites and do not replace StarUML MCP. Use them for deterministic export, fallback rendering, validation, and inspection.

Scripts must not fake native StarUML success. If a script writes `.puml`, PNG, docs, or any non-StarUML artifact, the manifest and final summary must identify the backend honestly.

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

## PlantUML Fallback Scripts

Generate PlantUML fallback only when StarUML/MCP preflight fails or the user explicitly asks for PlantUML.

Allowed outputs:

- `.puml`
- PNG rendered from `.puml`
- README/report documentation
- manifest with `deliveryBackend: plantuml-fallback`

Forbidden:

- Do not create or claim editable StarUML `.mdj`.
- Do not mark fallback PNG as `native`.
- Do not silently replace a requested StarUML delivery with PlantUML output.

If fallback is used, final status must be `Unverified: StarUML native delivery unavailable; provided PlantUML fallback` unless the user's requested deliverable was explicitly PlantUML.

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
  "consistency": "native | semantic-consistent | unverified"
}
```

If PNG source is `normalized`, also record `baseFile` when possible.
