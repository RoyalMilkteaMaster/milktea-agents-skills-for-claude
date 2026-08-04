# Task 交接

只在 Tickets 核准、`$milktea-skills-to-ticket` 已產生完整交接內容，且使用者選擇建立新的執行 Task 後讀取。交接內容是唯一 Task prompt；不得改寫或產生另一版本。

所有平台都先顯示同一份完整交接內容。Codex Desktop 可再直接建立 Task；其他平台保留內容供使用者複製。

## Codex Desktop

1. 使用 `list_projects` 找到目前專案。
2. 使用 `create_thread`，指定該專案與 `environment: local`。使用者選擇建立即構成明確授權；不要建立 Worktree，避免新 Task 看不到尚未提交的 `docs/work/`。
3. 將 `$milktea-skills-to-ticket` 產生並已顯示的完整交接內容原樣作為新 Task prompt。
4. 成功取得 `threadId` 後使用 `navigate_to_codex_page` 開啟新 Task，回報 `TASK_CREATED: <threadId>`；使用者不必手動複製。
5. 工具存在但建立失敗時，回報錯誤與完整啟動指令；不得假裝成功或在 Planner Task 實作。

## Codex CLI 或 Claude Code

沒有使用者可見的頂層 Task 建立工具時，保留已顯示的完整交接內容並回報 `TASK_CREATION_UNAVAILABLE`。不得啟動巢狀 CLI、建立 Subagent 冒充 Core Task，或留在 Planner Task 實作。
