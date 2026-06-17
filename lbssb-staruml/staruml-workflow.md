# StarUML Workflow

Use this flow for editable `.mdj` work.

## Mandatory Preflight

Before step 1, run the delivery preflight from `mcp-setup.md`.

Required status for native StarUML delivery:

```text
StarUML delivery preflight: Verified
```

If preflight fails, stop native `.mdj` work. Route only to PlantUML fallback or read-only analysis, and do not claim editable StarUML output.

## Steps

1. Locate source `.mdj`.
   - Input: user path, project scan, or `.lbssb/context.md`.
   - Tool: shell scan, MCP project info.
   - Output: source path.
   - Success: file exists and can be opened.

2. Create output directory.
   - Input: user output target or default `test/`.
   - Tool: shell.
   - Output: writable output folder.
   - Success: directory exists.

3. Copy timestamped backup / working copy.
   - Input: source `.mdj`.
   - Tool: shell or MCP `save_project_as`.
   - Output: working `.mdj`.
   - Success: source remains unchanged.

4. Modify only the working copy.
   - Input: working `.mdj`.
   - Tool: edit/write MCP or verified StarUML API/extension fallback.
   - Output: updated working model.
   - Success: source path is not touched; Model, Diagram, View, and Relationship objects are created by StarUML MCP/API, not direct JSON patching.

5. Read diagram list.
   - Input: working project.
   - Tool: read MCP `get_all_diagrams_info`.
   - Output: diagram inventory.
   - Success: IDs, names, and types are known.

6. Generate or repair diagrams.
   - Input: DiagramPlan and LayoutSpec.
   - Tool: MCP create/update tools.
   - Output: native StarUML diagrams.
   - Success: diagrams exist, are editable, and contain real views/relationships.

7. Save working copy.
   - Input: current StarUML project.
   - Tool: `save_project_as`.
   - Output: `.mdj` in output directory.
   - Success: file opens and contains expected diagrams.

8. Export PNG.
   - Input: diagram IDs.
   - Tool: MCP export, HTTP API, or `export_staruml_diagrams.mjs`.
   - Output: PNGs.
   - Success: count, names, and image sizes match manifest.

9. Render clear fallback if needed.
   - Input: DiagramPlan.
   - Tool: `draw_from_plan.py` or normalization script.
   - Output: readable white-background PNG.
   - Success: manifest marks source and consistency honestly.

10. Write manifest.
    - Input: `.mdj`, PNGs, source route.
    - Tool: script or manual JSON.
    - Output: `diagram-manifest.json`.
    - Success: every PNG has a record.

11. Update `.lbssb/next-action.md`.
    - Input: status and remaining work.
    - Tool: file update.
    - Output: continuation note.
    - Success: new session can continue without chat history.

12. Final auto verification.
    - Input: working `.mdj`, guide requirements, exported PNGs, manifest.
    - Tool: StarUML MCP/API, verification script if needed.
    - Output: manifest with validation result.
    - Success: StarUML opens the `.mdj`; diagram count matches requirements; every diagram has major elements and relationships/edges where expected; every diagram exports PNG.

## Forbidden

- Directly editing the original `.mdj`.
- Delivering only PNG with no editable `.mdj` when editable delivery is requested.
- Saving only `.mdj` with no PNG when screenshots are requested.
- Claiming completion when export or QualityGate fails.
- Replacing native `.mdj` quality claims with redraw-only PNG evidence.
- Directly constructing `.mdj` JSON and claiming it was generated through StarUML.
- Silent fallback from native `.mdj` delivery to image-only delivery.

## PlantUML Fallback

Use this only when StarUML/MCP preflight fails or the user explicitly asks for PlantUML.

Allowed outputs:

- `.puml`
- PNG rendered from `.puml`
- README/report documentation
- manifest that states `deliveryBackend: plantuml-fallback`

Forbidden claims:

- Do not say an editable StarUML `.mdj` was generated.
- Do not mark fallback PNG as `native`.
- Do not use PlantUML success to satisfy StarUML `.mdj` QualityGate.

## MDJ / PNG Consistency

Every PNG must be recorded in manifest with a consistency source label:

- `native`: exported directly from the StarUML `.mdj` diagram and visually passes.
- `normalized`: exported from StarUML and post-processed for background/contrast only.
- `semantic-consistent`: redrawn from the same DiagramPlan, usually by `draw_from_plan.py`.
- `unverified`: source or semantic parity cannot be verified.

If `draw_from_plan.py` redraws a PNG, do not claim the native `.mdj` layout has the same optimization. State that the PNG is a clear fallback and the `.mdj` remains the editable semantic source only if its diagrams exist.

Manifest must record the source/consistency label for every PNG before final `Verified`.
