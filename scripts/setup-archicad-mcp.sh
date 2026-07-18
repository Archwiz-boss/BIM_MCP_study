#!/usr/bin/env bash
# Prepare the optional Archicad MCP runtime on macOS/Linux.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CORE_SCRIPT="$SCRIPT_DIR/setup-archicad-mcp.py"

if ! command -v uv >/dev/null 2>&1; then
    echo "[FAIL] uv is required." >&2
    echo "       Install it from https://docs.astral.sh/uv/getting-started/installation/" >&2
    exit 2
fi

exec uv run --no-project --python 3.12 "$CORE_SCRIPT" "$@"
