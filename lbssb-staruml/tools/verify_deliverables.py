#!/usr/bin/env python3
"""Verify lbssb-staruml deliverables and write verification-report.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_manifest import validate_manifest  # noqa: E402


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def first_non_ws(path: Path) -> bytes:
    with path.open("rb") as f:
        data = f.read(64)
    return data.lstrip()[:4]


def root(manifest: Any) -> Dict[str, Any]:
    return manifest if isinstance(manifest, dict) else {}


def mdj_from_manifest(manifest: Dict[str, Any], manifest_path: Path) -> str:
    value = manifest.get("mdj") or manifest.get("mdjFile") or manifest.get("nativeMdj") or ""
    if not value:
        return ""
    p = Path(str(value))
    if p.is_absolute():
        return str(p)
    return str((manifest_path.parent / p).resolve())


def check_mdj(path: Path, native_required: bool) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []
    if not path.exists():
        errors.append(f".mdj missing: {path}")
        return errors, warnings
    if path.stat().st_size <= 0:
        errors.append(f".mdj empty: {path}")
        return errors, warnings
    head = first_non_ws(path)
    if head.startswith(b"PK"):
        errors.append(".mdj is a ZIP artifact (PK magic), not accepted as native StarUML delivery")
    elif native_required and not head.startswith(b"{"):
        errors.append(".mdj first non-whitespace byte is not JSON object start")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--mdj", default="")
    parser.add_argument("--preflight", default=".lbssb/preflight-report.json")
    parser.add_argument("--out", default=".lbssb/verification-report.json")
    parser.add_argument("--expect-diagrams", type=int, default=None)
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = (project_root / manifest_path).resolve()
    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = (project_root / out_path).resolve()
    preflight_path = Path(args.preflight)
    if not preflight_path.is_absolute():
        preflight_path = (project_root / preflight_path).resolve()

    errors: List[str] = []
    warnings: List[str] = []
    invalid_input = False

    if not manifest_path.exists():
        invalid_input = True
        errors.append(f"manifest missing: {manifest_path}")
        report = {"status": "Failed", "errors": errors, "warnings": warnings}
        write_json(out_path, report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 2

    try:
        manifest_obj = read_json(manifest_path)
    except Exception as exc:  # noqa: BLE001
        invalid_input = True
        errors.append(f"manifest unreadable: {exc}")
        report = {"status": "Failed", "errors": errors, "warnings": warnings}
        write_json(out_path, report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 2

    manifest_root = root(manifest_obj)
    manifest_ok, manifest_report = validate_manifest(manifest_path, args.expect_diagrams)
    errors.extend(manifest_report.get("errors", []))
    warnings.extend(manifest_report.get("warnings", []))

    preflight = {}
    if preflight_path.exists():
        try:
            preflight = read_json(preflight_path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"preflight report unreadable: {exc}")
    else:
        errors.append(f"preflight report missing: {preflight_path}")

    capability = str(manifest_root.get("capabilityLevel") or preflight.get("capabilityLevel") or "")
    preflight_status = str(manifest_root.get("preflightStatus") or preflight.get("status") or "")
    fallback_used = bool(manifest_root.get("fallbackUsed", False))
    native_verified = bool(manifest_root.get("nativeMdjVerified", False))
    backend = str(manifest_root.get("backend") or manifest_root.get("deliveryBackend") or "").lower()
    status_claim = str(manifest_root.get("status") or manifest_root.get("finalStatus") or "")

    mdj_value = args.mdj or mdj_from_manifest(manifest_root, manifest_path)
    native_required = not fallback_used and "plantuml" not in backend and "fallback" not in backend
    if native_required or mdj_value:
        if not mdj_value:
            errors.append("native .mdj required but no .mdj path was provided")
        else:
            mdj_path = Path(mdj_value)
            if not mdj_path.is_absolute():
                mdj_path = (project_root / mdj_path).resolve()
            mdj_errors, mdj_warnings = check_mdj(mdj_path, native_required)
            errors.extend(mdj_errors)
            warnings.extend(mdj_warnings)

    if fallback_used and native_verified:
        errors.append("fallbackUsed true forbids nativeMdjVerified true")
    if "plantuml" in backend and native_verified:
        errors.append("PlantUML fallback forbids nativeMdjVerified true")
    if capability != "L4" and status_claim == "Verified":
        errors.append("manifest claims Verified without capabilityLevel L4")
    if preflight_status != "Verified":
        errors.append("preflightStatus is not Verified")
    if capability != "L4":
        errors.append("capabilityLevel is not L4")
    if native_required and not native_verified:
        errors.append("native delivery required but nativeMdjVerified is false")

    verified = not errors and manifest_ok and capability == "L4" and preflight_status == "Verified" and native_verified
    final_status = "Verified" if verified else "Unverified"
    if invalid_input:
        final_status = "Failed"

    report: Dict[str, Any] = {
        "status": final_status,
        "manifest": str(manifest_path),
        "preflight": str(preflight_path),
        "capabilityLevel": capability,
        "preflightStatus": preflight_status,
        "nativeMdjVerified": native_verified,
        "fallbackUsed": fallback_used,
        "backend": backend,
        "errors": errors,
        "warnings": warnings,
        "manifestReport": manifest_report,
    }
    write_json(out_path, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if verified:
        return 0
    return 2 if invalid_input else 1


if __name__ == "__main__":
    raise SystemExit(main())
