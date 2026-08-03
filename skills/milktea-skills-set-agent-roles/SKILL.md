---
name: milktea-skills-set-agent-roles
description: 由使用者明確呼叫，偵測目前平台實際可用的 AI Agent 或 CLI，透過原生選項介面設定目前 Task 的 Developer、Reviewer A 與 Reviewer B。使用者想更換開發者、審查者或為特定角色指定模型時使用；只留下 Task 內分工狀態，不寫設定檔、不安裝工具、不派工。
disable-model-invocation: true
---

# Milktea Skills Set Agent Roles

只設定目前 Task 的分工，不開始實作或 Review。

## 流程

1. 盤點平台已提供的 Agent 能力、專案明確指定的命令，以及目前環境或 WSL 中可安全驗證的 AI CLI。只有確定可啟動的選項才算可用；不得遞迴掃描磁碟、安裝工具或接受任意 CLI 輸入。
2. 讀取本 Task 最新的完整分工狀態；沒有狀態時，若 Claude 與 Codex 都可用，建議 Developer 使用 Claude、兩名 Reviewer 使用 Codex。
3. 只有一個 CLI 可用時，直接把三個角色都設為該 CLI，並明示缺少跨模型獨立性。
4. 有多個 CLI 可用時，使用平台原生選項介面依序選擇 Developer、Reviewer A、Reviewer B；每次只顯示已驗證可用的 CLI，並把保持目前選項放在第一項。平台沒有原生選項介面時回報 `BLOCKED: AGENT_ROLE_CHOICE_UI_UNAVAILABLE`，不得假裝使用者已選擇。
5. 允許同一 CLI 擔任多個角色；執行時仍須建立彼此隔離的 Agent。
6. 預設不詢問模型。只有使用者明確指定時，才為該角色記錄 CLI 可接受的精確模型 ID；不得猜測或改寫模型名稱。

## Task 分工狀態

在回覆中輸出一份完整狀態；本 Task 最後一份完整狀態取代先前狀態：

```yaml
developer:
  cli: claude
reviewer_a:
  cli: codex
reviewer_b:
  cli: codex
```

明確指定模型時，只在對應角色增加 `model`：

```yaml
developer:
  cli: claude
reviewer_a:
  cli: codex
  model: gpt-5.6-luna
reviewer_b:
  cli: codex
```

最後顯示三個角色的 CLI、明確指定的模型，以及設定將從下一張尚未派發的 Ticket 生效。
