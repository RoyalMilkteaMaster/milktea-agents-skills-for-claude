---
name: milktea-skills-setup-issue-tracker
description: 由使用者明確呼叫，將預設的本機 Spec 與 Tickets 儲存模式切換為 GitHub、GitLab 或其他正式遠端 Tracker，或切回本機模式。確認 Repository、權限、標籤與阻擋方式後寫入 docs/agents/issue-tracker.md。不得由 grill-me、to-spec 或 to-ticket 自動啟動。
disable-model-invocation: true
---

# Milktea Skills Setup Issue Tracker

設定每個產品專案的選用遠端 Tracker。預設工作流不需要本 Skill；沒有明確遠端模式時，Spec 與 Tickets 留在 `docs/work/`。不得把設定寫進 `CONTEXT.md`、需求或架構文件。

## 切回本機

使用者要求使用本機時，只寫入：

```markdown
# Issue Tracker

- 模式：local
- Spec：`docs/work/<功能名稱>/spec.md`
- Tickets：`docs/work/<功能名稱>/tickets/`
```

不得刪除遠端 Issue、Repository 或 Git 歷史。

## 啟用遠端

1. 唯讀檢查既有設定、`git remote -v`、`.git/config`、可用 GitHub 工具、登入狀態、Repository 權限與 Issues 狀態。
2. 有 GitHub remote 時，推薦該產品 Repository 的 GitHub Issues；不得推薦 Agents Army Repository。
3. 沒有 remote 時，推薦選擇或建立私人 GitHub 產品 Repository。建立 Repository、加入 remote 或啟用 Issues 前必須取得明確授權；未授權不得建立、推送或修改遠端。
4. 使用者指定其他正式 Tracker 時，記錄其讀取、建立、留言、標籤、關閉與阻擋操作。
5. 一次顯示完整草案：平台、Repository、可見性、操作後端、標籤、阻擋方式與預計寫入內容，取得一次核准。
6. 核准後建立缺少的 `spec`、`ready-for-agent` 標籤，寫入設定，再重新驗證。既有同名標籤沿用，不重建。

工具或權限不足時列出實際缺口並停止，不安裝工具、不索取 Token、不假裝設定完成。

## 設定格式

寫入 `docs/agents/issue-tracker.md`：

```markdown
# Issue Tracker

- 模式：remote
- 平台：GitHub Issues
- Repository：owner/repository
- 可見性：private／public
- 操作後端：GitHub connector／API／gh
- Spec 標籤：spec
- Ticket 標籤：ready-for-agent
- 阻擋關係：GitHub issue dependencies
- 阻擋備援：Ticket 內 `Blocked by: #編號`

## 權限

- 讀取、建立、留言、標籤、更新狀態：已驗證／未驗證
```

只保存操作設定，不保存需求、架構、Token 或登入資訊。

## 完成條件

- 本機模式已寫入 `模式：local`，且沒有修改遠端。
- 遠端模式的 Repository 指向產品專案，不是 Agents Army，且 Tracker、權限、Issues 與標籤已實際驗證。
- `docs/agents/issue-tracker.md` 已寫入且可由後續 Task 讀取。
- 沒有未授權的 Repository 建立、remote 修改、程式碼 Push 或設定變更。
- 回報目前模式、Repository 與設定檔路徑。
