---
name: milktea-skills-set-agent-roles
description: 由使用者明確呼叫的快速 Task 設定器。入口先讓使用者只選一項要調整的功能：共同執行環境、Developer／Reviewer 角色與模型、Reviewer A／B 開關，或 Reviewer B 的 Open Code Review；只載入所選分支、批次收集該分支需要的答案，完成後立即退出。使用者直接說出要改的項目與值時跳過選單。只更新目前 Task 的設定，不派工；Reviewer 預設雙開且至少保留一位，OCR 安裝仍須兩層確認。
---

# Milktea Skills Set Agent Roles

只修改目前 Task 的設定，不開始實作或 Review。

## 快速入口（最高優先）

使用者沒有直接指定項目時，第一個動作必須是使用平台原生選項介面詢問：

> 這次要調整哪一項？

1. **開發環境** — PowerShell、WSL 或其他已安裝 CLI 的環境
2. **角色設定** — Developer、Reviewer A／B、模型與推理強度
3. **Reviewer A ＋ B（預設）** — 兩位都開啟
4. **只開 Reviewer A** — 關閉 Reviewer B
5. **只開 Reviewer B** — 關閉 Reviewer A
6. **Reviewer B OCR** — 開啟、關閉或安裝 Open Code Review

平台沒有原生選項介面時，直接用一則短訊息顯示上述 `1／2／3／4／5／6` 選單並等待一次回答；不得因此停止、載入其他資料或改成逐題詢問。

在使用者選擇前，不得：

- 讀取任何 `references/`。
- 掃描專案文件、磁碟、WSL、CLI 或 OCR。
- 詢問角色、模型、推理強度、Reviewer 開關或 OCR。

使用者已明說「改成 WSL」、「把 Reviewer A 改成 Codex high」、「只開 Reviewer A」或「關閉 OCR」等具體要求時，跳過入口選單，直接執行對應分支。

一次只執行一個分支。完成後輸出變更摘要並立即結束，不詢問是否還要調整其他項目。

## A. 開發環境

只有選擇本分支才讀 `references/execution-environments.md`。

未指定目標時，提供：

1. Windows PowerShell
2. WSL
3. 其他已安裝 CLI 的環境（AI 唯讀偵測）

只驗證使用者選中的環境：

- PowerShell：確認 PowerShell、Windows 專案路徑與 Git 工作樹。
- WSL：確認 `wsl.exe`、實際 distribution、預設 Shell 與 Linux 專案路徑；不假設 Ubuntu。多個 distribution 且沒有明確預設時才追加一次選擇。
- 其他環境：依參考契約做有限的唯讀偵測，不安裝或登入工具。

記錄 `preference`、kind、distribution、Shell、command prefix 與專案路徑。環境改變時保留角色選擇，但不立即偵測角色 CLI。

OCR 安裝是環境專屬。若先前 OCR 已開啟，環境改變後保留 `enabled: true`，但直接將 `review_engine` 改為 `native`、`cli_status` 改為 `not_checked`、`delegate_ready` 改為 false；不檢查、不安裝，等使用者日後選擇 OCR 分支再驗證。

完成後退出。

## B. 角色設定

本分支不讀任何 reference。

先顯示目前三個角色的 CLI、模型與推理強度，再用一個批次表單或一則結構化訊息收集本次修改。不要逐一詢問 Developer、Reviewer A、Reviewer B。

使用格式：

```text
只填要改的角色；未填或 keep 代表保持目前設定。
Developer: <cli> | <model 或 default> | <effort 或 default>
Reviewer A: <cli> | <model 或 default> | <effort 或 default>
Reviewer B: <cli> | <model 或 default> | <effort 或 default>
```

- `default` 用於 model 時移除明確 model；用於 effort 時移除 `model_reasoning_effort`。
- 使用者只想改一個角色時，只顯示該角色的一行。
- 平台無法提供批次表單時，顯示上述一次性文字模板；不得退回三個角色逐題詢問。

### 快速偵測

- 只改 model 或 effort 且保留目前 CLI 時，不做 CLI 偵測。
- 需要更換 CLI 時，只在目前 `execution_environment` 檢查平台已提供的 Agent 後端，以及 `claude`、`codex`、`agy` 的 `PATH` 與安全版本命令。
- Windows PowerShell 使用 `Get-Command`；Linux／WSL 使用 `command -v`；每個外部版本探測使用短逾時。
- 不讀專案 README／AGENTS，不遞迴掃描磁碟，不找任意名稱的 CLI，不安裝或登入工具。
- 使用者提供精確 CLI 路徑時可驗證該路徑；不得接受未經驗證的任意命令字串。

只有一個後端可用時允許三個可設定角色共用，但標示缺少跨模型獨立性。執行時只為 Developer 與啟用 Reviewer 建立隔離 Agent。

模型 ID 按使用者原文記錄，不猜測或改寫。不得為任何角色設定 Haiku；Sonnet 的 `model_reasoning_effort` 必須是 `high`、`xhigh`、`max` 或更高的使用者明確值。`max` 只在使用者明確指定時記錄。其他模型的推理強度可依使用者原文保存，留待派工時由後端驗證；它是推理強度，不是 Token 上限。

新格式 Ticket 的 Developer 模型與推理強度由 Ticket 的「初始執行配置」控制；本分支的 Developer 設定只作為 CLI 偏好與舊 Ticket 的明確回退。要更改已核准 Ticket 的模型時，必須更新該 Ticket，不得用 Task 設定無聲覆蓋。

只更新使用者填寫的角色，其他角色保持不變。完成後退出。

## C. Reviewer 開關

本分支不讀任何 reference，不偵測 CLI 或 OCR。快速入口的三個 Reviewer 選項直接對應：

- 快速入口 `3`：**Reviewer A ＋ B（預設）** — `both`
- 快速入口 `4`：**只開 Reviewer A** — `a_only`
- 快速入口 `5`：**只開 Reviewer B** — `b_only`

使用者在快速入口點選後立即記錄對應的 `reviewer_mode` 並退出，不顯示第二層選單、不追加問題。

只接受 `both`、`a_only`、`b_only`。不要改成兩個布林開關；單一模式必須從資料結構保證至少一位 Reviewer 啟用。沒有本分區更新時預設 `both`。

停用 Reviewer 只停止後續派工，不刪除該角色既有的 CLI、模型、`model_reasoning_effort` 或 OCR 設定；重新啟用時直接沿用。設定從下一張尚未派發的 Ticket 生效，已派發 Ticket 的 Reviewer 名單保持不變。

完成後退出。

## D. Reviewer B OCR

使用者已明確要求關閉時，直接記錄 `enabled: false`、`review_engine: native`、`cli_status: not_checked` 與 `delegate_ready: false`；不讀 reference、不做偵測，然後退出。

其他情況先用白話說明：

> Open Code Review（OCR）不是圖片文字辨識。它可以替 Reviewer B 的 Standards Review 整理 Git 變更檔案與 Review 規則，真正判斷仍由 Reviewer B 的 Claude／Codex 完成；Spec Review 不交給 OCR，Delegation Mode 也不需要 OCR 的 LLM API Key。要為目前 Task 開啟嗎？

提供「維持／改為關閉（建議）」與「開啟」。未取得肯定回答，不得偵測或安裝。

選擇開啟後才讀 `references/open-code-review.md`，並在目前執行環境執行 `scripts/open-code-review.js check --repo <project-path>`：

- 檢查成功：記錄 OCR 絕對路徑、版本與 `delegate_ready: true`。
- OCR 不可用：進行唯一允許的追加問題，也就是第二層安裝確認。完整揭露版本、安裝位置、網路與寫入範圍後，只有肯定回答才能執行 `install --confirmed`。
- 拒絕、條件不足或安裝失敗：保持 Reviewer B 原生 Review，不阻擋其他設定。

不得安裝 Git、Node.js 或 npm，不得執行 `ocr review`，不得要求 LLM API Key。完成後退出。

## 分區狀態

每次只輸出本次更新的分區；未輸出的分區沿用本 Task 先前值，沒有先前值時由 Implement 使用預設。每個分區最後一次更新取代該分區舊值。

```yaml
settings_update: execution_environment | roles | reviewers | open_code_review
```

角色更新可只包含一個角色：

```yaml
settings_update: roles
reviewer_a:
  cli: codex
  model: gpt-5.6-luna
  model_reasoning_effort: high
```

Reviewer 開關只輸出單一合法模式：

```yaml
settings_update: reviewers
reviewer_mode: a_only
```

最後只回報：更新了什麼、其他分區未變，以及設定從下一張尚未派發的 Ticket 生效。
