# Archicad MCP Runtime Contract

## Fixed runtime

```text
package: tapir-archicad-mcp==0.4.3
entry point: archicad-server
launcher: uvx
python: >=3.12
upstream: https://github.com/SzamosiMate/tapir-archicad-MCP
distribution: https://pypi.org/project/tapir-archicad-mcp/
license declared by distribution: MIT
```

Expected MCP entry:

```json
{
  "type": "stdio",
  "command": "uvx",
  "args": [
    "--from",
    "tapir-archicad-mcp==0.4.3",
    "archicad-server"
  ],
  "env": {}
}
```

## Non-impact invariants

1. The committed `.mcp.json` and `.vscode/mcp.json` remain Revit-only.
2. Setup changes only the `archicad-mcp` key after the user opts in.
3. Disablement removes only the `archicad-mcp` key.
4. Revit source, build, deployment scripts, port, and identifiers remain untouched.
5. The third-party package is resolved at runtime and is not vendored.
6. Revit `ElementId` and Archicad GUID values are never interchangeable.

## Version update checklist

Update the version in all of these locations together:

- `scripts/setup-archicad-mcp.py`
- `.claude/skills/setup-archicad-mcp/references/runtime-contract.md`
- `docs/integrations/archicad-mcp.md`
- `THIRD_PARTY_NOTICES.md`

Then verify package metadata, the `archicad-server` console entry point, both JSON merge paths, rollback, and a real Archicad/Tapir smoke test before release.
