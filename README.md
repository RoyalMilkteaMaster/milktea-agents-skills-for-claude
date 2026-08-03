# Milktea Agents Army for Claude

給 Claude Code 使用的繁體中文 AI 開發協作 Skills。

## 入口

- `/milktea-agents-army-claude:milktea-skills-grill-me`：新需求規劃。
- `/milktea-agents-army-claude:milktea-skills-brownfield-refactor-planner`：盤點並規劃既有專案重構。
- `/milktea-agents-army-claude:milktea-skills-implement`：接手已核准的 Tickets。
- `/milktea-agents-army-claude:milktea-skills-set-agent-roles`：設定目前 Task 的 Developer 與雙 Reviewer。
- `/milktea-agents-army-claude:milktea-skills-check-feasibility`：主動產生獨立可行性報告。
- `/milktea-agents-army-claude:milktea-skills-improve-codebase-architecture`：主動進行架構健檢。

其餘 Skills 由流程或臨時 Agent 按需載入。

Spec 與 Tickets 預設寫入 `docs/work/`，不需要 GitHub、Commit 或 Push。Claude Code 無法建立使用者可見的頂層 Task 時，會輸出完整啟動指令並停止 Planner Task。

## 測試載入

WSL：

```bash
cd /mnt/d/workstationD
claude --plugin-dir ./milktea-agents-army-claude
```

Windows：

```powershell
cd D:\workstationD
claude --plugin-dir .\milktea-agents-army-claude
```

## 安裝

WSL：

```bash
claude plugin marketplace add /mnt/d/workstationD/milktea-agents-army-claude
claude plugin install milktea-agents-army-claude@milktea-agents-army-claude
```

Windows：

```powershell
claude plugin marketplace add D:\workstationD\milktea-agents-army-claude
claude plugin install milktea-agents-army-claude@milktea-agents-army-claude
```

安裝或更新後，請重新啟動 Claude Code。

## 結構

```text
milktea-agents-army-claude/  # Claude 發行包
├── .claude-plugin/          # Plugin 與 Marketplace 設定
│   ├── plugin.json       # Claude Plugin 定義
│   └── marketplace.json  # Claude Marketplace 定義
├── skills/               # 15 個繁體中文 Skills
└── README.md             # 使用說明
```
