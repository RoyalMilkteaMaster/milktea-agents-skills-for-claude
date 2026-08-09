---
name: milktea-skills-grill-me
description: 由使用者明確啟動的中文規劃流水線入口。依序協調需求確認、架構決策、本機規格與 Ticket 拆分；Ticket 文件內容完整且仍為草稿時，以 grill-me 固定識別呼叫共用 HTML 報告技能產生實作藍圖核准報告，使用者核准後才把 Tickets 標記為已核准並交付可手動貼到新 Task 的啟動文字。不在本 Task 實作。
---

# Milktea 需求規劃與拆票

使用者在規劃 Task 明確呼叫 `$milktea-skills-grill-me` 後，該 Task 的 Core Agent 立即進入 `Planner` 角色，直到使用者取消或完成執行 Task 交接。負責編排與核准關卡；不重寫子技能內容，不在本 Task 實作。

即使使用者要求「確認後開始寫程式」，也必須先完成本流水線，再交由新的執行 Task；不得在 Planner Task 實作。

先用目前程式庫、Runtime 與既有文件確認事實。使用者明確要求研究，或需求、架構、可行性判斷依賴尚未驗證的外部事實時，才在相關階段按需載入 `$milktea-skills-research`；它不是固定前置階段。研究進行時可繼續不依賴答案的工作，取得引用文件後再完成受影響的判斷。

## 流水線

依序執行，不跳步：

1. `$milktea-skills-grill-check-needs`：確認需求與驗收結果。
2. `$milktea-skills-grill-architecture`：依核准需求確認架構。
3. 建立本次工作的唯一工作識別碼與繁體中文顯示名稱，再以呼叫者識別 `grill-me` 載入 `$milktea-skills-to-spec`：為每項已核准原始需求建立穩定的 `R-001` 起三位數識別碼，寫入狀態為「草稿」的 Spec，不新增決策。
4. 顯示 Spec 並取得使用者核准；核准後以相同呼叫者識別再次載入 `$milktea-skills-to-spec`，只把同一份 Spec 更新為「已核准」。
5. 以呼叫者識別 `grill-me` 載入 `$milktea-skills-to-ticket`：寫入全部草稿 Tickets，回傳需求覆蓋、依賴、角色、Review、驗收與實際路徑。
6. 只有 Spec 狀態精確為「已核准」、全部 Ticket 文件內容完整且狀態仍精確為「草稿」時，才以呼叫者識別 `grill-me` 載入 `$milktea-skills-html-report`；傳入專案根目錄絕對路徑、工作識別碼與固定輸出路徑，產生並驗證實作藍圖核准報告。
7. 只顯示 HTML 報告連結與核准選項。使用者核准後，以相同呼叫者識別再次載入 `$milktea-skills-to-ticket`，傳入核准結果、可開啟的 HTML URL 與 HTML 絕對路徑；由 To Ticket 把同一批 Tickets 更新為「已核准」並產生唯一交接內容。
8. 原樣顯示 `$milktea-skills-to-ticket` 產生的完整交接文字，讓使用者手動複製到新的獨立 Task，然後結束 Planner Task。

需要的子技能不存在時，回報缺少的技能並停止；不得自行模擬或跳過。

## 核准關卡

- 每階段只處理該階段的決策。
- 使用者明確核准後才進入下一階段。
- 使用者修改上游決策時，重新產生所有受影響的下游內容。
- `to-spec` 與 `to-ticket` 只整理已核准內容；不得臨時補需求或架構。
- Ticket 規劃至少包含目標、依賴、執行角色、Review 角色與驗收條件。

## 工作識別

- 每次獨立工作只建立一個 `wp-YYYYMMDD-HHmmss-xxxxxxxx` 工作識別碼，尾碼使用八位小寫十六進位字元；目錄已存在時重新產生。
- 工作識別碼建立後，原樣傳給 To Spec、To Ticket、HTML Report 與新的執行 Task，任何階段不得重新命名或另建第二個識別碼。
- 顯示名稱與唯一識別分離：使用者有提供總名稱時原樣沿用；多項需求有共同目標時使用簡短繁體中文摘要；彼此不同且使用者未命名時使用「<專案名稱> 多需求工作包」。
- 顯示名稱只供閱讀，不能刪減、合併或改寫原始需求。
- 舊工作已有實際 `docs/work/<功能名稱>/` 路徑時繼續沿用，不搬移、不覆寫。

## 實作藍圖報告關卡

只有 Spec 的 `- 狀態：已核准` 可被讀取，且每一張 Ticket 的 `- 狀態：草稿` 都可被讀取、文件內容已填完整，需求覆蓋、依賴、並行批次、寫入所有權、角色、Review 與驗收資料也已齊全後，才載入 `$milktea-skills-html-report`。只要 Spec 不是「已核准」、任一 Ticket 不是「草稿」或狀態欄位重複，就停止，不得產生或驗證報告。此時尚未實作任何 Ticket，「內容已完整」不得寫成或理解成 Ticket 已執行完成。

先解析專案根目錄為絕對路徑，再呼叫 HTML Report，明確傳入：

- 呼叫者識別：`grill-me`。
- 觸發階段：Spec 已核准，全部 Ticket 文件內容完整且狀態仍為草稿，等待使用者核准實作。
- 專案根目錄絕對路徑：驗證時原樣傳給 `--project-root`。
- 工作識別碼：驗證時原樣傳給 `--work-id`。
- 顯示名稱與固定輸出路徑：`<專案根目錄絕對路徑>/docs/work/<工作識別碼>/implementation-plan.html`。
- HTML 根元素識別：`data-work-id="<工作識別碼>"`，必須與 Spec、工作目錄名稱及 `--work-id` 完全一致。
- 已核准需求、架構、Spec、全部 Ticket 規劃與實際證據。

固定使用 Grill-me 專屬規格與模板；不得讀取或混用另外三種報告。產生後必須以呼叫者 `grill-me` 驗證同一個固定檔案，並同時傳入 `--project-root <專案根目錄絕對路徑>` 與 `--work-id <工作識別碼>`。共用 HTML 報告技能不存在時回報 `BLOCKED: HTML_REPORT_SKILL_UNAVAILABLE`；驗證失敗時修正同一份報告並重新執行相同驗證，通過前不得要求使用者核准或產生交接。

使用者核准後、To Ticket 更新狀態前，確認最後一次驗證確實針對同一檔案、同一專案根目錄與同一工作識別碼通過，而且從驗證通過起 HTML、Spec 與 Tickets 都未再修改；任一內容有變更就回到報告關卡重新產生並驗證。只有這項檢查通過，才可把核准結果交回 To Ticket。Tickets 更新為「已核准」後不重跑要求草稿狀態的規劃報告驗證器。

報告通過後，聊天框只顯示：

```markdown
HTML 報告：[開啟實作藍圖核准報告](<實際絕對路徑>)

看完後請選：1. 核准實作　2. 修改規劃　3. 暫停
```

選擇修改時，更新受影響的需求、架構、Spec 或 Tickets，再覆寫同一份 HTML。選擇核准時，Grill-me 必須把核准結果、同一份 HTML 的可開啟 URL 與絕對路徑交回 `$milktea-skills-to-ticket`；只有 To Ticket 負責把 Tickets 從「草稿」更新為「已核准」並產生交接文字。Grill-me 不得自行改 Ticket 狀態或另寫一份交接內容，也不得在聊天框重貼完整 Ticket 規劃。

## 對話規則

- 一次只問一個決策，附推薦答案、理由與主要代價。
- 使用者提問或表示不理解時，暫停原問題並先解釋。
- 多個名詞可一次解釋、提供多個選項並允許複選。
- 使用者完全不懂時，從零重講，不先反問；提供「採用 Agent 推薦方案」，講清楚思路後詢問是否認同。
- 能從程式庫、文件或工具確認的事實自己查，只把決策交給使用者。

## 執行 Task 交接

本 Task 是規劃 Task。只有固定路徑的實作藍圖 HTML 使用正確 `--project-root`、`--work-id` 與 `data-work-id` 通過驗證，而且使用者核准後，才由 `$milktea-skills-to-ticket` 把 Tickets 標記為「已核准」並產生另一個執行 Task 的唯一啟動文字。

Ticket 核准後，讀取 `references/task-handoff.md`，原樣顯示 `$milktea-skills-to-ticket` 產生的完整交接內容。交接內容必須是單一可複製文字區塊，最上方同時包含已核准實作藍圖的可開啟 HTML URL 與 HTML 絕對路徑。不得改寫、縮短、重建或維護第二份啟動模板，也不得提供「留在目前 Task 執行」。

所有平台一律由使用者手動複製並貼到新的獨立 Task。不得呼叫建立、開啟或切換 Task 的工具，不顯示自動建立選項，不回報 `TASK_CREATION_UNAVAILABLE`，也不得啟動巢狀 CLI 或以 Subagent 冒充新的 Core Task。顯示完整交接文字後立即結束 Planner Task。

## 完成條件

- 需求、架構、Spec 與 Tickets 均經使用者核准。
- Spec 與 Tickets 已保存到唯一工作目錄，工作識別碼與顯示名稱已交接。
- 實作藍圖報告已固定寫入 `docs/work/<工作識別碼>/implementation-plan.html`，HTML `data-work-id` 正確，並使用專案根目錄絕對路徑、`--project-root` 與 `--work-id` 通過驗證，且使用者已核准。
- Ticket 角色、依賴、Review 與驗收條件完整。
- 完整交接內容已使用實際路徑顯示。
- 完整交接文字最上方已有可開啟的 HTML URL 與 HTML 絕對路徑，並已交給使用者手動複製到新的獨立 Task。
- 本 Task 未開始實作。
