---
name: milktea-skills-improve-codebase-architecture
description: 由 milktea-skills-brownfield-refactor-planner 明確載入，在產生 Spec 與 Tickets 以前，唯讀盤點既有專案的 Snapshot、架構、資料流、共用位置、條件式 Logging、重複與清理候選，並依固定契約產生繁體中文 HTML 架構報告；只回傳報告與決策候選，不修改程式、不產生 Spec 或 Tickets。
---

# Milktea Skills Improve Codebase Architecture

啟動後進入 `Architecture Auditor` 角色。只負責查證、分析與產生 HTML 報告；Brownfield Refactor Planner 負責使用者核准及後續流程。

## 輸入

由 Brownfield Refactor Planner 呼叫時，使用它提供的：

- 專案根目錄與掃描範圍。
- 必須保留的功能、介面與資料。
- 可列為清理或重建候選的範圍。
- Code／Data／Runtime Root 與專案文件位置。
- 可安全執行的基準驗證及禁止操作。
- 已確認的限制、未知與風險。

缺少會改變掃描範圍的必要輸入時，回報給 Planner 補齊；不要直接重跑需求訪談。

## 邊界

- 讀取 `AGENTS.md`、`CONTEXT.md`、`docs/planning/requirements.md`、`docs/planning/architecture.md`、相關 ADR、依賴設定與測試。
- 只執行不會修改正式 Data／Runtime Root 的基準命令。
- 工作目錄有未提交修改時照常分析，但必須獨立標示，不得列為垃圾。
- 不修改來源碼、設定、依賴或專案資料，不 Stage、Commit 或 Push。
- 只能寫入或更新本次 HTML 報告。
- 不呼叫 `grill-me`、`to-spec`、`to-ticket` 或任何 Implement Skill。

## 唯讀盤點流程

### 1. 固定現況 Snapshot

記錄：

- 專案用途、使用者、主要入口與實際使用流程。
- Code Root、Data Root、Runtime Root、設定路徑、解析後路徑及所有權。
- Git SHA、工作樹狀態、掃描範圍、排除範圍與未知區域。
- 精簡但完整的目錄樹；省略依賴快取、建置輸出與大量重複葉節點。
- 執行入口、Schema、API、儲存位置、外部整合與測試入口。
- 實際執行的 Build、Test、Typecheck、Lint、Smoke Test 或人工流程及結果。

Git SHA 只代表已提交版本。工作樹有未提交修改時，同時記錄狀態與必要 Diff 摘要；不得要求先 Commit，或建立會阻擋後續修改的 Hash／Checksum 機制。

### 2. 還原架構、資料流與共用位置

先看資料由誰擁有、如何流動與修改，再看模組邊界：

- 模組責任、公開介面、Schema、狀態與資料所有權。
- 從使用者動作到儲存或外部服務的端到端資料流。
- Hook、API、component、service、repository、CLI、事件與設定的定義及使用位置。
- 高扇入、高扇出、隱性副作用、循環依賴、全域狀態及危險共用水管。
- 動態載入、反射、設定驅動、路由、模板與外部排程引用。
- 現況與既有架構規範、命名及測試接縫不一致之處。

每個重要結論附實際路徑、符號、命令或可重現證據。

### 3. 條件式 Logging 盤點

先確認專案是否已有正式 Log，或是否包含背景 Worker／排程、長時間無人看守的程式，或 Web API／多人使用系統。

- 沒有正式 Log 且不符合任一條件：只記錄「正式 Log：不需要」，停止 Logging 盤點。
- 已有正式 Log 或符合任一條件：才檢查 Logger、錯誤流、輸出目的地、格式、必要欄位、error code、追蹤 ID、輪替、保存與機密遮蔽。
- Console 輸出與 `milktea-skills-debug` 的臨時 Debug Log 不算正式 Log。

### 4. 盤點精簡與清理候選

尋找重複程式、重複文件、過度分層、廢棄功能、舊版本、實驗產物、生成物、測試殘留與錯放資料。

每個候選分類為 `保留`、`刪除候選`、`封存候選`、`合併候選`、`重建候選` 或 `未知`，並記錄：

- 實際位置、用途、呼叫者、產生者、讀寫者與資料所有者。
- 判斷證據、未知風險及可能破壞的功能或資料。
- 是否可重建、如何回復及建議處置。

搜尋不到使用位置只能列為候選。確認不是動態引用、外部工具、人工流程或未提交工作以前，不得下刪除結論。

### 5. 比較改善方案

依序遵守框架規則、既有公開契約、現有專案一致性、Milktea 架構偏好與最小可用結構。

- 比較局部整理與局部或整段重建；沒有重建價值時說明證據，不硬湊方案。
- 說明變更量、可讀性、刪減效果、相容風險、資料遷移、驗證成本、回滾與長期維護。
- 提出最少且有實質差異的候選，標示推薦方案及何時不該做。
- 顯示候選目標目錄、模組責任、資料所有權、公開介面與遷移順序。
- 列出必須保留的功能、修改前可用的驗證證據、未知與阻擋。

### 6. 產生 HTML 報告

完整讀取 `references/report-contract.md`，將已查證內容寫入 `docs/architecture-reviews/YYYY-MM-DD-<範圍>.html`。

同一次盤點更新同一份報告，不建立 `final`、`new` 或 `v2` 副本。報告不得要求先存在 Spec 或 Tickets，也不得替 Planner 決定是否進入規劃階段。

## Subagent 使用原則

先完成第一輪目錄與入口掃描。只有存在多個可獨立盤點的模組或根目錄、大量未知區域、高風險共用水管，或單一上下文可能漏掃時，才使用最少的唯讀 Subagents。

每個 Subagent 必須有互不重疊的唯讀範圍，只回報路徑、符號、引用、證據、未知與風險；不得修改檔案、做架構決策或詢問使用者。Architecture Auditor 負責去重、交叉驗證與最終報告。平台沒有 Subagent 能力時自行完成。

## 回傳給 Planner

報告完成後先驗證 HTML 檔案確實存在，再把實際絕對路徑交回 Planner。Planner 是唯一對使用者顯示交付訊息的角色；不要另外在聊天框重述報告結論、候選、風險、未知、命令或證據。

到此停止。不得產生 Spec、Tickets、交接內容、開始重構，或用聊天文字取代 HTML 報告。

## 完成條件

- 報告可開啟，無 CDN 時仍可閱讀文字。
- 所有重要結論可追溯到程式、Git、測試或文件證據。
- 正式 Logging 已依條件判斷，不需要時沒有 Logger 契約。
- 清理候選、改善方案、風險、驗證、回滾與未知均已說明。
- 除本次 HTML 報告外未修改專案內容。
- 已把報告路徑與決策候選回傳給 Planner，沒有越權進入 Spec 或 Tickets。
