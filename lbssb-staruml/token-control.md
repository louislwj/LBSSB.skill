# Token Control

## High-Value Token Use

- Read diagram list.
- Extract business actors, objects, and flows.
- Generate DiagramPlan and LayoutSpec.
- Execute MCP in batches.
- Export PNG.
- Perform visual review.
- Write `.lbssb` continuation notes.

## Wasteful Token Use

- Recursive scans of `node_modules`.
- Long environment explanations.
- Repeating configuration details already written to files.
- Repeated attempts against stale diagram IDs.
- Default StarUML theme repair when PNG fallback is enough.
- Rewriting long reports by default.
- Printing complete `.mdj` JSON.

## Low-Token Strategy

1. Scan only `mcp/*.mjs`, `tools/*.py`, `tools/*.ps1`, `test/*`, `.lbssb/*`.
2. Exclude `node_modules`, build outputs, archives unless explicitly needed.
3. Check ports `58321` and `58322` early.
4. Read diagram names/types, not full model JSON, unless repairing internals.
5. Generate DiagramPlan once and reuse it for MCP and fallback rendering.
6. Batch MCP operations.
7. After export, validate count, dimensions, and a visual sample.
8. If PNG is dark/low contrast, go directly to `normalize_png_background.py` or `draw_from_plan.py`.
9. Output compact status by default.

## MCP Token Control

- MCP install and environment debugging are high-token operations; run them only in `environment` route or when production work is blocked.
- Normal production tasks must not repeatedly explain MCP installation.
- If MCP is already verified, later tasks should read only `mcp/validate-staruml-mcp.md` and `.lbssb/toolchain.md`, then continue.
- Do not rescan `mcp/node_modules/`; rely on validation records and capability checks.

## Compact Final Shape

```text
已生成/修复 <target>。
输出：<mdj>, <png-count> PNG, manifest。
门禁：<pass/fail summary>
状态：Verified | Unverified: <reason> | Failed: <reason>
```
