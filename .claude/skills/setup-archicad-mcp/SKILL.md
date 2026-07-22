---
name: setup-archicad-mcp
description: "Installs, enables, verifies, or removes the optional Archicad MCP runtime without changing the Revit MCP implementation. Use for Archicad MCP installation, Tapir setup, environment checks, MCP client configuration, opt-in enablement, rollback, Archicad 安裝、環境設置、啟用、停用、移除、連線測試。"
---

# Setup Archicad MCP

Configure the optional Archicad backend as a separate MCP server. Keep the repository Revit-only until the user explicitly runs the setup.

## Safety Contract

- Never modify `MCP/`, `MCP-Server/src/`, `scripts/setup.ps1`, or `scripts/install-addon.ps1` for this workflow.
- Never replace, rename, or edit the `revit-mcp` JSON object.
- Pin the runtime to `tapir-archicad-mcp==0.4.3`; do not silently use `latest`.
- Do not install Archicad or the version-specific Tapir Add-On automatically.
- Treat configuration as proof of setup only, not proof of a live Archicad connection.
- Use `--disable-project` for rollback; it removes only `archicad-mcp`.

Read [references/runtime-contract.md](references/runtime-contract.md) before changing the pinned version or setup behavior.

## Workflow

### 1. Pre-flight

1. Confirm the repository root contains `.mcp.json`, `.vscode/mcp.json`, and `scripts/setup-archicad-mcp.py`.
2. Detect the operating system.
3. Confirm `uv` and `uvx` are available. If missing, stop and direct the user to the official uv installer.
4. Confirm Archicad is installed separately. For the full community command set, require a Tapir Add-On compatible with the user's Archicad version.

### 2. Check without changing files

Run the platform wrapper with `--check-only`:

```bash
./scripts/setup-archicad-mcp.sh --check-only
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup-archicad-mcp.ps1 -CheckOnly
```

Stop if the default Revit entry is missing or an existing Archicad entry is unpinned.

### 3. Enable project configuration

After the user requests installation or enablement, run:

```bash
./scripts/setup-archicad-mcp.sh
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup-archicad-mcp.ps1
```

The setup resolves the pinned Python package first, then adds `archicad-mcp` beside `revit-mcp` in the two project configs. It must leave the serialized Revit object unchanged.

For Claude Desktop or Gemini user-level configuration, add:

```text
--configure-user --client all
```

PowerShell equivalents are `-ConfigureUser -Client all`.

### 4. Verify configuration integrity

1. Re-run `--check-only`.
2. Inspect `git diff -- .mcp.json .vscode/mcp.json`.
3. Confirm the only semantic change is the `archicad-mcp` object.
4. Confirm Revit port `8964`, Node command, arguments, and environment remain unchanged.

### 5. Verify the live runtime

1. Install and enable the compatible Tapir Add-On manually.
2. Open Archicad and a test project.
3. Restart the MCP client.
4. Call `discovery_list_active_archicads`.
5. If one instance is returned, retain its `port` for the current workflow. If multiple instances are returned, ask the user to select one.
6. Use `archicad_discover_tools` before the first internal command, then dispatch with `archicad_call_tool`.

Do not claim success when the instance list is empty.

## Rollback

Remove only project-level Archicad entries:

```bash
./scripts/setup-archicad-mcp.sh --disable-project
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup-archicad-mcp.ps1 -DisableProject
```

Also remove selected user-level entries with `--remove-user --client ...` or `-RemoveUser -Client ...`.

## Error Handling

| Symptom | Response |
|---|---|
| `uv` or `uvx` missing | Stop; install uv from the official documentation, reopen the terminal, and retry. |
| Pinned package cannot resolve | Leave configs unchanged; check Python/network/proxy access. |
| Existing JSON is invalid | Refuse to overwrite it; report the exact file. |
| Archicad instance list is empty | Open a project, verify Tapir compatibility, and restart the MCP client. |
| Only three public Archicad tools appear | Expected; use discovery and dispatch for internal commands. |
| Revit no longer starts | Verify the `revit-mcp` object against Git and disable only the Archicad entry. |

## 工具 / Tools

| Tool | Purpose |
|---|---|
| `discovery_list_active_archicads` | List live Archicad instances and ports. |
| `archicad_discover_tools` | Find current internal Archicad commands and schemas. |
| `archicad_call_tool` | Execute one discovered command against a selected port. |

## Reference

- [Runtime contract](references/runtime-contract.md)
- `domain/tool-capability-boundary.md`
- `docs/integrations/archicad-mcp.md`
