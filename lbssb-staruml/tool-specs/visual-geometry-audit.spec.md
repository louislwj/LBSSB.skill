# visual_geometry_audit.py Spec

Purpose: audit whether `.lbssb/layout-plan.json` contains concrete geometry evidence before a native StarUML delivery is called visually verified.

Input:

- `--layout-plan <path>`: required layout plan JSON.
- `--out <path>`: optional JSON report.

Checks:

- complex diagrams have numeric `canvas.width` and `canvas.height`;
- complex diagrams have semantic `zones` or `lanes` with x/y/width/height bounds;
- complex diagrams have `elementBounds` or equivalent node bounds;
- primary edges/messages are recorded where applicable;
- label budgets and route policies are recorded;
- use case diagrams include actor and system-boundary zones;
- class diagrams include role/inheritance and core-domain zones.

Output:

```json
{
  "status": "Verified | Failed",
  "diagramsChecked": 0,
  "errors": [],
  "warnings": []
}
```

Use:

```powershell
python lbssb-staruml/tools/visual_geometry_audit.py --layout-plan .lbssb/layout-plan.json --out .lbssb/visual-geometry-audit.json
```

Rule:

- A passing geometry audit does not prove the PNG is visually good.
- A failing geometry audit means complex native diagrams are not ready for final `Verified`.
