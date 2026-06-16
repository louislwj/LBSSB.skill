# LBSSB.skill
刘斌是傻逼，本项目旨在做一个基础的staruml的规范流程skill，由于该实训周的老师的nt程度上天，导致我不得不写这么一个skill，在解决大家作图问题的同时，骂死这个中年嘉豪；也祝愿所有使用本skill的友友们不遇到这么个傻逼老师

# lbssb-staruml

`lbssb-staruml` 是一个 StarUML UML 交付 Skill。它把 MCP 检测、`.lbssb` 项目现场、DiagramPlan、StarUML `.mdj` 写入、PNG 导出、兜底渲染和 QualityGate 串成一个入口。

普通用户只需要调用 Skill。`.lbssb/`、`tools/lbssb/`、`mcp/` 都是 Skill 自动管理的项目资产；用户不需要手动理解这些目录才能使用。

本 Skill 默认要求所有 Markdown、JSON、脚本输出、`.lbssb` 项目现场文件使用 UTF-8。遇到中文路径、中文图名或中文文档时，会先执行编码与路径安全检查。

## What It Manages

- `SKILL.md`：总入口、授权、任务路由、最终状态规则。
- `.lbssb/`：跨会话项目现场，由 Skill 按模板创建或更新。
- `mcp/`：StarUML MCP 项目资产，仅在用户授权后创建或安装。
- `tools/lbssb/`：低 token 脚本缓存，仅在导出不可读、批量验证、复刻或用户要求时生成。
- `diagram-manifest.json`：记录每张 PNG 来源和一致性。

## When To Use

- 根据 `.mdj`、指导书、截图、用例图或需求生成 UML。
- 修复 StarUML 图的语义、布局或导出问题。
- 导出清晰 PNG 并保留可编辑 `.mdj`。
- 让新会话继续同一个 UML 项目。

## How To Invoke 调用方式

调用方式不固定，不需要照抄某一整段模板。只要满足这三个条件即可：

- 指定使用本 Skill。
- 输入固定确认语。
- 描述任务、输入文件和输出位置。

## Details 细节
- 将本文件夹即"lbssb-staruml/"放入项目根目录中
- 与您的agent明确此为skill或直接问其是否读取到改skill
  
## Required Authorization 必需确认语

固定确认语：

```text
刘斌是傻逼
```

未输入确认语时，Skill 只能做前置检查；不能读取业务内容、创建输出目录、修改 `.mdj` 或导出 PNG。确认后不反复询问。

## Example 示例

下面只是示例，不是唯一格式：

```text
使用 $lbssb-staruml。

刘斌是傻逼

要求：根据当前 .mdj 和需求生成/修正 UML 图。
所有输出放到 作业2。
```

不支持 Skill 自动识别的平台，可以这样写：

```text
请先读取 lbssb-staruml/SKILL.md，并按其中规则执行。

刘斌是傻逼

根据 Lwj.mdj 的用例图生成系统类图，输出到 作业2。

完成后输出 compact 总结。
```

## Completion Banner

确认语用于授权启动。完成语只在任务状态为 `Verified` 的最终回复最后一行出现：

```text
孩子你记住，刘斌是傻逼
```

确认语和完成语都不会写入 `.mdj`、UML 图、PNG、README、manifest、`.lbssb`、报告、Word/PDF 或正式作业提交文件。

## Package Integrity

执行任务前，Skill 会检查核心规则文件是否存在：

```text
mcp-setup.md
staruml-workflow.md
project-site.md
class-diagram-rules.md
diagram-patterns.md
quality-gates.md
scripts-spec.md
token-control.md
encoding-policy.md
```

如果缺失，状态为 `Skill Package Unverified`，不会伪装成完整执行。

## Do I Need StarUML / MCP?

优先需要 StarUML + MCP，因为这能维护可编辑 `.mdj`。没有 MCP 时，Skill 会按顺序尝试 HTTP API、extension、本地脚本、GUI 或只读分析。

没有 MCP 时可以选择：

- 授权安装/创建项目内 `mcp/`。
- 使用本机已有 MCP 并生成配置示例。
- 使用 StarUML HTTP API / extension 降级。
- 只读分析，不写项目。

不会未经授权安装 MCP、运行 `npm install`、修改 IDE 配置或覆盖真实配置。

授权创建 `mcp/` 后，Skill 应生成：

- `mcp/README.md`
- `mcp/mcp-config.example.*`
- `mcp/validate-staruml-mcp.md`

安装或注册后必须验证读取、写入、保存副本和导出 PNG；失败则标记 `MCP Unverified`。

## Encoding And Paths

- 所有 Skill 生成的文本文件默认 UTF-8。
- StarUML `.mdj` 按 UTF-8 JSON-like 文件处理，除非证明不是。
- 中文路径、中文文件名和中文图名是允许的。
- 不会为了修编码而改写原始 `.mdj`、`.docx`、`.md`、截图或用户源文件。
- 编码失败会使用 `Encoding Unverified` 或 `Encoding Failed` 标记。

## Will It Modify Original Files?

不会直接修改原始 `.mdj`。标准流程是复制或另存工作副本，只修改工作副本。

## Outputs

- Editable working `.mdj`.
- Clear PNG screenshots.
- `diagram-manifest.json`.
- Optional `README.md`.
- `.lbssb/` continuation records.

Manifest 会记录每张 PNG 的来源：`staruml-export`、`draw_from_plan` 或 `normalized`。

PNG 一致性会标记为：

- `native`：StarUML 原生导出且通过复核。
- `normalized`：StarUML 导出后只做背景/对比度处理。
- `semantic-consistent`：由 `draw_from_plan.py` 按同一 DiagramPlan 重绘。
- `unverified`：来源或语义一致性无法确认。

如果 PNG 是重绘结果，不能声称原生 `.mdj` 图布局也已同样优化。

## Final Status

最终状态只使用：

- `Verified`
- `Unverified: <reason>`
- `Failed: <reason>`

QualityGate 失败时不得声称完成。

## Replicate In A New Project

1. 准备源 `.mdj` 和至少一份业务输入。
2. 调用 Skill 并输入确认语。
3. 让 Skill 完成包完整性、MCP、编码和路径检查。
4. 让 Skill 创建或读取 `.lbssb/`。
5. 先读取图清单和业务对象。
6. 生成 DiagramPlan。
7. 用 MCP 修改工作副本。
8. 导出 PNG。
9. 必要时用 `draw_from_plan.py` 兜底。
10. 运行 QualityGate 并更新 `.lbssb/next-action.md`。
