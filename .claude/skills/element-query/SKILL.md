---
name: element-query
description: "Queries and optionally visualizes BIM elements with a three-phase explore→align→extract protocol across Revit and the opt-in Archicad backend. Use when the user asks for 查詢、篩選、參數查詢、元素屬性、上色、element query、find elements、filter、property query、color-code, including Archicad element or Zone queries."
---

# BIM 元素查詢與視覺化

## Backend Routing

1. Honor an explicit Revit or Archicad target.
2. If both backends are connected and the target is ambiguous, ask which application and project to use.
3. For Revit, continue with the existing Revit protocol below without changing its tools, identifiers, or view semantics.
4. For Archicad, read `../archicad-skill-adapter/SKILL.md` and `../archicad-skill-adapter/references/pilot-element-query.md`, then preserve this Skill's explore→align→extract method with Archicad-native GUIDs and schemas.
5. Never use a result or identifier from one backend in the other.

## Lessons Reference
- **L-001**：查詢房間時必須多語言容錯（走廊/Corridor/廊道/通道/廊下）。詳見 `domain/lessons.md`。

## Revit 3-Phase Query Protocol (MANDATORY)

### Phase 1：探索
`get_active_schema` → 探索作用中視圖的所有類別與元素數量。
**必須先執行此步驟**以確認目標類別存在。

### Phase 2：對齊
`get_category_fields` → 取得類別的精確本地化參數名稱。
**嚴禁猜測參數名稱** — 名稱會因語言和專案樣版而異。

選用 Phase 2.5：`get_field_values` → 取得參數值分佈（有助於設定篩選條件）。

### Phase 3：擷取
`query_elements_with_filter` → 支援多重條件篩選查詢。
- `field` 必須使用 Phase 2 取得的名稱
- 運算子：`equals`、`contains`、`less_than`、`greater_than`、`not_equals`
- 單位通常為 mm

## Visualization

查詢後上色標記結果：
1. `override_element_graphics` → 設定填充色、線條色、透明度
2. `clear_element_override` → 恢復預設顯示

## Quick Reference

```
簡單查詢：      Phase 1 → Phase 3
篩選查詢：      Phase 1 → Phase 2 → Phase 3
值分佈探索：    Phase 1 → Phase 2 → Phase 2.5 → Phase 3
含上色標記：    Phase 1 → Phase 2 → Phase 3 → override_element_graphics
```

## 工具 / Tools

| 工具 | 用途 |
|------|------|
| `get_active_schema` | Revit Phase 1：探索作用中視圖的類別與數量。 |
| `get_category_fields` | Revit Phase 2：取得精確欄位名稱。 |
| `get_field_values` | Revit Phase 2.5：取得欄位值分佈。 |
| `query_elements_with_filter` | Revit Phase 3：依已驗證欄位擷取元素。 |
| `override_element_graphics` | 在 Revit 視圖中標示結果。 |
| `clear_element_override` | 清除 Revit 視圖標示。 |
| `get_wall_types` | 列出牆體類型（支援搜尋篩選） |
| `change_element_type` | 依 ID 變更元素類型（2023+ 限定） |
| `list_family_symbols` | 瀏覽族群符號（支援名稱篩選） |
| `get_line_styles` | 列出可用線條樣式 |
| `discovery_list_active_archicads` | Archicad route：錨定 live project 與 port。 |
| `archicad_discover_tools` | Archicad route：依意圖取得目前 command schema。 |
| `archicad_call_tool` | Archicad route：執行已 discovery 的 command。 |

## Common Scenarios

- **房間邊界檢查**：詳見 `domain/room-boundary.md`
- **牆體檢查**：詳見 `domain/wall-check.md`

## Reference

- Revit method: `domain/element-query-workflow.md`、`domain/element-coloring-workflow.md`、`domain/room-boundary.md`、`domain/wall-check.md`
- Archicad adapter: `../archicad-skill-adapter/SKILL.md`
- Archicad pilot: `../archicad-skill-adapter/references/pilot-element-query.md`
