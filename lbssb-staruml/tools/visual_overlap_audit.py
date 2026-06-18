#!/usr/bin/env python3
"""Audit node, routed edge, and label overlap evidence for UML layout plans."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


Rect = Tuple[float, float, float, float]
Point = Tuple[float, float]


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


def diagrams(data: Any) -> List[Dict[str, Any]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        for key in ("diagrams", "layouts", "layoutPlans"):
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
            if isinstance(value, dict):
                return [item for item in value.values() if isinstance(item, dict)]
        if "type" in data or "title" in data:
            return [data]
    return []


def name_of(item: Dict[str, Any]) -> str:
    return str(item.get("name") or item.get("title") or item.get("id") or "")


def rect_of(item: Dict[str, Any]) -> Rect | None:
    if all(isinstance(item.get(k), (int, float)) for k in ("x", "y", "width", "height")):
        return (float(item["x"]), float(item["y"]), float(item["x"] + item["width"]), float(item["y"] + item["height"]))
    if all(isinstance(item.get(k), (int, float)) for k in ("left", "top", "right", "bottom")):
        return (float(item["left"]), float(item["top"]), float(item["right"]), float(item["bottom"]))
    return None


def inflate(rect: Rect, margin: float) -> Rect:
    return (rect[0] - margin, rect[1] - margin, rect[2] + margin, rect[3] + margin)


def rects_overlap(a: Rect, b: Rect) -> bool:
    return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]


def point_of(item: Any) -> Point | None:
    if isinstance(item, dict) and isinstance(item.get("x"), (int, float)) and isinstance(item.get("y"), (int, float)):
        return (float(item["x"]), float(item["y"]))
    if isinstance(item, (list, tuple)) and len(item) >= 2 and all(isinstance(v, (int, float)) for v in item[:2]):
        return (float(item[0]), float(item[1]))
    return None


def points_of(edge: Dict[str, Any], nodes: Dict[str, Rect]) -> List[Point]:
    raw = edge.get("points") or edge.get("route")
    points = [p for p in (point_of(item) for item in as_list(raw)) if p is not None]
    if len(points) >= 2:
        return points
    source = str(edge.get("from") or edge.get("source") or "")
    target = str(edge.get("to") or edge.get("target") or "")
    if source in nodes and target in nodes:
        a = nodes[source]
        b = nodes[target]
        return [((a[0] + a[2]) / 2, (a[1] + a[3]) / 2), ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)]
    return []


def label_rect(edge: Dict[str, Any]) -> Rect | None:
    label = edge.get("labelBox") or edge.get("labelBounds")
    if isinstance(label, dict):
        return rect_of(label)
    if all(isinstance(edge.get(k), (int, float)) for k in ("labelX", "labelY", "labelWidth", "labelHeight")):
        return (
            float(edge["labelX"]),
            float(edge["labelY"]),
            float(edge["labelX"] + edge["labelWidth"]),
            float(edge["labelY"] + edge["labelHeight"]),
        )
    text = str(edge.get("label") or edge.get("name") or "")
    anchor = point_of(edge.get("labelPoint"))
    if text and anchor:
        width = max(42.0, len(text) * 14.0 + 24.0)
        height = 28.0
        return (anchor[0] - width / 2, anchor[1] - height / 2, anchor[0] + width / 2, anchor[1] + height / 2)
    return None


def ccw(a: Point, b: Point, c: Point) -> bool:
    return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])


def segments_intersect(a: Point, b: Point, c: Point, d: Point) -> bool:
    return ccw(a, c, d) != ccw(b, c, d) and ccw(a, b, c) != ccw(a, b, d)


def point_in_rect(point: Point, rect: Rect) -> bool:
    return rect[0] < point[0] < rect[2] and rect[1] < point[1] < rect[3]


def segment_intersects_rect(a: Point, b: Point, rect: Rect) -> bool:
    x1, y1, x2, y2 = rect
    if point_in_rect(a, rect):
        return True
    if point_in_rect(b, rect):
        return True
    corners = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
    sides = list(zip(corners, corners[1:] + corners[:1]))
    return any(segments_intersect(a, b, c, d) for c, d in sides)


def endpoint_names(edge: Dict[str, Any]) -> set[str]:
    return {str(edge.get("from") or edge.get("source") or ""), str(edge.get("to") or edge.get("target") or "")}


def touches_endpoint_only(a: Point, b: Point, rect: Rect) -> bool:
    if point_in_rect(a, rect) or point_in_rect(b, rect):
        return True
    x1, y1, x2, y2 = rect
    on_vertical = (a[0] == b[0]) and (abs(a[0] - x1) <= 4 or abs(a[0] - x2) <= 4 or x1 <= a[0] <= x2)
    on_horizontal = (a[1] == b[1]) and (abs(a[1] - y1) <= 4 or abs(a[1] - y2) <= 4 or y1 <= a[1] <= y2)
    return on_vertical or on_horizontal


def add(findings: List[Dict[str, Any]], diagram: str, severity: str, code: str, message: str) -> None:
    findings.append({"diagram": diagram, "severity": severity, "code": code, "message": message})


def iter_edges(diagram: Dict[str, Any]) -> List[Dict[str, Any]]:
    edges: List[Dict[str, Any]] = []
    for key in ("primaryEdges", "secondaryEdges", "edges", "relations", "transitions", "messages", "includes", "extends"):
        edges.extend(item for item in as_list(diagram.get(key)) if isinstance(item, dict))
    return edges


def audit_diagram(diagram: Dict[str, Any], margin: float) -> List[Dict[str, Any]]:
    title = str(diagram.get("title") or diagram.get("diagram") or diagram.get("name") or "<unnamed>")
    dtype = str(diagram.get("type") or diagram.get("diagramType") or "").lower()
    findings: List[Dict[str, Any]] = []
    node_items = [item for item in as_list(diagram.get("elementBounds") or diagram.get("elements") or diagram.get("nodes")) if isinstance(item, dict)]
    nodes = {name_of(item): rect for item in node_items if name_of(item) and (rect := rect_of(item))}
    labels: List[Tuple[str, Rect]] = []
    edges = iter_edges(diagram)

    for edge in edges:
        edge_name = str(edge.get("label") or edge.get("name") or f"{edge.get('from')}>{edge.get('to')}")
        points = points_of(edge, nodes)
        endpoints = endpoint_names(edge)
        for a, b in zip(points, points[1:]):
            for node_name, node_rect in nodes.items():
                if node_name in endpoints and touches_endpoint_only(a, b, inflate(node_rect, margin)):
                    continue
                if segment_intersects_rect(a, b, inflate(node_rect, margin)):
                    add(findings, title, "error", "edge-crosses-node", f"Edge {edge_name} crosses or touches node {node_name}.")
        label = label_rect(edge)
        if label:
            labels.append((edge_name, label))
            for node_name, node_rect in nodes.items():
                if rects_overlap(label, inflate(node_rect, margin)):
                    add(findings, title, "error", "label-overlaps-node", f"Label {edge_name} overlaps node {node_name}.")

    for i, (name_a, rect_a) in enumerate(labels):
        for name_b, rect_b in labels[i + 1 :]:
            if rects_overlap(rect_a, rect_b):
                add(findings, title, "error", "label-overlaps-label", f"Label {name_a} overlaps label {name_b}.")

    if dtype in {"state", "umlstatechartdiagram"} and edges and not labels:
        add(findings, title, "error", "state-label-slots-missing", "State diagram has transitions but no label slots were recorded.")
    if dtype in {"usecase", "umlusecasediagram"} and len(nodes) > 8:
        routed = sum(1 for edge in edges if len(points_of(edge, nodes)) >= 3)
        if routed < max(1, len(edges) // 3):
            add(findings, title, "warning", "usecase-routes-too-direct", "Complex use case diagram has too few routed edges for side-corridor readability.")

    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--layout-plan", required=True)
    parser.add_argument("--out", default="")
    parser.add_argument("--margin", type=float, default=4.0)
    args = parser.parse_args()

    path = Path(args.layout_plan)
    if not path.exists():
        report = {
            "status": "Failed",
            "errors": [{"diagram": "<layout-plan>", "severity": "error", "code": "missing-layout-plan", "message": f"{path} does not exist."}],
            "warnings": [],
            "diagramsChecked": 0,
        }
    else:
        data = load_json(path)
        items = diagrams(data)
        findings: List[Dict[str, Any]] = []
        if not items:
            findings.append({"diagram": "<layout-plan>", "severity": "error", "code": "no-diagrams", "message": "No diagram layouts found."})
        for item in items:
            findings.extend(audit_diagram(item, args.margin))
        errors = [item for item in findings if item["severity"] == "error"]
        warnings = [item for item in findings if item["severity"] == "warning"]
        report = {"status": "Verified" if not errors else "Failed", "diagramsChecked": len(items), "errors": errors, "warnings": warnings}

    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if report["status"] == "Verified" else 1


if __name__ == "__main__":
    raise SystemExit(main())
