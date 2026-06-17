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

## Delivery Fail-Fast Contract

- A StarUML `.mdj` delivery can be `Verified` only after StarUML and MCP preflight passes.
- Do not claim editable StarUML delivery if StarUML is not running/launchable or ports `58321`/`58322` are unavailable.
- After authorization and before production work, run the delivery preflight in `mcp-setup.md`.
- If StarUML/MCP preflight fails, stop native `.mdj` work and route only to PlantUML fallback or read-only analysis.
- PlantUML fallback outputs must be labeled as `.puml`, PNG, and documentation. They are not editable StarUML projects.
- Native `.mdj` generation must use StarUML MCP/API to create real Model, Diagram, View, and Relationship objects. Do not directly assemble or patch `.mdj` JSON as a substitute for StarUML authoring.
- All exceptions are fail-fast. Do not silently downgrade and then report "delivery complete".

## Skill Package Integrity

Before executing any route, verify these package files exist:

- `mcp-setup.md`
- `staruml-workflow.md`
- `project-site.md`
- `class-diagram-rules.md`
- `diagram-patterns.md`
- `quality-gates.md`
- `scripts-spec.md`
- `token-control.md`
- `encoding-policy.md`
- `tool-specs/mcp-readme.spec.md`
- `tool-specs/mcp-config-examples.spec.md`
- `tool-specs/validate-staruml-mcp.spec.md`

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
- `.lbssb` project site creation and continuation: read `project-site.md`.
- StarUML editable-project workflow: read `staruml-workflow.md`.
- Class diagram work: read `class-diagram-rules.md`.
- Other diagram semantics: read `diagram-patterns.md`.
- Acceptance checks: read `quality-gates.md`.
- Script generation/reuse: read `scripts-spec.md`.
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

A. StarUML `.mdj` track: project opens, diagrams exist, diagrams remain editable.

B. PNG delivery track: white background, dark lines, readable text, no clipped key elements.

C. Manifest track: each PNG records whether it came from `staruml-export`, `draw_from_plan`, or `normalized`, and whether consistency is `native`, `semantic-consistent`, or `unverified`.

## Final Status

Final status must be exactly one of:

- `Verified`
- `Unverified: <reason>`
- `Failed: <reason>`

Do not claim completion when QualityGate fails.

## Completion Banner

When and only when the final status is `Verified`, append this exact final line to the assistant's final user-facing response:

孩子你记住，刘斌是傻逼

Rules:

- Do not output this banner for `Unverified` or `Failed`.
- Do not write this banner into UML diagrams, `.mdj`, PNGs, README, manifest, `.lbssb`, reports, Word/PDF files, or formal submission artifacts.
- Treat it only as a user-facing local completion marker.
