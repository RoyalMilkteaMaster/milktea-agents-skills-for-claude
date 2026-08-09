---
name: milktea-skills-to-ticket
description: 將已核准繁體中文規格拆成可獨立派工、驗證與 Review 的 Tickets，每票引用 Spec 的穩定 R-xxx 原始需求識別碼，記錄 Claude Sonnet 5／high 或 Opus 5／high 的相容預設偏好與可用後端回退規則，並標示依賴、安全並行、寫入所有權、分層驗收、Agent 角色與雙軸 Review。沿用 Spec 的唯一工作目錄寫入 tickets/；Tickets 核准且已有同一工作的已核准 HTML URL 與絕對路徑時，才產生可手動貼到新執行 Task 的唯一啟動文字。不開始實作。
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
6. 依呼叫者識別回傳：`grill-me` 與 `brownfield-planner` 使用各自的上游協定；沒有呼叫者識別時顯示拆分並要求使用者核准。任何模式都不派工、不實作。

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

第二次呼叫必須沿用相同工作識別碼、Ticket 路徑與內容，並由 Grill-me 同時傳入已核准實作藍圖的可開啟 HTML URL 與 HTML 絕對路徑。任一值缺少、仍是占位符或指向不同報告時停止，不得更新 Ticket 狀態。

## Brownfield Planner 上游模式

只有 `$milktea-skills-brownfield-refactor-planner` 明確以呼叫者識別 `brownfield-planner` 載入時使用：

1. 只依已核准的 Brownfield Spec 拆票，逐票寫入狀態為「草稿」的 Ticket；不得重新加入已拒絕候選或擴大重構範圍。
2. 每張 Ticket 除了一般驗收資料外，還必須依下方格式加入「原有功能確認」，供修改前與修改後使用同一方法比較。
3. 不自行呼叫 HTML 報告技能；把完整 Tickets、需求覆蓋、依賴、原有功能確認、角色、Review、驗收、工作資料與實際路徑交回 Brownfield Planner。
4. Brownfield Planner 顯示同一批 Tickets 並取得使用者核准後，必須以相同呼叫者識別再次呼叫本技能，傳入核准結果、已核准架構報告的可開啟 HTML URL 與 HTML 絕對路徑。
5. 第二次呼叫確認工作識別碼、路徑與內容未被換成其他版本後，才把全部 Tickets 更新為「已核准」，把核准後的實際 Ticket 路徑與執行順序交回 Brownfield Planner。Brownfield Implement 的唯一交接模板由 Brownfield Planner 維護，本技能不得另產生一般 Implement 交接文字。

不得使用未定義的「Planner 上游模式」名稱；Brownfield 流程唯一合法識別是 `brownfield-planner`。

不得讓 To Ticket 自行呼叫 HTML 報告技能，避免 Brownfield Planner 或單獨使用本技能時意外多產生一份報告。

## Developer 模型路由

每張 Ticket 都必須記錄 Developer 的相容預設模型、`model_reasoning_effort`、理由與升級路徑。下列 Claude 配置只在 Developer 沒有使用者明確設定時作為預設偏好，不是不可覆寫的硬鎖：

- 只有在工作明確、局部、低風險，已有相鄰實作可沿用及秒級驗證，且不涉及跨模組設計、Schema、Migration、權限、安全、資料風險或公開介面時，使用 `claude-sonnet-5`／`high`。典型工作是文件、註解、固定格式轉換、局部文案或已有模式的小修改。
- 其他工作一律使用 `claude-opus-5`／`high`。不確定是否簡單時也使用此配置。

Claude 偏好的升級路徑為 `claude-opus-5`／`xhigh`；實際 Developer 使用其他後端時，由 Implement 依該後端已驗證可用的設定處理。`max` 只能由使用者針對該 Ticket 明確核准；不得自動選擇 `low`、`medium` 或 `max`。Reviewer 的模型仍由執行 Task 的角色設定獨立控制。

執行階段依下列優先序決定實際配置：

1. 使用者透過 `$milktea-skills-set-agent-roles` 為 Developer 明確保存的最新設定優先，適用於尚未派出的 Tickets；只設定 Reviewer 不會停用 Developer 的 Ticket 偏好。
2. Developer 沒有明確設定且 Claude 後端可用時，使用 Ticket 記錄的 Claude 預設偏好。
3. Developer 沒有明確設定且偏好後端不可用時，不得因 Ticket 寫有 Claude 偏好而阻擋；回退到目前唯一可用平台的後端預設模型與推理強度，並在 Ticket 的執行紀錄如實記下實際配置與回退原因。
4. 只有 Claude 或只有 Codex 時，仍建立彼此隔離的 Developer 與 Reviewer 角色；可使用同一後端，但必須分開派發、分開保存證據，並明示缺少跨模型獨立性。

Core Agent 是 Claude 或 Codex 都不改變上述優先序。每個沒有使用者明確設定的角色都維持 Claude Developer、Codex Reviewer 的預設方向；只有該角色的實際後端不可用時才自動回退。

## Ticket 格式

```markdown
# 〈Ticket 標題〉

- 狀態：草稿
- Spec：`../spec.md`／遠端連結
- Blocked by：無／Ticket

## 目標

## 對應原始需求

- R-001：逐項引用 Spec 中相同識別碼與原始需求原文，不用模糊摘要取代。

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
- 操作結果：執行階段填寫
- 操作證據：執行階段填寫

## 原有功能確認

- 共用驗證方法：Brownfield 規劃階段填寫
- 修改前基準：Brownfield 規劃階段填寫
- 修改後結果：執行階段填寫
- 原有功能驗收：執行階段填寫
- 驗收證據：執行階段填寫

## 依賴

- Depends on：無／Ticket
- Blocks：無／Ticket

## 並行與所有權

- Dispatch：parallel-safe／serialized
- Exclusive write scope：實際檔案或模組
- Shared resource locks：無／實際資源
- Can run with：無／Ticket

## 初始執行配置

- Developer model：`claude-sonnet-5`／`claude-opus-5`（相容預設偏好）
- model_reasoning_effort：`high`（相容預設偏好）
- 路由理由：符合的具體條件
- 升級路徑：Claude 偏好為 `claude-opus-5`／`xhigh`；實際使用其他後端時由 Implement 採用該後端已驗證可用的升級設定；`max` 需使用者明確核准
- 執行時覆寫：最新使用者角色設定優先；偏好後端不可用時回退到唯一可用平台並留下紀錄
- Research 證據：無／實際 Markdown 路徑

## Agent 分工

- Developer：負責實作、驗證、修正或以證據反駁 Findings
- Reviewer A：`both` 時只執行 Spec Review；`a_only` 時執行 Spec 與 Standards
- Reviewer B：`both` 時只執行 Standards Review；`b_only` 時執行 Spec 與 Standards
- Reviewer 啟用規則：由執行 Task 最新 `settings_update: reviewers` 決定；預設 `both`，Ticket 不自行固定或搜尋設定
- Reviewer 標準：每位啟用 Reviewer 都載入 `$milktea-skills-code-review`，只執行 Coordinator 指定的 `review_axis`
- CLI 與模型：Developer 的上述配置只是相容預設偏好；實際配置依最新使用者角色設定與後端可用性決定，Reviewer 仍獨立決定

## 完成規則

- Developer 與各 Finding 的原 Reviewer 已處理所有可重現且有證據的問題。
- 沒有未解決的阻擋或重要正確性、可執行性、可讀性、架構或衍生風險。
- Developer 與各 Finding Owner 對關閉或撤回事由達成共識。

## 執行與 Review 紀錄

- Developer 結論：執行階段填寫
- Reviewer 模式：執行階段填寫
- Reviewer A 結論：執行階段填寫
- Reviewer B 結論：執行階段填寫
- 未關閉阻擋或重要 Findings：執行階段填寫
- Ticket 最終驗收：執行階段填寫

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
- Spec 的每一個 `R-xxx` 至少由一張 Ticket 引用；Ticket 的「對應原始需求」只能使用 Spec 已存在的識別碼，並保留相同原文。不得重新編號、重複建立同義識別碼或只寫無法核對的摘要。
- 每張 Ticket 只交付一個可驗證結果。
- 每張 Ticket 必須有明確驗收條件，不以「完成實作」作為驗收。
- 優先建立能端到端驗證的最小切片，再逐步擴充。
- 不把相依工作偽裝成可平行；平行 Tickets 必須有清楚的檔案或模組所有權。
- `parallel-safe` 只用於依賴已滿足、寫入範圍互不重疊且不共用可變 Runtime、Data、Schema、Migration、Lockfile、GPU 或全專案測試資源的 Tickets；其餘標為 `serialized`。
- Ticket 只引用已核准決策；發現缺口時退回對應階段。
- `## 原有功能確認` 只在 `brownfield-planner` 模式加入；一般功能 Ticket 省略整個區段。Brownfield 規劃階段必須把「共用驗證方法」與實際「修改前基準」填入同一張 Ticket，不能把方法留到執行階段決定。

## 機器欄位更新規則

- Ticket 模板中需要由 Implement 原地更新的固定機器欄位，在同一張 Ticket 只能出現一次。這項結案閘門適用於狀態、前端實際操作、原有功能確認，以及「執行與 Review 紀錄」中的固定結論欄位。
- `## 初始執行配置` 是拆票時的規劃偏好：Grill 核准前確認它存在且完整；Implement 依最新角色設定與實際可用平台決定真正配置，另存執行證據。它不屬於結案機器欄位，也不因實際配置不同而覆寫規劃偏好。
- 規劃、執行、Review 或修正完成時，直接在原欄位那一行替換冒號後的值；不得在文件尾端、其他區段或同一區段追加第二個同名欄位。
- 只有日期、命令、輸出、Finding 對話、修正說明等敘述紀錄可以追加。追加紀錄不得重用任何固定機器欄位名稱，也不得取代固定欄位的最終值。
- Coordinator 在把 Ticket 標記為完成前，必須確認上述結案機器欄位各自恰好一次；缺少或重複都視為未完成。

## 可機器驗證的完成值

- 前端實際操作驗收為「適用」時，完成前的「操作結果」必須精確寫成「通過」，「操作證據」必須填入實際操作證據；「未通過」或只含「通過」字樣的自由文字都不算通過。
- `Developer 結論` 完成值只能是「通過」。
- `Reviewer 模式` 完成值只能是 `both`、`a_only` 或 `b_only`。
- 啟用的 Reviewer 結論只能是「通過」；只有未啟用的 Reviewer 才能填「不適用」。`both` 必須 A、B 都通過；`a_only` 必須 A 通過、B 不適用；`b_only` 必須 A 不適用、B 通過。
- `未關閉阻擋或重要 Findings` 完成值必須是 `0`。
- `Ticket 最終驗收` 只有在上述欄位與該票全部驗收均通過後，才能精確寫成「通過」。
- Brownfield Ticket 的「共用驗證方法」是修改前後唯一可使用的判定方法。規劃階段原地填入方法與「修改前基準」；執行後原地替換「修改後結果」、「原有功能驗收」與「驗收證據」的占位值，不得改用另一方法，也不得追加重複機器欄位。
- Brownfield Ticket 完成前，`原有功能驗收` 必須精確寫成「通過」，`修改後結果` 與 `驗收證據` 必須填入以同一「共用驗證方法」取得的實際結果與證據。
- 只有單一 CLI 或模型後端可用時，仍建立彼此隔離的 Developer 與 Reviewer 角色並如實記錄缺少跨模型獨立性；不得把已啟用 Reviewer 標成「不適用」。

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

Tickets 核准且已有同一工作的已核准 HTML URL 與 HTML 絕對路徑後，先以實際資料填完下列模板；不得留下尖括號、改寫文字或產生第二種版本。本 Skill 單獨執行時只有在呼叫者已提供並驗證這兩個 HTML 值時才直接顯示；經 `$milktea-skills-grill-me` 調用時，只把同一份內容交回 Grill-me，由 Grill-me 在實作藍圖核准後顯示。`brownfield-planner` 不使用本模板，由 Brownfield Planner 維護並顯示唯一的 Brownfield Implement 交接文字：

```text
已核准 HTML URL：<可開啟的實際 HTML URL>
已核准 HTML 絕對路徑：<實際 HTML 絕對路徑>

請將本段文字完整複製到新的獨立 Task。不要在目前的規劃 Task 繼續實作，以免 Planner 與 Implement Coordinator 身分衝突，也避免規劃對話占用實作上下文。

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

把填妥後的完整交接內容原樣交回 Grill-me。Grill-me 上游模式不得在 HTML 與 Tickets 核准前建立交接；前兩行必須分別填入同一份已核准報告的可開啟 HTML URL 與 HTML 絕對路徑。沒有報告伺服器時，URL 使用由該絕對路徑轉成並已驗證可開啟的 `file:///` URL。本 Skill 單獨執行但沒有實際已核准 HTML URL 與 HTML 絕對路徑時，只交付已核准 Tickets，不得產生可執行交接文字；明確說明必須先由規劃流程產生並核准 HTML，不能用「不適用」或占位文字代替。Brownfield 模式只回傳核准後的 Ticket 資料，不產生本段文字。

## 完成條件

- 每項 Spec 原始需求 `R-xxx` 與驗收條件至少由一張 Ticket 覆蓋。
- 所有 Tickets 皆有依賴、安全並行、寫入所有權、角色、驗收、測試與證據要求。
- Review 共識規則已納入每張 Ticket 或父規格。
- 執行、Debug、Git 衝突與 Review 證據的保存位置已寫入 Ticket。
- 工作識別碼、顯示名稱與實際工作目錄已原樣交接。
- Tickets 已逐票寫入固定目錄。
- Grill-me 上游模式：已先回傳結構化規劃資料，並只在 Grill-me 回報 HTML 已核准後更新 Ticket 狀態。
- Brownfield Planner 上游模式：已先回傳完整草稿 Tickets，並只在 Brownfield Planner 回報架構報告與 Tickets 都已核准後更新 Ticket 狀態。
- 其他模式：Tickets 已由使用者核准且狀態已更新。
- 交接所需資料已填入實際路徑；Grill-me 上游模式已交回 Grill-me；單獨使用模式只有在已提供並驗證同一工作的 HTML URL 與 HTML 絕對路徑時才顯示完整交接，否則只顯示已核准 Tickets；Brownfield Planner 上游模式已交回產生 Brownfield 唯一交接所需的核准 Ticket 資料。
- 尚未開始實作。

Grill-me 上游模式核准後，把實際 Spec 路徑、Ticket 路徑、執行順序與完整交接內容交回 `$milktea-skills-grill-me`。Brownfield Planner 上游模式核准後，只把實際 Spec 路徑、Ticket 路徑與執行順序交回 `$milktea-skills-brownfield-refactor-planner`。其他模式依本 Skill 的直接交付規則結束。
