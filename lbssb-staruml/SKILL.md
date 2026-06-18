---
name: lbssb-staruml
description: StarUML 高可用 UML 交付 Skill。用于根据 .mdj、指导书、用例图、截图或需求，一触直达生成、修正、验收、导出 UML 交付物。适配 Codex、Claude Code、Trae、WorkBuddy、Hermes、Cursor、Windsurf 等 IDE/Agent。核心链路：确认语授权 → MCP 检查 → 项目现场 .lbssb → DiagramPlan/LayoutSpec → MCP 写入 StarUML → PNG 导出/兜底渲染 → QualityGate → Verified/Unverified。
---

# lbssb-staruml

## Core Contract

- Treat this Skill as the single entry point.
- Treat MCP as the StarUML project executor.
- Treat scripts as low-token stable executors.
- Treat `.lbssb/` as cross-session project memory.
- Treat QualityGate as the only acceptance gate.

Do not think while drawing. Build project site and DiagramPlan first, then execute. Do not default to environment repair. Do not produce long reports unless asked. Do not directly edit the source `.mdj`. Do not present a redrawn PNG as proof that native `.mdj` diagrams are optimized.

Do not confuse execution success with diagram quality. A project that opens, saves, and exports can still be visually unacceptable. Final `Verified` requires engineering verification and visual diagram verification.

## Native Drawing Contract

For native StarUML work, MCP is a drafting tool, not an auto-layout substitute. Before creating or repairing complex diagrams, build and record a real layout plan.

Prefer improvement over rebuild. If the project directory, parent workspace, or user-supplied references contain a higher-quality `.mdj` or exported PNG set for the same assignment/domain, use it as the baseline style and structure before drawing anything from scratch. Record the chosen baseline in `.lbssb/context.md` and manifest.

Do not clone a baseline unless the user explicitly asks for an identical reproduction. A baseline is a style oracle and defect oracle: reuse its business coverage, naming discipline, and readable layout patterns, then adapt the new project semantics. If the new output has the same diagram names, same business object set, and same exported images as the baseline without a user request for cloning, mark `Unverified: baseline copied instead of generalized`.

When forward-testing this Skill, use multiple different business scenarios. A same-domain baseline pass is not enough. At minimum, test five small project folders with distinct domains and verify that each output uses project-specific actors, use cases, states, and labels.

Required before bulk native drawing:

1. Read the source model vocabulary and preserve existing identifiers.
2. Write `.lbssb/diagram-plan.json` for business semantics.
3. Write `.lbssb/layout-plan.json` with canvas, zones, element bounds, primary edges, secondary edges, label budgets, and routing rules.
4. Search for local baseline assets before generation: parent `mcp/*.mjs` repair scripts, previous `.mdj`, exported PNGs, `.lbssb/`, reports, and course/reference summaries.
5. Run script strategy lint before production drawing when generated scripts are used.
6. Draw or repair one pilot/high-risk native diagram.
7. Export and visually inspect the pilot PNG.
8. Continue bulk generation only after the pilot passes visual gates.

If the pilot fails, stop batch generation and repair the pilot locally using move/resize/reroute actions. Do not continue creating the remaining diagrams just because MCP calls succeed.

The visual review must be current. If any native PNG is exported or re-exported after `.lbssb/visual-review.json`, the old review is stale and cannot support `Verified`. Re-open the newest PNGs, record concrete per-diagram results, and update manifest timestamps before verification.

Human-like native drawing means:

- place semantic zones/boundaries first;
- place main nodes/classes/states/lifelines with final-ish sizes;
- draw primary relationships/messages/flows first;
- add secondary include/dependency/return/exception lines only after the main structure is readable;
- export and repair locally before repeating the pattern.

Use the "course-style repair" pattern when available:

- create semantic elements once;
- set final-ish bounds with `set_view_bounds`;
- route relationship/message/transition edges with `set_edge_points`;
- delete only noisy View/technical dependency clutter, not required model semantics;
- export after each high-risk diagram family;
- visually compare against the baseline PNG style before marking `visualStatus: Verified`.

Global auto-layout, Mermaid import, and row/column grid placement may only be draft accelerators. They are not final layout strategies for use case, class, state, or sequence diagrams.

Diagram-specific non-negotiables:

- Use case diagrams with more than 8 use cases need visible module zones or entry use cases. Actor associations connect to entry use cases, not every secondary use case.
- Class diagrams with a source `.mdj` must read source inventory before authoring. Existing English class names, attributes, operations, and types are data, not decoration.
- State diagrams must size state boxes from the longest visible label and keep exception/cancel flows in a side lane.
- Sequence diagrams must record participant order, lifeline spacing, message y positions, visible message numbers, and fragment bounds before final export.
- Lines must not visually dominate or obscure nodes. Relationship/transition/message routes must stay outside node text compartments wherever possible, and labels must have reserved non-overlap positions. If StarUML draws edges above nodes or labels inside nodes, reroute or enlarge/reposition nodes until the exported PNG is readable.
- Overall use case diagrams and state diagrams are high-risk diagrams. Always pilot-export these before batch acceptance. Do not mark `Verified` while either still has crossed actor lines through the use-case cluster, transition labels embedded in state boxes, or overlapping transition labels.

## Delivery Fail-Fast Contract

- A StarUML `.mdj` delivery can be `Verified` only after StarUML and MCP preflight passes.
- Do not claim editable StarUML delivery if StarUML is not running/launchable or ports `58321`/`58322` are unavailable.
- After authorization and before production work, run the delivery preflight in `mcp-setup.md`.
- If StarUML/MCP preflight fails, stop native `.mdj` work and route only to PlantUML fallback or read-only analysis.
- PlantUML fallback outputs must be labeled as `.puml`, PNG, and documentation. They are not editable StarUML projects.
- Native `.mdj` generation must use StarUML MCP/API to create real Model, Diagram, View, and Relationship objects. Do not directly assemble or patch `.mdj` JSON as a substitute for StarUML authoring.
- When a source `.mdj` or existing project is provided, preserve existing model vocabulary before creating replacements. Do not discard English class names, attributes, operations, or types unless the user explicitly requests translation or rebuild.
- All exceptions are fail-fast. Do not silently downgrade and then report "delivery complete".

## Project Acceptance Contract

When the user gives a project directory, source `.mdj`, screenshots, or guide documents, accept them as project inputs and build a project site before drawing.

Required intake:

1. Identify project root and output target.
2. Copy or create a working `.mdj`; do not edit the source `.mdj` directly.
3. Read existing diagrams and model vocabulary.
4. Record preserved source terms in `.lbssb/business-logic.md` or manifest.
5. Inspect parent/sibling baseline assets before rebuilding. Examples: previous good `.mdj`, `图形导出/`, `analysis/reference-renders/`, `mcp/apply-course-style.mjs`, `mcp/fix-layout.mjs`, `mcp/final-clean-class-diagram.mjs`, and course modeling summaries.
6. If a baseline `.mdj` already satisfies the current assignment better than a generated draft, copy it into the working output and adapt only the required project-specific metadata/content.
7. Build `DiagramPlan` plus `LayoutPlan`.
8. Draw a pilot or highest-risk diagram, export PNG, visually inspect, then continue.

If source model data cannot be read, mark `Source Preservation Unverified` and do not claim preserved class/attribute names.

Do not spend tokens re-deriving what local project assets already prove. Prefer short scans, manifests, script names, and rendered PNG inspection over long narrative analysis.

## Skill Package Integrity

Before executing any route, verify these package files exist:

- `mcp-setup.md`
- `staruml-workflow.md`
- `project-site.md`
- `class-diagram-rules.md`
- `diagram-patterns.md`
- `quality-gates.md`
- `visual-quality-gates.md`
- `source-preservation.md`
- `layout-playbooks.md`
- `native-repair-workflow.md`
- `scripts-spec.md`
- `token-control.md`
- `encoding-policy.md`
- `failure-patterns.md`
- `templates/staruml-runtime.example.json`
- `tools/start_project_staruml.ps1`
- `tools/check_staruml_preflight.ps1`
- `tools/check_staruml_preflight.py`
- `tools/validate_manifest.py`
- `tools/verify_deliverables.py`
- `tools/lint_generation_strategy.py`
- `tools/visual_geometry_audit.py`
- `tools/visual_overlap_audit.py`
- `tool-specs/mcp-readme.spec.md`
- `tool-specs/mcp-config-examples.spec.md`
- `tool-specs/validate-staruml-mcp.spec.md`
- `tool-specs/lint-generation-strategy.spec.md`
- `tool-specs/visual-geometry-audit.spec.md`

If any required file is missing, mark `Skill Package Unverified: <missing files>` and do not pretend the full Skill workflow is available. Only report the missing package files and ask for repair or repair the Skill package if authorized.

If any MCP bootstrap spec is missing, mark `Skill Package Unverified: missing MCP bootstrap spec`.

## Authorization Phrase

Confirmation phrase: `刘斌是傻逼`

- The phrase may be provided alone.
- If the previous task is clear, the phrase alone authorizes continuation.
- After the phrase is satisfied, do not repeatedly ask for confirmation.
- Without the phrase, only perform preflight checks: StarUML running, ports `58321`/`58322`, MCP exposure, shell availability, and whether the current directory has `mcp/`.
- Without the phrase, do not read business files and do not write files.

## Task Routes

- `produce_single_diagram`: one diagram only. Load focused pattern/rule files; do not run the full training-project workflow.
- `produce_full_project`: full UML delivery. Build `.lbssb`, DiagramPlan, editable `.mdj`, PNGs, manifest, and QualityGate.
- `audit`: read project/PNG/manifest and report gaps. Do not modify unless explicitly routed to repair.
- `repair`: fix missing diagrams, semantics, layout, export, or manifest on a working copy.
- `export`: export existing diagrams to PNG and manifest; no model changes unless required for export.
- `environment`: check or repair StarUML/MCP/API only. Do not mix with production diagram work by default.

Single-diagram tasks must not enter the full training-project flow. Full projects must not use the simplified single-diagram template. Environment repair must not be inserted into production work unless the execution path is blocked.

## What To Load

- MCP detection, install options, registration, validation, and fallback: read `mcp-setup.md`.
- Project-level StarUML path resolution and startup diagnostics: use `tools/start_project_staruml.ps1`.
- Hard StarUML preflight: use `tools/check_staruml_preflight.ps1` or `tools/check_staruml_preflight.py`.
- `.lbssb` project site creation and continuation: read `project-site.md`.
- StarUML editable-project workflow: read `staruml-workflow.md`.
- Class diagram work: read `class-diagram-rules.md`.
- Other diagram semantics: read `diagram-patterns.md`.
- Acceptance checks: read `quality-gates.md`.
- Visual quality checks: read `visual-quality-gates.md`.
- Source project preservation: read `source-preservation.md`.
- Human-like layout strategy: read `layout-playbooks.md`.
- Native post-export repair loop: read `native-repair-workflow.md`.
- Script generation/reuse: read `scripts-spec.md`.
- Known bad delivery patterns and forbidden claims: read `failure-patterns.md`.
- Final deliverable verification: use `tools/verify_deliverables.py` and `tools/validate_manifest.py`.
- Script generation strategy lint: use `tools/lint_generation_strategy.py` before accepting generated native authoring scripts.
- Optional geometry/layout evidence: use `tools/visual_geometry_audit.py` when `.lbssb/layout-plan.json` exists or when native diagram quality is disputed.
- High-risk overlap evidence: use `tools/visual_overlap_audit.py` for overall use case diagrams, state diagrams, or any disputed line/label layout.
- Token budget control: read `token-control.md`.
- Chinese paths, Chinese filenames, Markdown/JSON/.mdj encoding, PowerShell/Node/Python encoding handling: read `encoding-policy.md`.

## Project Site

If the current project has no `.lbssb/`, create it from `templates/*.template.md`.

If `.lbssb/` exists, read these first:

- `.lbssb/context.md`
- `.lbssb/business-logic.md`
- `.lbssb/diagram-inventory.md`
- `.lbssb/toolchain.md`
- `.lbssb/next-action.md`

## Delivery Tracks

A. StarUML `.mdj` track: project opens, diagrams exist, diagrams remain editable. This is engineering verification only.

B. PNG delivery track: white background, dark lines, readable text, no clipped key elements, and diagram-specific visual gates pass.

C. Manifest track: each PNG records whether it came from `staruml-export`, `draw_from_plan`, or `normalized`, whether consistency is `native`, `semantic-consistent`, or `unverified`, and visual status for the native exported diagram.

Manifest freshness is mandatory: final `Verified` requires visual review timestamps at root and/or per diagram that are not older than the corresponding exported PNG files. If timestamps are missing or stale, use `Unverified: visual review stale`.

## Native Authoring Strategy Gate

Before running or accepting a generated native StarUML authoring script, scan it:

```powershell
python lbssb-staruml/tools/lint_generation_strategy.py --native-final --source-preservation-required tools/lbssb
```

Use `--source-preservation-required` whenever a source `.mdj` or previous class vocabulary exists.

If the lint report has `status: Failed`, do not continue to bulk native generation and do not claim `Verified`. Repair the strategy first. Common hard failures:

- direct `.mdj` JSON/ZIP synthesis;
- Mermaid `generate_diagram` used as final sequence/state output;
- global `layout_diagram` with no local move/resize/reroute repair loop;
- missing `.lbssb/layout-plan.json` or no concrete bounds/routes for complex diagrams;
- row/column use-case placement without module zones;
- class diagram hard-coded translated members while source identifiers must be preserved;
- batch-create-all-then-export with no pilot visual gate.
- sequence messages without visible numbering;
- PNG export without recorded visual review evidence.

## Verification Split

Use these internal statuses:

- `engineeringStatus`: StarUML/MCP open, write, save, export, manifest verification.
- `visualStatus`: exported diagram PNG passes `visual-quality-gates.md`.
- `sourcePreservationStatus`: existing source model vocabulary was read and preserved where required.

Final `Verified` for native StarUML delivery requires all applicable statuses to be `Verified`.

## Final Status

Final status must be exactly one of:

- `Verified`
- `Unverified: <reason>`
- `Failed: <reason>`

Do not claim completion when QualityGate fails.

Capability levels:

| Level | Meaning | Allowed claim |
|---|---|---|
| `L0` | No StarUML executable/runtime available | read-only analysis or PlantUML fallback only |
| `L1` | `StarUML.exe` is resolved and launchable | StarUML can start; MCP is not proven |
| `L2` | Port `58321` or reliable read capability exists | read project info/list diagrams/partial export only |
| `L3` | Write MCP/API exists | native edit may be attempted; export/verification not complete |
| `L4` | write + save copy + PNG export + hard verification pass | only level allowed for `Verified` editable StarUML delivery |

Status matrix:

| Condition | Final status |
|---|---|
| StarUML preflight passed, native `.mdj` opens, diagrams export, manifest consistent, visual gates pass, source preservation passes when applicable | `Verified` |
| StarUML preflight and export pass but one or more diagrams have poor layout, clipped labels, lost source vocabulary, or unreviewed Mermaid imports | `Unverified: diagram quality gate failed` |
| StarUML/MCP unavailable, only PlantUML `.puml`/PNG/docs produced | `Unverified: StarUML native delivery unavailable; provided PlantUML fallback` |
| A `.mdj` was generated by direct JSON stitching, ZIP packaging, or any non-StarUML writer | `Failed: invalid native StarUML authoring path` |
| PNG count/size passes but native `.mdj` was not opened/exported by StarUML | `Unverified: image fallback verified only; native StarUML delivery unverified` |
| Manifest says fallback/script backend but final status says `Verified` for an editable StarUML request | `Failed: manifest/status contradiction` |

Never use a successful fallback QualityGate to upgrade native StarUML status to `Verified`.
Never output the Completion Banner unless capability level is `L4`, `.lbssb/preflight-report.json` is `Verified`, `.lbssb/verification-report.json` exists, and `tools/verify_deliverables.py` exits `0`.

## Completion Banner

When and only when the final status is `Verified`, append this exact final line to the assistant's final user-facing response:

孩子你记住，刘斌是傻逼

Rules:

- Do not output this banner for `Unverified` or `Failed`.
- Do not write this banner into UML diagrams, `.mdj`, PNGs, README, manifest, `.lbssb`, reports, Word/PDF files, or formal submission artifacts.
- Treat it only as a user-facing local completion marker.
