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


def name_of(item: Any) -> str:
    return str(item.get("name") or item.get("title") or item.get("id") or "") if isinstance(item, dict) else ""


def box_map(items: List[Any]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for item in items:
        if isinstance(item, dict) and has_box(item):
            name = name_of(item)
            if name:
                out[name] = item
    return out


def text_len(value: Any) -> int:
    return len(str(value or ""))


def edge_endpoint(edge: Any, key: str) -> str:
    if not isinstance(edge, dict):
        return ""
    value = edge.get(key)
    if isinstance(value, dict):
        return name_of(value)
    return str(value or "")


def is_actor_like(name: str, zones: List[Any], bounds_by_name: Dict[str, Dict[str, Any]]) -> bool:
    lowered = name.lower()
    if "actor" in lowered or lowered in {"reader", "teacher", "admin", "user"}:
        return True
    if any(ch in name for ch in "读者教师管理员用户"):
        return name in bounds_by_name and text_len(name) <= 4
    actor_zones = [z for z in zones if isinstance(z, dict) and "actor" in str(z.get("name", "")).lower() and has_box(z)]
    box = bounds_by_name.get(name)
    if not box:
        return False
    cx = float(box["x"]) + float(box["width"]) / 2
    cy = float(box["y"]) + float(box["height"]) / 2
    for zone in actor_zones:
        if (
            float(zone["x"]) <= cx <= float(zone["x"]) + float(zone["width"])
            and float(zone["y"]) <= cy <= float(zone["y"]) + float(zone["height"])
        ):
            return True
    return False


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
    bounds_by_name = box_map(bounds)
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
        all_edges = primary_edges + as_list(item.get("secondaryEdges") or item.get("includes") or item.get("extends"))
        actor_edges: Dict[str, int] = {}
        for edge in all_edges:
            source = edge_endpoint(edge, "from") or edge_endpoint(edge, "source")
            target = edge_endpoint(edge, "to") or edge_endpoint(edge, "target")
            for endpoint in (source, target):
                if is_actor_like(endpoint, zones, bounds_by_name):
                    actor_edges[endpoint] = actor_edges.get(endpoint, 0) + 1
        max_actor_edges = int((item.get("thresholds") or {}).get("maxActorAssociations", 6))
        for actor, count in actor_edges.items():
            if count > max_actor_edges:
                add(
                    findings,
                    title,
                    "error",
                    "usecase-too-many-actor-associations",
                    f"Actor {actor} has {count} associations; introduce module entry use cases or split the diagram.",
                )
        if len(bounded) > 8 and len(zones) < 3:
            add(findings, title, "error", "usecase-missing-module-zones", "Use case diagrams with more than 8 elements require visible module zones.")

    if dtype.lower() in {"class", "umlclassdiagram"}:
        names = " ".join(str(zone.get("name", "")).lower() for zone in zones if isinstance(zone, dict))
        if "role" not in names or "core" not in names:
            add(findings, title, "error", "class-missing-role-core-zones", "Class layout requires role/inheritance and core-domain zones.")
        label_budget_dict = label_budget if isinstance(label_budget, dict) else {}
        if label_budget_dict.get("preserveEnglishMembers") is not True:
            add(findings, title, "warning", "class-source-preservation-not-recorded", "Class layout should record preserveEnglishMembers: true when source vocabulary exists.")

    if dtype.lower() in {"state", "umlstatechartdiagram"}:
        label_budget_dict = label_budget if isinstance(label_budget, dict) else {}
        min_width = float(label_budget_dict.get("stateMinWidth") or 160)
        char_px = float(label_budget_dict.get("stateCharPx") or 14)
        for box in bounded:
            required = max(min_width, text_len(name_of(box)) * char_px + 40)
            if float(box.get("width", 0)) < required:
                add(
                    findings,
                    title,
                    "error",
                    "state-box-too-narrow",
                    f"State {name_of(box)} width {box.get('width')} is below required text budget {int(required)}.",
                )
        max_transition_chars = int(label_budget_dict.get("maxTransitionChars") or 12)
        for edge in primary_edges + as_list(item.get("secondaryEdges") or item.get("transitions")):
            label = edge.get("label") if isinstance(edge, dict) else None
            if label is None and isinstance(edge, dict):
                label = edge.get("name")
            if label and text_len(label) > max_transition_chars:
                add(findings, title, "warning", "state-transition-label-long", f"Transition label is longer than budget: {label}")

    if dtype.lower() in {"sequence", "umlsequencediagram"}:
        label_budget_dict = label_budget if isinstance(label_budget, dict) else {}
        if not any(key in label_budget_dict for key in ("lifelineGap", "messageGap", "maxMessageChars")):
            add(findings, title, "error", "sequence-missing-spacing-budget", "Sequence layouts require lifelineGap/messageGap label budgets.")
        participant_bounds = bounded
        if len(participant_bounds) >= 2:
            centers = sorted(float(box["x"]) + float(box["width"]) / 2 for box in participant_bounds)
            gaps = [b - a for a, b in zip(centers, centers[1:])]
            min_gap = float(label_budget_dict.get("lifelineGap") or 220)
            if gaps and min(gaps) < min_gap:
                add(findings, title, "error", "sequence-lifeline-gap-too-small", f"Minimum lifeline gap {int(min(gaps))} is below required {int(min_gap)}.")
        message_gap = float(label_budget_dict.get("messageGap") or 54)
        y_values: List[float] = []
        for message in primary_edges + as_list(item.get("secondaryEdges")):
            if isinstance(message, dict):
                if "y" in message and isinstance(message["y"], (int, float)):
                    y_values.append(float(message["y"]))
                points = message.get("points")
                if isinstance(points, list) and points and isinstance(points[0], dict) and isinstance(points[0].get("y"), (int, float)):
                    y_values.append(float(points[0]["y"]))
        if len(y_values) >= 2:
            gaps = [b - a for a, b in zip(sorted(y_values), sorted(y_values)[1:])]
            if gaps and min(gaps) < message_gap:
                add(findings, title, "error", "sequence-message-gap-too-small", f"Minimum message gap {int(min(gaps))} is below required {int(message_gap)}.")
        else:
            add(findings, title, "warning", "sequence-message-y-not-recorded", "Sequence message y positions are not recorded.")
        for message in primary_edges + as_list(item.get("secondaryEdges")):
            label = message.get("label") if isinstance(message, dict) else None
            if label and not str(label).strip()[0].isdigit():
                add(findings, title, "warning", "sequence-message-missing-number", f"Message lacks a visible sequence number: {label}")

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
