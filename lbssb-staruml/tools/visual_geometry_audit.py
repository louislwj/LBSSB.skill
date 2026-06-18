#!/usr/bin/env python3
"""Audit layout-plan geometry evidence for StarUML visual quality gates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


COMPLEX_TYPES = {
    "usecase",
    "class",
    "state",
    "sequence",
    "communication",
    "activity",
    "UMLUseCaseDiagram",
    "UMLClassDiagram",
    "UMLStatechartDiagram",
    "UMLSequenceDiagram",
    "UMLCommunicationDiagram",
    "UMLActivityDiagram",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return list(value.values())
    return []


def get_diagrams(data: Any) -> List[Dict[str, Any]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        for key in ("diagrams", "layouts", "layoutPlans"):
            items = data.get(key)
            if isinstance(items, list):
                return [item for item in items if isinstance(item, dict)]
            if isinstance(items, dict):
                return [item for item in items.values() if isinstance(item, dict)]
        if "type" in data or "diagram" in data or "title" in data:
            return [data]
    return []


def has_box(box: Any) -> bool:
    if not isinstance(box, dict):
        return False
    keys = {"x", "y", "width", "height"}
    return keys.issubset(box.keys()) and all(isinstance(box.get(key), (int, float)) for key in keys)


def add(findings: List[Dict[str, Any]], diagram: str, severity: str, code: str, message: str) -> None:
    findings.append({"diagram": diagram, "severity": severity, "code": code, "message": message})


def audit_diagram(item: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    title = str(item.get("title") or item.get("diagram") or item.get("name") or "<unnamed>")
    dtype = str(item.get("type") or item.get("diagramType") or "")
    is_complex = dtype in COMPLEX_TYPES or dtype.lower() in COMPLEX_TYPES
    if not is_complex:
        return findings

    canvas = item.get("canvas") or item.get("page")
    if not isinstance(canvas, dict) or not all(isinstance(canvas.get(key), (int, float)) for key in ("width", "height")):
        add(findings, title, "error", "missing-canvas", "Complex diagram layout requires numeric canvas width and height.")

    zones = as_list(item.get("zones") or item.get("lanes"))
    if not zones:
        add(findings, title, "error", "missing-zones", "Complex diagram layout requires semantic zones or lanes.")
    elif not any(has_box(zone) for zone in zones):
        add(findings, title, "error", "zones-without-bounds", "Zones/lanes must include x/y/width/height bounds.")

    bounds = as_list(item.get("elementBounds") or item.get("elements") or item.get("nodes"))
    bounded = [box for box in bounds if has_box(box)]
    if not bounded:
        add(findings, title, "error", "missing-element-bounds", "Complex diagram layout requires element bounds.")

    primary_edges = as_list(item.get("primaryEdges") or item.get("mainEdges") or item.get("relations") or item.get("messages"))
    if dtype.lower() not in {"state", "UMLStatechartDiagram".lower()} and not primary_edges:
        add(findings, title, "warning", "missing-primary-edges", "No primary edge/message plan was found.")

    label_budget = item.get("labelBudget") or item.get("textBudget")
    if not isinstance(label_budget, dict):
        add(findings, title, "warning", "missing-label-budget", "No label budget was recorded for text fitting.")

    route_policy = item.get("routePolicy") or item.get("routing") or item.get("routing_rules")
    if not route_policy:
        add(findings, title, "warning", "missing-route-policy", "No routing policy was recorded for relationship/message lines.")

    if dtype.lower() in {"usecase", "umlusecasediagram"}:
        names = " ".join(str(zone.get("name", "")).lower() for zone in zones if isinstance(zone, dict))
        if "actor" not in names or ("boundary" not in names and "system" not in names):
            add(findings, title, "error", "usecase-missing-actor-boundary-zones", "Use case layout requires actor and system-boundary zones.")

    if dtype.lower() in {"class", "umlclassdiagram"}:
        names = " ".join(str(zone.get("name", "")).lower() for zone in zones if isinstance(zone, dict))
        if "role" not in names or "core" not in names:
            add(findings, title, "error", "class-missing-role-core-zones", "Class layout requires role/inheritance and core-domain zones.")

    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--layout-plan", required=True, help="Path to .lbssb/layout-plan.json")
    parser.add_argument("--out", default="", help="Optional JSON report output path")
    args = parser.parse_args()

    path = Path(args.layout_plan)
    if not path.exists():
        report: Dict[str, Any] = {
            "status": "Failed",
            "errors": [{"severity": "error", "code": "missing-layout-plan", "message": f"{path} does not exist."}],
            "warnings": [],
            "diagramsChecked": 0,
        }
    else:
        data = load_json(path)
        diagrams = get_diagrams(data)
        findings: List[Dict[str, Any]] = []
        if not diagrams:
            findings.append(
                {
                    "diagram": "<layout-plan>",
                    "severity": "error",
                    "code": "no-diagram-layouts",
                    "message": "Layout plan contains no diagram layout entries.",
                }
            )
        for diagram in diagrams:
            findings.extend(audit_diagram(diagram))
        errors = [item for item in findings if item["severity"] == "error"]
        warnings = [item for item in findings if item["severity"] == "warning"]
        report = {
            "status": "Verified" if not errors else "Failed",
            "diagramsChecked": len(diagrams),
            "errors": errors,
            "warnings": warnings,
        }

    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if report["status"] == "Verified" else 1


if __name__ == "__main__":
    raise SystemExit(main())
