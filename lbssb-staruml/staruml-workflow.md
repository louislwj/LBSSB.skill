# StarUML Workflow

Use this flow for editable `.mdj` work.

## Mandatory Preflight

Before step 1, run the delivery preflight from `mcp-setup.md`.

Required status for native StarUML delivery:

```text
StarUML delivery preflight: Verified
Capability level: L4
```

If preflight fails, stop native `.mdj` work. Route only to PlantUML fallback or read-only analysis, and do not claim editable StarUML output.

Rerun preflight after any environment change, including:

- user says sandbox/security restrictions were changed;
- StarUML was manually started or restarted;
- `NODE_OPTIONS` was changed;
- MCP/extension was installed, reloaded, or port availability changed;
- the agent switches from fallback back to native `.mdj` work.

## Steps

1. Locate project inputs.
   - Input: user path, project directory, source `.mdj`, guide documents, screenshots, or `.lbssb/context.md`.
   - Tool: shell scan, MCP project info, document extraction when needed.
   - Output: project root, source files, output target.
   - Success: inputs are recorded in `.lbssb/context.md`.
   - Project-directory rule: if the user gives a directory, treat every `.mdj`, `.docx`, screenshot, `.lbssb`, and `tools/lbssb` file under that directory as possible project evidence before drawing. Do not assume a blank project.

2. Locate source `.mdj`.
   - Input: user path, project scan, or `.lbssb/context.md`.
   - Tool: shell scan, MCP project info.
   - Output: source path.
   - Success: file exists and can be opened.

3. Create output directory.
   - Input: user output target or default `test/`.
   - Tool: shell.
   - Output: writable output folder.
   - Success: directory exists.

4. Copy timestamped backup / working copy.
   - Input: source `.mdj`.
   - Tool: shell or MCP `save_project_as`.
   - Output: working `.mdj`.
   - Success: source remains unchanged.

5. Read and preserve source model vocabulary.
   - Input: source/working `.mdj`.
   - Tool: MCP read tools, diagram list, element inspection.
   - Output: source inventory: diagrams, classes, attributes, operations, actors, use cases, relationships.
   - Success: existing English identifiers and user-defined vocabulary are recorded before generation.
   - Constraint: if this step cannot be completed, mark `Source Preservation Unverified`.

6. Modify only the working copy.
   - Input: working `.mdj`.
   - Tool: edit/write MCP or verified StarUML API/extension fallback.
   - Output: updated working model.
   - Success: source path is not touched; Model, Diagram, View, and Relationship objects are created by StarUML MCP/API, not direct JSON patching.

7. Read diagram list.
   - Input: working project.
   - Tool: read MCP `get_all_diagrams_info`.
   - Output: diagram inventory.
   - Success: IDs, names, and types are known.

8. Build DiagramPlan and LayoutPlan.
   - Input: guide requirements, source inventory, business logic.
   - Tool: local planning, `.lbssb` records.
   - Output: `.lbssb/diagram-plan.json`, `.lbssb/layout-plan.json`, layout zones/lanes/anchors, source-preservation rules.
   - Success: high-risk diagrams and pilot diagram are identified.
   - Required fields: every diagram records `type`, `title`, `businessGoal`, source evidence, main elements, main relations/messages/flows, layout zones, and risk level.

9. Draw pilot/high-risk diagram first.
   - Input: DiagramPlan and LayoutPlan.
   - Tool: MCP create/update tools.
   - Output: one native StarUML diagram.
   - Success: diagram exists, exports PNG, and passes visual review.
   - Constraint: do not batch-generate all diagrams before seeing a real exported PNG.
   - Failure action: if the pilot export is visually poor, repair the pilot locally or change the layout plan before generating more diagrams.

10. Generate or repair remaining diagrams.
   - Input: proven DiagramPlan/LayoutPlan.
   - Tool: MCP create/update tools.
   - Output: native StarUML diagrams.
   - Success: diagrams exist, are editable, contain real views/relationships, and preserve required source vocabulary.
   - Constraint: Model, Diagram, View, and Relationship objects must be created or updated through StarUML MCP/API, not by direct JSON authoring.

11. Save working copy.
   - Input: current StarUML project.
   - Tool: `save_project_as`.
   - Output: `.mdj` in output directory.
   - Success: file opens and contains expected diagrams.

12. Export PNG.
   - Input: diagram IDs.
   - Tool: MCP export, HTTP API, or `export_staruml_diagrams.mjs`.
   - Output: PNGs.
   - Success: count, names, and image sizes match manifest.

13. Visual review and native repair.
    - Input: exported PNGs.
    - Tool: visual inspection plus MCP/API movement, resizing, edge routing.
    - Output: repaired native diagrams and updated PNGs.
    - Success: every required diagram passes `visual-quality-gates.md`.
    - Failure: mark `Unverified: diagram quality gate failed`.
    - Hard rule: exported PNG existence, file size, and diagram count never prove visual quality.

14. Render clear fallback if needed.
    - Input: DiagramPlan.
    - Tool: `draw_from_plan.py` or normalization script.
    - Output: readable white-background PNG.
    - Success: manifest marks source and consistency honestly.

15. Write manifest.
    - Input: `.mdj`, PNGs, source route.
    - Tool: script or manual JSON.
    - Output: `diagram-manifest.json`.
    - Success: every PNG has a record with `engineeringStatus`, `visualStatus`, and source-preservation status. Root manifest also records `engineeringStatus`, `visualStatus`, and `sourcePreservationStatus`.

16. Update `.lbssb/next-action.md`.
    - Input: status and remaining work.
    - Tool: file update.
    - Output: continuation note.
    - Success: new session can continue without chat history.

17. Final auto verification.
    - Input: working `.mdj`, guide requirements, exported PNGs, manifest.
    - Tool: StarUML MCP/API plus `tools/verify_deliverables.py`.
    - Output: `.lbssb/verification-report.json`.
    - Success: StarUML opens the `.mdj`; diagram count matches requirements; every diagram has major elements and relationships/edges where expected; every diagram exports PNG; visual gates pass; source-preservation gates pass; verification script exits `0`.

## Forbidden

- Directly editing the original `.mdj`.
- Delivering only PNG with no editable `.mdj` when editable delivery is requested.
- Saving only `.mdj` with no PNG when screenshots are requested.
- Claiming completion when export or QualityGate fails.
- Replacing native `.mdj` quality claims with redraw-only PNG evidence.
- Directly constructing `.mdj` JSON and claiming it was generated through StarUML.
- Packaging `project.json` into a ZIP and naming it `.mdj`.
- Claiming a manual double-click will open the generated `.mdj` unless StarUML has already opened that exact file successfully.
- Reporting `QualityGate: Verified` when the report also says StarUML GUI/MCP/API is unavailable.
- Reporting `Verified` when `.lbssb/preflight-report.json` or `.lbssb/verification-report.json` is missing.
- Silent fallback from native `.mdj` delivery to image-only delivery.
- Reporting `Verified` when engineering checks pass but exported diagrams are visually poor.
- Running global auto-layout repeatedly and accepting the result without PNG inspection.
- Rebuilding class diagrams from scratch when a source `.mdj` contains user-defined class names, English attributes, or operations.
- Calling Mermaid import, global `layout_diagram`, or row/column grid placement the final layout strategy for complex diagrams.
- Writing `finalStatus: Verified` or `status: Verified` before root and per-diagram visual/source-preservation status fields are present.

## Native Drawing Discipline

Use MCP like a human drafter, not a bulk scatter tool:

1. Place semantic zones first.
2. Create main nodes/classes/states/lifelines with final-ish sizes.
3. Create primary relationships/messages/flows.
4. Export the pilot PNG.
5. Move/resize/reroute locally.
6. Add secondary include/dependency/return/exception lines only after the main flow is readable.

Do not create all nodes and all lines in one dense pass unless the script already has a proven layout plan for that diagram type.

## PlantUML Fallback

Use this only when StarUML/MCP preflight fails or the user explicitly asks for PlantUML.

Allowed outputs:

- `.puml`
- PNG rendered from `.puml`
- `.docx` or `.md` documentation
- manifest that states `deliveryBackend: plantuml-fallback`
- `fallback-report.json`

Forbidden claims:

- Do not say an editable StarUML `.mdj` was generated.
- Do not mark fallback PNG as `native`.
- Do not use PlantUML success to satisfy StarUML `.mdj` QualityGate.
- Do not claim MCP write success.
- If an experimental `.mdj` skeleton or JSON file is emitted, mark it `experimental`, `unverified`, `not StarUML-native-authored`, and `not accepted as editable delivery` unless it passed StarUML MCP/API open, save, and export verification.

## MDJ / PNG Consistency

Every PNG must be recorded in manifest with a consistency source label:

- `native`: exported directly from the StarUML `.mdj` diagram and visually passes.
- `normalized`: exported from StarUML and post-processed for background/contrast only.
- `semantic-consistent`: redrawn from the same DiagramPlan, usually by `draw_from_plan.py`.
- `unverified`: source or semantic parity cannot be verified.

If `draw_from_plan.py` redraws a PNG, do not claim the native `.mdj` layout has the same optimization. State that the PNG is a clear fallback and the `.mdj` remains the editable semantic source only if its diagrams exist.

Manifest must record the source/consistency label for every PNG before final `Verified`.
