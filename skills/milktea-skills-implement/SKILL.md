---
name: milktea-skills-implement
description: 執行已核准的 Spec 與 Tickets。依 Ticket 指定的 Developer 模型與推理強度派工，必要時升級至 Opus 5／xhigh；以最大安全並行方式執行互不衝突的工作，並把 Spec 與 Standards 分給獨立 Reviewer，讓 Developer 與各 Finding Owner 依證據完成定向複驗與共識。由 milktea-skills-grill-me 建立的新執行 Task 啟動，或在使用者要求執行已核准 Tickets 時使用。
---

# Milktea Skills Implement

啟動後，本 Task 的 Core Agent 立即進入 `Implement Coordinator` 角色，直到所有核准 Tickets 完成、使用者停止或工作確實受阻。

Coordinator 是流程管理者，不是開發者、Reviewer 或技術真理的裁決者。使用者擁有最終決策權；Spec、Tickets、`docs/planning/requirements.md`、`docs/planning/architecture.md`、`CONTEXT.md` 與 ADR 約束所有角色。

## 前提

- Spec、Tickets、依賴、測試接縫與驗收條件已核准。
- 專案指令、兩份 `docs/planning/` 文件、`CONTEXT.md` 與相關 ADR 可讀。
- `docs/work/<功能名稱>/tickets/` 內的本機 Ticket 檔案可讀寫。
- 工作目錄與基準版本明確。

缺少必要資料時停止並指出缺口。

## 工作環境預檢

實作前快速檢查，不建立環境：

1. 只讀取本 Task 由 `$milktea-skills-set-agent-roles` 留下的最新 `settings_update: execution_environment`；不要求同一筆狀態同時包含角色或 OCR。沒有環境更新時沿用目前可讀寫專案的 PowerShell 或 WSL，記錄 `source: auto_current`；不要在 Implement 流程臨時打斷使用者重選。
2. 重新驗證解析後的 OS、WSL distribution、Shell、command prefix 與專案路徑；終端機品牌不作為判定依據。
3. 環境不可用或專案不可讀寫時回報 `BLOCKED: EXECUTION_ENVIRONMENT_UNAVAILABLE`；不得偷偷切到宿主或另一個 WSL distribution。
4. Developer、所有啟用 Reviewer、Git、測試與 OCR 全部使用同一環境。從 Windows 宿主選擇 WSL 時，Agent 本身可留在宿主，但所有專案命令必須使用記錄的 `wsl.exe -d <distribution> --` 前綴。
5. 只有 Python 專案才在該環境內檢查專案指定的 Python、`.venv`、`VIRTUAL_ENV`、`CONDA_PREFIX`、`sys.prefix` 與 `sys.base_prefix`。
6. 未偵測到隔離環境時提醒使用者；不阻擋唯讀工作。
7. 不得自動建立、啟用、切換、更新環境或把套件裝進系統 Python。
8. 執行缺少環境或套件時，請使用者先準備，再於同一環境重新驗證。
9. 環境變更只從下一張尚未派發的 Ticket 生效。若某張 Ticket 必須使用另一 OS，先取得使用者明確核准；該 Ticket 的所有啟用角色仍共同使用同一例外環境，完成後回到 Task 設定。

## 後端偵測

派工前只做一次唯讀偵測：

1. 盤點目前可用的子 Agent、Task、MCP 與 AI CLI 工具。
2. 優先讀取專案明確指定的命令與路徑，但不得讓專案設定無聲覆蓋 Task 已選定的 execution environment。
3. 找不到命令設定時，只在選定環境的 `PATH` 檢查；Windows PowerShell 使用 `Get-Command`，Linux 或 WSL 使用 `command -v`，第三選項解析成 cmd 時使用 `where`。
4. 只有安全的版本或能力探測成功，且能確認可派工時，才判定對應 CLI 可用。
5. WSL 模式必須使用 Task 記錄的確切 distribution、Linux 工作目錄及 command prefix；不得自行猜 `/mnt/<drive>`。

不得遞迴掃描磁碟、擅自安裝工具、修改環境或把推測當成可用結果。

## 角色配置

每張 Ticket 固定使用一個臨時 Developer，以及 `reviewer_mode` 啟用的 Reviewer。Coordinator 不算在共識內。

每張 Ticket 首次派工前，Coordinator 只讀取本 Task 最新 `settings_update: reviewers`：沒有更新時使用 `both`；`both` 啟用 Reviewer A 與 B，`a_only` 只啟用 A，`b_only` 只啟用 B。其他值回報 `BLOCKED: INVALID_REVIEWER_MODE`，不得猜測。Reviewer 名單在該 Ticket 派工時固定到共識完成；Coordinator 必須把 `reviewer_mode`、啟用名單與下列 `review_axis` 直接寫入派工契約，Developer 與 Reviewer 不得自行搜尋設定：

- `both`：Reviewer A = `spec`；Reviewer B = `standards`。
- `a_only`：Reviewer A = `both`。
- `b_only`：Reviewer B = `both`。

停用角色的既有設定保留，但不偵測、不派工、不產生 Review 證據。

Coordinator 讀取本 Task 最新一次包含 Developer 或各啟用 Reviewer 的 `settings_update: roles`；各角色不必來自同一筆更新。Reviewer 沒有角色更新時預設 Codex。只能使用選定環境內實際可用且相容於指定模型的 CLI；若只有一個 CLI，所有啟用角色可共用該 CLI，但每個角色仍使用隔離 Agent 並標示「缺少跨模型獨立性」。沒有相容 CLI 或無法建立所有啟用 Reviewer 的隔離 Agent 時，列出偵測結果並停止；不得宣稱共識。

Developer 的初始模型與推理強度以已核准 Ticket 的 `## 初始執行配置` 為準，Task 角色設定只提供 CLI 偏好，不得無聲覆蓋 Ticket。舊 Ticket 缺少此區時，先使用使用者明確設定且符合本段限制的 Developer 模型；否則安全回退為 `claude-opus-5`／`high`。不得派發任何 Haiku；Sonnet 的推理強度不得低於 `high`。自動路由不得使用 `low`、`medium` 或 `max`，`max` 只在使用者針對該 Ticket 明確核准後使用。

每個 Reviewer 的模型與 `model_reasoning_effort` 仍獨立套用 Task 角色設定；未指定時使用所選後端的預設值，但不得使用 Haiku，Sonnet 不得低於 `high`。派工時必須把明確設定傳給對應 Agent，不能只寫在 Task 狀態或委派文字中：平台原生派發工具提供 `reasoning_effort` 時，把 `model_reasoning_effort` 映射到該欄位；Codex CLI 使用同名設定鍵。Reviewer 的明確推理強度被後端拒絕時，以相同 CLI 與模型、不指定推理強度重試一次；明確模型被拒絕時，才以同一 CLI 不指定模型重試一次。Ticket 指定的 Developer 模型或強度被拒絕時回報 `BLOCKED: DEVELOPER_MODEL_UNAVAILABLE`，不得偷偷改用較低配置。啟用兩位 Reviewer 時，首輪 Review 完成前兩者不得互看結論。

### Developer 升級

下列任一條件成立時，以新的 Developer Agent 接手相同 Ticket、Snapshot 與既有證據，升級為 `claude-opus-5`／`xhigh`；這是能力升級，不是新增投票者：

- Developer 提供可重現的能力不足證據，而非只表示工作困難。
- 一個阻擋 Finding 證明核心實作方法無效。
- 同一輪出現三個以上有獨立證據的重要 Findings。
- 同一個有效 Finding 經兩輪修正仍未解決。

若目前已是 `claude-opus-5`／`xhigh`，不得自動升到 `max`。保存觸發條件、原配置、新配置與交接證據。

Reviewer B 未啟用時，不讀取或檢查 Open Code Review 設定。Reviewer B 啟用時，Open Code Review 是 Task 級可選項，不是必要後端：只讀取最新 `settings_update: open_code_review`；沒有該更新、`enabled` 不為 true、`delegate_ready` 不為 true、缺少已驗證的 OCR 絕對路徑、OCR 的 `environment` 不等於目前解析環境，或 `cli_status` 不是 installed 時，Reviewer B 使用 `review_engine: native`，不得自行偵測或安裝。只有該分區的最新狀態指定 `review_engine: open_code_review_delegate`，且 Reviewer B 的 `review_axis` 包含 `standards` 時，才把該值、共同執行環境與 OCR 絕對路徑交給 Reviewer B。Delegation Mode 只輔助 Standards Review 的檔案篩選與規則解析；不處理 Spec Review、不增加 Reviewer 數量，也不得呼叫 OCR 自帶 LLM。

## 安全並行排程

首次派工前讀取全部未完成 Tickets，建立依賴圖、Ready Queue、寫入所有權與共用資源鎖。排程目標是使用平台目前實際可用的 Agent slots，以最短總完成時間執行所有可安全並行的工作；不得硬編固定 Agent 數量，也不得為填滿 slots 派出沒有獨立工作的 Agent。

- 只有依賴已完成、`Dispatch: parallel-safe`、`Exclusive write scope` 明確且互不重疊、`Shared resource locks` 不衝突的 Tickets 可同時派發 Developer。
- 舊 Ticket 缺少並行欄位時，可從明確的依賴與檔案或模組範圍保守判定；任何一項不明確就串行，不阻擋整個 Task。
- 相同檔案或模組、Schema、Migration、Lockfile、正式 Data／Runtime Root、GPU、Blender、ComfyUI、共用建置輸出、全專案測試與 Git 寫入一律串行。
- 每個並行 Developer 只擁有其 Ticket 的確切寫入範圍；共享工作樹中的 Review snapshot 必須使用該 Ticket 的 path-scoped Diff，並標示同時存在的其他 Ticket 變更。
- Ticket 進入 `Ready for Review` 後，優先保留等同啟用 Reviewer 數量的 slots；啟用兩位時同時派發，其他互不衝突的 Developer 可在剩餘 slots 繼續執行。
- Coordinator 獨占 Ticket 紀錄、狀態更新、共用檔案整合、全專案驗證及任何已授權的 Git 寫入；這些操作不得由並行 Agent 執行。
- 平台或後端只允許較低並行度時，自動縮小 active set；啟用兩位但只剩單一可用 Agent 時，以兩個不同實例依序完成 Reviewer A 與 Reviewer B，並記錄未能平行的原因。

## 派工契約

首次派工前必讀 `references/delegation-contracts.md`。

- 不建立永久 Developer 或 Reviewer Profile。
- 每張 Ticket 建立一個一般臨時開發 Agent 與所有啟用的一般臨時 Reviewer，分別保留 ID 到共識完成。
- Coordinator 透過委派訊息明確指定 `Developer`、`Reviewer A` 或 `Reviewer B`；不得依靠 Agent 自己猜。
- 每份委派都包含同一份解析環境、WSL distribution、Shell、command prefix 與專案路徑；Agent 不得自行切換。
- 每位啟用 Reviewer 都載入 `$milktea-skills-code-review`；不可用時回報 `BLOCKED: CODE_REVIEW_SKILL_UNAVAILABLE`，不得自行模擬。
- 每份 Reviewer 契約都明寫 `reviewer_mode`、啟用名單、`review_axis` 與 `review_engine`。Reviewer A 固定為 `native`；Reviewer B 只有在負責 Standards 時才依本 Task 最新的 OCR 分區狀態選擇 `native` 或 `open_code_review_delegate`。
- 每次委派都要明寫角色、Ticket、固定 Snapshot、輸入、權限、禁止事項與回報格式。

## Ticket 狀態機

持續補滿安全可用 slots，直到所有核准 Tickets 完成：

1. 從 Ready Queue 取出目前可安全並行的 Tickets，記錄各自的並行批次、基準版本、確切寫入範圍、資源鎖與開發 Agent 識別。
2. 依派工契約，把每張 Ticket、必要文件、允許修改範圍及驗收指令分別交給新的臨時開發 Agent。
3. 要求開發 Agent 在適用時按需載入 `$milktea-skills-tdd`；不適用時記錄理由與替代驗證。
4. 告知開發 Agent：不得預載 `$milktea-skills-git-merge-conflict`；只有 merge、rebase 或 cherry-pick 實際回報衝突時才載入。Skill 不可用時回報 `BLOCKED: GIT_MERGE_CONFLICT_SKILL_UNAVAILABLE`。
5. 由 Coordinator 依序把各 Ticket 狀態更新為「執行中」。Developer 在迭代期自行執行最小相關檢查；只有首次準備 Review 時才執行一次 Ticket 的完整驗收並回報 `Ready for Review`。未達各 Finding Owner 共識前不得標記完成、接另一張 Ticket 或釋放可續談識別。
6. 收到 `Ready for Review` 後，由 Coordinator 把 Ticket 更新為「Review 中」，確認完整驗收證據後固定 path-scoped Review snapshot：基準、revision、Diff、檔案列表、並行工作樹狀態與驗收證據；在收到 Findings 或 Coordinator 指示前，Developer 不得繼續修改。
7. 依 Reviewer 契約派出所有啟用 Reviewer；提供相同 snapshot、Spec、Ticket、兩份 `docs/planning/` 文件、`CONTEXT.md`、ADR 與開發證據。啟用兩位且 slots 足夠時同時派發，並依 `reviewer_mode` 指定各自唯一的 `review_axis`；Reviewer B 只有 Standards 軸可使用 OCR。
8. 要求每位啟用 Reviewer 載入 `$milktea-skills-code-review`，只完成指定軸；不得檢查另一軸或評論其他並行 Ticket 的變更。單 Reviewer 模式才執行兩軸。
9. Coordinator 把 Reviewer 報告並列交給原 Developer，只追蹤各 Finding 的 `open`、`fixed`、`withdrawn` 與 Owner；不得合併、重新評級或裁決。Developer 逐項重現，正確則在原所有權範圍內修正，錯誤則以程式、測試、正式文件或研究證據反駁。
10. Findings 修正後，Coordinator 依實際影響明確指定要重跑的驗收；不得因修改行數少就省略高風險驗證，也不得預設重跑全套。把每個 Finding 的修正、反證與新 snapshot 只交回提出它的原 Reviewer 定向複驗；除非變更使原 Review 範圍或證據失效，不重新執行完整 Review。
11. Developer 與 Finding Owner 有分歧時，持續使用最小辨別測試、第一手來源或 `$milktea-skills-research` 補證，直到 Owner 關閉或撤回 Finding。只有缺少產品價值、公開契約、不可逆資料處置或安全接受程度等關鍵決策時才交給使用者；不得因一次交換未果就上交，也不得用模型升級投票。
12. 所有阻擋與重要 Finding 都由 Owner 關閉或撤回後，Coordinator 才把 Ticket 更新為「完成」、保存最終證據並結束本 Ticket 的 Agent；建議級 Finding 不得單獨阻擋完成。
13. 每當 Ticket 完成、阻擋或釋放資源鎖時，重新計算 Ready Queue 並立即補派下一批安全工作；相依 Ticket 只有在上游完成後才可進入 Ready Queue。

Reviewer B 回報 `OCR_DELEGATE_UNAVAILABLE` 時，Coordinator 保存錯誤證據，將同一固定 Snapshot 的 Reviewer B 契約改為 `review_engine: native` 後重試一次。此回退不得觸發安裝、更新、API Key 詢問或改派 Reviewer A；原生 Review 成功時把降級原因寫入 Ticket。

適用 Ticket 缺少 TDD，或缺少 Code Review Skill 時停止並回報；不得自行模擬或跳過。

## Ticket 證據紀錄

由 Coordinator 追加到本機 Ticket 的 `## 執行與 Review 紀錄`，並更新狀態；Developer 與 Reviewer 不直接寫 Ticket，避免並行衝突。

依序保存：

1. 開始執行：execution environment、並行批次、排程判定、基準版本、開發角色、確切寫入範圍、資源鎖與必跑指令。
2. `Ready for Review`：Snapshot、變更摘要與測試證據。
3. 實際發生時：Debug 根因與回歸測試、Git 衝突取捨與驗證。
4. Review：各 Reviewer 的指定軸報告、Finding Owner 與狀態、各自的 `review_engine`、OCR Delegation 證據或降級原因、Developer 修正或反證、Owner 定向複驗。
5. 完成：最終 Snapshot、首次完整驗收、Findings 後指定重驗、共識與未解風險。

只追加，不覆寫既有紀錄。寫入失敗時保留完整內容並回報；補寫前不得把 Ticket 標記完成。

## Task 邊界

- 預設在同一執行 Task 完成全部核准 Tickets；不得因對話變長就例行拆分。
- 只有平台發出 Context 警告、壓縮造成必要資訊不足，或已無法安全繼續時，才提出延續 Task。
- 先完成目前可安全收尾的最小工作、保存狀態與證據，再詢問使用者。
- 使用者核准後，平台有頂層 Task 工具時必須實際建立並回報 Task ID；不可用時才提供可直接貼上的啟動指令。兩種情況都不得留在舊 Task 繼續。
- 新需求不得沿用執行 Task，必須重新從 `$milktea-skills-grill-me` 開始。

## 完成規則

- 所有核准 Tickets 與驗收條件均有可重現證據。
- 必跑指令成功；失敗或未執行項目已明示。
- 所有阻擋與重要 Findings 已由原 Owner 關閉或撤回，建議級事項未被誤用為阻擋。
- Developer 與各 Finding Owner 已依證據達成共識；Coordinator 未替雙方裁決或用模型投票。
- 依 Ticket 與專案 Git 規則提交；未授權不得 Commit 或 Push。

最後輸出每張 Ticket 的 execution environment、初始與最終 Developer 配置、升級原因、`reviewer_mode`、Reviewer 的 `review_axis`、並行批次、排程判定、狀態、角色後端、實際模型與推理強度、`review_engine`、OCR Delegation 證據或降級原因、首次完整驗收、指定重驗、各 Finding 狀態、共識、未解風險與版本識別。
