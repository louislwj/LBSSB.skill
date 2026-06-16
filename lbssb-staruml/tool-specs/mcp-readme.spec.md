# mcp/README.md Spec

When the user authorizes project-local MCP bootstrap, generate `mcp/README.md` from this spec. Do not install dependencies merely because this spec exists.

````md
# StarUML MCP Setup

## Purpose

本目录用于存放 lbssb-staruml 的项目本地 StarUML MCP 工具。

## Included MCPs

- staruml-mcp-server：读取、生成、导出辅助
- staruml-mcp：写入、保存、图元操作
- staruml-mcp-extension：StarUML 内部增强扩展

## Required Runtime

- StarUML v7+
- Node.js 20+，推荐 22+
- PowerShell / Shell
- StarUML API Server 58321
- Extension Server 58322

## Install

只在用户授权后执行：

```powershell
npm init -y
npm install staruml-mcp-server staruml-mcp
```

## StarUML API

确认 `%APPDATA%\StarUML\settings.json` 中：

```json
{
  "apiServer": true,
  "apiServerPort": 58321
}
```

## Extension

安装 staruml-mcp-extension 后重启 StarUML，并确认 58322 可用。

## Validate

完成安装后必须执行：

1. 检查 StarUML 进程。
2. 检查端口 58321。
3. 检查端口 58322。
4. 检查 Agent 是否暴露 staruml_official。
5. 检查 Agent 是否暴露 staruml_third_party。
6. 用读取 MCP 获取图清单。
7. 用写入 MCP 保存副本。
8. 导出或获取一张 PNG。

失败则标记 `MCP Unverified`。
````
