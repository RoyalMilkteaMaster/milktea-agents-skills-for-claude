---
name: milktea-skills-to-ticket
description: 將已核准中文規格拆成可獨立派工、驗證與 Review 的 Tickets，固定每票寫入 docs/work/功能名稱/tickets/，並在核准後產生可交給新執行 Task 的共用啟動內容。標示依賴、安全並行、寫入所有權、Agent 角色、驗收條件與三角色共識規則。由 milktea-skills-grill-me 在拆票階段調用，或在使用者要求把規格拆成 Tickets 時使用；不開始實作。
---

# Milktea Skills To Ticket

把核准規格拆成最小、可驗證的垂直切片。不得重新設計需求或架構。

## 前提

- Spec 已核准並可直接開啟。

Spec 缺少時停止，不猜測。

## 儲存位置

- 固定把每張 Ticket 寫成 `docs/work/<功能名稱>/tickets/<NN>-<slug>.md`。
- `<功能名稱>` 必須沿用 Spec 所在工作目錄；Ticket 從 `01` 連續編號，不自行建立另一個工作包。
- 不為了拆票或交接執行 `git add`、Commit、Push、建立 Repository 或修改 Git 設定。

## 流程

1. 讀取 Spec、`docs/planning/requirements.md`、`docs/planning/architecture.md`、專案指令、`CONTEXT.md`、ADR 與程式庫現況。
2. 依使用者價值切成可獨立驗證的 Tickets；避免純分層或模糊雜務票。
3. 標示依賴、阻擋關係、建議順序與可安全平行的工作。
4. 為每張 Ticket 指定執行角色、兩個隔離 Reviewer 與驗收證據；實際後端由執行階段偵測。
5. 逐票寫入固定目錄。
6. 顯示完整拆分、關係與實際路徑，要求使用者核准；核准後把狀態改為「已核准」，不派工、不實作。

## Ticket 格式

```markdown
# 〈Ticket 標題〉

- 狀態：草稿
- Spec：`../spec.md`／遠端連結
- Blocked by：無／Ticket

## 目標

## 使用者價值

## 範圍

## 已確認實作決策

## 驗收條件

- 每條都必須可觀察、可判定。

## 測試與證據

- 測試接縫：
- 必跑指令：
- 必交證據：測試結果、必要的執行輸出與變更摘要。
- 保存位置：本 Ticket 的「執行與 Review 紀錄」。

## 依賴

- Depends on：無／Ticket
- Blocks：無／Ticket

## 並行與所有權

- Dispatch：parallel-safe／serialized
- Exclusive write scope：實際檔案或模組
- Shared resource locks：無／實際資源
- Can run with：無／Ticket

## Agent 分工

- Developer：負責實作、驗證、修正或以證據反駁 Findings
- Reviewer A：使用隔離上下文執行 Review
- Reviewer B：使用另一個隔離上下文執行 Review
- Reviewer 標準：兩者都載入 `$milktea-skills-code-review`，並同時執行 Standards 與 Spec Review
- CLI 與模型：由執行 Task 的 Coordinator 依目前 Task 分工與實際可用能力決定

## 完成規則

- 三個角色已處理所有可重現且有證據的問題。
- 沒有未解決的正確性、可執行性、可讀性、架構或衍生風險。
- 三個角色對完成狀態達成共識。

## 執行與 Review 紀錄
```

## 拆票規則

- 狀態只能是「草稿、已核准、執行中、Review 中、完成、阻擋」之一。
- 每張 Ticket 只交付一個可驗證結果。
- 每張 Ticket 必須有明確驗收條件，不以「完成實作」作為驗收。
- 優先建立能端到端驗證的最小切片，再逐步擴充。
- 不把相依工作偽裝成可平行；平行 Tickets 必須有清楚的檔案或模組所有權。
- `parallel-safe` 只用於依賴已滿足、寫入範圍互不重疊且不共用可變 Runtime、Data、Schema、Migration、Lockfile、GPU 或全專案測試資源的 Tickets；其餘標為 `serialized`。
- Ticket 只引用已核准決策；發現缺口時退回對應階段。

## Review 共識

- Reviewer 的目標是驗證能跑、符合 Spec、可讀、架構清楚且無明顯衍生問題，不是強迫找錯。
- 開發 Agent 不得照單全收 Reviewer 建議；必須重現、查證或以測試驗證。
- 建議不正確時，開發 Agent 應提出證據並維持立場；Reviewer 也必須依證據修正判斷。
- 有合理分歧時繼續交換證據，直到三個角色同意修改、接受現況或明確回報使用者裁決。
- 未達共識前，Ticket 不得標記完成，開發 Agent 不得休息或接下一張 Ticket。

只有單一 CLI 可用時，三個角色仍須彼此隔離並明示缺少跨模型獨立性；不得因此跳過 Review。

## 執行 Task 交接

Tickets 核准後，先以實際資料填完下列模板；不得留下尖括號、改寫文字或產生第二種版本。無論由本 Skill 單獨執行，或經 `$milktea-skills-grill-me` 調用，都必須顯示同一份完整內容：

````markdown
請開啟一個新的 Task，並將以下內容完整貼上。不要在目前的規劃 Task 繼續實作，以免 Planner 與 Implement Coordinator 身分衝突，也避免規劃對話占用實作上下文。

```text
$milktea-skills-implement

這是一個全新的執行 Task。你是 Core Agent；載入 Skill 後立即成為 Implement Coordinator，只負責派工、傳遞證據、協調 Review 與完成關卡，不親自實作或審查。

不要重新執行 grill-me，不要重新訪談、設計架構、產生 Spec 或拆票。以下已核准文件是唯一工作來源。

專案根目錄：<實際路徑>
必讀：AGENTS.md、CONTEXT.md、docs/planning/requirements.md、docs/planning/architecture.md、相關 ADR。
Spec：<已核准的實際路徑>
Tickets（已核准清單）：<已核准的實際路徑>

先驗證環境、可用後端、Ticket 依賴、寫入所有權與共用資源鎖，再建立 Ready Queue，以最大安全並行方式派發所有可同時執行的 Tickets。
```
````

把填妥後的完整交接內容原樣交回 `$milktea-skills-grill-me`。本 Skill 單獨執行時，顯示內容後結束；不建立 Task，也不啟動實作。

## 完成條件

- 每項 Spec 驗收條件至少由一張 Ticket 覆蓋。
- 所有 Tickets 皆有依賴、安全並行、寫入所有權、角色、驗收、測試與證據要求。
- Review 共識規則已納入每張 Ticket 或父規格。
- 執行、Debug、Git 衝突與 Review 證據的保存位置已寫入 Ticket。
- Tickets 已逐票寫入固定目錄。
- Tickets 已由使用者核准且狀態已更新。
- 完整交接內容已填入實際路徑並顯示。
- 尚未開始實作。

核准後把實際 Spec 路徑、Ticket 路徑、執行順序與完整交接內容交回 `$milktea-skills-grill-me`。
