# Project Site `.lbssb`

## Why

Agent conversations may be isolated. Do not depend on chat memory. Write project facts to `.lbssb/` so a new session can continue safely.

## Auto Create

If missing, create:

```text
.lbssb/
  context.md
  business-logic.md
  diagram-inventory.md
  layout-rules.md
  toolchain.md
  scripts-inventory.md
  workflow.md
  quality-gates.md
  token-control.md
  replication-guide.md
  next-action.md
```

Use `templates/*.template.md` as the initial content.

## Project Directory Intake

When the user gives a directory as the task input, scan that directory before drawing.

Required scan targets:

- `.mdj` files: source or previous working StarUML projects.
- `.docx`, `.pdf`, `.md`, `.txt`: requirements, guide books, reports, or user notes.
- image files: reference screenshots or previous exports.
- `.lbssb/`: continuation context and previous status.
- `tools/lbssb/`: reusable project scripts.
- `output/` or named delivery folders: existing deliverables to repair or avoid overwriting.

Record the result in `.lbssb/context.md` and `.lbssb/diagram-inventory.md`.

If a source `.mdj` or previous output exists, this is a repair/continuation task by default, not a blank regeneration task.

Do not replace source model vocabulary until `source-preservation.md` has been applied.

## File Roles

| File | Role |
|---|---|
| `context.md` | Project inputs, real starting point, output targets, known risks. |
| `business-logic.md` | System scope, actors, domain objects, relationships, main flows. |
| `diagram-inventory.md` | Existing diagrams, required diagrams, generated diagrams, source IDs. |
| `layout-rules.md` | Visual layout rules and route-specific constraints. |
| `toolchain.md` | StarUML version, ports, MCP names/capabilities, scripts, fallback route. |
| `scripts-inventory.md` | Reusable scripts, inputs, outputs, parameters, recommended commands. |
| `workflow.md` | Executed or planned workflow with success standards. |
| `quality-gates.md` | Project-specific acceptance checklist. |
| `token-control.md` | What to read, what to skip, and low-token route. |
| `replication-guide.md` | How to reuse the approach in a new project. |
| `next-action.md` | Exact continuation instructions for the next session. |

## Required Machine-Readable Records

For full projects or repairs, also create or update:

```text
.lbssb/source-inventory.json
.lbssb/diagram-plan.json
.lbssb/layout-plan.json
.lbssb/visual-review.json
```

`source-inventory.json` records preserved model terms. `diagram-plan.json` records UML semantics. `layout-plan.json` records zones, lanes, node sizes, and routing expectations. `visual-review.json` records which exported PNGs were inspected and why they passed or failed.

## Writing Rules

- Keep content concise.
- Make each item executable.
- Make records reusable.
- Do not write long reflections.
- Do not include hidden reasoning.
- Avoid unnecessary absolute local paths.
- Use relative paths or descriptive placeholders when possible.

## New Session Continuation

Read in order:

1. `.lbssb/context.md`
2. `.lbssb/next-action.md`
3. `.lbssb/diagram-inventory.md`
4. `.lbssb/toolchain.md`

Then run preflight, choose a route, and continue.
