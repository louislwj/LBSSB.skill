# MCP Setup

## Goal

Define how to detect, suggest, register, validate, and degrade StarUML MCP capabilities. Do not install or modify user IDE configuration without explicit authorization.

This repository is the `lbssb-staruml` Skill package, not StarUML, not a StarUML MCP implementation, and not a redistributor of StarUML binaries.

## Project-level StarUML Runtime

Project-level StarUML support means path resolution and launch support only. Do not commit StarUML installers, portable binaries, user logs, user `.mdj` files, or private local paths to the repository.

StarUML executable lookup priority:

1. Project runtime config:
   - `.lbssb/staruml-runtime.json`
   - `lbssb-staruml/runtime/staruml-runtime.json`
2. Environment variable:
   - `LBSSB_STARUML_EXE`
3. Project-local portable paths, if the user placed StarUML there:
   - `tools/StarUML/StarUML.exe`
   - `.lbssb/runtime/StarUML/StarUML.exe`
   - `mcp/StarUML/StarUML.exe`
4. Common system install paths:
   - `C:\Program Files\StarUML\StarUML.exe`
   - `C:\Program Files (x86)\StarUML\StarUML.exe`
5. `StarUML.exe` found on `PATH`.

Template:

```text
lbssb-staruml/templates/staruml-runtime.example.json
```

Copy it to `.lbssb/staruml-runtime.json` in a project when a project-specific StarUML path is needed. If a project-local StarUML executable is used, the user must place it there themselves.

Startup helper:

```powershell
powershell -ExecutionPolicy Bypass -File lbssb-staruml/tools/start_project_staruml.ps1
```

This helper resolves StarUML, reports the source, checks `NODE_OPTIONS`, clears risky process-local `NODE_OPTIONS` only for the StarUML launch, starts StarUML with optional `--enable-logging`, checks process existence, and checks ports `58321` and `58322`.

## Delivery Capability Levels

| Level | Requirements | Allowed work |
|---|---|---|
| `L0` | no StarUML | read-only analysis or PlantUML fallback |
| `L1` | `StarUML.exe` resolved and launchable | startup diagnosis only |
| `L2` | `58321` or reliable read capability | read project info, list diagrams, partial export |
| `L3` | write MCP/API capability | edit working copy, but no verified delivery claim |
| `L4` | write + save copy + export PNG + hard verification | `Verified` editable StarUML delivery allowed |

If capability is below `L4`, do not claim `Verified` editable StarUML delivery.

## Capability Model

Judge MCPs by capability, not by hard-coded server name.

### StarUML Official / Read MCP

Recommended name: `staruml_official`

Recommended local path:

```text
project/mcp/node_modules/staruml-mcp-server/build/index.js
```

Recommended npm package:

```text
staruml-mcp-server
```

Minimum capabilities:

- `get_project_info`
- `get_all_diagrams_info`
- `get_current_diagram_info`
- `get_diagram_image_by_id`
- `generate_diagram` or equivalent generation capability

Responsibilities:

- Read project.
- Read diagram list.
- Get current diagram.
- Get images.
- Export or support PNG acceptance.

If the platform exposes a different MCP name, match by capability, not name.

### StarUML Third-party / Write MCP

Recommended name: `staruml_third_party`

Recommended local path:

```text
project/mcp/node_modules/staruml-mcp/dist/index.js
```

Recommended npm package:

```text
staruml-mcp
```

Minimum capabilities:

- `open_project`
- `save_project_as`
- `create_element_with_view`
- `create_edge_with_view`
- `update_element`
- `delete_element`
- `get_all_commands`

Responsibilities:

- Open `.mdj`.
- Save a working copy.
- Create diagrams.
- Create elements.
- Create relationships.
- Move/update/delete diagram elements.
- Execute or inspect StarUML commands.

If a third-party MCP exposes only read capabilities, do not mark it as the write MCP.

### StarUML Internal Extension

Recommended directory:

```text
project/mcp/staruml-mcp-extension/
```

Recommended extension:

```text
staruml-mcp-extension
```

Responsibilities:

- Enable enhanced HTTP capabilities inside StarUML.
- Provide project, diagram, element, command, and layout endpoints.
- Support third-party MCP and local `.mjs` scripts.

Default port:

```text
58322
```

`staruml-mcp-extension` is not an Agent-side MCP name. It is installed inside StarUML.

## StarUML Ports

- `58321`: StarUML built-in API Server.
- `58322`: `staruml-mcp-extension` HTTP Server.
- `58323`: `staruml-mcp` HTTP transport default port, only needed when using HTTP transport.

This Skill defaults to stdio MCP registration in the Agent. Ports `58321` and `58322` mainly support StarUML API, extension calls, and local Node/Python scripts.

## StarUML API Server Setup

Windows settings path:

```text
%APPDATA%\StarUML\settings.json
```

Minimum settings:

```json
{
  "apiServer": true,
  "apiServerPort": 58321
}
```

Rules:

1. Restart StarUML after changing settings.
2. After restart, check `58321`.
3. If `58321` is unreachable, do not claim StarUML API is available.
4. If multiple StarUML processes are running, ask the user to close extra instances to avoid API and Extension pointing at different projects.

## Delivery Preflight Required

Run this after authorization and before any production StarUML `.mdj` task.

Required checks:

1. Check `StarUML.exe` is installed and launchable.
   - Locate it through PATH, Start Menu install path, or common install locations.
   - If it cannot be found or launched, native `.mdj` delivery is `Failed` or must route to PlantUML fallback.
2. Check `NODE_OPTIONS`.
   - Inspect whether `NODE_OPTIONS` exists.
   - Pay special attention to `--use-system-ca`.
   - If StarUML reports an Electron main process error and `NODE_OPTIONS` contains risky flags, tell the user to clear or correct `NODE_OPTIONS`; do not blame antivirus or security software by default.
3. Check MCP/API ports.
   - Verify `58321` is connectable for StarUML API.
   - Verify `58322` is connectable for `staruml-mcp-extension`.
   - If either required port is unavailable, do not claim native `.mdj` delivery.
4. Create a minimum test `.mdj`.
   - Use a working temp/output directory, never the user's source project.
   - Open it with StarUML through MCP/API.
   - Confirm StarUML can read the project back.
5. Export one test diagram screenshot through MCP/API.
   - The test may be a tiny model with one diagram and one relationship.
   - Success requires a non-empty PNG/image response.

Compact preflight status:

```text
StarUML delivery preflight:
- StarUML.exe launchable:
- NODE_OPTIONS:
- 58321:
- 58322:
- test mdj open:
- test PNG export:
- status: Verified | Failed: <reason>
```

If any required step fails, stop native StarUML delivery immediately. Use only PlantUML fallback or read-only analysis, and label the final status honestly.

If the user later says sandbox/security restrictions were lifted, StarUML was opened manually, `NODE_OPTIONS` was changed, or MCP was installed, rerun the full preflight. Do not resume native `.mdj` work from a previous failed preflight.

Hard preflight command:

```powershell
powershell -ExecutionPolicy Bypass -File lbssb-staruml/tools/check_staruml_preflight.ps1
```

Expected report:

```text
.lbssb/preflight-report.json
```

The command must return non-zero when capability is below `L4`. Text-only judgment is not enough for `Verified`.

## Preflight Before Confirmation Phrase

Before the authorization phrase, only check:

- StarUML process is running.
- `http://127.0.0.1:58321` is reachable.
- `http://127.0.0.1:58322` is reachable.
- Read MCP is exposed.
- Edit MCP is exposed.
- Shell is available.
- Current directory has `mcp/`.

Do not read business diagrams, screenshots, requirements, or `.mdj` contents. Do not write files.

## Missing MCP Options

If no suitable MCP is available, present options:

- A. Install into current project `mcp/`.
- B. Use an existing local MCP and generate registration examples.
- C. Degrade to StarUML HTTP API / extension.
- D. Do read-only analysis.

Without user authorization, do not download, run `npm install`, create `mcp/`, edit `.codex/config.toml`, or edit Claude Code, Trae, WorkBuddy, Hermes, Cursor, or Windsurf configuration.

## Authorized Bootstrap Plan

Use this only after explicit user authorization to bootstrap MCP assets. Before authorization, do not create `mcp/` and do not install packages.

Authorized bootstrap must create or update these project assets:

- `mcp/README.md`: purpose, expected StarUML ports, installed/available MCP routes, verification commands.
- `mcp/mcp-config.example.*`: IDE-specific example configuration only; never overwrite live IDE config.
- `mcp/validate-staruml-mcp.md`: checklist for read, write, save-copy, and PNG export validation.

After install or registration, validate all of:

1. Read project info and diagram list.
2. Create or update a harmless test diagram/element in a working copy.
3. Save a copy with `save_project_as` or equivalent.
4. Export PNG or fetch a diagram image.

If any validation step fails, mark `MCP Unverified: <failed step>` and continue only through an approved fallback route.

## Authorized Project-local MCP Install

Without explicit user authorization, do not create `mcp/`, run `npm install`, download extensions, or modify IDE configuration.

After user authorization, the recommended project-local install logic is:

```powershell
mkdir mcp
cd mcp
npm init -y
npm install staruml-mcp-server staruml-mcp
```

This document is a specification, not permission to run those commands automatically.

If the StarUML internal extension is required, use one of these approved paths only after showing the exact commands or URL to the user and receiving confirmation.

Option A: StarUML GUI install

```text
StarUML -> Tools -> Extension Manager -> Install From URL
Enter the staruml-mcp-extension repository URL
Restart StarUML
```

Option B: project-local extension install

```powershell
cd mcp
git clone <staruml-mcp-extension repo> staruml-mcp-extension
cd staruml-mcp-extension
npm install
npm run build
npm run install:local
```

Rules:

1. If using URL or `git clone`, output the command/URL for user confirmation first.
2. Do not download automatically.
3. Restart StarUML after install.
4. After restart, check `58322`.

## Recommended Project MCP Directory

```text
project/
  mcp/
    package.json
    package-lock.json
    node_modules/
      staruml-mcp/
      staruml-mcp-server/
    staruml-mcp-extension/
    mcp-config.example.toml
    mcp-config.example.json
    README.md
    validate-staruml-mcp.md
```

Rules:

- `mcp/` is a project-local MCP tool cache.
- Do not upload `mcp/node_modules/` to GitHub.
- Upload only `mcp/README.md`, `mcp/mcp-config.example.toml`, `mcp/mcp-config.example.json`, `mcp/validate-staruml-mcp.md`, and `mcp/package.json` when needed.
- `.gitignore` should ignore `mcp/node_modules/`, local logs, verification outputs, and optionally `mcp/package-lock.json` if the project does not lock versions.
- Configuration snippets are examples only. Do not overwrite real IDE config unless authorized.

When authorized to create project MCP docs, follow:

- `tool-specs/mcp-readme.spec.md`
- `tool-specs/mcp-config-examples.spec.md`
- `tool-specs/validate-staruml-mcp.spec.md`

## Validation Flow

Minimum successful validation:

1. Open target project or inspect the currently open project.
2. Read project info.
3. Read diagram list.
4. Create/read a small test diagram or verify a known existing diagram.
5. Save a copy, never the source `.mdj`.
6. Export PNG or fetch diagram image.

If any mandatory step fails, mark `MCP Unverified` and choose a fallback path.

## Fallback Order

1. Formal MCP.
2. StarUML HTTP API on `58321` and `staruml-mcp-extension` on `58322`, only if StarUML preflight is verified.
3. Local Node/Python scripts that call verified StarUML API/extension.
4. PlantUML fallback when StarUML/MCP is unavailable.
5. Read-only analysis.

PlantUML fallback may create `.puml`, PNG, and documentation only. It must not claim editable StarUML `.mdj` output.

## IDE Registration Guidance

Supported targets:

- Codex
- Claude Code
- Trae
- WorkBuddy
- Hermes
- Cursor
- Windsurf

For each target, provide an example server entry with command, args, working directory, and environment. Keep examples in `mcp/mcp-config.example.*` unless the user explicitly asks to modify live config.

## Platform Usage

### Codex

Recommended:

1. Put `lbssb-staruml/` in the project root.
2. Create or reuse project-local `mcp/`.
3. Register these MCPs in Codex MCP config:
   - `staruml_official`
   - `staruml_third_party`
4. Start StarUML and open the target `.mdj`.
5. Verify `58321` and `58322`.
6. Ask Codex:

```text
请读取 lbssb-staruml/SKILL.md 并按其中规则执行。

刘斌是傻逼

根据当前 .mdj 和需求生成/修正 UML 图。
```

### Claude Code

Recommended:

1. Put the Skill folder in the project.
2. Ask Claude Code to read `lbssb-staruml/SKILL.md`.
3. Register both StarUML MCPs through Claude Code MCP configuration.
4. If the config format is uncertain, generate examples only; do not modify live config.
5. Verify MCP tools are exposed before production work.

### Trae / WorkBuddy / Hermes / Cursor / Windsurf

Unified rules:

1. If the platform supports MCP, register both MCPs using the platform's MCP config.
2. If it lacks MCP but supports Shell, degrade to HTTP API plus Node/Python scripts.
3. If it only supports file reads/writes, create `.lbssb`, DiagramPlan, scripts, and instructions only; do not guarantee `.mdj` writeback.
4. If it is chat-only, perform read-only analysis.

## Runtime MCP Usage Order

1. Use `staruml_official` to read project information:
   - `get_project_info`
   - `get_all_diagrams_info`
   - `get_current_diagram_info`

2. Use `staruml_official` to fetch images or initial PNG export:
   - `get_diagram_image_by_id`
   - `export_diagram` or equivalent capability

3. Use `staruml_third_party` to open/create/update/save:
   - `open_project`
   - `create_element_with_view`
   - `create_edge_with_view`
   - `update_element`
   - `delete_element`
   - `save_project_as`

4. Use `staruml_third_party` or extension to inspect StarUML commands:
   - `get_all_commands`

5. If MCP write fails but HTTP extension `58322` is available, use local `.mjs` scripts calling `58322` as fallback.

6. If StarUML PNG export is dark or unclear, use `normalize_png_background.py` or `draw_from_plan.py` fallback, and record the source in manifest.

Do not pretend shell script fallback is MCP success. If script fallback is used, final status must state the backend is `script fallback`.

## Native MDJ Authoring Rule

Native StarUML delivery requires real StarUML object creation:

- Model elements must be created through StarUML MCP/API.
- Diagrams must be created through StarUML MCP/API.
- Views must be created through StarUML MCP/API.
- Relationships must be created through StarUML MCP/API.
- Layout updates must be applied through StarUML MCP/API or verified extension endpoints.

Do not directly concatenate, hand-patch, or synthesize `.mdj` JSON and call it a StarUML-generated project. Direct JSON inspection is allowed for read-only diagnosis only.

Do not create `.mdj` by writing a ZIP archive that contains `project.json`. For this Skill, an accepted generated `.mdj` must be saved by StarUML MCP/API and must open/export after generation.

## Common Failures

- StarUML is not running.
- API server disabled in StarUML settings.
- `NODE_OPTIONS` breaks Electron startup, especially inherited flags such as `--use-system-ca`.
- Multiple StarUML processes point ports to different projects.
- Port `58321` or `58322` is blocked.
- MCP server exposes read tools but no write tools.
- Extension is installed but not enabled.
- Diagram IDs changed after regeneration.
- Export succeeds but image theme is unreadable.

Electron main process error handling:

- First inspect `NODE_OPTIONS`.
- If `NODE_OPTIONS` contains `--use-system-ca` or other Electron-incompatible flags, ask the user to clear or adjust it and restart StarUML.
- Do not attribute this failure to antivirus/security software unless there is separate evidence.

Specific observed Electron failure:

```text
A JavaScript error occurred in the main process
TypeError: Error processing argument at index 1
conversion failure from undefined
at Object.showErrorBox
```

Interpretation:

- This is usually a secondary crash in StarUML/Electron's error dialog handler after an earlier main-process startup error.
- Do not immediately conclude the target `.mdj` is corrupt.
- First check `NODE_OPTIONS`, especially `--use-system-ca`, the StarUML launch environment, and StarUML user configuration.
- Treat the target `.mdj` as a high-probability cause only when StarUML starts cleanly with no project and then crashes when opening that specific `.mdj`.

## New Project Check

Run preflight in this order:

```text
check shell
check StarUML process
check 58321
check 58322
list MCP tools
validate read capability
validate write capability
choose route
```
