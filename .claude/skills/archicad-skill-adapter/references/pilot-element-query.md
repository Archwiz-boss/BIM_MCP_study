# Archicad Pilot: Element Query

## Scope

Apply the originating `element-query` intent to the selected Archicad project while preserving the Domain sequence: explore, align, then extract. This pilot supports element and property reads. Highlighting is optional and must be discovered separately.

## Backend Route

- Revit selected: return to `.claude/skills/element-query/SKILL.md` and use its existing Revit workflow.
- Archicad selected: continue below and keep all GUIDs isolated from Revit ElementIds.
- Target ambiguous: ask which application and project to use.

## Archicad Workflow

1. Anchor the live project with `discovery_list_active_archicads`; retain the selected project and port.
2. Explore by discovering a command that lists the requested Archicad element type. Dispatch only the returned schema and follow pagination until complete.
3. Align by discovering element-detail and property-definition/value commands. Determine whether the user's term maps to element type, classification, property, attribute, or Library Part parameter.
4. Extract by discovering either a server-side filter or a property-value read. Preserve each result's GUID and the exact property identifier used.
5. If highlighting was requested, discover a highlight command, apply it only to current-chain GUIDs, and verify that a compatible clear operation exists.
6. Report the selected project/port, discovered commands, returned count, property source, pagination state, and any approximate mappings.

## Observed Capability Hints

The pinned runtime has exposed commands resembling the following during implementation. These names are search hints only; run discovery and use the returned schema every time.

| Intent | Observed command hint |
|---|---|
| List by element type | `elements_get_elements_by_type` |
| Filter elements | `elements_filter_elements` |
| Read element details | `elements_get_details_of_elements` |
| Read property values | `properties_get_property_values_of_elements` |
| Highlight results | `elements_highlight_elements` |

## Stop Conditions

- The target type or property has more than one plausible Archicad mapping.
- A filter would require guessing localized property names or enum values.
- Pagination cannot be completed or the selected port changes.
- Visualization is requested but no clear/revert path is discoverable.

## Live-Test Evidence

Record these fields so capability use can be distinguished from Skill use:

```text
backend: archicad
canonical_skill: element-query
domain_method: domain/element-query-workflow.md
adapter_reference: pilot-element-query.md
project_port: <current port>
discovered_commands: <names returned by discovery>
result_guids: <count, not fabricated values>
verification: read-only result or highlight cleared
```

### Recorded run 2026-08-18

```text
backend: archicad
canonical_skill: element-query
agy_codex_mirror: .agents/skills/element-query/SKILL.md
domain_method: domain/element-query-workflow.md
adapter_reference: pilot-element-query.md
runtime: tapir-archicad-mcp==0.4.3 (uvx), Archicad 28, Tapir Add-On 1.5.8
project_port: 19723
project: AC28 空白樣板20260709 (solo)
discovered_commands:
  explore: elements_get_elements_by_type, elements_get_all_elements
  align:   elements_get_details_of_elements, properties_get_all_property_names,
           properties_get_property_ids
  extract: properties_get_property_values_of_elements
  visualize (discovered, NOT dispatched): elements_highlight_elements
result_guids: 304 Wall GUIDs, scope elementType=Wall + filters=["OnActualFloor"],
              pagination exhausted (offsets 0/100/200 = 100 each, offset 300 = 4,
              final page returned no next_page_token)
              Unscoped project-wide Wall enumeration reached 1600 GUIDs over 16 pages
              and then failed; see the Stop Conditions section above.
property_source: BuiltIn property definitions resolved by name via GetPropertyIds
  Wall_ReferenceLineLength -> 736276cc-0825-4738-a2e8-cdd740c7f635
  Wall_CenterLength        -> 6651c8de-502e-47f0-9a96-671a3c5255f2
extract_sample: 4 Wall GUIDs from the final explore page, values returned
  5cc16bbe-1d8a-4eb6-b5ab-0ed0f4b53770 -> 0.85 / 0.78
  ea3dc95e-2569-42a6-a99f-876288a4ff6a -> 4.70 / 4.63
  1d415f56-5909-44dc-93b6-603cce626832 -> 1.95 / 1.95
  6fd1a710-0de7-4321-9f4d-e741724af798 -> 17.50 / 17.50
identifiers: Archicad GUID only; no Revit ElementId entered or left this chain
verification: read-only; no write command dispatched; no highlight applied,
              so no highlight had to be cleared
unsupported_steps: none required for this read path
```

### Runtime findings from this run

1. `archicad_discover_tools` in this pinned runtime behaves as a case-insensitive
   **literal substring match over command description text**, not the semantic search its
   own tool description advertises. Long application-neutral sentences return `[]`, including
   the tool's own documented example `get the currently selected elements`. The query
   `all elements` matches `CreateWalls`/`ModifyWalls` only because their description contains
   `Wall elements`, i.e. the substring `all elements`. Single broad words appear to cap at
   10 results ordered by command name.
   Practical consequence: step 4.1's "describe the application-neutral operation" produces
   false negatives here. Query short noun phrases that are likely to appear verbatim in a
   command description (`given type`, `property names`, `all elements`, `details of`), and
   never read an empty result as proof that a capability is absent.

2. Pagination sessions expire. An unscoped `elements_get_elements_by_type` walk over
   `Wall` in this project succeeded for 16 consecutive pages (1600 GUIDs) and then returned
   `Pagination session expired. Please start a new request.` This triggers the
   "Pagination cannot be completed" Stop Condition above, so step 2's "follow pagination
   until complete" is not achievable for large element types. Bound the scope first with a
   discovered server-side filter (here `filters: ["OnActualFloor"]`), then exhaust pagination
   within that scope.

3. `GetPropertyValuesOfElements` returns `propertyValuesForElements` positionally and does
   **not** echo the element GUID or the property GUID. The caller must preserve the request
   ordering to keep the GUID-to-value evidence chain intact.

4. The `ElementFilter` enum (`IsEditable`, `OnActualFloor`, `IsVisibleByLayer`, ...) filters by
   visibility/editability state, not by element type. Element type selection comes only from
   the separate `elementType` enum.

5. `elements_highlight_elements` carries its own clear path: passing an empty `elements`
   array removes all previously set highlights. The clear operation required by step 5 was
   confirmed from the schema without dispatching any highlight.

## Reference

- [Terminology and boundary map](revit-archicad-terminology.md)
- `domain/element-query-workflow.md`
- `domain/tool-capability-boundary.md`
