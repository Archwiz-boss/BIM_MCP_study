#!/usr/bin/env python3
"""Opt in to the pinned Archicad MCP runtime without changing Revit MCP."""

from __future__ import annotations

import argparse
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any


PACKAGE_NAME = "tapir-archicad-mcp"
PACKAGE_VERSION = "0.4.3"
SERVER_COMMAND = "archicad-server"
SERVER_NAME = "archicad-mcp"
REVIT_SERVER_NAME = "revit-mcp"
PINNED_PACKAGE = f"{PACKAGE_NAME}=={PACKAGE_VERSION}"
SERVER_ARGS = ["--from", PINNED_PACKAGE, SERVER_COMMAND]
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def info(message: str) -> None:
    print(f"[INFO] {message}")


def ok(message: str) -> None:
    print(f"[ OK ] {message}")


def fail(message: str) -> None:
    print(f"[FAIL] {message}", file=sys.stderr)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as stream:
        data = json.load(stream)
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")
    return data


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def archicad_entry() -> dict[str, Any]:
    return {
        "type": "stdio",
        "command": "uvx",
        "args": SERVER_ARGS,
        "env": {},
    }


def validate_project_config(path: Path, root_key: str) -> bool:
    if not path.exists():
        fail(f"Missing project MCP config: {path}")
        return False

    try:
        data = load_json(path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        fail(f"Invalid JSON in {path}: {exc}")
        return False

    servers = data.get(root_key)
    if not isinstance(servers, dict):
        fail(f"{path} does not contain an object named '{root_key}'")
        return False
    if not isinstance(servers.get(REVIT_SERVER_NAME), dict):
        fail(f"{path} must retain the existing '{REVIT_SERVER_NAME}' object")
        return False

    existing = servers.get(SERVER_NAME)
    if existing is not None and existing != archicad_entry():
        fail(f"{path} contains an unexpected or unpinned '{SERVER_NAME}' entry")
        return False

    state = "enabled" if existing is not None else "disabled (default)"
    ok(f"Project config valid: {display_path(path)}; Archicad is {state}")
    return True


def write_json_atomically(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def set_project_entry(path: Path, root_key: str, enable: bool) -> bool:
    try:
        data = load_json(path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        fail(f"Refusing to modify invalid JSON in {path}: {exc}")
        return False

    servers = data.get(root_key)
    if not isinstance(servers, dict):
        fail(f"Refusing to replace non-object '{root_key}' in {path}")
        return False

    revit_before = copy.deepcopy(servers.get(REVIT_SERVER_NAME))
    if not isinstance(revit_before, dict):
        fail(f"Refusing to modify {path}: '{REVIT_SERVER_NAME}' is missing")
        return False

    changed = False
    if enable:
        expected = archicad_entry()
        if servers.get(SERVER_NAME) != expected:
            servers[SERVER_NAME] = expected
            changed = True
    elif SERVER_NAME in servers:
        del servers[SERVER_NAME]
        changed = True

    if servers.get(REVIT_SERVER_NAME) != revit_before:
        fail(f"Safety invariant failed: '{REVIT_SERVER_NAME}' changed in memory")
        return False

    if changed:
        try:
            write_json_atomically(path, data)
        except OSError as exc:
            fail(f"Could not write {path}: {exc}")
            return False

    action = "enabled" if enable else "disabled"
    suffix = "" if changed else " (already in requested state)"
    ok(f"Archicad {action}: {display_path(path)}{suffix}")
    return True


def require_uv() -> bool:
    uv_path = shutil.which("uv")
    uvx_path = shutil.which("uvx")
    if not uv_path or not uvx_path:
        fail("uv and uvx must be installed and available on PATH")
        info("Install uv from https://docs.astral.sh/uv/getting-started/installation/")
        return False
    ok(f"uv: {uv_path}")
    ok(f"uvx: {uvx_path}")
    return True


def resolve_runtime() -> bool:
    verification_code = (
        "import importlib.metadata as m; "
        f"d=m.distribution('{PACKAGE_NAME}'); "
        f"assert d.version=='{PACKAGE_VERSION}', d.version; "
        "entries=[e.value for e in d.entry_points "
        f"if e.group=='console_scripts' and e.name=='{SERVER_COMMAND}']; "
        "assert entries==['tapir_archicad_mcp.server:main'], entries; "
        "print(d.metadata['Name'], d.version, entries[0])"
    )
    command = [
        "uv",
        "run",
        "--isolated",
        "--python",
        "3.12",
        "--with",
        PINNED_PACKAGE,
        "python",
        "-c",
        verification_code,
    ]
    info(f"Resolving and validating {PINNED_PACKAGE}...")
    try:
        result = subprocess.run(
            command, check=False, capture_output=True, text=True, timeout=600
        )
    except subprocess.TimeoutExpired:
        fail("Runtime verification timed out after 10 minutes")
        return False
    except OSError as exc:
        fail(f"Could not start uv: {exc}")
        return False

    combined = f"{result.stdout}\n{result.stderr}"
    if result.returncode != 0:
        fail(f"uv returned exit code {result.returncode}; project configs were not changed")
        tail = "\n".join(combined.strip().splitlines()[-12:])
        if tail:
            print(tail, file=sys.stderr)
        return False
    if "tapir_archicad_mcp.server:main" not in combined:
        fail("Resolved package lacks the expected archicad-server entry point")
        return False

    ok(f"Pinned runtime is available: {PINNED_PACKAGE}")
    return True


def user_config_paths() -> dict[str, Path | None]:
    home = Path.home()
    if sys.platform == "darwin":
        claude = home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    elif os.name == "nt":
        appdata = os.environ.get("APPDATA")
        claude = Path(appdata) / "Claude" / "claude_desktop_config.json" if appdata else None
    else:
        claude = home / ".config" / "Claude" / "claude_desktop_config.json"
    return {
        "claude-desktop": claude,
        "gemini": home / ".gemini" / "settings.json",
    }


def set_user_entry(client: str, path: Path | None, enable: bool) -> bool:
    if path is None:
        fail(f"Could not determine the {client} config path")
        return False
    if not path.exists() and not enable:
        ok(f"{client}: no config to update")
        return True

    data: dict[str, Any] = {}
    if path.exists():
        try:
            data = load_json(path)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            fail(f"Refusing to overwrite invalid JSON in {path}: {exc}")
            return False

    servers = data.setdefault("mcpServers", {})
    if not isinstance(servers, dict):
        fail(f"Refusing to replace non-object 'mcpServers' in {path}")
        return False

    changed = False
    if enable:
        expected = archicad_entry()
        if servers.get(SERVER_NAME) != expected:
            servers[SERVER_NAME] = expected
            changed = True
    elif SERVER_NAME in servers:
        del servers[SERVER_NAME]
        changed = True

    if not changed:
        ok(f"{client}: already in requested state")
        return True

    if path.exists():
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        backup = path.with_name(f"{path.name}.bak-{timestamp}")
        shutil.copy2(path, backup)
        info(f"Backed up {client} config to {backup}")

    try:
        write_json_atomically(path, data)
    except OSError as exc:
        fail(f"Could not write {path}: {exc}")
        return False

    action = "configured" if enable else "removed Archicad from"
    ok(f"{client}: {action} {path}")
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Opt in to the pinned Archicad MCP runtime used with BIM_MCP."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--check-only",
        action="store_true",
        help="Validate commands and configs without downloads or writes.",
    )
    mode.add_argument(
        "--disable-project",
        action="store_true",
        help="Remove only archicad-mcp from project configs.",
    )
    parser.add_argument(
        "--skip-resolve",
        action="store_true",
        help="Enable configs without resolving the pinned package first.",
    )
    user_mode = parser.add_mutually_exclusive_group()
    user_mode.add_argument(
        "--configure-user",
        action="store_true",
        help="Add archicad-mcp to selected user-level MCP configs.",
    )
    user_mode.add_argument(
        "--remove-user",
        action="store_true",
        help="Remove archicad-mcp from selected user-level MCP configs; use with --disable-project.",
    )
    parser.add_argument(
        "--client",
        choices=("all", "claude-desktop", "gemini"),
        default="all",
        help="User-level client for --configure-user/--remove-user.",
    )
    args = parser.parse_args()
    if args.check_only and (args.configure_user or args.remove_user):
        parser.error("--check-only cannot modify user configs")
    if args.disable_project and args.configure_user:
        parser.error("--disable-project cannot be combined with --configure-user")
    if args.remove_user and not args.disable_project:
        parser.error("--remove-user requires --disable-project")
    return args


def main() -> int:
    args = parse_args()
    print(f"BIM_MCP optional Archicad setup ({PINNED_PACKAGE})")

    configs = (
        (PROJECT_ROOT / ".mcp.json", "mcpServers"),
        (PROJECT_ROOT / ".vscode" / "mcp.json", "servers"),
    )
    if not all(validate_project_config(path, root_key) for path, root_key in configs):
        return 3

    if args.check_only:
        if not require_uv():
            return 2
        ok("Check completed without modifying files")
        return 0

    if not args.disable_project:
        if not require_uv():
            return 2
        if not args.skip_resolve and not resolve_runtime():
            return 4

    enable_project = not args.disable_project
    if not all(set_project_entry(path, root_key, enable_project) for path, root_key in configs):
        return 5

    paths = user_config_paths()
    selected = paths.keys() if args.client == "all" else (args.client,)
    if args.configure_user:
        if not all(set_user_entry(client, paths[client], True) for client in selected):
            return 6
    if args.remove_user:
        if not all(set_user_entry(client, paths[client], False) for client in selected):
            return 7

    print()
    if enable_project:
        ok("Archicad MCP is enabled as a separate project server")
        info("Install/enable the matching Tapir Add-On, open Archicad, and restart the MCP client")
    else:
        ok("Archicad MCP is disabled; Revit MCP was preserved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
