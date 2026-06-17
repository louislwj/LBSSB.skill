# validate-staruml-mcp.md Spec

When the user authorizes project-local MCP bootstrap, generate `mcp/validate-staruml-mcp.md` from this spec.

## Windows PowerShell Checks

Node/npm:

```powershell
node -v
npm -v
where node
where npm
```

Ports:

```powershell
netstat -ano | Select-String -Pattern ":58321|:58322|:58323"
```

Node/Electron environment:

```powershell
Get-ChildItem Env:NODE_OPTIONS
```

Requirement:

```text
If StarUML reports Electron main process error, inspect NODE_OPTIONS first.
If NODE_OPTIONS contains --use-system-ca or other incompatible flags, ask the user to clear/correct it and restart StarUML.
```

Project-local MCP files:

```powershell
Test-Path .\mcp\node_modules\staruml-mcp
Test-Path .\mcp\node_modules\staruml-mcp-server
Test-Path .\mcp\staruml-mcp-extension
```

StarUML settings:

```powershell
Get-Content "$env:APPDATA\StarUML\settings.json" -Raw -Encoding UTF8
```

Requirements:

```text
apiServer must be true
apiServerPort must be 58321
```

## Agent MCP Checks

The Agent must confirm through its own tool list:

```text
is staruml_official exposed?
is staruml_third_party exposed?
does staruml_official have get_all_diagrams_info?
does staruml_third_party have open_project / save_project_as?
```

## Functional Validation

Validate only on a working copy:

1. Confirm `StarUML.exe` is installed and launchable.
2. Create a minimum test `.mdj` in a temp/output directory.
3. Open the test `.mdj` in StarUML.
4. Create/read a tiny test model and diagram through MCP/API.
5. Export or fetch one test PNG.
6. Open or read the target `.mdj`.
7. Read project basic info.
8. Read diagram list.
9. Save one copy to the output directory.
10. Re-read the copied project's diagram list.

Success:

```text
MCP Verified
```

Failure:

```text
MCP Unverified: <reason>
```
