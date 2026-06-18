#!/usr/bin/env python3
"""Validate lbssb-staruml diagram manifest consistency."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


REQUIRED_ROOT_FIELDS = [
    "backend",
    "capabilityLevel",
    "starumlExecutable",
    "preflightStatus",
    "diagramCountExpected",
    "diagramCountActual",
    "exportedPngCount",
    "nativeMdjVerified",
    "fallbackUsed",
    "engineeringStatus",
    "visualStatus",
    "sourcePreservationStatus",
]

REQUIRED_DIAGRAM_FIELDS = [
    "file",
    "diagramTitle",
    "type",
    "source",
    "consistency",
    "engineeringStatus",
    "visualStatus",
]

ALLOWED_SOURCES = {"staruml-export", "draw_from_plan", "normalized", "plantuml-fallback"}
ALLOWED_CONSISTENCY = {"native", "semantic-consistent", "normalized", "unverified"}


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def diagram_records(manifest: Any) -> List[Dict[str, Any]]:
    if isinstance(manifest, list):
        return [item for item in manifest if isinstance(item, dict)]
    if not isinstance(manifest, dict):
        return []
    for key in ("diagrams", "files", "images", "pngs"):
        value = manifest.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def root(manifest: Any) -> Dict[str, Any]:
    return manifest if isinstance(manifest, dict) else {}


def resolve_file(base: Path, value: str) -> Path:
    p = Path(value)
    if p.is_absolute():
        return p
    return base / p


def is_verified(value: Any) -> bool:
    return str(value) == "Verified"


def is_unverified_or_failed(value: Any) -> bool:
    text = str(value)
    return text == "Unverified" or text.startswith("Unverified:") or text == "Failed" or text.startswith("Failed:")


def validate_manifest(path: Path, expect_diagrams: int | None = None) -> Tuple[bool, Dict[str, Any]]:
    errors: List[str] = []
    warnings: List[str] = []
    if not path.exists():
        return False, {"errors": [f"manifest missing: {path}"], "warnings": []}

    try:
        manifest = read_json(path)
    except Exception as exc:  # noqa: BLE001
        return False, {"errors": [f"manifest unreadable: {exc}"], "warnings": []}

    data = root(manifest)
    records = diagram_records(manifest)
    base = path.parent

    for field in REQUIRED_ROOT_FIELDS:
        if field not in data:
            errors.append(f"missing root field: {field}")

    backend = str(data.get("backend") or data.get("deliveryBackend") or "").lower()
    capability = str(data.get("capabilityLevel", ""))
    status = str(data.get("status") or data.get("finalStatus") or "")
    fallback_used = bool(data.get("fallbackUsed", False)) or "fallback" in backend or "plantuml" in backend
    native_verified = bool(data.get("nativeMdjVerified", False))
    engineering_status = str(data.get("engineeringStatus", ""))
    visual_status = str(data.get("visualStatus", ""))
    source_status = str(data.get("sourcePreservationStatus", ""))

    if expect_diagrams is not None and data.get("diagramCountExpected") not in (None, expect_diagrams):
        errors.append("diagramCountExpected does not match expected CLI value")
    if expect_diagrams is not None and int(data.get("diagramCountActual", -1)) != expect_diagrams:
        errors.append("diagramCountActual does not match expected CLI value")
    if records and int(data.get("exportedPngCount", len(records))) != len(records):
        errors.append("exportedPngCount does not match diagram records")

    for idx, record in enumerate(records, start=1):
        for field in REQUIRED_DIAGRAM_FIELDS:
            if field not in record:
                errors.append(f"diagram record {idx} missing field: {field}")
        file_value = record.get("file") or record.get("png") or record.get("path")
        if not file_value:
            errors.append(f"diagram record {idx} missing PNG file path")
            continue
        png = resolve_file(base, str(file_value))
        if not png.exists() or png.stat().st_size <= 0:
            errors.append(f"diagram record {idx} PNG missing or empty: {png}")
        source = str(record.get("source", ""))
        consistency = str(record.get("consistency", ""))
        diagram_visual = str(record.get("visualStatus", ""))
        diagram_engineering = str(record.get("engineeringStatus", ""))
        if source and source not in ALLOWED_SOURCES:
            errors.append(f"diagram record {idx} has invalid source: {source}")
        if consistency and consistency not in ALLOWED_CONSISTENCY:
            errors.append(f"diagram record {idx} has invalid consistency: {consistency}")
        if source == "plantuml-fallback" and consistency == "native":
            errors.append(f"diagram record {idx} plantuml-fallback cannot use consistency native")
        if source in {"draw_from_plan", "plantuml-fallback"} and consistency == "native":
            errors.append(f"diagram record {idx} non-native source cannot use consistency native")
        if status == "Verified" and not is_verified(diagram_engineering):
            errors.append(f"diagram record {idx} missing engineeringStatus Verified for final Verified")
        if status == "Verified" and not is_verified(diagram_visual):
            errors.append(f"diagram record {idx} missing visualStatus Verified for final Verified")

    if fallback_used and native_verified:
        errors.append("fallbackUsed is true but nativeMdjVerified is true")
    if fallback_used and capability == "L4":
        warnings.append("fallbackUsed is true with L4 capability; ensure native and fallback statuses are separate")
    if capability != "L4" and status == "Verified":
        errors.append("status Verified is forbidden without capabilityLevel L4")
    if "plantuml" in backend and native_verified:
        errors.append("PlantUML fallback cannot set nativeMdjVerified true")
    if status == "Verified" and not is_verified(engineering_status):
        errors.append("status Verified requires root engineeringStatus Verified")
    if status == "Verified" and not is_verified(visual_status):
        errors.append("status Verified requires root visualStatus Verified")
    if status == "Verified" and source_status and not is_verified(source_status):
        errors.append("status Verified requires root sourcePreservationStatus Verified when present")
    if status == "Verified" and not records:
        errors.append("status Verified requires at least one diagram record")
    for field_name, value in (
        ("engineeringStatus", engineering_status),
        ("visualStatus", visual_status),
        ("sourcePreservationStatus", source_status),
    ):
        if value and not is_verified(value) and not is_unverified_or_failed(value):
            errors.append(f"invalid root {field_name}: {value}")

    ok = not errors
    return ok, {
        "manifest": str(path),
        "ok": ok,
        "errors": errors,
        "warnings": warnings,
        "diagramRecords": len(records),
        "backend": backend,
        "capabilityLevel": capability,
        "nativeMdjVerified": native_verified,
        "fallbackUsed": fallback_used,
        "engineeringStatus": engineering_status,
        "visualStatus": visual_status,
        "sourcePreservationStatus": source_status,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--expect-diagrams", type=int, default=None)
    args = parser.parse_args()

    ok, report = validate_manifest(Path(args.manifest), args.expect_diagrams)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
