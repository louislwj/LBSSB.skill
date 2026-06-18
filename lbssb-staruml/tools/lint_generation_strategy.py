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


def has_regex(text: str, patterns: Iterable[str], flags: int = 0) -> bool:
    return any(re.search(pattern, text, flags) for pattern in patterns)


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
    name_lower = path.name.lower()
    findings: List[Dict[str, Any]] = []
    mutating_native_script = has_any(
        lower,
        [
            "create_element",
            "createelement",
            "create_model",
            "create diagram",
            "creatediagram",
            "create_diagram",
            "create_view",
            "createview",
            "set_view_bounds",
            "setviewbounds",
            "set_edge_points",
            "setedgepoints",
            "update_element",
            "updateelement",
            "delete_element",
            "deleteelement",
            "generate_diagram",
            "layout_diagram",
            "save_project_as",
        ],
    )
    complex_native_markers = has_any(
        text,
        [
            "UMLUseCaseDiagram",
            "UMLClassDiagram",
            "UMLStatechartDiagram",
            "UMLSequenceDiagram",
            "UMLCommunicationDiagram",
            "UMLActivityDiagram",
            "UMLUseCase",
            "UMLClass",
            "UMLState",
            "UMLLifeline",
        ],
    )
    layout_plan_markers = has_any(
        lower,
        [
            "layout-plan.json",
            "layoutplan",
            "elementbounds",
            "set_view_bounds",
            "setviewbounds",
            "view bounds",
            "bounds:",
            "primaryedges",
            "routepolicy",
        ],
    )
    reads_layout_plan = has_regex(
        lower,
        [
            r"readfilesync\s*\([^)]*layout-plan\.json",
            r"read_text\s*\([^)]*layout-plan\.json",
            r"open\s*\([^)]*layout-plan\.json",
            r"json\.loads?\([^)]*layout-plan",
        ],
        re.DOTALL,
    )
    utility_script = any(
        marker in name_lower
        for marker in (
            "preflight",
            "export",
            "reopen",
            "verify",
            "validate",
            "render",
            "normalize",
            "flatten",
            "status",
            "manifest",
        )
    )
    final_authoring_script = mutating_native_script and not utility_script

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

    if native_final and final_authoring_script and complex_native_markers and not layout_plan_markers:
        add(
            findings,
            path,
            "error",
            "missing-layout-plan",
            "Complex native diagrams require a LayoutPlan or explicit bounds/routes before final generation.",
        )
    if native_final and final_authoring_script and complex_native_markers and "layout-plan.json" in lower and not reads_layout_plan:
        add(
            findings,
            path,
            "warning",
            "layout-plan-mentioned-not-read",
            "Script mentions layout-plan.json but does not appear to parse it; confirm bounds/routes are not stale hard-coded copies.",
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

    sequence_without_spacing = (
        native_final
        and final_authoring_script
        and ("UMLSequenceDiagram" in text or "UMLLifeline" in text or "sequenceDiagram" in text)
        and not has_any(lower, ["lifelinegap", "messagegap", "message y", "messagey", "set_view_bounds", "elementbounds"])
    )
    if sequence_without_spacing:
        add(
            findings,
            path,
            "error",
            "sequence-without-spacing-plan",
            "Final sequence diagrams require explicit lifeline spacing and message vertical positions.",
        )

    sequence_labels = re.findall(r'["\']([^"\']{1,80})["\']', text)
    likely_sequence_script = native_final and final_authoring_script and (
        "UMLSequenceDiagram" in text or "UMLLifeline" in text or "sequenceDiagram" in text
    )
    if likely_sequence_script:
        human_message_labels = [
            label
            for label in sequence_labels
            if re.search(r"[\u4e00-\u9fff]", label) and not re.match(r"^\d+(\.\d+)?:", label.strip())
        ]
        if len(human_message_labels) >= 3 and not has_any(lower, ["message number", "messagenumber", "sequence number", "numbered"]):
            add(
                findings,
                path,
                "warning",
                "sequence-messages-not-numbered",
                "Sequence diagram appears to contain unnumbered message labels; final diagrams require visible sequence numbers.",
            )

    state_without_box_sizing = (
        native_final
        and final_authoring_script
        and ("UMLStatechartDiagram" in text or "UMLState" in text or "stateDiagram" in text)
        and not has_any(lower, ["state width", "statewidth", "labelbudget", "elementbounds", "set_view_bounds"])
    )
    if state_without_box_sizing:
        add(
            findings,
            path,
            "error",
            "state-without-box-sizing",
            "Final state diagrams require explicit state box sizing from label length.",
        )

    source_inventory_markers = has_any(lower, ["source-inventory", "sourceinventory", "preservedclasses", "preserve_existing"])
    class_without_source_inventory = (
        native_final
        and final_authoring_script
        and source_preservation_required
        and ("UMLClassDiagram" in text or "UMLClass" in text or "createClassDiagram" in text)
        and not source_inventory_markers
    )
    if class_without_source_inventory:
        add(
            findings,
            path,
            "error",
            "class-without-source-inventory",
            "Class diagram scripts must read or embed source inventory when source preservation is required.",
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

    exports_png = has_any(text, ["get_diagram_image_by_id", "exportImages", "export_diagram", "native-current-diagrams"])
    visual_review_markers = has_any(
        lower,
        [
            "visual-review.json",
            "visualstatus",
            "visualreviewedat",
            "reviewedat",
            "pilot-review",
            "screenshot",
            "view_image",
        ],
    )
    if native_final and final_authoring_script and exports_png and not visual_review_markers:
        add(
            findings,
            path,
            "warning",
            "export-without-visual-review-record",
            "Script exports PNGs but does not record visual review evidence; exports alone cannot prove diagram quality.",
        )

    usecase_actor_entry_markers = has_any(lower, ["actorentry", "entryusecase", "module entry", "actor connects"])
    if native_final and final_authoring_script and "UMLUseCaseDiagram" in text and "UMLAssociation" in text and not usecase_actor_entry_markers:
        add(
            findings,
            path,
            "warning",
            "usecase-without-entry-policy",
            "Use case script creates actor associations without an explicit actor-entry/module policy.",
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
