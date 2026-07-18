#!/usr/bin/env python3
"""Prepare the pinned Archicad MCP runtime and optionally configure user clients."""

from __future__ import annotations

import argparse
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
PINNED_PACKAGE = f"{PACKAGE_NAME}=={PACKAGE_VERSION}"
SERVER_ARGS = ["--from", PINNED_PACKAGE, SERVER_COMMAND]
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def info(message: str) -> None:
    print(f"[INFO] {message}")


def ok(message: str) -> None:
    print(f"[ OK ] {message}")


def warn(message: str) -> None:
    print(f"[WARN] {message}")


def fail(message: str) -> None:
    print(f"[FAIL] {message}", file=sys.stderr)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as stream:
        data = json.load(stream)
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")
    return data


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

    entry = servers.get(SERVER_NAME)
    if not isinstance(entry, dict):
        fail(f"{path} does not define '{SERVER_NAME}'")
        return False

    if entry.get("command") != "uvx" or entry.get("args") != SERVER_ARGS:
        fail(f"{path} does not use the expected pinned runtime: {PINNED_PACKAGE}")
        return False

    ok(f"Project config validated: {path.relative_to(PROJECT_ROOT)}")
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
        "--no-project",
        "--python",
        "3.12",
        "--with",
        PINNED_PACKAGE,
        "python",
        "-c",
        verification_code,
    ]
    info(f"Resolving and validating {PINNED_PACKAGE} (first run may take several minutes)...")
    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=600,
        )
    except subprocess.TimeoutExpired:
        fail("Runtime verification timed out after 10 minutes")
        return False
    except OSError as exc:
        fail(f"Could not start uv: {exc}")
        return False

    combined_output = f"{result.stdout}\n{result.stderr}"
    if result.returncode != 0:
        fail(f"uv returned exit code {result.returncode}")
        tail = "\n".join(combined_output.strip().splitlines()[-12:])
        if tail:
            print(tail, file=sys.stderr)
        return False

    if "tapir_archicad_mcp.server:main" not in combined_output:
        fail("Resolved package does not expose the expected archicad-server entry point")
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


def write_json_atomically(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def configure_user_client(client: str, path: Path | None) -> bool:
    if path is None:
        fail(f"Could not determine the {client} config path")
        return False

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

    expected_entry = {"command": "uvx", "args": SERVER_ARGS}
    if servers.get(SERVER_NAME) == expected_entry:
        ok(f"{client} already uses {PINNED_PACKAGE}")
        return True

    if path.exists():
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = path.with_name(f"{path.name}.bak-{timestamp}")
        shutil.copy2(path, backup_path)
        info(f"Backed up {client} config to {backup_path}")

    servers[SERVER_NAME] = expected_entry
    try:
        write_json_atomically(path, data)
    except OSError as exc:
        fail(f"Could not write {path}: {exc}")
        return False

    ok(f"Configured {client}: {path}")
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare the pinned Archicad MCP runtime used by BIM_MCP.",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Validate local commands and committed configs without resolving the Archicad MCP package.",
    )
    parser.add_argument(
        "--skip-resolve",
        action="store_true",
        help="Skip the uvx package resolution/import check.",
    )
    parser.add_argument(
        "--configure-user",
        action="store_true",
        help="Add archicad-mcp to selected user-level MCP client configs.",
    )
    parser.add_argument(
        "--client",
        choices=("all", "claude-desktop", "gemini"),
        default="all",
        help="User-level client to configure with --configure-user. Defaults to all.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    print(f"BIM_MCP Archicad MCP setup ({PINNED_PACKAGE})")

    uv_path = shutil.which("uv")
    uvx_path = shutil.which("uvx")
    if not uv_path or not uvx_path:
        fail("uv and uvx must be installed and available on PATH")
        info("Install uv from https://docs.astral.sh/uv/getting-started/installation/")
        return 2
    ok(f"uv: {uv_path}")
    ok(f"uvx: {uvx_path}")

    config_ok = all(
        (
            validate_project_config(PROJECT_ROOT / ".mcp.json", "mcpServers"),
            validate_project_config(PROJECT_ROOT / ".vscode" / "mcp.json", "servers"),
        )
    )
    if not config_ok:
        return 3

    if not args.check_only and not args.skip_resolve and not resolve_runtime():
        return 4

    if args.configure_user:
        paths = user_config_paths()
        selected_clients = paths.keys() if args.client == "all" else (args.client,)
        if not all(configure_user_client(client, paths[client]) for client in selected_clients):
            return 5

    print()
    ok("Archicad MCP environment setup completed")
    info("Next: install/enable the Tapir Add-On, open Archicad, then restart your MCP client")
    info("The first real MCP start may download the semantic-search model and build ~/.tapir_mcp")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
