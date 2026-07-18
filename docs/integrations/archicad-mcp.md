# Archicad MCP 安裝與環境設置

本文件說明如何在不複製或覆寫 Revit MCP 的前提下，啟用 BIM_MCP 內建的 Archicad MCP runtime 設定。

## 整合方式

BIM_MCP 不內嵌第三方 Archicad MCP 原始碼。專案設定透過 `uvx` 執行固定版本：

```text
tapir-archicad-mcp==0.4.3 -> archicad-server
```

這讓 Revit MCP 與 Archicad MCP 成為兩個並列的 MCP server：

```text
AI Client
├── revit-mcp    -> BIM_MCP/MCP-Server/build/index.js
└── archicad-mcp -> uvx -> tapir-archicad-mcp==0.4.3
```

## 前置需求

| 項目 | 說明 |
|---|---|
| Archicad | 必須已安裝並開啟目標專案 |
| Archicad JSON API | 隨 Archicad 提供 |
| [Tapir Add-On](https://github.com/ENZYME-APD/tapir-archicad-automation) | 完整社群指令集所需，需依 Archicad 版本安裝 |
| uv / uvx | 下載並在隔離環境執行 Python MCP server |
| 網路 | 第一次解析套件及下載語意搜尋模型時需要 |
| MCP Client | Claude Code、Claude Desktop、Gemini CLI 或 VS Code |

安裝 uv 請依官方文件操作：<https://docs.astral.sh/uv/getting-started/installation/>

## 快速安裝

### macOS

```bash
./scripts/setup-archicad-mcp.sh
```

如果 shell 顯示沒有執行權限：

```bash
chmod +x scripts/setup-archicad-mcp.sh
./scripts/setup-archicad-mcp.sh
```

### Windows PowerShell

可直接雙擊：

```text
scripts\setup-archicad-mcp.bat
```

或從 PowerShell 執行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup-archicad-mcp.ps1
```

安裝腳本會：

1. 確認 `uv` 與 `uvx` 可用。
2. 驗證 `.mcp.json` 和 `.vscode/mcp.json` 使用固定版本。
3. 解析 `tapir-archicad-mcp==0.4.3`，核對版本與 `archicad-server` entry point，建立 uv 快取。
4. 不修改 Archicad 專案，不安裝 Archicad，也不替使用者安裝 Tapir Add-On。

## 設定使用者層級 MCP Client

Claude Code 與 VS Code 可直接讀取 repository 內設定。Claude Desktop 或 Gemini CLI 可選擇讓腳本安全合併使用者設定：

### macOS

```bash
./scripts/setup-archicad-mcp.sh --configure-user --client all
```

### Windows

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup-archicad-mcp.ps1 `
  -ConfigureUser -Client all
```

可用 client：

- `claude-desktop`
- `gemini`
- `all`

若設定檔已存在，腳本會先建立時間戳備份，再以原子寫入方式加入 `archicad-mcp`。如果既有 JSON 已損壞，腳本會停止，不會覆蓋原檔。

## 離線檢查與 CI

只驗證本機命令和已提交的專案設定，不解析 Archicad MCP 套件：

```bash
./scripts/setup-archicad-mcp.sh --check-only
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup-archicad-mcp.ps1 -CheckOnly
```

已下載過 runtime、只想跳過解析時，可使用 `--skip-resolve` 或 `-SkipResolve`。

## 啟動後驗證

1. 安裝並啟用與 Archicad 版本相符的 Tapir Add-On。
2. 開啟 Archicad 與一個測試專案。
3. 重新啟動 MCP Client。
4. 確認 `revit-mcp` 與 `archicad-mcp` 都出現在 MCP server 清單。
5. 先呼叫 `discovery_list_active_archicads`。
6. 取得 instance port 後，再使用 `archicad_discover_tools` 與 `archicad_call_tool`。

Archicad port、GUID 與 Revit ElementId 屬於不同 namespace，不得跨 server 混用。

## 第一次啟動較慢

安裝預檢只會確認套件 metadata 與 Python console entry point。第一次真正啟動 MCP server 時，可能還會：

- 下載 `all-MiniLM-L6-v2` 語意搜尋模型。
- 在使用者目錄建立模型快取。
- 建立 `~/.tapir_mcp/tool_index.faiss` 與 metadata。

完成後，後續啟動會重用快取。若公司網路阻擋模型下載，工具搜尋會降級或無法提供完整語意搜尋，需檢查 proxy、防火牆與模型快取權限。

## 常見問題

### 找不到 `uv` 或 `uvx`

安裝 uv 後關閉並重開終端機，確認：

```bash
uv --version
uvx --version
```

### MCP Client 顯示 server 啟動失敗

執行以下不啟動 MCP server 的套件檢查：

```bash
uv run --no-project --python 3.12 \
  --with "tapir-archicad-mcp==0.4.3" \
  python -c "import importlib.metadata as m; print(m.version('tapir-archicad-mcp'))"
```

若這一步失敗，先處理 Python、套件下載或企業網路問題。

### 找不到 Archicad instance

確認：

- Archicad 已開啟完整專案，而非只停留在啟動畫面。
- Tapir Add-On 版本與 Archicad 相容。
- 沒有另一個安全軟體阻擋本機程序通訊。

### 只有三個 Archicad MCP tools

這是預期設計。AI Client 只會直接看到 instance discovery、tool discovery 與 tool dispatch；其他 Archicad API 指令由 `archicad_discover_tools` 搜尋後交給 `archicad_call_tool` 執行。

## 升級版本

不要只修改單一設定檔。升級時必須同步更新：

- `.mcp.json`
- `.vscode/mcp.json`
- `scripts/setup-archicad-mcp.py` 的 `PACKAGE_VERSION`
- 本文件中的版本與手動命令

升級後先執行 `--check-only`，再執行完整 setup。正式合併前應以實際 Archicad + Tapir 環境做 smoke test。

## 上游與授權

- 上游：<https://github.com/SzamosiMate/tapir-archicad-MCP>
- 套件：<https://pypi.org/project/tapir-archicad-mcp/>
- 宣告授權：MIT

BIM_MCP 目前只引用並執行固定套件，沒有 vendor 上游原始碼。若未來 fork、subtree 或直接複製程式碼，必須同時保留上游授權與 copyright notice。
