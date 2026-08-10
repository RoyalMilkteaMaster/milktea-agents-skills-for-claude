---
name: milktea-skills-set-agent-roles
description: 快速設定目前專案共用的執行環境，以及 Developer、Reviewer A、Reviewer B 的 Agent、CLI、模型與推理強度。設定固定寫入專案的 `.milktea/agent-settings.yaml`，供之後所有 Implement 與 Brownfield Implement Task 直接使用；也可檢查或安裝 Reviewer B 使用的 Open Code Review。不派工、不實作。
disable-model-invocation: true
---
# Milktea Skills Set Agent Roles

快速修改目前專案共用的 Agent 設定，不開始實作或 Review。

## 專案設定檔

使用者已提供專案根目錄時直接使用；否則使用目前唯一的工作區根目錄。只有無法判斷目標專案時才詢問一次，不讀取專案文件或掃描其他目錄。

設定只保存在：

```text
<專案根目錄>/.milktea/agent-settings.yaml
```

這是唯一設定來源。檔案不存在時，以自動環境與自動角色建立；檔案內容無法安全讀取時停止並指出問題，不覆寫原檔。

## 快速入口

使用者沒有直接指定要改什麼時，第一個動作是使用平台原生選項介面詢問：

> 這次要調整哪一項？

1. **開發環境** — PowerShell、WSL 或其他已安裝 CLI 的環境
2. **角色設定** — Developer、Reviewer A／B、模型與推理強度
3. **Reviewer B OCR** — 檢查或安裝 Open Code Review

平台沒有原生選項介面時，以一則短訊息顯示 `1／2／3` 並等待一次回答。

使用者已直接說明「改成 WSL」、「把 Reviewer A 改成 Codex high」或「安裝 OCR」等具體要求時，跳過選單並執行對應分支。

選擇分支前不讀 Reference、不偵測環境、CLI 或 OCR。進入分支後，只讀設定檔與該分支需要的資料；一次只處理一個分支，完成後立即結束。

## A. 開發環境

只有進入本分支才讀取 `references/execution-environments.md`。

使用者沒有指定目標時，提供：

1. Windows PowerShell
2. WSL
3. 其他已安裝 CLI 的環境

只驗證選中的環境。多個 WSL distribution 或其他環境會實際改變結果時，才追加一次選擇；不安裝、不登入，也不檢查角色 CLI。

把實際環境、Shell、命令前綴與專案路徑寫入設定檔，保留三個角色的設定。

## B. 角色設定

本分支不讀取 Reference，也不掃描專案文件。

先從設定檔顯示三個角色目前的 Agent／CLI、模型與推理強度，再用一次批次表單或一則結構化訊息收集修改：

```text
只填要改的角色；未填或 keep 代表保持目前設定。
Developer: <auto 或 agent／cli> | <model 或 default> | <effort 或 default>
Reviewer A: <auto 或 agent／cli> | <model 或 default> | <effort 或 default>
Reviewer B: <auto 或 agent／cli> | <model 或 default> | <effort 或 default>
```

使用者只修改一個角色時，只顯示該角色的一行。Developer 使用 `auto` 時，由 Implement 依每張 Ticket 難度分派；Reviewer 使用 `auto` 時，由 Implement 選擇可用角色。`default` 用於 model 或 effort 時，移除該欄的明確設定。

### 快速驗證

- 只改 model 或 effort 且保留目前 Agent／CLI 時，不重新偵測 CLI。
- 更換 Agent／CLI 時，只檢查平台已提供的 Agent，以及設定環境中 `claude`、`codex` 的 `PATH` 與安全版本命令。
- Windows PowerShell 使用 `Get-Command`；Linux／WSL 使用 `command -v`；外部版本探測使用短逾時。
- 不遞迴掃描磁碟、不安裝、不登入，也不接受未驗證的任意命令字串。

三個角色固定存在，執行時使用彼此隔離的 Agent。模型 ID 按使用者原文記錄，不猜測或改寫。不得設定 Haiku；Sonnet 的推理強度至少為 `high`，`max` 只在使用者明確指定時記錄。

## C. Reviewer B OCR

本分支不設定 OCR 開關。先讀取 `references/open-code-review.md`，再於專案設定的執行環境執行：

```text
node <本 Skill 實際路徑>/scripts/open-code-review.js check --repo <專案實際路徑>
```

- 已安裝且可用：顯示版本與實際路徑；之後 Reviewer B 自動使用，不再詢問是否開啟。
- 尚未安裝：先揭露安裝版本、位置、網路與寫入範圍，再詢問唯一一次安裝確認；肯定回答後才能使用 `install --confirmed`。
- 拒絕、條件不足或安裝失敗：Reviewer B 使用原生 Review，不阻擋其他工作。

取得使用者確認後，可以安裝 OCR；若缺少 Git、Node.js 或 npm，先說明需要安裝的項目、位置與影響，取得使用者確認後一併安裝。不得未經確認自行安裝或升級。

`不得要求 LLM API Key`

## 寫入與完成

沒有設定檔時，以以下內容建立：

```yaml
agent_settings:
  execution_environment:
    preference: auto
  developer:
    cli: auto
  reviewer_a:
    cli: auto
  reviewer_b:
    cli: auto
```

只修改本次選定的區塊，保留其他設定，並將最新完整內容寫回同一個檔案。不得建立 Task 級副本或第二份設定檔。

最後只顯示設定檔實際路徑、本次修改與目前三個角色；新設定適用於之後尚未派發的 Tickets，已經派出的 Ticket 不變。
