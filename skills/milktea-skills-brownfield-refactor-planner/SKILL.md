---
name: milktea-skills-brownfield-refactor-planner
description: 協調既有專案的安全重構規劃。確認盤點範圍後立即建立唯一工作識別碼，載入 milktea-skills-improve-codebase-architecture 完成唯讀盤點，再以 brownfield-planner 固定識別呼叫共用 HTML 報告技能寫入該工作專屬路徑；使用者看完可直接結束，只有決定繼續重構時才確認目標架構、產生 Spec 與 Tickets，最後交付可手動貼到新 Task 的 Brownfield Implement 啟動文字。
---

# Milktea 既有系統重構規劃

## 使用時機

當既有專案架構混亂、重複或廢棄內容增加，或準備進行可能牽動多個既有功能的重構與高風險變更時使用。

新增一般功能使用 `$milktea-skills-grill-me`。如果專案已經混亂，先完成 Brownfield 清整，再另開規劃 Task 處理新功能。

## 角色與邊界

啟動後，本 Task 的 Core Agent 進入 `Brownfield Refactor Planner` 角色，負責範圍確認、Skill 編排、使用者核准與最後交接。

- 先理解現有行為、資料和限制，再開始架構健檢。
- 不重做 Architecture Auditor 的唯讀盤點；HTML 只依它回傳的證據產生。
- 不修改來源碼，不移動、重新命名或刪除專案資料，不安裝依賴，不 Commit 或 Push。
- 工作目錄內尚未提交的修改視為使用者進行中的工作，不得列為垃圾。
- 搜尋不到使用位置時只能列為候選；不得直接建議刪除。
- 使用者只需要報告時，不產生 Spec、Tickets 或 Implement 交接。
- 使用者決定繼續重構後，才進入規劃與派工文件階段；不得在 Planner Task 實作。

先以本地程式碼、Runtime、文件與 Architecture Auditor 還原現況。使用者明確要求研究，或外部框架、API、標準等未驗證事實會實質影響報告或重構判斷時，才按需載入 `$milktea-skills-research`；它不取代本地盤點，也不是固定前置階段。研究進行時可繼續不依賴答案的工作。

## 流程

依序完成，不跳過報告決策關卡：

1. 確認盤點目標與邊界，立即建立唯一工作識別碼與繁體中文顯示名稱。
2. 載入 `$milktea-skills-improve-codebase-architecture` 完成唯讀架構盤點，全程沿用同一工作識別碼。
3. 以呼叫者識別 `brownfield-planner` 載入 `$milktea-skills-html-report`，在該工作專屬路徑產生架構健檢決策報告。
4. 讓使用者看完報告並決定是否繼續。
5. 只有決定繼續時，確認目標架構與原有功能驗證方式。
6. 產生並核准 Spec 與 Tickets。
7. 顯示 Brownfield Implement 交接內容。

### 1. 確認盤點目標與邊界

先讀目前對話、專案指令、`AGENTS.md`、`CONTEXT.md`、`docs/planning/requirements.md`、`docs/planning/architecture.md`、相關 ADR 與現有產品行為。

只詢問會改變盤點或後續計畫的決策；需要補問多項時，一次集中詢問：

- 本次處理的專案、根目錄、模組與優先順序。
- 必須保持相容的功能、使用流程、公開介面與資料。
- 可以列為刪除、封存、合併、搬移或重建候選的範圍。
- 可使用的測試、人工操作與回滾條件。

能從程式庫與文件確認的事實自行查證。問題很小或答案已明確時，省略無用提問。

專案根目錄與本次初始掃描範圍一經確認，就立即建立唯一的 `wp-YYYYMMDD-HHmmss-xxxxxxxx` 工作識別碼，尾碼使用八位小寫十六進位字元；識別碼碰撞時重新產生。另建立繁體中文顯示名稱，只供閱讀，不改寫盤點範圍。不得等到使用者決定重構後才建立識別碼，也不得在後續 Spec、Tickets 或交接階段另建第二個識別碼。

### 2. 完成唯讀架構盤點

明確載入 `$milktea-skills-improve-codebase-architecture`。Skill 不存在時，回報缺少的 Skill 並停止；不得自行模擬另一套盤點流程。

把下列已確認內容交給 Architecture Auditor：

- 專案根目錄與掃描範圍。
- 必須保留的功能、介面與資料。
- 可列為清理或重建候選的範圍。
- 已知 Code／Data／Runtime Root 與專案文件位置。
- 可安全執行的基準驗證及禁止執行的操作。
- 使用者已確認的限制、未知與風險。

Architecture Auditor 負責唯讀 Snapshot、架構與資料流還原、共用位置追蹤、條件式 Logging 盤點、清理候選、方案比較與原有功能基準。Planner 不重複掃描。

### 3. 產生架構健檢決策報告

完整收到 Architecture Auditor 的盤點證據後，載入 `$milktea-skills-html-report`，明確傳入：

- 呼叫者識別：`brownfield-planner`。
- 觸發階段：唯讀架構盤點完成，等待使用者決定是否繼續。
- 專案根目錄絕對路徑（傳給驗證器的 `--project-root`）、工作識別碼（`--work-id`）、顯示名稱、專案名稱、掃描範圍與輸出路徑。
- Architecture Auditor 的完整盤點證據與實際來源。

固定使用 Brownfield Planner 專屬規格與模板，寫入 `docs/architecture-reviews/<工作識別碼>/architecture-review.html`。每次盤點使用自己的唯一目錄；不得使用日期加範圍作為唯一性，也不得覆寫其他工作報告。不得讀取或混用 Grill-me、Implement 或 Brownfield Implement 的規格。

共用 HTML 報告技能不存在時回報 `BLOCKED: HTML_REPORT_SKILL_UNAVAILABLE`；驗證未通過時修正同一份報告，通過前不得進入決策關卡。

### 4. 報告決策關卡

先驗證 HTML 報告存在，再只用下列兩行格式交付；把占位符換成可直接點擊的實際絕對路徑，路徑含空格時在 Markdown 連結目標外加角括號，不在聊天框重述報告結論、候選、風險、未知、命令或證據：

```markdown
HTML 報告：[開啟架構健檢報告](<實際絕對路徑>)

看完後請選：1. 只保留報告　2. 繼續進入 to-spec　3. 修改這份報告
```

使用者選擇：

1. **只保留報告，到此結束。**
2. **依報告繼續產生重構 Spec 與 Tickets。**
3. **先修改同一份報告。**

選擇只保留報告時，完成本 Task；不得產生空白或草稿 Spec／Tickets，也不得顯示 Implement 交接。

選擇修改時，若回饋涉及盤點事實就交回 `$milktea-skills-improve-codebase-architecture` 補證；再以相同呼叫者識別交給 `$milktea-skills-html-report` 更新同一份 HTML。不得建立 `final`、`new` 或 `v2` 副本。更新後重新回到本關卡。

只有使用者選擇繼續，才記錄採用的改善候選、拒絕的候選及理由，進入下一階段。

### 5. 確認目標架構與驗證

載入 `$milktea-skills-grill-architecture`，只把使用者選定的報告候選整理成正式架構決策；不得重新進行完整健檢、重問報告已完成的正式 Log 判定，或新增報告未提出且使用者未核准的重構範圍。

規劃至少包含：

- 目標目錄、模組責任、資料所有權與公開介面。
- 保留、搬移、合併、新建、封存與移除的內容。
- 可分段驗證、可回滾的遷移順序。
- 必須保留的功能清單，以及每項功能唯一的共用驗證方法與修改前實際基準。
- 報告判定需要正式 Log 時，才規劃 Logger 與 Logging Ticket；判定不需要時完全不處理。

所有必須保留的功能都要在規劃階段選定一種修改前可重現的共用驗證方法，立即執行並保存修改前基準；執行階段只能用同一方法取得修改後結果：

- 使用者可見的 UI 與瀏覽器操作流程，使用 Claude／Codex 現有原生瀏覽器控制能力實際操作並保存證據。
- API、CLI、Worker、排程、Migration、資料庫或其他非 UI 功能，使用對應的 API 請求、CLI 指令、自動化測試、資料查詢或可重現基準；不得為了符合格式硬寫成瀏覽器操作。
- 同一項功能修改前後只能採用該票「共用驗證方法」欄位記錄的單一方法，不得在修改後換用較容易通過的替代方法。無法在規劃階段取得修改前基準的項目列為阻擋或交由使用者決定，不得宣稱一定不會壞。

### 6. 產生 Spec 與 Tickets

1. 既有需求文件缺少、過期或衝突時，載入 `$milktea-skills-grill-check-needs`，只補本次重構需要的決策。
2. 沿用盤點開始時已建立的唯一工作識別碼與繁體中文顯示名稱；不得在此階段重新產生。
3. 以呼叫者識別 `brownfield-planner` 載入 `$milktea-skills-to-spec`，把工作識別碼、顯示名稱、已核准的報告選擇與架構決策寫入狀態為「草稿」的 `docs/work/<工作識別碼>/spec.md`，並為每項原始需求建立穩定的 `R-001` 起三位數識別碼。
4. 顯示同一份 Spec 並取得使用者核准；核准後以相同呼叫者識別再次載入 `$milktea-skills-to-spec`，只把同一份 Spec 更新為「已核准」。需要修改時先維持或改回「草稿」，更新同一份文件並重新核准。
5. 以呼叫者識別 `brownfield-planner` 載入 `$milktea-skills-to-ticket`，把已核准 Spec 拆到 `docs/work/<工作識別碼>/tickets/`；全部 Ticket 初次寫入狀態為「草稿」，且逐票引用對應的 `R-xxx`。每張 Brownfield Ticket 的「原有功能確認」只建立一次，規劃時原地填妥「共用驗證方法」與「修改前基準」，並保留「修改後結果」、「原有功能驗收」、「驗收證據」供執行階段原地替換。
6. 顯示完整 Tickets、需求覆蓋、依賴、角色、Review、原有功能確認及驗收條件，取得使用者核准。先確認每個預填機器欄位在每張 Ticket 中恰好一次；核准後以相同呼叫者識別再次載入 `$milktea-skills-to-ticket`，同時傳入架構報告的可開啟 HTML URL 與 HTML 絕對路徑；只由 To Ticket 把同一批 Tickets 的原狀態欄位更新為「已核准」，再把實際 Ticket 路徑與執行順序交回 Brownfield Planner。唯一 Brownfield Implement 交接文字由下一節的固定模板產生。

`to-spec` 與 `to-ticket` 只整理已核准的報告選擇及架構決策，不得臨時新增需求或擴大重構範圍。不得使用不存在的「Planner 上游模式」；兩個技能都只接受明確的呼叫者識別 `brownfield-planner`，首次呼叫產生草稿，第二次呼叫接收使用者核准結果並更新同一份文件。

舊工作已有實際 `docs/work/<功能名稱>/` 交接路徑時繼續沿用，不搬移、不改名、不覆寫；新工作把同一工作識別碼原樣交給 Spec、Tickets、HTML 與 Brownfield Implement。

### 7. 唯一 Task 交接

Spec 與 Tickets 核准後，顯示下列同一份內容，並把所有占位符換成實際值；不得縮短、改寫或產生第二版本：

```text
已核准 HTML URL：<可開啟的實際架構報告 HTML URL>
已核准 HTML 絕對路徑：<實際架構報告 HTML 絕對路徑>

請將以下內容完整複製到新的獨立 Task／對話視窗。不要在目前的 Planner 視窗執行，以免規劃與實作身分衝突。

請載入並執行 `milktea-skills-brownfield-refactor-implement` Skill。
如果目前環境找不到此 Skill，請停止並回報，不得自行模擬或改用其他流程。

專案根目錄：<實際路徑>
工作識別碼：<實際工作識別碼>
顯示名稱：<實際繁體中文顯示名稱>
工作目錄：<實際工作目錄>
必讀：AGENTS.md、CONTEXT.md、docs/planning/requirements.md、docs/planning/architecture.md、相關 ADR。
HTML 架構報告：<同上方的實際絕對路徑>
Spec：<已核准的實際路徑>
Tickets：<依執行順序的已核准實際路徑>
使用者已核准報告中的重構方案、Spec 與 Tickets。

先驗證所有文件、Snapshot、依賴與工作目錄，再依 Tickets 派工。不得重新規劃或擴大範圍。
```

所有平台一律原樣顯示上述單一文字區塊，讓使用者手動複製並貼到新的獨立 Task。不得呼叫建立、開啟或切換 Task 的工具，不顯示自動建立選項，不啟動巢狀 CLI，也不得用 Subagent 冒充新的 Core Task。文字區塊第一行與第二行必須分別是同一份已核准架構報告的可開啟 HTML URL 與 HTML 絕對路徑；沒有報告伺服器時，URL 使用由該絕對路徑轉成並已驗證可開啟的 `file:///` URL。

## 完成條件

### 報告結束

- HTML 報告已使用呼叫者識別 `brownfield-planner` 產生、通過驗證並顯示實際路徑。
- HTML 報告已寫入 `docs/architecture-reviews/<工作識別碼>/architecture-review.html`，沒有覆寫其他工作的報告。
- 使用者明確選擇只保留報告。
- 沒有產生 Spec、Tickets、交接內容或修改程式。

### 重構規劃完成

- 使用者已從報告選定重構方案。
- 目標架構、遷移、回滾與原有功能確認方式已核准。
- Spec 與 Tickets 只包含核准範圍，且皆已核准。
- 盤點開始時建立的工作識別碼、顯示名稱與實際工作目錄已原樣交接，沒有重新產生或覆寫既有工作。
- 唯一交接內容最上方已有可開啟的 HTML URL 與 HTML 絕對路徑，並已顯示供使用者手動複製。
- Planner Task 尚未開始實作。
