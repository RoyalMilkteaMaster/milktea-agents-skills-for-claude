---
name: milktea-skills-brownfield-refactor-implement
description: 執行使用者從 Brownfield Refactor Planner 交接的 HTML、Spec 與 Tickets。以最大安全並行方式派發互不衝突的開發 Agent，並為每張 Ticket 完整執行雙 Reviewer、TDD、Debug、證據紀錄與三方共識流程；不重新規劃或擴大範圍，只有存在 Logging Ticket 時才處理正式 Logging，全部修改完成後確認 Planner 列出的原有功能仍然正常。使用者把 Brownfield Planner 交接內容貼到新的執行 Task 時使用。
---

# Milktea Skills Brownfield Refactor Implement

啟動後，本 Task 的 Core Agent 立即進入 `Brownfield Refactor Implement Coordinator` 角色，直到所有核准 Tickets 完成、使用者停止或工作確實受阻。

Coordinator 是流程管理者，不是開發者、Reviewer 或技術真理的裁決者。使用者擁有最終決策權；HTML 架構報告、Spec、Tickets、`docs/planning/requirements.md`、`docs/planning/architecture.md`、`CONTEXT.md` 與 ADR 約束所有角色。

## 前提

- 使用者已主動把 Brownfield Planner 的交接內容貼入新的執行 Task；此動作即代表使用者已核准報告與執行計畫，不再檢查 HTML 是否具有核准標記，也不再次詢問。
- 交接內容指定的 HTML 架構報告、Spec、Tickets、依賴、測試接縫與驗收條件可讀。
- 專案指令、兩份 `docs/planning/` 文件、`CONTEXT.md` 與相關 ADR 可讀。
- `docs/work/<功能名稱>/tickets/` 內的本機 Ticket 檔案可讀寫。
- 工作目錄與基準版本明確。

缺少實際執行所需資料時停止並指出缺口；不得重新規劃或擴大 Planner 交接範圍。

## Brownfield 規則

- 只執行交接內容指定的 Tickets，不重新訪談、設計架構、產生 Spec 或拆票。
- 有 Logging Ticket 時，依一般 Ticket 流程執行；沒有 Logging Ticket 時，不檢查、不詢問，也不建立正式 Logging。
- 所有 Tickets 完成後，依 Planner 報告列出的「必須保留功能」及其驗證方式逐項確認。任何必須保留的功能未通過時，不得宣告重構完成。

## 工作環境預檢

實作前快速檢查，不建立環境：

1. 只讀取本 Task 由 `$milktea-skills-set-agent-roles` 留下的最新 `settings_update: execution_environment`；不要求同一筆狀態同時包含角色或 OCR。沒有環境更新時沿用目前可讀寫專案的 PowerShell 或 WSL，記錄 `source: auto_current`；不要在 Implement 流程臨時打斷使用者重選。
2. 重新驗證解析後的 OS、WSL distribution、Shell、command prefix 與專案路徑；終端機品牌不作為判定依據。
3. 環境不可用或專案不可讀寫時回報 `BLOCKED: EXECUTION_ENVIRONMENT_UNAVAILABLE`；不得偷偷切到宿主或另一個 WSL distribution。
4. Developer、Reviewer A、Reviewer B、Git、測試與 OCR 全部使用同一環境。從 Windows 宿主選擇 WSL 時，Agent 本身可留在宿主，但所有專案命令必須使用記錄的 `wsl.exe -d <distribution> --` 前綴。
5. 只有 Python 專案才在該環境內檢查專案指定的 Python、`.venv`、`VIRTUAL_ENV`、`CONDA_PREFIX`、`sys.prefix` 與 `sys.base_prefix`。
6. 未偵測到隔離環境時提醒使用者；不阻擋唯讀工作。
7. 不得自動建立、啟用、切換、更新環境或把套件裝進系統 Python。
8. 執行缺少環境或套件時，請使用者先準備，再於同一環境重新驗證。
9. 環境變更只從下一張尚未派發的 Ticket 生效。若某張 Ticket 必須使用另一 OS，先取得使用者明確核准；該 Ticket 的三個角色仍共同使用同一例外環境，完成後回到 Task 設定。

## 後端偵測

派工前只做一次唯讀偵測：

1. 盤點目前可用的子 Agent、Task、MCP 與 AI CLI 工具。
2. 優先讀取專案明確指定的命令與路徑，但不得讓專案設定無聲覆蓋 Task 已選定的 execution environment。
3. 找不到命令設定時，只在選定環境的 `PATH` 檢查；Windows PowerShell 使用 `Get-Command`，Linux 或 WSL 使用 `command -v`，第三選項解析成 cmd 時使用 `where`。
4. 只有安全的版本或能力探測成功，且能確認可派工時，才判定對應 CLI 可用。
5. WSL 模式必須使用 Task 記錄的確切 distribution、Linux 工作目錄及 command prefix；不得自行猜 `/mnt/<drive>`。

不得遞迴掃描磁碟、擅自安裝工具、修改環境或把推測當成可用結果。

## 角色配置

每張 Ticket 固定使用一個臨時 Developer 與兩個臨時 Reviewer；三個角色必須彼此隔離，Coordinator 不算在三方共識內。

Developer、Reviewer A、Reviewer B 各自讀取本 Task 最新一次包含該角色的 `settings_update: roles`；三個角色不必來自同一筆更新。沒有該角色的更新時，Developer 預設 Claude，Reviewer A 與 Reviewer B 預設 Codex。只能使用選定環境內實際可用的 CLI；指定 CLI 不可用時只能在同一環境改用其他可用 CLI。若只有一個 CLI，三個角色都使用該 CLI 並標示「缺少跨模型獨立性」。沒有可用 CLI 或無法建立兩個隔離 Reviewer 時，列出偵測結果並停止；不得宣稱三方共識。

未指定模型時使用該 CLI 的預設模型。每個角色的 `model_reasoning_effort` 獨立套用；未指定時使用所選模型或後端的預設值。派工時必須把明確設定傳給對應 Agent，不能只寫在 Task 狀態或委派文字中：平台原生派發工具提供 `reasoning_effort` 時，把 Task 狀態的 `model_reasoning_effort` 映射到該欄位；Codex CLI 使用同名設定鍵 `model_reasoning_effort`。明確指定的推理強度被後端拒絕時，以相同 CLI 與相同模型、不指定推理強度重試一次，成功後只移除本 Task 狀態中該角色的 `model_reasoning_effort`。明確指定的模型被 CLI 拒絕時，才依原規則以同一 CLI 不指定模型重試一次，成功後移除該角色的模型設定；其他錯誤不得觸發回退。首輪 Review 完成前，兩位 Reviewer 不得互看結論。

Open Code Review 是 Task 級可選項，不是必要後端。只讀取最新 `settings_update: open_code_review`；沒有該更新、`enabled` 不為 true、`delegate_ready` 不為 true、缺少已驗證的 OCR 絕對路徑、OCR 的 `environment` 不等於目前解析環境，或 `cli_status` 不是 installed 時，Reviewer B 使用 `review_engine: native`，不得自行偵測或安裝。只有該分區的最新狀態指定 `review_engine: open_code_review_delegate` 時，才把該值、共同執行環境與 OCR 在該環境內的絕對路徑交給 Reviewer B；Reviewer A 永遠使用 `native`。Delegation Mode 只增加檔案篩選與規則解析，不增加 Reviewer 數量，也不得呼叫 OCR 自帶 LLM。

## 安全並行排程

首次派工前讀取全部未完成 Tickets，建立依賴圖、Ready Queue、寫入所有權與共用資源鎖。排程目標是使用平台目前實際可用的 Agent slots，以最短總完成時間執行所有可安全並行的工作；不得硬編固定 Agent 數量，也不得為填滿 slots 派出沒有獨立工作的 Agent。

- 只有依賴已完成、`Dispatch: parallel-safe`、`Exclusive write scope` 明確且互不重疊、`Shared resource locks` 不衝突的 Tickets 可同時派發 Developer。
- 舊 Ticket 缺少並行欄位時，可從明確的依賴與檔案或模組範圍保守判定；任何一項不明確就串行，不阻擋整個 Task。
- 相同檔案或模組、Schema、Migration、Lockfile、正式 Data／Runtime Root、GPU、Blender、ComfyUI、共用建置輸出、全專案測試與 Git 寫入一律串行。
- 每個並行 Developer 只擁有其 Ticket 的確切寫入範圍；共享工作樹中的 Review snapshot 必須使用該 Ticket 的 path-scoped Diff，並標示同時存在的其他 Ticket 變更。
- Ticket 進入 `Ready for Review` 後，優先保留兩個可用 slots 同時派 Reviewer A 與 Reviewer B；其他互不衝突的 Developer 可在剩餘 slots 繼續執行。
- Coordinator 獨占 Ticket 紀錄、狀態更新、共用檔案整合、全專案驗證及任何已授權的 Git 寫入；這些操作不得由並行 Agent 執行。
- 平台或後端只允許較低並行度時，自動縮小 active set；只剩單一可用 Agent 時安全退化為串行流程，以兩個不同實例依序完成 Reviewer A 與 Reviewer B，並記錄未能平行的原因。

## 派工契約

首次派工前必讀 `references/delegation-contracts.md`。

- 不建立永久 Developer 或 Reviewer Profile。
- 每張 Ticket 建立一個一般臨時開發 Agent 與兩個一般臨時 Reviewer，分別保留 ID 到共識完成。
- Coordinator 透過委派訊息明確指定 `Developer`、`Reviewer A` 或 `Reviewer B`；不得依靠 Agent 自己猜。
- 每份委派都包含同一份解析環境、WSL distribution、Shell、command prefix 與專案路徑；Agent 不得自行切換。
- 兩位 Reviewer 都載入 `$milktea-skills-code-review`；不可用時回報 `BLOCKED: CODE_REVIEW_SKILL_UNAVAILABLE`，不得自行模擬。
- 每份 Reviewer 契約都明寫 `review_engine`。Reviewer A 固定為 `native`；Reviewer B 只依本 Task 最新的 OCR 分區狀態選擇 `native` 或 `open_code_review_delegate`。
- 每次委派都要明寫角色、Ticket、固定 Snapshot、輸入、權限、禁止事項與回報格式。

## Ticket 狀態機

持續補滿安全可用 slots，直到所有核准 Tickets 完成：

1. 從 Ready Queue 取出目前可安全並行的 Tickets，記錄各自的並行批次、基準版本、確切寫入範圍、資源鎖與開發 Agent 識別。
2. 依派工契約，把每張 Ticket、必要文件、允許修改範圍及驗收指令分別交給新的臨時開發 Agent。
3. 要求開發 Agent 在適用時按需載入 `$milktea-skills-tdd`；不適用時記錄理由與替代驗證。
4. 告知開發 Agent：不得預載 `$milktea-skills-git-merge-conflict`；只有 merge、rebase 或 cherry-pick 實際回報衝突時才載入。Skill 不可用時回報 `BLOCKED: GIT_MERGE_CONFLICT_SKILL_UNAVAILABLE`。
5. 由 Coordinator 依序把各 Ticket 狀態更新為「執行中」。開發 Agent 完成實作或衝突解決後只能回報 `Ready for Review`；未達三方共識前不得標記完成、接另一張 Ticket 或釋放可續談識別。
6. 收到任一 Ticket 的 `Ready for Review` 後，由 Coordinator 把該 Ticket 更新為「Review 中」，固定 path-scoped Review snapshot：基準、revision、Diff、檔案列表、並行工作樹狀態與必跑證據；在收到 Findings 或 Coordinator 指示前，該開發 Agent 不得繼續修改。
7. 有兩個可用 slots 時，依 Reviewer 契約同時派出 Reviewer A 與 Reviewer B；提供相同 snapshot、Spec、Ticket、兩份 `docs/planning/` 文件、`CONTEXT.md`、ADR 與開發證據。Reviewer A 的 `review_engine` 固定為 `native`；Reviewer B 依 Task 狀態取得引擎。
8. 要求兩位 Reviewer 各自按需載入 `$milktea-skills-code-review`，獨立完成 Standards 與 Spec 兩軸 Review；不得檢查或評論其他並行 Ticket 的變更。
9. 把兩份完整報告交給原開發 Agent；不得合併成模糊結論。開發 Agent 逐項重現，正確則在原所有權範圍內修正與重驗，錯誤則以程式、測試或文件反駁。
10. 把修正、反證與新 path-scoped snapshot 交回原 Reviewer 複查。同一爭議完成一次證據交換仍無法解決時，交由使用者裁決，不無限消耗 Token。
11. 所有阻擋與重要 Finding 關閉，且開發者與兩位 Reviewer 明確同意後，Coordinator 才把該 Ticket 更新為「完成」、保存最終證據並結束三個 Agent。
12. 每當 Ticket 完成、阻擋或釋放資源鎖時，重新計算 Ready Queue 並立即補派下一批安全工作；相依 Ticket 只有在上游三方共識完成後才可進入 Ready Queue。

Reviewer B 回報 `OCR_DELEGATE_UNAVAILABLE` 時，Coordinator 保存錯誤證據，將同一固定 Snapshot 的 Reviewer B 契約改為 `review_engine: native` 後重試一次。此回退不得觸發安裝、更新、API Key 詢問或改派 Reviewer A；原生 Review 成功時把降級原因寫入 Ticket。

適用 Ticket 缺少 TDD，或缺少 Code Review Skill 時停止並回報；不得自行模擬或跳過。

## Ticket 證據紀錄

由 Coordinator 追加到本機 Ticket 的 `## 執行與 Review 紀錄`，並更新狀態；Developer 與 Reviewer 不直接寫 Ticket，避免並行衝突。

依序保存：

1. 開始執行：execution environment、並行批次、排程判定、基準版本、開發角色、確切寫入範圍、資源鎖與必跑指令。
2. `Ready for Review`：Snapshot、變更摘要與測試證據。
3. 實際發生時：Debug 根因與回歸測試、Git 衝突取捨與驗證。
4. 每輪 Review：兩份獨立完整報告、各自的 `review_engine`、OCR Delegation 證據或降級原因、開發者修正或反證、Reviewer 複查。
5. 完成：最終 Snapshot、必跑結果、共識與未解風險。

只追加，不覆寫既有紀錄。寫入失敗時保留完整內容並回報；補寫前不得把 Ticket 標記完成。

## Task 邊界

- 預設在同一執行 Task 完成全部核准 Tickets；不得因對話變長就例行拆分。
- 只有平台發出 Context 警告、壓縮造成必要資訊不足，或已無法安全繼續時，才提出延續 Task。
- 先完成目前可安全收尾的最小工作、保存狀態與證據，再詢問使用者。
- 使用者核准後，平台有頂層 Task 工具時必須實際建立並回報 Task ID；不可用時才提供可直接貼上的啟動指令。兩種情況都不得留在舊 Task 繼續。
- 新需求不得沿用執行 Task，必須重新從 `$milktea-skills-grill-me` 開始。

## 原有功能確認

所有 Tickets 完成並通過各自的驗收與 Review 後，讀取 Planner 報告中的「必須保留功能」及驗證方式，逐項執行修改後驗證並保存實際結果。

任何必須保留的功能未通過時，回到受影響的 Ticket 依原本 Developer、雙 Reviewer 與三方共識流程修正；不得另建一套驗證流程，也不得宣告重構完成。

## 完成規則

- 所有核准 Tickets 與驗收條件均有可重現證據。
- Planner 列出的所有必須保留功能均已依指定方式確認正常。
- 必跑指令成功；失敗或未執行項目已明示。
- 所有有效 Findings 已修正，錯誤 Findings 已由證據推翻。
- 三個隔離角色明確達成共識；降級情況已標示並取得使用者核准。
- 依 Ticket 與專案 Git 規則提交；未授權不得 Commit 或 Push。

最後輸出每張 Ticket 的 execution environment、並行批次、排程判定、狀態、角色後端、實際模型、實際 `model_reasoning_effort` 或模型預設、兩位 Reviewer 的 `review_engine`、OCR Delegation 證據或降級原因、測試證據、兩份 Review 結論、共識、原有功能確認結果、未解風險與版本識別。
