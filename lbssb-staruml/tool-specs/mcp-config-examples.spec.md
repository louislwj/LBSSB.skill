# MCP Config Examples Spec

When the user authorizes project-local MCP bootstrap, generate these example files:

- `mcp/mcp-config.example.toml`
- `mcp/mcp-config.example.json`

Do not overwrite real IDE/Agent configuration unless the user explicitly authorizes it.

## Codex-style TOML Example

```toml
# Example only. Do not blindly copy without checking your Agent config schema.

[mcp_servers.staruml_official]
command = "node"
args = ["mcp/node_modules/staruml-mcp-server/build/index.js"]
cwd = "."

[mcp_servers.staruml_third_party]
command = "node"
args = ["mcp/node_modules/staruml-mcp/dist/index.js"]
cwd = "."
```

Rule:

```text
If the current Codex config format differs from this example, the Agent must read the local config format before producing an adapted version. Do not force-write this example.
```

## Claude / Cursor / Other JSON Example

```json
{
  "mcpServers": {
    "staruml_official": {
      "command": "node",
      "args": ["mcp/node_modules/staruml-mcp-server/build/index.js"]
    },
    "staruml_third_party": {
      "command": "node",
      "args": ["mcp/node_modules/staruml-mcp/dist/index.js"]
    }
  }
}
```

Rule:

```text
JSON is only a generic MCP config shape. Platform-specific locations and fields may differ; the Agent must confirm the platform before advising a live config change.
```
