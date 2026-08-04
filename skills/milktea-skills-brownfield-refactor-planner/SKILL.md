---
name: milktea-skills-brownfield-refactor-planner
description: 協調既有專案的安全重構規劃。先確認盤點範圍與不可破壞的功能，再明確載入 milktea-skills-improve-codebase-architecture 產生唯讀 HTML 架構報告；使用者看完可直接結束，只有決定繼續重構時才確認目標架構、產生 Spec 與 Tickets，最後交給 Brownfield Implement。使用者要求整理混亂架構、去重、清理廢棄內容、改善可讀性或評估局部重建時使用；不修改來源碼或清除資料。
---

# Milktea Skills Brownfield Refactor Planner

## 使用時機

當既有專案架構混亂、重複或廢棄內容增加，或準備進行可能牽動多個既有功能的重構與高風險變更時使用。

新增一般功能使用 `$milktea-skills-grill-me`。如果專案已經混亂，先完成 Brownfield 清整，再另開規劃 Task 處理新功能。

## 角色與邊界

啟動後，本 Task 的 Core Agent 進入 `Brownfield Refactor Planner` 角色，負責範圍確認、Skill 編排、使用者核准與最後交接。

- 先理解現有行為、資料和限制，再開始架構健檢。
- 不重做 Architecture Auditor 的唯讀盤點或 HTML 報告。
- 不修改來源碼，不移動、重新命名或刪除專案資料，不安裝依賴，不 Commit 或 Push。
- 工作目錄內尚未提交的修改視為使用者進行中的工作，不得列為垃圾。
- 搜尋不到使用位置時只能列為候選；不得直接建議刪除。
- 使用者只需要報告時，不產生 Spec、Tickets 或 Implement 交接。
- 使用者決定繼續重構後，才進入規劃與派工文件階段；不得在 Planner Task 實作。

## 流程

依序完成，不跳過報告決策關卡：

1. 確認盤點目標與邊界。
2. 載入 `$milktea-skills-improve-codebase-architecture` 產生 HTML 架構報告。
3. 讓使用者看完報告並決定是否繼續。
4. 只有決定繼續時，確認目標架構與原有功能驗證方式。
5. 產生並核准 Spec 與 Tickets。
6. 顯示 Brownfield Implement 交接內容。

### 1. 確認盤點目標與邊界

先讀目前對話、專案指令、`AGENTS.md`、`CONTEXT.md`、`docs/planning/requirements.md`、`docs/planning/architecture.md`、相關 ADR 與現有產品行為。

只詢問會改變盤點或後續計畫的決策；需要補問多項時，一次集中詢問：

- 本次處理的專案、根目錄、模組與優先順序。
- 必須保持相容的功能、使用流程、公開介面與資料。
- 可以列為刪除、封存、合併、搬移或重建候選的範圍。
- 可使用的測試、人工操作與回滾條件。

能從程式庫與文件確認的事實自行查證。問題很小或答案已明確時，省略無用提問。

### 2. 產生 HTML 架構報告

明確載入 `$milktea-skills-improve-codebase-architecture`。Skill 不存在時，回報缺少的 Skill 並停止；不得自行模擬另一套報告流程。

把下列已確認內容交給 Architecture Auditor：

- 專案根目錄與掃描範圍。
- 必須保留的功能、介面與資料。
- 可列為清理或重建候選的範圍。
- 已知 Code／Data／Runtime Root 與專案文件位置。
- 可安全執行的基準驗證及禁止執行的操作。
- 使用者已確認的限制、未知與風險。

Architecture Auditor 負責唯讀 Snapshot、架構與資料流還原、共用位置追蹤、條件式 Logging 盤點、清理候選、方案比較及 HTML 報告。Planner 不重複掃描或維護第二份報告規格。

### 3. 報告決策關卡

顯示 HTML 報告的實際路徑與 Architecture Auditor 回報的推薦方案、未知事項及待決策項目。讓使用者選擇：

1. **只保留報告，到此結束。**
2. **依報告繼續產生重構 Spec 與 Tickets。**
3. **先修改同一份報告。**

選擇只保留報告時，完成本 Task；不得產生空白或草稿 Spec／Tickets，也不得顯示 Implement 交接。

選擇修改時，把具體回饋交回 `$milktea-skills-improve-codebase-architecture`，更新同一份 HTML；不得建立 `final`、`new` 或 `v2` 副本。更新後重新回到本關卡。

只有使用者選擇繼續，才記錄採用的改善候選、拒絕的候選及理由，進入下一階段。

### 4. 確認目標架構與驗證

載入 `$milktea-skills-grill-architecture`，只把使用者選定的報告候選整理成正式架構決策；不得重新進行完整健檢、重問報告已完成的正式 Log 判定，或新增報告未提出且使用者未核准的重構範圍。

規劃至少包含：

- 目標目錄、模組責任、資料所有權與公開介面。
- 保留、搬移、合併、新建、封存與移除的內容。
- 可分段驗證、可回滾的遷移順序。
- 必須保留的功能清單，以及修改前、修改後使用同一方法確認的證據表。
- 報告判定需要正式 Log 時，才規劃 Logger 與 Logging Ticket；判定不需要時完全不處理。

所有必須保留的功能都要有修改前可重現的驗證方式。無法驗證的項目列為阻擋或交由使用者決定，不得宣稱一定不會壞。

### 5. 產生 Spec 與 Tickets

1. 既有需求文件缺少、過期或衝突時，載入 `$milktea-skills-grill-check-needs`，只補本次重構需要的決策。
2. 以 Planner 上游模式載入 `$milktea-skills-to-spec`，把已核准的報告選擇與架構決策寫入 `docs/work/<功能名稱>/spec.md`。
3. 顯示 Spec 並取得使用者核准；需要修改時更新同一份文件。
4. 以 Planner 上游模式載入 `$milktea-skills-to-ticket`，把已核准 Spec 拆到 `docs/work/<功能名稱>/tickets/`。
5. 顯示完整 Tickets、依賴、角色、Review、原有功能確認及驗收條件，取得使用者核准。

`to-spec` 與 `to-ticket` 只整理已核准的報告選擇及架構決策，不得臨時新增需求或擴大重構範圍。

### 6. 唯一 Task 交接

Spec 與 Tickets 核准後，顯示下列同一份內容，並把所有占位符換成實際值；不得縮短、改寫或產生第二版本：

```text
請將以下內容完整複製到新的獨立 Task／對話視窗。不要在目前的 Planner 視窗執行，以免規劃與實作身分衝突。

請載入並執行 `milktea-skills-brownfield-refactor-implement` Skill。
如果目前環境找不到此 Skill，請停止並回報，不得自行模擬或改用其他流程。

專案根目錄：<實際路徑>
必讀：AGENTS.md、CONTEXT.md、docs/planning/requirements.md、docs/planning/architecture.md、相關 ADR。
HTML 架構報告：<實際路徑>
Spec：<已核准的實際路徑>
Tickets：<依執行順序的已核准實際路徑>
使用者已核准報告中的重構方案、Spec 與 Tickets。

先驗證所有文件、Snapshot、依賴與工作目錄，再依 Tickets 派工。不得重新規劃或擴大範圍。
```

Codex Desktop 有使用者可見的頂層 Task 建立工具時，顯示內容後提供「直接建立新的執行 Task（推薦）」與「暫不執行」。使用者選擇建立後，以相同內容建立 local Task 並開啟；不要建立 Worktree。其他平台保留完整內容供使用者複製，不啟動巢狀 CLI 或用 Subagent 冒充新的 Core Task。

## 完成條件

### 報告結束

- HTML 報告已產生並顯示實際路徑。
- 使用者明確選擇只保留報告。
- 沒有產生 Spec、Tickets、交接內容或修改程式。

### 重構規劃完成

- 使用者已從報告選定重構方案。
- 目標架構、遷移、回滾與原有功能確認方式已核准。
- Spec 與 Tickets 只包含核准範圍，且皆已核准。
- 唯一交接內容已填入實際路徑並顯示。
- Planner Task 尚未開始實作。
