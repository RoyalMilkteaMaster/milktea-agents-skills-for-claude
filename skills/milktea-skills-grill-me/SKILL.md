---
name: milktea-skills-grill-me
description: 由使用者明確啟動的中文規劃流水線入口。依序協調需求確認、架構決策、本機規格與 Ticket 拆分；全部 Tickets 完成後以 grill-me 固定識別呼叫共用 HTML 報告技能產生實作藍圖核准報告，使用者核准後才建立新的執行 Task。不在本 Task 實作。
---

# Milktea 需求規劃與拆票

使用者在規劃 Task 明確呼叫 `$milktea-skills-grill-me` 後，該 Task 的 Core Agent 立即進入 `Planner` 角色，直到使用者取消或完成執行 Task 交接。負責編排與核准關卡；不重寫子技能內容，不在本 Task 實作。

即使使用者要求「確認後開始寫程式」，也必須先完成本流水線，再交由新的執行 Task；不得在 Planner Task 實作。

先用目前程式庫、Runtime 與既有文件確認事實。使用者明確要求研究，或需求、架構、可行性判斷依賴尚未驗證的外部事實時，才在相關階段按需載入 `$milktea-skills-research`；它不是固定前置階段。研究進行時可繼續不依賴答案的工作，取得引用文件後再完成受影響的判斷。

## 流水線

依序執行，不跳步：

1. `$milktea-skills-grill-check-needs`：確認需求與驗收結果。
2. `$milktea-skills-grill-architecture`：依核准需求確認架構。
3. 建立本次工作的唯一工作識別碼與繁體中文顯示名稱，再由 `$milktea-skills-to-spec` 整理已核准內容，不新增決策。
4. 以上游呼叫者 `grill-me` 載入 `$milktea-skills-to-ticket`：寫入全部草稿 Tickets，回傳依賴、角色、Review、驗收與實際路徑。
5. 以呼叫者識別 `grill-me` 載入 `$milktea-skills-html-report`，產生實作藍圖核准報告。
6. 只顯示 HTML 報告連結與核准選項；使用者核准後才把 Tickets 更新為「已核准」。
7. 顯示 `$milktea-skills-to-ticket` 產生的唯一交接內容，再詢問是否開始執行。

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

只有 Spec 與全部 Tickets 都已完成，且需求覆蓋、依賴、並行批次、寫入所有權、角色、Review 與驗收資料齊全後，才載入 `$milktea-skills-html-report`，並明確傳入：

- 呼叫者識別：`grill-me`。
- 觸發階段：Spec 與全部 Tickets 已完成，等待使用者核准實作。
- 工作識別碼、顯示名稱與輸出路徑：`docs/work/<工作識別碼>/implementation-plan.html`；舊工作使用已交接的實際路徑。
- 已核准需求、架構、Spec、全部 Ticket 規劃與實際證據。

固定使用 Grill-me 專屬規格與模板；不得讀取或混用另外三種報告。共用 HTML 報告技能不存在時回報 `BLOCKED: HTML_REPORT_SKILL_UNAVAILABLE`；驗證失敗時修正同一份報告，通過前不得要求使用者核准或產生交接。

報告通過後，聊天框只顯示：

```markdown
HTML 報告：[開啟實作藍圖核准報告](<實際絕對路徑>)

看完後請選：1. 核准實作　2. 修改規劃　3. 暫停
```

選擇修改時，更新受影響的需求、架構、Spec 或 Tickets，再覆寫同一份 HTML。選擇核准時才將 Tickets 更新為「已核准」並進入交接；不得在聊天框重貼完整 Ticket 規劃。

## 對話規則

- 一次只問一個決策，附推薦答案、理由與主要代價。
- 使用者提問或表示不理解時，暫停原問題並先解釋。
- 多個名詞可一次解釋、提供多個選項並允許複選。
- 使用者完全不懂時，從零重講，不先反問；提供「採用 Agent 推薦方案」，講清楚思路後詢問是否認同。
- 能從程式庫、文件或工具確認的事實自己查，只把決策交給使用者。

## 執行 Task 交接

本 Task 是規劃 Task。只有實作藍圖 HTML 通過驗證且使用者核准後，才把 Tickets 標記為「已核准」並建立另一個執行 Task。

Ticket 核准後，原樣顯示 `$milktea-skills-to-ticket` 產生的完整交接內容。不得改寫、縮短、重建或維護第二份啟動模板，也不得提供「留在目前 Task 執行」。

Codex Desktop 有頂層 Task 工具時，只提供：

1. **直接建立新的執行 Task（推薦）**
2. **暫不執行**

有選項工具時使用選項工具；否則使用編號選單。使用者選擇建立後：

1. 確認 `AGENTS.md`、`CONTEXT.md`、`docs/planning/requirements.md`、`docs/planning/architecture.md`、相關 ADR、實際 Spec、Tickets、角色與 Review 規則皆已保存，且新 Task 可讀取相同版本。
2. 讀取 `references/task-handoff.md`，把已顯示的同一份交接內容原樣交給目前平台；不複製完整訪談對話。
3. Codex Desktop 有頂層 Task 工具時，使用同一份交接內容直接建立並開啟新的 local Task，回報 Task ID；使用者不必手動複製。
4. Claude Code、Codex CLI 或無頂層 Task 工具的平台，只保留已顯示的可複製內容；不得啟動巢狀 CLI 或以 Subagent 冒充新 Task。
5. 建立失敗時回報實際錯誤並保留完整可複製內容；不得假裝成功或留在 Planner Task 實作。

Claude Code、Codex CLI 或無頂層 Task 工具的平台，不顯示無法執行的自動建立選項；顯示完整交接內容、回報 `TASK_CREATION_UNAVAILABLE` 後結束規劃 Task。

## 完成條件

- 需求、架構、Spec 與 Tickets 均經使用者核准。
- Spec 與 Tickets 已保存到唯一工作目錄，工作識別碼與顯示名稱已交接。
- 實作藍圖報告已使用呼叫者識別 `grill-me` 產生並通過驗證，且使用者已核准。
- Ticket 角色、依賴、Review 與驗收條件完整。
- 完整交接內容已使用實際路徑顯示。
- Codex Desktop 使用者已選擇建立新 Task 或暫不執行；選擇建立時已有 Task ID。其他平台已明示不支援自動建立並保留完整可複製內容。
- 本 Task 未開始實作。
