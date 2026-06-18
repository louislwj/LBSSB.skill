# LBSSB StarUML Skill

`lbssb-staruml` 是一个面向 StarUML UML 作业与实训交付的 Agent Skill。它用于把 MCP 检测、`.lbssb` 项目现场、DiagramPlan、StarUML `.mdj` 写入、PNG 导出、兜底渲染和 QualityGate 串成一个统一入口。

本项目诞生于一次极其折磨的 UML 实训周。它的目标很简单：让使用者少被低质量流程、混乱图形和反复返工折磨。
本 Skill 保留一个固定确认语作为启动仪式；这是项目风格的一部分，也是对本项目来源的纪念。确认语和完成语只出现在用户侧交互中，不会写入任何正式交付物。

普通用户只需要调用 Skill。`.lbssb/`、`tools/lbssb/`、`mcp/` 都是 Skill 自动管理的项目资产；用户不需要手动理解这些目录才能使用。

这个仓库是 StarUML Skill 包，不是 StarUML 软件本体，也不是 StarUML MCP 本体。仓库不会携带或重新分发 StarUML 二进制文件。

本 Skill 默认要求所有 Markdown、JSON、脚本输出、`.lbssb` 项目现场文件使用 UTF-8。遇到中文路径、中文图名或中文文档时，会先执行编码与路径安全检查。

## What It Manages

- `SKILL.md`：总入口、授权、任务路由、最终状态规则。
- `.lbssb/`：跨会话项目现场，由 Skill 按模板创建或更新。
- `mcp/`：StarUML MCP 项目资产，仅在用户授权后创建或安装。
- `tools/lbssb/`：低 token 脚本缓存，仅在导出不可读、批量验证、复刻或用户要求时生成。
- `lbssb-staruml/tools/`：Skill 自带诊断与验收工具，例如 StarUML 启动、preflight、manifest 校验、交付验收。
- `diagram-manifest.json`：记录每张 PNG 来源和一致性。
- `diagram-plan.json` / `layout-plan.json`：复杂项目中的语义与布局计划。

## When To Use

- 根据 `.mdj`、指导书、截图、用例图或需求生成 UML。
- 接受一个项目目录作为输入，读取源 `.mdj`、指导书、`.lbssb` 和已有脚本后继续工作。
- 修复 StarUML 图的语义、布局或导出问题。
- 导出清晰 PNG 并保留可编辑 `.mdj`。
- 让新会话继续同一个 UML 项目。
- 接受一个项目目录作为输入，先读取其中 `.mdj`、指导书、截图、`.lbssb/` 和 `tools/lbssb/`，再判断是继续修复还是新建。

## How To Invoke 调用方式

调用方式不固定，不需要照抄某一整段模板。只要满足这三个条件即可：

- 指定使用本 Skill。
- 输入固定确认语。
- 描述任务、输入文件和输出位置。

## Installation / Placement 放置方式
- 将 `lbssb-staruml/` 文件夹放入项目根目录。
- 在 Agent 中明确要求读取 `lbssb-staruml/SKILL.md` 并按其中规则执行。
- 如果平台支持 Skill 自动识别，可以直接使用 `$lbssb-staruml` 调用。
- 如果平台不支持 Skill 自动识别，请手动说明：“请先读取 lbssb-staruml/SKILL.md”。
  
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
所有输出放到 作业。
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
failure-patterns.md
tool-specs/mcp-readme.spec.md
tool-specs/mcp-config-examples.spec.md
tool-specs/validate-staruml-mcp.spec.md
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

StarUML `.mdj` 交付必须先通过 preflight：StarUML 可启动、`NODE_OPTIONS` 已检查、`58321/58322` 可连接、测试 `.mdj` 可打开、测试图可导出 PNG。未通过时不能声称完成可编辑 StarUML 工程。

如果 StarUML 启动出现 Electron main process error，优先检查并清理 `NODE_OPTIONS`，尤其是 `--use-system-ca`，不要默认归因于杀毒软件或安全软件。

如果只生成 PlantUML `.puml`、PNG 或文档，状态只能说明 fallback 产物完成，不能说 StarUML `.mdj` 已完成。PNG 数量和文件大小通过，不等于可编辑 `.mdj` 已通过。

本 Skill 明确禁止用脚本拼 JSON、打包 `project.json`、或把 ZIP 改名为 `.mdj` 来冒充 StarUML 工程。可编辑 `.mdj` 必须由 StarUML MCP/API 创建真实 Model、Diagram、View、Relationship，并在生成后由 StarUML 打开和导出验证。

授权创建 `mcp/` 后，Skill 应生成：

- `mcp/README.md`
- `mcp/mcp-config.example.*`
- `mcp/validate-staruml-mcp.md`

安装或注册后必须验证读取、写入、保存副本和导出 PNG；失败则标记 `MCP Unverified`。

## Project-level StarUML Runtime

项目级 StarUML 支持的是“路径解析与启动支持”，不是把 StarUML 安装包提交到仓库。如果要使用项目内 StarUML，可执行文件需要用户自己放置。

StarUML 查找优先级：

1. `.lbssb/staruml-runtime.json` 或 `lbssb-staruml/runtime/staruml-runtime.json`
2. 环境变量 `LBSSB_STARUML_EXE`
3. 项目内便携式路径：
   - `tools/StarUML/StarUML.exe`
   - `.lbssb/runtime/StarUML/StarUML.exe`
   - `mcp/StarUML/StarUML.exe`
4. 常见系统路径：
   - `C:\Program Files\StarUML\StarUML.exe`
   - `C:\Program Files (x86)\StarUML\StarUML.exe`
5. PATH 中的 `StarUML.exe`

配置模板：

```text
lbssb-staruml/templates/staruml-runtime.example.json
```

启动诊断：

```powershell
powershell -ExecutionPolicy Bypass -File lbssb-staruml/tools/start_project_staruml.ps1
```

输出：结构化 JSON，包含 `starumlExecutable`、`resolvedFrom`、`nodeOptionsDetected`、`nodeOptionsClearedForLaunch`、`processStarted`、`apiServer58321`、`extension58322`、`status`。

## Hard Preflight / Verification

preflight：

```powershell
powershell -ExecutionPolicy Bypass -File lbssb-staruml/tools/check_staruml_preflight.ps1
```

输出：

```text
.lbssb/preflight-report.json
```

交付验收：

```powershell
python lbssb-staruml/tools/verify_deliverables.py --manifest .lbssb/diagram-manifest.json
```

输出：

```text
.lbssb/verification-report.json
```

manifest 单独校验：

```powershell
python lbssb-staruml/tools/validate_manifest.py --manifest .lbssb/diagram-manifest.json
```

`Verified` 必须同时满足：

- capability level 是 `L4`；
- `.lbssb/preflight-report.json` 中 `status` 是 `Verified`；
- `.lbssb/verification-report.json` 存在；
- `verify_deliverables.py` exit code 是 `0`。

低于 `L4` 时只能 `Unverified` 或 fallback。`L0/L1/L2` 只能只读分析或 PlantUML fallback；`L3` 可以尝试 native edit，但必须说明导出/验收未完成。

## Electron showErrorBox Undefined

如果出现：

```text
A JavaScript error occurred in the main process
TypeError: Error processing argument at index 1
conversion failure from undefined
at Object.showErrorBox
```

优先按 Electron 启动环境故障处理：检查 `NODE_OPTIONS`，尤其是 `--use-system-ca`；再检查 StarUML 启动环境和用户配置。只有 StarUML 空启动正常、打开目标 `.mdj` 才崩溃时，才把 `.mdj` 文件列为高疑点。

## StarUML MCP Quick Setup

完整 MCP 闭环需要三部分：

1. `staruml_official`：读取、图清单、导出。
2. `staruml_third_party`：打开、创建、修改、保存。
3. `staruml-mcp-extension`：安装在 StarUML 内部，提供 `58322` 增强接口。

推荐项目内路径：

```text
project/mcp/
```

用户不需要一开始手动理解这些目录；当 Skill 检测到 MCP 缺失时，会提示授权创建 `mcp/` 并生成安装说明、配置示例和验证清单。

未授权时，本 Skill 不会安装依赖、下载扩展或修改 IDE 配置。

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

如果 manifest 里记录了 `plantuml-fallback`、`script fallback` 或类似后端，最终状态不得写成 StarUML native `Verified`。这类交付需要明确写：`PlantUML fallback 已生成；StarUML native .mdj 未验证/不可用。`

PNG 一致性会标记为：

- `native`：StarUML 原生导出且通过复核。
- `normalized`：StarUML 导出后只做背景/对比度处理。
- `semantic-consistent`：由 `draw_from_plan.py` 按同一 DiagramPlan 重绘。
- `unverified`：来源或语义一致性无法确认。

如果 PNG 是重绘结果，不能声称原生 `.mdj` 图布局也已同样优化。

## PlantUML Fallback

当 StarUML/MCP 不可用时，只能进入 PlantUML fallback。fallback 交付物必须明确标注为 `.puml`、PNG 或文档，不得声称生成了可编辑 StarUML `.mdj`。

PlantUML fallback 允许输出 `.puml`、`.png`、`.docx`、`.md`、`diagram-manifest.json`、`fallback-report.json`。禁止宣称 `Verified editable StarUML .mdj`、`StarUML native delivery complete`、`MCP write success`。

如果 fallback 生成 `.mdj` 骨架或 JSON 文件，必须标记为 `experimental`、`unverified`、`not StarUML-native-authored`、`not accepted as editable delivery`。

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
5. 先读取图清单、业务对象和已有类/属性/操作。
6. 生成 DiagramPlan 和 LayoutPlan。
7. 先绘制或修复一张高风险图，导出 PNG 并复核；不允许未看首张图就批量扫完并声称完成。
8. 复核通过后再批量生成或修复剩余图。
9. 用 MCP 对原生 `.mdj` 做局部移动、缩放、改线，不用全局 auto-layout 充当最终修复。
10. 导出 PNG，运行工程验收和视觉验收，并更新 `.lbssb/next-action.md`。

## Verified Means More Than Exported

`Verified` 不再只表示 `.mdj` 能打开、PNG 能导出。Native StarUML 交付需要同时通过：

- Engineering verification：StarUML/MCP 能打开、写入、保存、导出。
- Visual verification：PNG 不截字、不压线、不乱线，布局层次通过 `visual-quality-gates.md`。
- Source preservation：存在源 `.mdj` 时，已有英文类名、属性、方法和类型不会被静默覆盖。

如果工程链路通过但图像质量差，状态必须是：

```text
Unverified: diagram quality gate failed
```

manifest 根节点和每张图都必须记录：

```text
engineeringStatus
visualStatus
sourcePreservationStatus
```

缺少这些字段时，`verify_deliverables.py` 会拒绝 `Verified`。这能防止“图能导出但线乱、文字截断、源英文成员被覆盖”的交付被误报成功。
