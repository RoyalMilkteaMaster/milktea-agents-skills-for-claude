# Milktea Agents Army for Claude

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

使用 `/milktea-agents-army-claude:milktea-skills-grill-me`。

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
/milktea-agents-army-claude:milktea-skills-grill-me

先跟我確認需求與架構，再產生 Spec、Tickets 並向 implement 執行交接。
```

</details>

### 2. 整理或重構既有專案

使用 `/milktea-agents-army-claude:milktea-skills-brownfield-refactor-planner`。

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
/milktea-agents-army-claude:milktea-skills-brownfield-refactor-planner

先盤點現況、架構、資料流與清理風險，產生 HTML 架構報告讓我判斷。等我決定繼續後，才產生重構 Spec 與 Tickets。現在不要直接修改或刪除程式。
```

</details>

### 3. 先確認想法能不能做

使用 `/milktea-agents-army-claude:milktea-skills-check-feasibility`。

適合在投入開發前，先確認技術能力、外部依賴、成本、時間、風險與成功機率。它只產生評估報告，不會自動開始規劃或實作。

<details>
<summary>可直接複製的用法</summary>

```text
我想做＿＿＿＿，但還不確定是否可行或值得投入。

我的環境與限制：
- ＿＿＿＿
- ＿＿＿＿

請使用：
/milktea-agents-army-claude:milktea-skills-check-feasibility

查證後評估技術可行性、成本、時間、主要風險與最小驗證方式。不要修改程式。
```

</details>

### 4. 更換 Developer 與 Reviewer

使用 `/milktea-agents-army-claude:milktea-skills-set-agent-roles`。

只有想改變預設分工時才需要。它只設定目前 Task 的 Developer、Reviewer A 與 Reviewer B，不會開始派工，也不會影響其他 Task。

請在實際執行 Tickets 的 Task 中使用，並在下一張 Ticket 尚未派發前完成設定。

<details>
<summary>可直接複製的用法</summary>

```text
請使用：
/milktea-agents-army-claude:milktea-skills-set-agent-roles

幫我設定目前 Task 的 Developer、Reviewer A 與 Reviewer B。
```

</details>

## 快速開始

使用者必須先取得 GitHub 存取權。

### Windows(新手推建)

```powershell
git clone https://github.com/RoyalMilkteaMaster/milktea-agents-army-claude.git D:\tools\milktea-agents-army-claude

cd D:\你的專案
claude --plugin-dir D:\tools\milktea-agents-army-claude
```

### Linux／WSL(長期開發者推薦)

```bash
git clone https://github.com/RoyalMilkteaMaster/milktea-agents-army-claude.git ~/tools/milktea-agents-army-claude

cd ~/你的專案
claude --plugin-dir ~/tools/milktea-agents-army-claude
```

`git clone` 只負責下載檔案；`claude --plugin-dir` 才會在該次 Claude Code 對話載入這包 Plugin。

## 全域共用單一 Skill（選用）

這包的主要工作流會互相呼叫其他 Plugin Skills，不適合只把 Grill Me 或 Brownfield Planner 單獨連到全域目錄。

如果只想讓沒有跨 Skill 流程的獨立工具在所有專案可用，例如 `check-feasibility`，可以建立全域 Symlink。

### Linux／WSL

```bash
mkdir -p ~/.claude/skills
ln -s ~/tools/milktea-agents-army-claude/skills/milktea-skills-check-feasibility \
      ~/.claude/skills/milktea-skills-check-feasibility
```

### Windows Command Prompt

```cmd
mkdir "%USERPROFILE%\.claude\skills"
mklink /D "%USERPROFILE%\.claude\skills\milktea-skills-check-feasibility" "D:\tools\milktea-agents-army-claude\skills\milktea-skills-check-feasibility"
```

優點是 Skill 實體仍留在 Git Repository，更新一處即可同步。Windows 建立連結時可能需要啟用 Developer Mode 或使用系統管理員權限。

以全域 Symlink 載入後，使用 `/milktea-skills-check-feasibility`；以 Plugin 載入時，使用 `/milktea-agents-army-claude:milktea-skills-check-feasibility`。
