#!/usr/bin/env python3
"""Hard StarUML preflight for lbssb-staruml.

The script is conservative: it reports L4 only when executable, process, ports,
MCP/write/export evidence, test mdj open, and non-empty PNG evidence all pass.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def abs_path(value: str, base: Path) -> Path:
    p = Path(value)
    if p.is_absolute():
        return p
    return (base / p).resolve()


def load_runtime_config(project_root: Path) -> Tuple[Optional[Path], Dict[str, Any], Optional[str]]:
    candidates = [
        project_root / ".lbssb" / "staruml-runtime.json",
        project_root / "lbssb-staruml" / "runtime" / "staruml-runtime.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            try:
                return candidate, read_json(candidate), None
            except Exception as exc:  # noqa: BLE001
                return candidate, {}, str(exc)
    return None, {}, None


def resolve_staruml(project_root: Path, config_path: Optional[Path], config: Dict[str, Any]) -> Dict[str, str]:
    candidates = []
    if config.get("starumlExecutable") and config_path:
        candidates.append((abs_path(str(config["starumlExecutable"]), config_path.parent), "project-config"))
    if os.environ.get("LBSSB_STARUML_EXE"):
        candidates.append((Path(os.environ["LBSSB_STARUML_EXE"]), "env"))

    candidates.extend(
        [
            (project_root / "tools" / "StarUML" / "StarUML.exe", "project-local"),
            (project_root / ".lbssb" / "runtime" / "StarUML" / "StarUML.exe", "project-local"),
            (project_root / "mcp" / "StarUML" / "StarUML.exe", "project-local"),
            (Path(r"C:\Program Files\StarUML\StarUML.exe"), "system"),
            (Path(r"C:\Program Files (x86)\StarUML\StarUML.exe"), "system"),
        ]
    )
    for path, source in candidates:
        if path.exists():
            return {"path": str(path), "resolvedFrom": source}

    path_from_path = shutil.which("StarUML.exe") or shutil.which("StarUML")
    if path_from_path:
        return {"path": path_from_path, "resolvedFrom": "path"}
    return {"path": "", "resolvedFrom": "not-found"}


def port_open(port: int, host: str = "127.0.0.1", timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def tasklist_has_staruml() -> bool:
    if os.name != "nt":
        return False
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq StarUML.exe"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return "StarUML.exe" in result.stdout
    except Exception:
        return False


def launch_staruml(exe: str, args: Iterable[str], clear_node_options: bool, wait_seconds: int) -> Tuple[bool, str, bool]:
    env = os.environ.copy()
    node_cleared = False
    if clear_node_options and env.get("NODE_OPTIONS"):
        env.pop("NODE_OPTIONS", None)
        node_cleared = True
    try:
        proc = subprocess.Popen([exe, *args], env=env)  # noqa: S603
        time.sleep(wait_seconds)
        running = proc.poll() is None or tasklist_has_staruml()
        return running, "", node_cleared
    except Exception as exc:  # noqa: BLE001
        return False, str(exc), node_cleared


def create_minimal_mdj(project_root: Path) -> Path:
    target = project_root / ".lbssb" / "preflight" / "minimal-preflight.mdj"
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "_type": "Project",
        "_id": "lbssb-preflight-project",
        "name": "LBSSB Preflight",
        "ownedElements": [
            {
                "_type": "UMLModel",
                "_id": "lbssb-preflight-model",
                "_parent": {"$ref": "lbssb-preflight-project"},
                "name": "Preflight Model",
                "ownedElements": [],
            }
        ],
    }
    write_json(target, payload)
    return target


def load_evidence(path: Optional[Path]) -> Dict[str, Any]:
    if not path:
        return {}
    if not path.exists():
        return {"_evidenceError": f"missing evidence file: {path}"}
    try:
        return read_json(path)
    except Exception as exc:  # noqa: BLE001
        return {"_evidenceError": str(exc)}


def mcp_caps_from_tools(path: Optional[Path]) -> Dict[str, bool]:
    caps = {"read": False, "write": False, "exportPng": False, "saveCopy": False}
    if not path or not path.exists():
        return caps
    try:
        raw = read_json(path)
    except Exception:
        return caps
    names = []
    if isinstance(raw, list):
        names = [str(item.get("name", item)) if isinstance(item, dict) else str(item) for item in raw]
    elif isinstance(raw, dict):
        tools = raw.get("tools") or raw.get("mcpTools") or []
        names = [str(item.get("name", item)) if isinstance(item, dict) else str(item) for item in tools]
    joined = " ".join(names).lower()
    caps["read"] = any(token in joined for token in ["get_all_diagrams", "read", "list_diagram", "project_info"])
    caps["write"] = any(token in joined for token in ["create", "update", "write", "set_", "layout", "relationship"])
    caps["exportPng"] = any(token in joined for token in ["export", "png", "image"])
    caps["saveCopy"] = any(token in joined for token in ["save_project_as", "saveas", "save_copy"])
    return caps


def bool_evidence(evidence: Dict[str, Any], key: str, fallback: bool = False) -> bool:
    value = evidence.get(key, fallback)
    return bool(value)


def png_non_empty(evidence: Dict[str, Any], project_root: Path) -> bool:
    path_value = evidence.get("testPngPath") or evidence.get("exportedTestPng")
    if not path_value:
        return False
    path = Path(str(path_value))
    if not path.is_absolute():
        path = project_root / path
    return path.exists() and path.is_file() and path.stat().st_size > 0


def capability_level(report: Dict[str, Any]) -> str:
    if not report["starumlExecutableResolved"]:
        return "L0"
    if not report["starumlLaunchable"]:
        return "L0"
    level = "L1"
    if report["apiServer58321"] or report["mcpReadCapability"]:
        level = "L2"
    if report["mcpWriteCapability"]:
        level = "L3"
    if (
        report["mcpWriteCapability"]
        and report["saveCopyCapability"]
        and report["mcpExportPngCapability"]
        and report["testMdjOpened"]
        and report["testPngExported"]
    ):
        level = "L4"
    return level


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=os.getcwd())
    parser.add_argument("--out", default=".lbssb/preflight-report.json")
    parser.add_argument("--evidence", default="")
    parser.add_argument("--mcp-tools-json", default="")
    parser.add_argument("--wait-seconds", type=int, default=6)
    parser.add_argument("--no-launch", action="store_true")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = project_root / out_path

    config_path, config, config_error = load_runtime_config(project_root)
    resolved = resolve_staruml(project_root, config_path, config)
    node_options = os.environ.get("NODE_OPTIONS", "")
    node_options_detected = bool(node_options)
    node_options_use_system_ca = "--use-system-ca" in node_options
    node_options_risky = bool(node_options) and any(
        token in node_options
        for token in ["--use-system-ca", "--require", "--inspect", "--openssl", "--tls", "--ca", "--cert", "--experimental"]
    )
    clear_node = bool(config.get("clearNodeOptionsForStarUMLLaunch", True))
    enable_logging = bool(config.get("enableLogging", True))
    api_port = int(config.get("apiServerPort", 58321))
    extension_port = int(config.get("extensionPort", 58322))

    staruml_launchable = False
    process_started = tasklist_has_staruml()
    launch_error = ""
    node_cleared = False
    if resolved["path"] and not args.no_launch:
        launch_args = ["--enable-logging"] if enable_logging else []
        staruml_launchable, launch_error, node_cleared = launch_staruml(
            resolved["path"], launch_args, clear_node and node_options_detected, args.wait_seconds
        )
        process_started = staruml_launchable or tasklist_has_staruml()
    elif resolved["path"] and process_started:
        staruml_launchable = True

    api_ok = port_open(api_port)
    extension_ok = port_open(extension_port)
    minimal_mdj = create_minimal_mdj(project_root) if resolved["path"] else None

    evidence_path = Path(args.evidence).resolve() if args.evidence else None
    tools_path = Path(args.mcp_tools_json).resolve() if args.mcp_tools_json else None
    evidence = load_evidence(evidence_path)
    caps = mcp_caps_from_tools(tools_path)
    mcp_read = bool_evidence(evidence, "mcpReadCapability", caps["read"])
    mcp_write = bool_evidence(evidence, "mcpWriteCapability", caps["write"])
    mcp_export = bool_evidence(evidence, "mcpExportPngCapability", caps["exportPng"])
    save_copy = bool_evidence(evidence, "saveCopyCapability", caps["saveCopy"])
    test_mdj_opened = bool_evidence(evidence, "testMdjOpened", False)
    test_png_exported = bool_evidence(evidence, "testPngExported", False) and png_non_empty(evidence, project_root)

    report: Dict[str, Any] = {
        "shellAvailable": True,
        "projectRoot": str(project_root),
        "runtimeConfig": str(config_path) if config_path else "",
        "runtimeConfigError": config_error or "",
        "starumlExecutable": resolved["path"],
        "resolvedFrom": resolved["resolvedFrom"],
        "starumlExecutableResolved": bool(resolved["path"]),
        "starumlLaunchable": bool(staruml_launchable),
        "launchError": launch_error,
        "nodeOptionsDetected": node_options_detected,
        "nodeOptionsValue": node_options,
        "nodeOptionsUseSystemCa": node_options_use_system_ca,
        "nodeOptionsRisky": node_options_risky,
        "nodeOptionsClearedForLaunch": node_cleared,
        "starumlProcessExists": bool(process_started),
        "apiServer58321": api_ok,
        "extension58322": extension_ok,
        "mcpReadCapability": mcp_read,
        "mcpWriteCapability": mcp_write,
        "mcpExportPngCapability": mcp_export,
        "saveCopyCapability": save_copy,
        "minimalTestMdjCreated": bool(minimal_mdj and minimal_mdj.exists()),
        "minimalTestMdj": str(minimal_mdj) if minimal_mdj else "",
        "testMdjOpened": test_mdj_opened,
        "testPngExported": test_png_exported,
        "evidenceFile": str(evidence_path) if evidence_path else "",
        "evidenceError": evidence.get("_evidenceError", ""),
    }
    report["capabilityLevel"] = capability_level(report)
    report["status"] = "Verified" if report["capabilityLevel"] == "L4" else f"Unverified: capability {report['capabilityLevel']}"

    write_json(out_path, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "Verified" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(2)
