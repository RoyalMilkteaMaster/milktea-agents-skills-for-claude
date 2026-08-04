# Milktea Agents Skills for Claude

![Milktea Agents Skills](assets/milktea-agents-skills.png)

## 專案簡介

這是皇家奶茶大師給 Claude Code 使用的 AI 開發協作 Skills。

你會用到的技能只有四個。
平常你只需要依照你的需求使用技能或是輸入範本。  
後續需要的規劃、實作、測試與 Review Skills 都會由流程接手。


## 四種milktea技能該怎麼用?

#先選你現在要做的事

```text
你現在想做什麼？
│
├─ 想要開始新專案，或替專案新增功能
│  └─ grill-me
│
├─ 覺得自己專案的架構太過混亂了，想要清整專案或重構部分內容
│  └─ brownfield-refactor-planner
│
├─ 想要一份自己計劃的可行性報告、根據成本、開發時間、Agents訂閱方案、設備規格...等
│  └─ check-feasibility
│
└─ 想更換 預設 的 臨時寫手agents 或 臨時複審agents 的 模型規格
   └─ set-agent-roles
```

## 奶茶流怎麼運作(核心思路)

### 新專案或新增功能(grill-me)

```text
想法
  ↓
Grill Me
  ↓
確認需求 → 確認架構 → 寫 Spec → 拆 Tickets
  ↓
產生執行交接文字
  ↓
貼到新的 Claude Code 對話
  ↓
Implement → Developer 實作 → Reviewer A + Reviewer B 獨立審查
```

### 整理既有專案(brownfield-refactor-planner)

```text
混亂或需要重構的舊專案
  ↓
Brownfield Refactor Planner
  ↓
內部呼叫 Architecture Auditor
  ↓
HTML 架構報告
  ├─ 只需要報告 → 到此結束
  └─ 決定重構
       ↓
     確認目標架構 → 重構 Spec → Tickets
       ↓
     產生執行交接文字
       ↓
     貼到新的 Claude Code 對話執行重構
```

## 具體操作範本(可以直接複製貼上)

### 1. 開始新專案或新增功能(grill-me)

使用 `/milktea-agents-skills-for-claude:milktea-skills-grill-me`。

它會依序跟你確認需求與架構，再寫成 Spec、拆成 Tickets。它只負責規劃，不會在同一個對話直接寫程式。

另外，如果舊專案已經明顯混亂，先使用 Brownfield Planner，不要一邊整理舊架構、一邊規劃新功能。

<details>
<summary>可直接複製的用法</summary>

```text
我要開發一個＿＿＿＿專案／新增＿＿＿＿功能。

目前已知需求：
- ＿＿＿＿
- ＿＿＿＿

請使用：
/milktea-agents-skills-for-claude:milktea-skills-grill-me

先跟我確認需求與架構，再產生 Spec、Tickets 並向 implement 執行交接。
```

</details>

### 2. 整理或重構既有專案

使用 `/milktea-agents-skills-for-claude:milktea-skills-brownfield-refactor-planner`。

適合情境:當你面對架構混亂、重複程式增加、舊功能殘留，你想進行清整，或你還不確定這個專案是否值得重構。

它會先呼叫內部的架構健檢 Skill，用唯讀方式盤點現況並產生 HTML 報告。你可以拿到報告就結束；也可以選擇請Agents繼續根據報告，產生重構 Spec 與 Tickets。

<details>
<summary>可直接複製的用法</summary>

```text
我的專案已經開發一段時間，現在有以下問題：
- ＿＿＿＿
- ＿＿＿＿

必須保留的功能：
- ＿＿＿＿

請使用：
/milktea-agents-skills-for-claude:milktea-skills-brownfield-refactor-planner

先盤點現況、架構、資料流與清理風險，產生 HTML 架構報告讓我判斷。等我決定繼續後，才產生重構 Spec 與 Tickets。現在不要直接修改或刪除程式。
```

</details>

### 3. 先確認想法能不能做

使用 `/milktea-agents-skills-for-claude:milktea-skills-check-feasibility`。

適合在投入開發前，先確認技術能力、外部依賴、成本、時間、風險與成功機率。它只產生評估報告，不會自動開始規劃或實作。

<details>
<summary>可直接複製的用法</summary>

```text
我想做＿＿＿＿，但還不確定是否可行或值得投入。

我的環境與限制：
- ＿＿＿＿
- ＿＿＿＿

請使用：
/milktea-agents-skills-for-claude:milktea-skills-check-feasibility

查證後評估技術可行性、成本、時間、主要風險與最小驗證方式。不要修改程式。
```

</details>

### 4. 快速調整 Task 設定

使用 `/milktea-agents-skills-for-claude:milktea-skills-set-agent-roles`。

只有想改變目前 Task 的環境、角色或 Reviewer B OCR 時才需要。它不會開始派工，也不會影響其他 Task。

請在實際執行 Tickets 的 Task 中使用，並在下一張 Ticket 尚未派發前完成設定。

進入後只問這次要調整哪一項：

1. 開發環境
2. 角色設定
3. Reviewer B OCR

只執行選中的分支，完成後立即結束；不會接著追問另外兩項。使用者若已直接說「改成 WSL」、「Reviewer A 改成 Codex low」或「關閉 OCR」，會跳過選單。角色設定以一份批次表單收集，不會依序詢問三個角色；未填的角色保持原設定。

選擇「開發環境」後才會提供 Windows PowerShell、WSL、其他已安裝 CLI 的環境三個子選項。WSL 會讀取實際 distribution，不假設一定是 Ubuntu；其他環境才由 AI 唯讀尋找 cmd、Git Bash、Container 等已可用環境。偵測不會替你安裝或登入工具。選定後，Developer、兩位 Reviewer、Git、測試與可選 OCR 都使用同一個環境。

<details>
<summary>可直接複製的用法</summary>

```text
請使用：
/milktea-agents-skills-for-claude:milktea-skills-set-agent-roles

讓我選這次只調整開發環境、角色設定或 Reviewer B OCR；完成後立即結束。
```

</details>


### Reviewer B 可選使用 Open Code Review

[Alibaba Open Code Review](https://github.com/alibaba/open-code-review) 是外部開源 CLI，**不是圖片文字辨識 OCR**。Milktea 不會把它包進專案，也不會讓所有 Reviewer 強制使用：

- 預設關閉；Reviewer A 永遠維持原生 Review。
- 只有 Reviewer B 可選擇 Delegation Mode，讓 OCR 先整理 Git 變更檔案與 Review 規則，再由原本的 Codex／Claude 模型判斷。
- Delegation Mode 不使用 OCR 自己的 LLM，因此不需要另外提供 OCR API Key。
- 一般 implement 與 brownfield refactor implement 都支援；小問題不想增加規則內容時保持關閉即可。
- Windows 與 WSL 分開安裝；Windows CLI 在目前 npm 全域目錄，Linux／WSL CLI 在使用者的 `~/.local`，執行狀態在 `~/.opencodereview/`，不會因安裝而進入 Git 專案。

只有選擇「Reviewer B OCR」時才會進入兩層確認：

1. 是否為 Reviewer B 開啟 OCR，並先解釋功能、資料邊界與 API Key 行為。
2. 只有已開啟但目前環境沒有可用 `ocr` 時，才再詢問是否安裝；同意後才執行固定版本的 npm 全域安裝並驗證。

安裝前會檢查 OCR 官方需求 Git ≥ 2.41、Node.js ≥ 18 與 npm。Milktea 不會擅自安裝或升級這三個系統工具。拒絕安裝、條件不足或 OCR 執行失敗時，Reviewer B 會安全回退到原生 Review。

<details>
<summary>可直接複製的測試用法</summary>

```text
請使用：
/milktea-agents-skills-for-claude:milktea-skills-set-agent-roles

只調整 Reviewer B OCR。先說明功能與資料邊界；如果本機沒有 OCR，請先說明安裝會寫到哪裡，再經過第二次確認才安裝。完成後立即結束。
```

</details>


## 快速開始

請根據您習慣的開發習慣，選擇實際要使用 Claude Code 的環境，並在同一個環境完成以下所有步驟。

如果 `claude auth status` 已顯示登入成功，可以略過登入命令。

### Windows（新手推薦）

在 PowerShell 執行：

```powershell
claude auth login
claude auth status

claude plugin marketplace add RoyalMilkteaMaster/milktea-agents-skills-for-claude
claude plugin install milktea-agents-skills-for-claude@milktea-agents-skills-for-claude --scope user
claude plugin list
```

### Linux／WSL（長期開發者推薦）

在 Linux／WSL Terminal 執行：

```bash
claude auth login
claude auth status

claude plugin marketplace add RoyalMilkteaMaster/milktea-agents-skills-for-claude
claude plugin install milktea-agents-skills-for-claude@milktea-agents-skills-for-claude --scope user
claude plugin list
```

Windows 與 WSL 是兩個獨立環境。在 Windows 完成的 Claude Code 登入與 Plugin 安裝，不會自動套用到 WSL；反之亦然。

Plugin 安裝完成後，請重新開啟 Claude Code。Milktea Skills 將套用至該使用者在此環境中的所有專案。


完成後，即可在 Claude Code 對話中使用 Plugin Skill：

-用法:  

```text
/milktea-agents-skills-for-claude:milktea-skills-grill-me
```

Plugin 以使用者範圍安裝後，即可在該環境的所有專案使用，並完整保留工作流需要的相依 Skills。


## 多 Agent 協作（推薦）

Milktea Skills 支援 多方 Agent 協作。  
雖然只使用 Claude Code 也能執行；不過若可以同時使用不同的 AI CLI，通常能獲得更好的交叉驗證，降低單一模型的審查盲點。

建議先把要協作的 AI CLI 安裝並登入在同一個 **Windows PowerShell** 或 **Linux／WSL** 環境。`/milktea-agents-skills-for-claude:milktea-skills-set-agent-roles` 會把三個角色固定在同一個選定環境；Windows 與 WSL 的登入及安裝狀態彼此獨立，不能把另一邊已登入誤當成目前環境可用。

若已擁有 [Codex CLI](https://learn.chatgpt.com/docs/codex/cli) 與 [Antigravity CLI](https://antigravity.google/docs/cli-getting-started) 帳號，請在重開一個與剛剛相同環境的 Terminal 執行：

```shell
# Codex
codex login
codex login status
```


```
# Antigravity CLI
agy
```

Antigravity CLI 沒有另外的 `auth login` 指令。第一次執行 `agy` 時會開啟 Google 登入流程；完成後可在 Antigravity CLI 輸入 `/exit` 回到 Terminal。

如果電腦上有兩種以上的 AI CLI，建議全部登入。工作流只會使用目前環境中實際可用的 CLI。
