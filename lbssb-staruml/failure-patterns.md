# Failure Patterns

Use this file to reject known bad StarUML delivery claims.

## Screenshot-Derived WorkBuddy Failure

Observed bad pattern:

- The agent reported `QualityGate: Verified`.
- The same report said StarUML GUI/MCP was unavailable.
- Outputs were PlantUML `.puml`, PNG, and documents.
- A later step created a `.mdj` anyway.
- The final text claimed the `.mdj` could be opened manually in StarUML without verified StarUML open/export evidence.

Required judgment:

- This is not a verified StarUML `.mdj` delivery.
- PNG/PlantUML success can verify only fallback images/source, not editable StarUML projects.
- If the user requested editable StarUML output, final status must be `Unverified` or `Failed`.

## Forbidden Claim Combinations

Reject the delivery if any pair appears together:

| Evidence | Forbidden claim |
|---|---|
| StarUML GUI could not launch | `Verified` native StarUML delivery |
| MCP/API ports unavailable | `.mdj` was generated as editable StarUML output |
| Manifest backend is `plantuml-fallback` or `script fallback` | `final_status: Verified` for StarUML `.mdj` delivery |
| PNG count/size passed only | StarUML project opens and diagrams are editable |
| Electron main process error remains unresolved | Manual open should work |
| Capability level is below `L4` | Completion Banner or native `Verified` |

## Forbidden Final Wording

When StarUML/MCP preflight fails, do not write:

- `UML 交付完成`
- `.mdj 文件已生成`
- `可编辑 StarUML 工程`
- `手动打开即可看到`
- `QualityGate: Verified`
- `StarUML 图已完成`

Allowed fallback wording:

```text
PlantUML fallback 已生成；StarUML native `.mdj` 未验证/不可用。
```

## Invalid `.mdj` Construction

Reject as native StarUML delivery if a script:

- uses `zipfile.ZipFile` to create `.mdj`;
- writes `project.json` into a ZIP;
- directly writes `.mdj` with `write_text`, `write_bytes`, `fs.writeFile*`, or equivalent;
- hand-builds `_type`, `_id`, `views`, relationships, or diagram JSON and calls it StarUML-generated;
- uses a direct JSON patch as the authoring mechanism instead of StarUML MCP/API.

Direct JSON reading is allowed for audit/diagnosis only.

Native StarUML delivery requires:

- Model elements created or updated through StarUML MCP/API.
- Diagrams created or updated through StarUML MCP/API.
- Views created or updated through StarUML MCP/API.
- Relationships created or updated through StarUML MCP/API.
- Project opened by StarUML after generation.
- Project saved as a copy.
- PNG exported through StarUML MCP/API.
- `tools/verify_deliverables.py` exits `0`.

## MDJ File Format Gate

For this Skill, an accepted native StarUML `.mdj` output must pass all checks:

- First non-whitespace byte is `{`.
- File parses as UTF-8 JSON-like StarUML project data.
- It was saved by StarUML MCP/API or `save_project_as`.
- It can be opened by StarUML after generation.
- It can export at least one verified PNG through StarUML MCP/API.

If first bytes are `PK\x03\x04`, treat it as a ZIP artifact, not a verified StarUML `.mdj`.

## Electron showErrorBox Undefined Failure

Observed failure:

```text
A JavaScript error occurred in the main process
TypeError: Error processing argument at index 1
conversion failure from undefined
at Object.showErrorBox
```

Rules:

- Treat this as an Electron startup/environment failure first.
- It is often a secondary crash in the error dialog handler, not the original root cause.
- First inspect `NODE_OPTIONS`, especially `--use-system-ca`.
- Then inspect StarUML launch environment and StarUML user configuration.
- Do not claim the target `.mdj` is corrupt unless StarUML can open normally with no project and crashes only when opening that `.mdj`.

## Script Static Scan

Before accepting generated helper scripts, scan for these patterns:

```text
zipfile.ZipFile
writestr('project.json'
writestr("project.json"
"_type": "Project"
write_text(
write_bytes(
fs.writeFile
final_status = "Verified"
"backend": "script fallback"
"deliveryBackend": "plantuml-fallback"
```

If a script contains fallback/backend markers and also sets native final status to `Verified`, fail the gate.
