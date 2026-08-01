---
name: milktea-skills-setup-issue-tracker
description: 首次使用 milktea-skills-grill-me，或 to-spec、to-ticket 找不到有效 Issue Tracker 設定時，自動設定或修復正式 Tracker。優先偵測產品 Repository 的 GitHub Issues，確認 Repository、權限、標籤與阻擋方式後寫入 docs/agents/issue-tracker.md；已有有效設定時安靜完成。這是專案預檢，不是需求或架構決策。
---

# Milktea Skills Setup Issue Tracker

設定每個產品專案自己的正式 Issue Tracker。不得把設定寫進 `CONTEXT.md`、需求或架構文件。

## 快速通過

讀取 `docs/agents/issue-tracker.md`。下列項目完整且可用時，不詢問、不重寫，只回報 `TRACKER_READY`：

- 平台與 Repository。
- 可用的 GitHub connector、API 或 `gh`。
- Issues 已啟用，且目前身分可建立、留言及更新 Issue。
- Spec 與 Ticket 標籤存在。
- 阻擋關係的原生方式與文字備援已定義。

## 首次設定

1. 唯讀檢查既有設定、`git remote -v`、`.git/config`、可用 GitHub 工具、登入狀態、Repository 權限與 Issues 狀態。
2. 有 GitHub remote 時，推薦該產品 Repository 的 GitHub Issues；不得推薦 Agents Army Repository。
3. 沒有 remote 時，推薦選擇或建立私人 GitHub 產品 Repository。建立 Repository、加入 remote 或啟用 Issues 前必須取得明確授權；未授權不得建立、推送或修改遠端。
4. 使用者指定其他正式 Tracker 時，記錄其讀取、建立、留言、標籤、關閉與阻擋操作；不得自行退回本機 Markdown。
5. 一次顯示完整草案：平台、Repository、可見性、操作後端、標籤、阻擋方式與預計寫入內容，取得一次核准。
6. 核准後建立缺少的 `spec`、`ready-for-agent` 標籤，寫入設定，再重新驗證。既有同名標籤沿用，不重建。

工具或權限不足時列出實際缺口並停止，不安裝工具、不索取 Token、不假裝設定完成。

## 設定格式

寫入 `docs/agents/issue-tracker.md`：

```markdown
# Issue Tracker

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

- Repository 指向產品專案，不是 Agents Army。
- Tracker、權限、Issues 與標籤已實際驗證。
- `docs/agents/issue-tracker.md` 已寫入且可由後續 Task 讀取。
- 沒有未授權的 Repository 建立、remote 修改、程式碼 Push 或設定變更。
- 回報 `TRACKER_READY`、Repository 與設定檔路徑。
