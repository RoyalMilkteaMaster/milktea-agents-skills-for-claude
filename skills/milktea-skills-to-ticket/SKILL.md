---
name: milktea-skills-to-ticket
description: 將已核准繁體中文規格拆成可獨立派工、驗證與 Review 的 Tickets，為每票選擇 Sonnet 5／high 或 Opus 5／high 及升級路徑，並標示依賴、安全並行、寫入所有權、分層驗收、Agent 角色與雙軸 Review。沿用 Spec 的唯一工作目錄寫入 tickets/，核准後產生新執行 Task 的共用啟動內容；不開始實作。
---

# Milktea 規格拆票

把核准規格拆成最小、可驗證的垂直切片。不得重新設計需求或架構。

## 前提

- Spec 已核准並可直接開啟。

Spec 缺少時停止，不猜測。

## 儲存位置

- 固定把每張 Ticket 寫入 Spec 所在工作目錄的 `tickets/<NN>-<slug>.md`。新工作實際路徑為 `docs/work/<工作識別碼>/tickets/<NN>-<slug>.md`。
- 工作識別碼、顯示名稱與工作目錄必須沿用 Spec；Ticket 從 `01` 連續編號，不自行建立另一個工作包或重新命名。
- 舊 Spec 位於 `docs/work/<功能名稱>/` 時沿用其實際目錄，不搬移、不改名。
- 不為了拆票或交接執行 `git add`、Commit、Push、建立 Repository 或修改 Git 設定。

## 流程

1. 讀取 Spec、`docs/planning/requirements.md`、`docs/planning/architecture.md`、專案指令、`CONTEXT.md`、ADR 與程式庫現況。
2. 依使用者價值切成可獨立驗證的 Tickets；避免純分層或模糊雜務票。
3. 標示依賴、阻擋關係、建議順序與可安全平行的工作。
4. 為每張 Ticket 指定執行角色、一或兩個隔離 Reviewer 與驗收證據；實際 Reviewer 名單由執行 Task 的 `reviewer_mode` 決定，實際後端由執行階段偵測。
5. 逐票寫入固定目錄。
6. 依呼叫模式回傳：Grill-me 上游模式只回傳結構化規劃資料；其他模式維持顯示拆分並要求使用者核准。任何模式都不派工、不實作。

## Grill-me 上游模式

只有 `$milktea-skills-grill-me` 明確以呼叫者識別 `grill-me` 載入時使用：

1. 逐票寫入狀態為「草稿」的 Ticket。
2. 不在聊天框顯示完整 Ticket 長文、不詢問核准、不產生 HTML。
3. 把下列結構化資料交回 Grill-me：
   - 原始需求到 Ticket 的覆蓋。
   - Ticket 目標、依賴、阻擋、順序與可安全並行批次。
   - 寫入所有權、共用資源鎖與衝突原因。
   - Developer 配置摘要、Reviewer 分工、測試與驗收。
   - 風險、回復方式、Spec 與全部 Ticket 實際路徑。
   - 工作識別碼、繁體中文顯示名稱與實際工作目錄。
4. Grill-me 使用上述資料產生並顯示實作藍圖 HTML。
5. 只有 Grill-me 回報使用者已核准 HTML 後，才把全部 Tickets 更新為「已核准」，填妥唯一交接內容並交回 Grill-me。

不得讓 To Ticket 自行呼叫 HTML 報告技能，避免 Brownfield Planner 或單獨使用本技能時意外多產生一份報告。

## Developer 模型路由

每張 Ticket 都必須指定初始 Developer 模型、`model_reasoning_effort`、理由與升級路徑。不得使用 Haiku；自動路由只使用下列兩種起點：

- 只有在工作明確、局部、低風險，已有相鄰實作可沿用及秒級驗證，且不涉及跨模組設計、Schema、Migration、權限、安全、資料風險或公開介面時，使用 `claude-sonnet-5`／`high`。典型工作是文件、註解、固定格式轉換、局部文案或已有模式的小修改。
- 其他工作一律使用 `claude-opus-5`／`high`。不確定是否簡單時也使用此配置。

固定升級路徑為 `claude-opus-5`／`xhigh`。`max` 只能由使用者針對該 Ticket 明確核准；不得自動選擇 `low`、`medium` 或 `max`。Reviewer 的模型仍由執行 Task 的角色設定獨立控制。

## Ticket 格式

```markdown
# 〈Ticket 標題〉

- 狀態：草稿
- Spec：`../spec.md`／遠端連結
- Blocked by：無／Ticket

## 目標

## 對應原始需求

- 逐項保留核准需求的原文或穩定識別，不用模糊摘要取代。

## 使用者價值

## 範圍

## 已確認實作決策

## 驗收條件

- 每條都必須可觀察、可判定。

## 測試與證據

- 測試接縫：
- 迭代期快速檢查：秒級、與目前修改直接相關的測試、型別、lint 或 validator。
- Ready for Review 完整驗收：只在首次準備 Review 前執行一次的指令。
- Findings 修正後：由 Coordinator 依影響範圍指定要重跑的指令，不預設重跑全套。
- 必交證據：Ready for Review 的完整驗收結果、退出碼、必要執行輸出與變更摘要。
- 保存位置：本 Ticket 的「執行與 Review 紀錄」。

## 前端實際操作驗收

- 適用性：適用／不適用
- 判定依據：對應哪項使用者介面需求；不適用時寫明理由
- 操作環境與實際網址：執行階段填寫
- 使用的原生瀏覽器工具：執行階段填寫
- 操作步驟與預期結果：適用時逐項列出
- 操作結果與證據：執行階段填寫；通過前不得標記完成

## 依賴

- Depends on：無／Ticket
- Blocks：無／Ticket

## 並行與所有權

- Dispatch：parallel-safe／serialized
- Exclusive write scope：實際檔案或模組
- Shared resource locks：無／實際資源
- Can run with：無／Ticket

## 初始執行配置

- Developer model：`claude-sonnet-5`／`claude-opus-5`
- model_reasoning_effort：`high`
- 路由理由：符合的具體條件
- 升級路徑：`claude-opus-5`／`xhigh`；`max` 需使用者明確核准
- Research 證據：無／實際 Markdown 路徑

## Agent 分工

- Developer：負責實作、驗證、修正或以證據反駁 Findings
- Reviewer A：`both` 時只執行 Spec Review；`a_only` 時執行 Spec 與 Standards
- Reviewer B：`both` 時只執行 Standards Review；`b_only` 時執行 Spec 與 Standards
- Reviewer 模式：由執行 Task 最新 `settings_update: reviewers` 決定；預設 `both`，Ticket 不自行固定或搜尋設定
- Reviewer 標準：每位啟用 Reviewer 都載入 `$milktea-skills-code-review`，只執行 Coordinator 指定的 `review_axis`
- CLI 與模型：Developer 初始模型與推理強度以上述配置為準；Reviewer 由執行 Task 的角色設定獨立決定

## 完成規則

- Developer 與各 Finding 的原 Reviewer 已處理所有可重現且有證據的問題。
- 沒有未解決的阻擋或重要正確性、可執行性、可讀性、架構或衍生風險。
- Developer 與各 Finding Owner 對關閉或撤回事由達成共識。

## 執行與 Review 紀錄

## 阻擋與裁決紀錄

只有真正需要方向裁決時才追加下列欄位；一般 Bug 修正、測試失敗、Review Finding 或同一方案內的迭代不得寫成使用者阻擋：

- 原始需求：
- 目前理解：
- 實際卡住的原因：
- 已嘗試方案與證據：
- 為什麼不能繼續盲修：
- 簡單可行方案：
- Agent 建議：
- 需要使用者決定：
```

## 拆票規則

- 狀態只能是「草稿、已核准、執行中、Review 中、修正中、完成、阻擋」之一。
- 每張 Ticket 只交付一個可驗證結果。
- 每張 Ticket 必須有明確驗收條件，不以「完成實作」作為驗收。
- 優先建立能端到端驗證的最小切片，再逐步擴充。
- 不把相依工作偽裝成可平行；平行 Tickets 必須有清楚的檔案或模組所有權。
- `parallel-safe` 只用於依賴已滿足、寫入範圍互不重疊且不共用可變 Runtime、Data、Schema、Migration、Lockfile、GPU 或全專案測試資源的 Tickets；其餘標為 `serialized`。
- Ticket 只引用已核准決策；發現缺口時退回對應階段。

## Review 共識

- Reviewer 的目標是驗證能跑、符合 Spec、可讀、架構清楚且無明顯衍生問題，不是強迫找錯。
- `both` 模式由 Reviewer A 審 Spec、Reviewer B 審 Standards；單 Reviewer 模式才由該 Reviewer 覆蓋兩軸，避免重複審查。
- 開發 Agent 不得照單全收 Reviewer 建議；必須重現、查證或以測試驗證。
- 每個 Finding 由提出它的原 Reviewer 擁有；Developer 修正或反駁後，只交回該 Owner 定向複驗。Coordinator 不重排嚴重度、不合併成裁決，也不用另一個模型投票。
- 建議不正確時，Developer 應提出證據並維持立場；Finding Owner 也必須依證據關閉、降級或撤回。
- 證據依序採信：可重現失敗與安全／資料風險、核准 Spec 與驗收條件、ADR／正式標準／公開契約、測試與型別證據、經驗法則、個人偏好。
- 有合理分歧時使用最小辨別測試、第一手來源或 `$milktea-skills-research` 繼續查證，直到雙方同意。只有缺少產品價值、公開契約、不可逆資料處置或安全接受程度等關鍵決策時才交給使用者。
- 未達共識前，Ticket 不得標記完成，開發 Agent 不得休息或接下一張 Ticket。

只有單一 CLI 可用時，所有啟用角色仍須彼此隔離並明示缺少跨模型獨立性；不得因此跳過 Review。

## 執行 Task 交接

Tickets 核准後，先以實際資料填完下列模板；不得留下尖括號、改寫文字或產生第二種版本。本 Skill 單獨執行時直接顯示；經 `$milktea-skills-grill-me` 調用時，只把同一份內容交回 Grill-me，由 Grill-me 在實作藍圖核准後顯示：

````markdown
請開啟一個新的 Task，並將以下內容完整貼上。不要在目前的規劃 Task 繼續實作，以免 Planner 與 Implement Coordinator 身分衝突，也避免規劃對話占用實作上下文。

```text
$milktea-skills-implement

這是一個全新的執行 Task。你是 Core Agent；載入 Skill 後立即成為 Implement Coordinator，只負責派工、傳遞證據、協調 Review 與完成關卡，不親自實作或審查。

不要重新執行 grill-me，不要重新訪談、設計架構、產生 Spec 或拆票。以下已核准文件是唯一工作來源。

專案根目錄：<實際路徑>
工作識別碼：<實際工作識別碼>
顯示名稱：<實際繁體中文顯示名稱>
工作目錄：<實際工作目錄>
必讀：AGENTS.md、CONTEXT.md、docs/planning/requirements.md、docs/planning/architecture.md、相關 ADR。
Spec：<已核准的實際路徑>
Tickets（已核准清單）：<已核准的實際路徑>

先驗證環境、可用後端、Ticket 依賴、寫入所有權與共用資源鎖，再建立 Ready Queue，以最大安全並行方式派發所有可同時執行的 Tickets。
```
````

把填妥後的完整交接內容原樣交回 `$milktea-skills-grill-me`。Grill-me 上游模式不得在 HTML 核准前建立交接。本 Skill 單獨執行時，顯示內容後結束；不建立 Task，也不啟動實作。

## 完成條件

- 每項 Spec 驗收條件至少由一張 Ticket 覆蓋。
- 所有 Tickets 皆有依賴、安全並行、寫入所有權、角色、驗收、測試與證據要求。
- Review 共識規則已納入每張 Ticket 或父規格。
- 執行、Debug、Git 衝突與 Review 證據的保存位置已寫入 Ticket。
- 工作識別碼、顯示名稱與實際工作目錄已原樣交接。
- Tickets 已逐票寫入固定目錄。
- Grill-me 上游模式：已先回傳結構化規劃資料，並只在 Grill-me 回報 HTML 已核准後更新 Ticket 狀態。
- 其他模式：Tickets 已由使用者核准且狀態已更新。
- 完整交接內容已填入實際路徑；Grill-me 上游模式已交回 Grill-me，其他模式已直接顯示。
- 尚未開始實作。

Grill-me 上游模式核准後，把實際 Spec 路徑、Ticket 路徑、執行順序與完整交接內容交回 `$milktea-skills-grill-me`；其他模式依本 Skill 的直接交付規則結束。
