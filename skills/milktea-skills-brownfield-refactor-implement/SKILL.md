---
name: milktea-skills-brownfield-refactor-implement
description: 執行 Brownfield Refactor Planner 已核准的重構方案、Spec 與 Tickets，沿用 Implement 的派工、雙 Reviewer、證據共識與驗收流程，並確認重構後原有功能仍然正常。使用者把 Brownfield Planner 的交接內容貼到新 Task 時使用；不重新規劃或擴大範圍。
disable-model-invocation: true
---

# Milktea Skills Brownfield Refactor Implement

把已核准的 Brownfield 重構方案落實成可驗證的修改，同時保護原本能正常運作的功能。啟動後，目前 Task 的 Core Agent 擔任 Brownfield Implement Coordinator。

## 輸入

- 專案根目錄。
- Brownfield Planner 產生並經使用者核准的 HTML 架構報告。
- 已核准的 Spec 與全部 Tickets 實際路徑。
- `AGENTS.md`、`CONTEXT.md`、`docs/planning/requirements.md`、`docs/planning/architecture.md` 與相關 ADR。

使用者把 Planner 產生的交接內容貼到新 Task，即視為同意開始執行。先讀完上述資料；缺少會改變實作結果的內容時，直接說明缺口，不自行補成新的規劃。

## 共通執行流程

在目前 Task 內載入 `/milktea-agents-skills-for-claude:milktea-skills-implement`，作為唯一的共通執行流程；不另開 Task，也不另外複製一套派工規則。

Developer 難度分派、安全並行、兩位獨立 Reviewer、臨時派工契約、證據共識、精簡進度回報、Context 交接、Research 使用條件、前端瀏覽器驗證及完成報告，全部依 Implement 執行。Coordinator 仍由本 Skill 擔任，並套用下列 Brownfield 專用規則。

若無法載入 Implement，說明缺少的 Skill 並停止執行。

## Brownfield 專用規則

- HTML 架構報告、Spec、Tickets 與必讀專案文件共同構成核准範圍；只執行其中已核准的工作。
- 不重新設計架構、不新增 Ticket，也不順手處理範圍外問題。發現新問題時記錄證據，交由使用者決定是否另行規劃。
- 刪除、合併或搬移內容，必須能對應到核准報告、Spec 或 Ticket；不得只因看起來多餘就移除。
- 保留工作目錄中不屬於本次 Tickets 的既有修改，不覆蓋或清除使用者工作。
- 只有 Tickets 明確包含 Logging 工作時，才建立正式 Logging；一般執行證據直接放入同一份完成報告。

## 驗證原有功能

開始修改前，依 Planner 報告與專案現有驗證方式，確認本次必須保留的原有行為及修改前結果。現有資料不足以判定時，先從相關測試、介面或實際操作補足可重現的基準；仍無法確認時，向使用者說明缺口，不捏造結果。

相關 Tickets 完成後，以相同層級的方式再次驗證：

- 前端或互動流程：實際開啟瀏覽器或可操作介面驗證。
- API、CLI、背景工作或資料流程：執行對應測試、命令或查詢驗證。
- 搬移、合併或刪除：確認原入口、相依關係與使用方式沒有被意外破壞。

若原有行為退化，把問題退回相關 Ticket，沿用同一組 Developer、兩位 Reviewer 與證據共識流程處理；驗證恢復前不得宣告完成。

## 完成與交付

所有 Tickets 通過 Implement 的完成條件，且核准範圍內必須保留的原有行為均已實際驗證後，才算完成 Brownfield 實作。

沿用 Implement 產生的同一份 `docs/work/<功能名稱>/completion-report.html`，並加入：

- 本次實際完成的重構結果。
- 保留、搬移、合併與刪除的內容。
- 修改前後的原有功能驗證證據。
- 架構或資料流影響、剩餘風險與必要的回復方式。

不另產生第二份完成報告。聊天只需提供完成狀態、報告實際路徑，以及需要使用者親自確認的畫面或產品判斷。
