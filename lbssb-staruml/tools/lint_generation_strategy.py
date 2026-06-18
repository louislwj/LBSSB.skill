#!/usr/bin/env python3
"""Lint StarUML generation scripts for unsafe final-delivery patterns."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List


SCRIPT_SUFFIXES = {".js", ".mjs", ".cjs", ".py", ".ps1", ".ts"}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def iter_scripts(paths: Iterable[Path]) -> Iterable[Path]:
    for path in paths:
        if path.is_file() and path.suffix.lower() in SCRIPT_SUFFIXES:
            yield path
        elif path.is_dir():
            for child in path.rglob("*"):
                if child.is_file() and child.suffix.lower() in SCRIPT_SUFFIXES:
                    yield child


def add(findings: List[Dict[str, Any]], path: Path, severity: str, code: str, message: str) -> None:
    findings.append(
        {
            "file": str(path),
            "severity": severity,
            "code": code,
            "message": message,
        }
    )


def has_any(text: str, patterns: Iterable[str]) -> bool:
    return any(pattern in text for pattern in patterns)


def writes_mdj_directly(text: str) -> bool:
    if has_any(text, ["zipfile.ZipFile", "writestr('project.json'", 'writestr("project.json"']):
        return True

    write_call_patterns = [
        r"write_text\s*\([^)]*\.mdj",
        r"write_bytes\s*\([^)]*\.mdj",
        r"open\s*\([^)]*\.mdj[^)]*['\"]w",
        r"fs\.writeFile(?:Sync)?\s*\([^,\n)]*\.mdj",
    ]
    if any(re.search(pattern, text, re.IGNORECASE | re.DOTALL) for pattern in write_call_patterns):
        return True

    project_json_synthesis = '"_type": "Project"' in text and has_any(
        text,
        ["write_text", "write_bytes", "fs.writeFile", "fs.writeFileSync", "json.dump", "JSON.stringify"],
    )
    return project_json_synthesis


def lint_file(path: Path, native_final: bool, source_preservation_required: bool) -> List[Dict[str, Any]]:
    text = read_text(path)
    lower = text.lower()
    findings: List[Dict[str, Any]] = []

    if writes_mdj_directly(text):
        add(
            findings,
            path,
            "error",
            "direct-mdj-synthesis",
            "Script appears to synthesize or write .mdj/project JSON directly; native delivery must use StarUML MCP/API.",
        )

    mermaid_final = "generate_diagram" in text and has_any(
        text,
        ["sequenceDiagram", "stateDiagram-v2", "stateDiagram", "flowchart ", "graph TD", "graph LR"],
    )
    if mermaid_final:
        add(
            findings,
            path,
            "error" if native_final else "warning",
            "mermaid-import-final-risk",
            "Mermaid import is a draft accelerator only; final native diagrams require export review and local repair.",
        )

    global_layout = "/layout_diagram" in text or "layout_diagram" in text or re.search(r"\bawait\s+layout\s*\(", text)
    local_repair_markers = has_any(
        lower,
        ["repairpass", "repair_pass", "move view", "resize view", "reroute", "edge routing", "local repair"],
    )
    if global_layout and not local_repair_markers:
        add(
            findings,
            path,
            "error" if native_final else "warning",
            "global-layout-without-repair",
            "Global auto-layout is present without evidence of a local move/resize/reroute repair loop.",
        )

    class_rebuild = has_any(text, ["createClassDiagram", "UMLClass"]) and re.search(
        r'["\'].*[\u4e00-\u9fff].*:\s*(String|Integer|Decimal|Date|DateTime|Time|Boolean)',
        text,
    )
    if class_rebuild and source_preservation_required:
        add(
            findings,
            path,
            "error",
            "class-source-vocabulary-loss-risk",
            "Class diagram appears to hard-code translated members while source preservation is required.",
        )
    elif class_rebuild:
        add(
            findings,
            path,
            "warning",
            "hard-coded-class-members",
            "Class diagram contains hard-coded member definitions; confirm they came from source inventory or diagram-plan.",
        )

    row_column_usecase = "UMLUseCase" in text and re.search(r"\(i\s*%\s*\d+\)|Math\.floor\s*\(\s*i\s*/", text)
    if row_column_usecase:
        add(
            findings,
            path,
            "error" if native_final else "warning",
            "grid-usecase-layout",
            "Use case diagram uses row/column placement; final use case layout must use module zones and boundary planning.",
        )

    export_only_at_end = (
        re.search(r"diagramRecords\.length\s*[=!]=+\s*\d+", text)
        and has_any(text, ["exportImages", "get_diagram_image_by_id"])
        and not has_any(lower, ["pilot", "highest-risk", "visual review before batch"])
    )
    if export_only_at_end:
        add(
            findings,
            path,
            "error" if native_final else "warning",
            "missing-pilot-gate",
            "Script appears to batch-create diagrams and export at the end without a pilot visual gate.",
        )

    hard_coded_absolute = re.search(r'["\'][A-Za-z]:[\\/]', text)
    if hard_coded_absolute:
        add(
            findings,
            path,
            "warning",
            "hard-coded-absolute-path",
            "Script contains hard-coded absolute paths; reusable Skill scripts should accept project-root parameters.",
        )

    verified_claim = has_any(text, ['"status": "Verified"', '"finalStatus": "Verified"', "final_status = \"Verified\""])
    delivery_context = has_any(
        lower,
        ["diagram-manifest", "nativemdjverified", "finalstatus", "deliverable", "staruml", "mdj"],
    )
    visual_fields = has_any(text, ["visualStatus", "sourcePreservationStatus", "engineeringStatus"])
    if verified_claim and delivery_context and not visual_fields:
        add(
            findings,
            path,
            "error",
            "verified-without-split-status",
            "Script can claim Verified without split engineering/visual/source-preservation status fields.",
        )

    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", help="Script files or directories to scan")
    parser.add_argument("--native-final", action="store_true", help="Treat scanned scripts as candidates for final native StarUML delivery")
    parser.add_argument(
        "--source-preservation-required",
        action="store_true",
        help="Fail hard-coded translated class members when source vocabulary must be preserved",
    )
    parser.add_argument("--out", default="", help="Optional JSON report output path")
    args = parser.parse_args()

    input_paths = [Path(value).resolve() for value in args.paths]
    files = sorted({path for path in iter_scripts(input_paths)})
    findings: List[Dict[str, Any]] = []
    for file_path in files:
        findings.extend(lint_file(file_path, args.native_final, args.source_preservation_required))

    errors = [item for item in findings if item["severity"] == "error"]
    warnings = [item for item in findings if item["severity"] == "warning"]
    report: Dict[str, Any] = {
        "status": "Verified" if not errors else "Failed",
        "filesScanned": len(files),
        "errors": errors,
        "warnings": warnings,
        "nativeFinal": args.native_final,
        "sourcePreservationRequired": args.source_preservation_required,
    }

    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        out = Path(args.out).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
