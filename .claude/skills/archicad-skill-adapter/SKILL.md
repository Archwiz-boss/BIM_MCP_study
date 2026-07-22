---
name: archicad-skill-adapter
description: "Translates Revit-oriented BIM Skill intent and terminology into a guarded Archicad MCP discovery-and-dispatch workflow while preserving the original Domain method. Use when applying BIM_MCP Skills to Archicad, selecting an Archicad backend, mapping Revit terms, or handling Revit→Archicad 轉譯、名詞對照、GUID、Story、Zone、Layout、Tapir。"
---

# Archicad Skill Adapter

Use existing BIM_MCP Domain knowledge and workflow intent with an Archicad backend. Translate orchestration only; never pretend that similarly named Revit and Archicad objects are API-equivalent.

## Hard Boundaries

- Use one backend for each operation chain. Do not send Archicad identifiers to Revit tools or Revit identifiers to Archicad tools.
- Preserve the selected Archicad instance `port` throughout the current chain.
- Discover the current Archicad command and schema before dispatch. Internal command names are not a stable Skill contract.
- Preserve the original Domain method, formulas, exclusions, and decision gates.
- Treat writes as unverified until a follow-up read confirms the result.
- Stop when no discovered command supports a required capability. Report the gap instead of inventing a payload.

Read [references/revit-archicad-terminology.md](references/revit-archicad-terminology.md) before translating object names, properties, views, documentation objects, units, or identifiers.

## Workflow

### 1. Select the backend

1. Honor an explicit Revit or Archicad request.
2. If the request is ambiguous and both backends are available, ask which application and project to target.
3. If Archicad is selected, do not call Revit MCP merely because the originating Skill contains Revit tool names.

### 2. Preserve the BIM method

1. Read the Domain referenced by the originating Skill.
2. Extract application-neutral intent: required inputs, filters, calculations, decision points, mutations, and verification.
3. Mark every Revit-specific operation as `direct`, `approximate`, `discover`, or `unsupported` using the terminology reference.
4. Keep unsupported steps visible in the final result.

### 3. Anchor the Archicad instance

1. Call `discovery_list_active_archicads`.
2. Stop if no instance is returned.
3. If multiple instances are returned, ask the user to select by project and port.
4. Retain the selected port. Never guess or reuse a port from an earlier turn.

### 4. Discover the capability

1. Describe the application-neutral operation in the discovery query, for example `list wall elements with properties` rather than a Revit MCP tool name.
2. Call `archicad_discover_tools`.
3. Inspect the returned command name, description, and input schema.
4. Prefer official JSON API commands when they fully cover the operation; use Tapir commands when the required capability is Add-On-specific.
5. If results are ambiguous, refine discovery once. Do not loop through guessed command names.

### 5. Translate and dispatch

1. Build arguments from the discovered schema, not from memory.
2. Use Archicad-native enum values exactly as the schema defines them; do not translate enum strings into Chinese.
3. Include the selected `port` and use GUIDs returned by the current Archicad chain.
4. Do not assume Revit internal feet, parameter names, category names, coordinates, or view semantics apply.
5. Call `archicad_call_tool`.

### 6. Verify and report

1. For writes, discover or reuse a compatible read command and re-read the affected GUIDs.
2. Report verified outcomes separately from approximate mappings and unsupported steps.
3. Cite the original Domain method used.
4. State that the result came from Archicad, including the selected project/port, without exposing unrelated instances.

## Translation Example

For an existing element-query workflow and the user request `查出 Archicad 目前專案所有牆`:

1. Keep the Domain's discover → align → extract method.
2. Map Revit `Category: Walls` to Archicad element type `Wall`, not to a Revit category ID.
3. Discover `list/get elements by type` against the current Archicad runtime.
4. Dispatch the returned command schema with the selected port.
5. Preserve returned GUIDs for follow-up property reads; never relabel them as ElementIds.

## 工具 / Tools

| Tool | Purpose |
|---|---|
| `discovery_list_active_archicads` | Anchor a live project and port. |
| `archicad_discover_tools` | Resolve an application-neutral operation to a current command and schema. |
| `archicad_call_tool` | Dispatch the discovered command. |

## Reference

- [Revit to Archicad terminology](references/revit-archicad-terminology.md)
- `domain/tool-capability-boundary.md`
- `domain/skill-authoring-standard.md`
