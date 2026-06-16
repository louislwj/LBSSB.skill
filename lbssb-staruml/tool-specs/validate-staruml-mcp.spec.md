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

1. Open or read the target `.mdj`.
2. Read project basic info.
3. Read diagram list.
4. Export or fetch one PNG.
5. Save one copy to the output directory.
6. Re-read the copied project's diagram list.

Success:

```text
MCP Verified
```

Failure:

```text
MCP Unverified: <reason>
```
