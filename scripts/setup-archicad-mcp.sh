#!/usr/bin/env bash
# Configure the optional Archicad MCP runtime on macOS/Linux.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CORE_SCRIPT="$SCRIPT_DIR/setup-archicad-mcp.py"

if command -v uv >/dev/null 2>&1; then
    exec uv run --isolated --python 3.12 "$CORE_SCRIPT" "$@"
fi

# Rollback must remain possible even if uv was removed after setup.
for arg in "$@"; do
    if [[ "$arg" == "--disable-project" ]]; then
        if command -v python3 >/dev/null 2>&1; then
            exec python3 "$CORE_SCRIPT" "$@"
        fi
        if command -v python >/dev/null 2>&1; then
            exec python "$CORE_SCRIPT" "$@"
        fi
    fi
done

echo "[FAIL] uv is required for setup and verification." >&2
echo "       Install it from https://docs.astral.sh/uv/getting-started/installation/" >&2
echo "       Rollback without uv also requires python3 or python." >&2
exit 2
