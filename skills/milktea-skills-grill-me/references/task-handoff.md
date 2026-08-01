# Task 交接

只在 Tickets 核准且使用者選擇「在目前專案目錄建立新的執行 Task」後讀取。

## Codex Desktop

1. 使用 `list_projects` 找到目前專案。
2. 使用 `create_thread`，指定該專案與 `environment: local`。使用者選擇上述選項即明確要求使用目前專案目錄；不要建立 Worktree，避免看不到未提交的 `docs/work/`。
3. 將 `SKILL.md` 產生的完整啟動指令作為新 Task prompt。
4. 成功取得 `threadId` 後使用 `navigate_to_codex_page` 開啟新 Task，回報 `TASK_CREATED: <threadId>`。
5. 工具存在但建立失敗時，回報錯誤與完整啟動指令；不得假裝成功或在 Planner Task 實作。

## Codex CLI 或 Claude Code

沒有使用者可見的頂層 Task 建立工具時，輸出完整啟動指令並回報 `TASK_CREATION_UNAVAILABLE`。不得啟動巢狀 CLI、建立 Subagent 冒充 Core Task，或留在 Planner Task 實作。
