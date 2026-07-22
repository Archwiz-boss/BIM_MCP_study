# Revit／Archicad Skill 可攜性矩陣

本文件用來區分「Archicad MCP 指令能執行」與「BIM_MCP 的 Skill／Domain 確實有參與」。狀態盤點以 2026-07-22 的 52 個 canonical Skills（`.claude/skills/*/SKILL.md`）為準。

上游討論入口：[`shuotao/REVIT_MCP_study#98`](https://github.com/shuotao/REVIT_MCP_study/issues/98)

## 狀態定義

| 狀態 | 意義 | 可以如何宣稱 |
|---|---|---|
| A：可直接共用 | Skill 處理的是知識、文件或 repository 工作，不依賴 Revit／Archicad 模型物件。 | 可共用編排；仍須遵守其原始輸入與驗證規則。 |
| B：需要 adapter | Domain 的目的、公式或決策流程可共用，但工具、識別碼、單位或 BIM 名詞必須依 backend 轉譯。 | 只有完成 discovery、資料對齊與驗證的步驟可稱為支援。 |
| C：backend-specific | 目前實作緊綁 Revit API／Revit 文件模型，或本身就是某一 backend 的安裝／開發工具。 | 保留原路徑；在有獨立 Archicad 設計與測試前，不自動轉譯。 |

狀態 B 不是「已完整支援」。目前只有三個 Skill 有正式 Archicad pilot 規格：`element-query`、`room-numbering`、`quantity-takeoff-excel`。

## A：可直接共用（3）

| Skill | 共用範圍 |
|---|---|
| `claude-md-sync` | Repository 文件與規則一致性檢查。 |
| `domain-diagram` | 將 Domain SOP 轉成流程圖的文件工作。 |
| `hj-pr-proposal` | Fork、知識內容與 PR 草案整理。 |

## B：需要 Archicad adapter（29）

| Skill | Archicad 可攜性判斷 | 階段 |
|---|---|---|
| `auto-dimension` | 尺寸意圖可共用；見證點與標註物件需重新對齊。 | candidate |
| `batch-material` | 批次材質意圖可共用；Material 必須拆成 Building Material／Surface 等概念。 | candidate |
| `batch-room-height` | 房間高度規則可轉為 Zone／Story 資料；可寫欄位需 discovery。 | candidate |
| `building-compliance` | 法規公式可共用；模型資料取得與視覺化需 adapter。 | candidate |
| `curtain-wall` | 設計意圖接近；panel／frame 階層與 schema 不同。 | candidate |
| `detect-clashes` | 碰撞判斷方法可共用；幾何與結果標記需 adapter。 | candidate |
| `element-coloring` | 參數分組與色碼可共用；Archicad Highlight／Graphic Override 邊界需驗證。 | candidate |
| `element-query` | 保留探索→對齊→擷取；Category／parameter 改由 element type／property discovery。 | **pilot** |
| `facade-generation` | 立面設計意圖可共用；幾何生成能力需逐步驗證。 | candidate |
| `family-inventory-cleanup` | 盤點／提案／確認流程可共用；Family 與 Library Part 無 1:1。 | candidate |
| `finish-schedule-governance` | 編碼治理方法可共用；Room／材料版改為 Zone／Property／Attribute 對齊。 | candidate |
| `fire-safety-check` | 法規與檢查順序可共用；元素、屬性及上色需 adapter。 | candidate |
| `ifc-structural-sync` | IFC 對齊與驗證概念可共用；原生梁柱建立 schema 不同。 | candidate |
| `parking-check` | 車位規則可共用；元素類型、Zone 與淨高資料需 adapter。 | candidate |
| `partition-takeoff` | 公式可共用；牆高與門窗宿主證據需 Archicad 關係資料。 | candidate |
| `qa-review` | 檢核框架可共用；每個 QA 項目的 model query 需 backend 路由。 | candidate |
| `quantity-takeoff-excel` | 稽核欄位、公式與 workbook 驗證可共用；RoomId 等欄位改為 Zone GUID 證據鏈。 | **pilot** |
| `room-numbering` | 排序、dry-run、衝突檢查與驗證可共用；Room／Level 改為 Zone／Story。 | **pilot** |
| `scaffold-takeoff` | 公式可共用；周長、高度與來源元素需 Archicad 證據。 | candidate |
| `sheet-management` | 文件管理意圖可轉為 Layout Book；Sheet／Viewport 不可直接改名。 | candidate |
| `smoke-detector-check` | 覆蓋半徑與檢核規則可共用；Object／Zone 關係需 adapter。 | candidate |
| `smoke-exhaust` | 法規與面積比方法可共用；模型資料與視覺化需 adapter。 | candidate |
| `tall-partition-index` | 高牆判斷可共用；牆頂、Story 與 Slab 關係需驗證。 | candidate |
| `text-note-batch` | 批次文字意圖可共用；TextNote 與 Archicad Text／Label 邊界需確認。 | candidate |
| `threshold-opening-takeoff` | 洞口算量方法可共用；門檻、宿主與 Zone 關係需 adapter。 | candidate |
| `viewport-arrangement` | 圖面配置意圖可轉為 Drawing on Layout；座標與更新規則不同。 | candidate |
| `wall-orientation-check` | 牆方向判斷可共用；法線、參考線與座標資料需 adapter。 | candidate |
| `wall-section-batch` | 批次剖面意圖可共用；剖面 viewpoint／drawing 建立需 discovery。 | candidate |
| `archicad-skill-adapter` | 本身就是狀態 B 的 routing／discovery 保護層。 | infrastructure |

## C：目前 backend-specific（20）

| Skill | 保留為 backend-specific 的原因 |
|---|---|
| `align-views-on-sheets` | 緊綁 Revit ScopeBox、TitleBlock、Viewport。 |
| `batch-apply-view-template` | Revit View Template 與 Archicad saved-view settings 無 1:1。 |
| `build-revit` | 建置 Revit add-in。 |
| `copy-detail-items` | 緊綁 Revit detail element 類型與 view ownership。 |
| `copy-sheets-cross-project` | 緊綁 Revit 文件開啟、Sheet／View 重建與跨文件複製。 |
| `core-reload-dev` | Revit loader／CoreRuntime 開發流程。 |
| `dedup-detail-elements` | 去重鍵與 Detail Group 保留規則為 Revit-specific。 |
| `dependent-view-crop` | 緊綁 Revit dependent view、Grid 與 CropBox。 |
| `deploy-addon` | 部署 Revit add-in。 |
| `detail-component-sync` | 緊綁 Revit DetailComponent、Family Symbol 與 Sheet metadata。 |
| `dll-to-mcp-tool` | 將 Revit IExternalCommand／DLL 包裝為 Revit MCP tool。 |
| `dwg-beam-import` | 目前輸出與建立流程鎖定 Revit structural framing。 |
| `dwg-column-import` | 目前輸出與建立流程鎖定 Revit structural columns。 |
| `excel-to-legend` | 緊綁 Revit Drafting View／Legend／Viewport 建立。 |
| `floor-plan-from-template` | 緊綁 Revit ViewFamilyType、View Template 與 CropBox。 |
| `scale-drafting-width` | 直接縮放 Revit DraftingView 的 DetailCurve／TextNote。 |
| `setup-archicad-mcp` | Archicad runtime 專用安裝／復原基礎設施，不是跨 backend 模型工作流。 |
| `stair-hidden-line` | 緊綁 Revit 視圖隱藏線與樓梯幾何。 |
| `unjoin-geometry` | 緊綁 Revit JoinGeometry 行為。 |
| `view-category-visibility` | Revit category visibility 與 Archicad Layer／MVO／Graphic Override 無 1:1。 |

## 三個 Pilot 的檔案入口

| Pilot | Canonical Skill | Archicad adapter 規格 | Agy／Codex mirror |
|---|---|---|---|
| 元素查詢 | `.claude/skills/element-query/SKILL.md` | `.claude/skills/archicad-skill-adapter/references/pilot-element-query.md` | `.agents/skills/element-query/SKILL.md` |
| Room／Zone 編號 | `.claude/skills/room-numbering/SKILL.md` | `.claude/skills/archicad-skill-adapter/references/pilot-room-numbering.md` | `.agents/skills/room-numbering/SKILL.md` |
| 算量 Excel | `.claude/skills/quantity-takeoff-excel/SKILL.md` | `.claude/skills/archicad-skill-adapter/references/pilot-quantity-takeoff-excel.md` | `.agents/skills/quantity-takeoff-excel/SKILL.md` |

## 如何證明有用到 Skill 與 Domain

只看到 `discovery_list_active_archicads`、`archicad_discover_tools`、`archicad_call_tool` 成功，僅能證明 Archicad MCP capability 可用。Live test 應要求 Agent 在操作前後回報下列 trace：

```text
backend: revit | archicad
canonical_skill: <skill name>
domain_method: <domain path>
adapter_reference: <pilot reference or none>
project_port: <Archicad only, current turn>
discovered_commands: <Archicad only>
identifiers: ElementId | GUID, never mixed
verification: <read-back / count / workbook reconciliation>
unsupported_steps: <explicit list>
```

建議測試 prompt：

```text
請使用 element-query 查詢目前 Archicad 專案的所有 Wall。
操作前先列出 backend、canonical Skill、Domain method 與 adapter reference；
完成後列出選定 port、discovery 得到的 command、GUID 數量、驗證方式與 unsupported steps。
不要呼叫 Revit MCP，也不要把 GUID 稱為 ElementId。
```

若 Agent 無法指出 `.agents/skills/<name>/SKILL.md` mirror、canonical Skill、Domain 與 pilot reference，只能記錄為「MCP capability live test」，不能記錄為「BIM_MCP Skill live test」。

## Revit 不受影響的驗收條件

- Committed `.mcp.json` 與 `.vscode/mcp.json` 仍只有預設 `revit-mcp`。
- Revit 目標直接走原 Skill；不載入 Archicad port、GUID 或 dynamic command schema。
- Archicad 只有在目標明確或使用者選定後才進 adapter。
- 不修改 Revit MCP source、port `8964`、C# dispatcher、TypeScript tool registry、build 或 deploy script。
- 新增 `.agents` mirror 不改變 52 個 canonical Skill 的 source-of-truth 計數。

## 下一批實作順序

Wave 2 的逐項工具對照、能力缺口、live-test cases 與審核勾選清單，見 [Archicad Skill 轉譯 Wave 2 實作前審核清單](archicad-skill-translation-wave2.md)。

1. 完成三個 pilot 的真實 trace 測試，保留成功與 capability gap。
2. 先升級狀態 B 中的唯讀工作流，再處理可寫工作流。
3. 每個新 adapter 都以獨立 PR／commit 加入，包含 Revit regression evidence。
4. 只有在資料契約、寫入驗證與 rollback 邊界明確後，才把 candidate 標成 pilot 或 supported。
