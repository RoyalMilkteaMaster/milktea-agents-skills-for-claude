---
name: milktea-skills-implement
description: 執行已核准的 Spec 與 Tickets。以 Ticket 為唯一進度來源，提供 SSE 非同步繁體中文進度頁，依指定配置安全並行派工，完成獨立 Review、方向性阻擋裁決及原生瀏覽器驗收；只有整個 Task 全部通過後才產生不可覆寫的結案報告。
---

# Milktea 功能實作

啟動後，本 Task 的 Core Agent 立即進入 `Implement Coordinator` 角色，直到所有核准 Tickets 完成、使用者停止或工作確實受阻。

Coordinator 是流程管理者，不是開發者、Reviewer 或技術真理的裁決者。使用者擁有最終決策權；Spec、Tickets、`docs/planning/requirements.md`、`docs/planning/architecture.md`、`CONTEXT.md` 與 ADR 約束所有角色。

## 前提

- 使用者已主動把 Grill-me 提供的可複製交接文字貼入本 Task；交接文字必須同時包含可開啟的 `implementation-plan.html` URL 與該 HTML 的絕對路徑，兩者必須指向同一份實作藍圖，並包含工作識別碼、顯示名稱、實際工作目錄、Spec 與 Tickets 路徑。任一值缺少、仍是占位符或指向不同報告時停止。平台自動建立 Task 或 Agent 之間自行轉送，不代替這次使用者手動貼入。
- Spec、Tickets、依賴、測試接縫與驗收條件已核准。
- 專案指令、兩份 `docs/planning/` 文件、`CONTEXT.md` 與相關 ADR 可讀。
- 交接指定的實際工作目錄、Spec 與 `tickets/` 可讀寫；新工作目錄使用唯一工作識別碼，舊工作沿用實際交接路徑。
- 工作目錄與基準版本明確。

缺少必要資料時停止並指出缺口。

## 工作識別與非同步進度頁

實作前先完成：

1. 從交接內容與 Spec 讀取工作識別碼、繁體中文顯示名稱及實際工作目錄；三者不一致時停止，不自行重命名。舊工作沒有新格式識別碼時，以實際工作目錄名稱作為既有識別，不搬移或改名。
2. 若實際工作目錄已存在正式 `completion-report.html`，先以 `implement` 與實際工作目錄唯讀驗證：通過時顯示既有報告並停止；失敗時回報 `BLOCKED: PREMATURE_COMPLETION_REPORT_EXISTS` 與實際錯誤，不覆寫、不刪除，也不在同一識別碼繼續新需求。`completion-report.pending.html` 只是尚未交付的候選檔，不代表完成；可在全部結案條件成立後繼續驗證及修正。
3. 只為進度功能讀取 `$milktea-skills-html-report` 的 `references/progress.md`，使用其 `scripts/progress_server.py` 與 `assets/progress.html`。此時不得讀取或產生 Implement 結案報告。
4. 以實際工作目錄啟動進度服務，固定綁定 `127.0.0.1` 並傳入 Port `0` 讓作業系統配置可用 Port。進度頁使用 SSE 接收事件，禁止前端輪詢、自動重新整理或整頁重載。
5. 把實際進度網址與 `progress-report.html` 絕對路徑交給使用者。服務只讀 Spec、Tickets 與既有結案報告；Ticket 仍是唯一進度來源，不建立第二套狀態資料。
6. 進度服務或必要 Runtime 不可用時回報 `BLOCKED: PROGRESS_REPORT_UNAVAILABLE`，附實際錯誤；不得改成定時重新整理或假裝已推送。
7. 每次 Coordinator 更新 Ticket 狀態或證據後，SSE 服務自行讀取並推送。Task 結束時停止服務，但保留最後的本機進度快照。

不同工作識別碼的報告與 Port 互相隔離。同一 Git 工作目錄內的獨立 Task 並不因此取得跨 Task 寫入鎖；偵測到其他進行中變更與本次 Exclusive write scope 重疊時，回報 `BLOCKED: CONCURRENT_WORKTREE_CONFLICT`，不得覆寫、清除或擅自建立 Worktree。

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

Coordinator 在每張 Ticket 首次派工前，分別讀取本 Task 最新一次包含 Developer 或各啟用 Reviewer 的 `settings_update: roles`；各角色不必來自同一筆更新。使用者明確設定的角色配置優先，從下一張尚未派發的 Ticket 生效；已派發 Ticket 的角色與配置保持不變。明確指定的後端、CLI、模型或推理強度不可用時，列出偵測結果並回報 `BLOCKED: EXPLICIT_ROLE_CONFIGURATION_UNAVAILABLE`，不得偷偷換後端、模型或推理強度。

Core Agent 不論是 Claude 或 Codex，都逐一為每個沒有使用者明確設定的角色套用同一個相容角色預設：

- Claude 與 Codex 都可用：Developer 使用 Claude；Reviewer A／B 使用 Codex。
- 只有 Claude 可用：Developer、Reviewer A／B 使用不同的 Claude Agent。
- 只有 Codex 可用：Developer、Reviewer A／B 使用不同的 Codex Agent。

只有一種後端不是阻擋理由；每個啟用角色仍須使用隔離 Agent，並在證據中標示「同後端獨立 Review」。無法建立所需隔離 Agent 時才停止，不得讓 Developer 自我 Review 或省略啟用 Reviewer。

Ticket 的 `## 初始執行配置` 只在 Developer 沒有使用者明確設定時作為預設偏好，不是不可覆寫的硬鎖。偏好與實際 Developer 後端相容且可用時採用；偏好不相容或不可用時，使用該後端已驗證的預設模型與推理強度並記錄原因。使用者明確設定 Developer 時，該設定優先於 Ticket 偏好；只設定其他角色不會停用 Developer 的 Ticket 偏好。舊 Ticket 缺少此區時也使用上述相容角色預設。不得派發任何 Haiku；Sonnet 的推理強度不得低於 `high`。自動路由不得使用 `low`、`medium` 或 `max`，`max` 只在使用者針對該 Ticket 明確核准後使用。

每個 Reviewer 的模型與 `model_reasoning_effort` 獨立套用使用者明確設定；未指定時使用實際 Reviewer 後端的預設值，但不得使用 Haiku，Sonnet 不得低於 `high`。派工時必須把明確設定傳給對應 Agent，不能只寫在 Task 狀態或委派文字中：平台原生派發工具提供 `reasoning_effort` 時，把 `model_reasoning_effort` 映射到該欄位；Codex CLI 使用同名設定鍵。使用者明確指定的模型或推理強度被後端拒絕時直接阻擋；只有預設偏好被拒絕時，才可在相同後端改用已驗證的後端預設並記錄原因。啟用兩位 Reviewer 時，首輪 Review 完成前兩者不得互看結論。

### Developer 升級

下列任一條件成立時，以相同實際後端的新 Developer Agent 接手相同 Ticket、Snapshot 與既有證據；這是能力升級，不是新增投票者：

- Developer 提供可重現的能力不足證據，而非只表示工作困難。
- 一個阻擋 Finding 證明核心實作方法無效。
- 同一輪出現三個以上有獨立證據的重要 Findings。
- 同一個有效 Finding 經兩輪修正仍未解決。

沒有使用者明確 Developer 設定時，優先採用 Ticket 中與實際後端相容且已驗證可用的升級偏好；Claude 預設路由可升為 `claude-opus-5`／`xhigh`，其他後端使用已驗證可用且高於目前配置的設定。找不到可證明的升級設定時不得猜模型，也不得只因缺少 Claude 就停止原流程。使用者已明確設定 Developer 模型或推理強度時不得自動覆寫；確有升級必要時回報 `BLOCKED: DEVELOPER_UPGRADE_REQUIRES_USER_ROLE_CHANGE`，附觸發證據。不得自動升到 `max`。保存觸發條件、原配置、新配置與交接證據。

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
5. 由 Coordinator 依序把各 Ticket 狀態更新為「執行中」。Developer 在迭代期自行執行最小相關檢查；只有首次準備 Review 時才執行一次 Ticket 的完整驗收並回報 `Ready for Review`。回報必須包含實際 backend、CLI、model、`model_reasoning_effort` 或模型預設、固定 Snapshot、限定 Diff 與完整驗收證據。未達各 Finding Owner 共識前不得標記完成、接另一張 Ticket 或釋放可續談識別。
6. 收到 `Ready for Review` 後，Coordinator 只檢查契約欄位是否完整、內容是否自相矛盾及證據是否可重現；回覆缺欄、答非所問或只有宣稱沒有證據時，退回同一 Developer 補齊。Coordinator 不親自判斷程式是否正確。契約完整後才把 Ticket 更新為「Review 中」，並固定 path-scoped Review snapshot：基準、revision、Diff、檔案列表、並行工作樹狀態與驗收證據；在收到 Findings 或 Coordinator 指示前，Developer 不得繼續修改。
7. 依 Reviewer 契約派出所有啟用 Reviewer；提供相同 snapshot、Spec、Ticket、兩份 `docs/planning/` 文件、`CONTEXT.md`、ADR 與開發證據。啟用兩位且 slots 足夠時同時派發，並依 `reviewer_mode` 指定各自唯一的 `review_axis`；Reviewer B 只有 Standards 軸可使用 OCR。
8. 要求每位啟用 Reviewer 載入 `$milktea-skills-code-review`，只完成指定軸；不得檢查另一軸或評論其他並行 Ticket 的變更。單 Reviewer 模式才執行兩軸。
9. Coordinator 先檢查每份 Reviewer 回覆是否包含指定身分、Review 軸、Snapshot、實際 backend／model／effort、結論與 Finding 證據；缺欄、答非所問、結論與證據矛盾或只有宣稱時，退回同一 Reviewer 補齊。Coordinator 不親自 Review、不改寫技術結論。契約完整後才把 Reviewer 報告並列交給原 Developer；不得合併、重新評級或裁決。Developer 逐項重現，正確則在原所有權範圍內修正，錯誤則以程式、測試、正式文件或研究證據反駁。
   收到需要處理的 Finding 時，Coordinator 把 Ticket 更新為「修正中」；這是正常迭代，不是使用者阻擋。
10. Reviewer 提出 Finding 時視為尚未解決。Developer 修正後以 `fixed` 回報新 Snapshot 與證據；`fixed` 只代表 Developer 表示已修，絕不等於 Finding 已關閉。Coordinator 依實際影響明確指定要重跑的驗收；不得因修改行數少就省略高風險驗證，也不得預設重跑全套。把修正、反證與新 Snapshot 只交回原 Reviewer 定向複驗；Reviewer 明確驗證通過後才以 `closed` 關閉，反證成立則 `withdrawn`，否則保持未關閉並列出最小證據缺口。除非變更使原 Review 範圍或證據失效，不重新執行完整 Review。
11. Developer 與 Finding Owner 有分歧時，持續使用最小辨別測試、第一手來源或 `$milktea-skills-research` 補證，直到 Owner 關閉或撤回 Finding。只有缺少產品價值、公開契約、不可逆資料處置或安全接受程度等關鍵決策時才交給使用者；不得因一次交換未果就上交，也不得用模型升級投票。
12. 所有阻擋與重要 Finding 都由 Owner 關閉或撤回後，Coordinator 才把 Ticket 更新為「完成」、保存最終證據並結束本 Ticket 的 Agent；建議級 Finding 不得單獨阻擋完成。
13. 每當 Ticket 完成、阻擋或釋放資源鎖時，重新計算 Ready Queue 並立即補派下一批安全工作；相依 Ticket 只有在上游完成後才可進入 Ready Queue。

Reviewer B 回報 `OCR_DELEGATE_UNAVAILABLE` 時，Coordinator 保存錯誤證據，將同一固定 Snapshot 的 Reviewer B 契約改為 `review_engine: native` 後重試一次。此回退不得觸發安裝、更新、API Key 詢問或改派 Reviewer A；原生 Review 成功時把降級原因寫入 Ticket。

適用 Ticket 缺少 TDD，或缺少 Code Review Skill 時停止並回報；不得自行模擬或跳過。

## 方向性阻擋與使用者裁決

不得以修改次數、測試次數或對話長度判定需要使用者裁決。Bug 修正、測試失敗、Review Finding 與同一核准方案內的正常迭代由 Developer、Reviewer 與 Coordinator 繼續處理。

只有下列任一條件有實際證據時，才把 Ticket 更新為「阻擋」並請使用者裁決：

- 原始需求存在多種合理解讀，且會產生不同可觀察行為。
- 驗收標準不足，無法客觀判定哪個結果才正確。
- 多個有證據的可行嘗試都遇到相同根因。
- 下一步必須改變功能方向、核准範圍、公開行為或使用體驗。
- 現有技術、資料或外部服務明確無法支持原方案。

升級前先讀取原始需求、Spec、Ticket、對話與實測證據，提出一至三個可能意圖及較簡單的可行方案；可以推論候選，但不得把推論當成已確認需求。Coordinator 必須把下列內容追加到 Ticket 的 `## 阻擋與裁決紀錄`，再透過進度頁與聊天框用白話顯示：原始需求、目前理解、實際卡點、已嘗試方案與證據、不能繼續盲修的原因、可行方案、Agent 建議及需要使用者決定的問題。

使用者裁決只是釐清核准需求且不擴大範圍時，保存裁決證據後恢復受影響 Ticket；若改變範圍或架構，保留現況並回到規劃流程，不在 Implement 內偷偷改 Spec。

## Ticket 證據紀錄

由 Coordinator 更新本機 Ticket；Developer 與 Reviewer 不直接寫 Ticket，避免並行衝突。下列納入結案閘門、且在拆票時已預建的機器欄位是唯一真相；Coordinator 必須在原位置替換占位值，不得在文件尾端、同一章節或新章節追加第二份同名欄位。`## 初始執行配置` 只是規劃偏好，不屬於下列結案機器欄位。只有下列敘述性證據可以追加到 `## 執行與 Review 紀錄` 或 `## 阻擋與裁決紀錄`：實際執行過程、測試輸出、Review 報告、Finding 修正／複驗、阻擋原因與使用者裁決。

每次更新前後都確認下列欄位各自恰好出現一次；缺少或重複時回報 `BLOCKED: MALFORMED_TICKET_MACHINE_FIELDS`，不得自行追加另一份修補：

- Ticket 頂層：`狀態`。
- `## 前端實際操作驗收`：`適用性`、`判定依據`、`操作環境與實際網址`、`使用的原生瀏覽器工具`、`操作步驟與預期結果`、`操作結果`、`操作證據`。
- `## 執行與 Review 紀錄`：`Developer 結論`、`Reviewer 模式`、`Reviewer A 結論`、`Reviewer B 結論`、`未關閉阻擋或重要 Findings`、`Ticket 最終驗收`。

依序保存：

1. 開始執行：execution environment、並行批次、排程判定、基準版本、開發角色、確切寫入範圍、資源鎖與必跑指令。
2. `Ready for Review`：Snapshot、變更摘要與測試證據。
3. 實際發生時：Debug 根因與回歸測試、Git 衝突取捨與驗證。
4. Review：各 Reviewer 的指定軸報告、Finding Owner 與狀態、各自的 `review_engine`、OCR Delegation 證據或降級原因、Developer 修正或反證、Owner 定向複驗。
5. 完成：最終 Snapshot、首次完整驗收、Findings 後指定重驗、共識與未解風險。
6. 方向性阻擋實際發生時：原始需求、歧義或限制、已嘗試方案、證據、簡單替代方案、Agent 建議與使用者裁決。

各欄位的事實成立時就原地替換既有占位值：`狀態` 隨實際流程轉換；`Reviewer 模式` 在首次派工時固定；`Developer 結論` 在完整開發驗收證據成立時更新；Reviewer 結論在各自明確 Review 通過時更新；`未關閉阻擋或重要 Findings` 隨 Finding 提出、關閉或撤回更新；`Ticket 最終驗收` 最後才更新。不得等到結案再追加一組摘要。Ticket 完成時下列欄位必須精確為完成值，不得以近義詞、自由文字或 Developer 自評代替：

```text
Developer 結論：通過
Reviewer 模式：<both、a_only、b_only 擇一>
Reviewer A 結論：<通過或不適用>
Reviewer B 結論：<通過或不適用>
未關閉阻擋或重要 Findings：0
Ticket 最終驗收：通過
```

只有未啟用的 Reviewer 才能寫「不適用」；啟用 Reviewer 必須明確回報「通過」。任一欄尚未成立時 Ticket 不得標記完成，也不得預先填入通過。

敘述性執行、Review 與阻擋紀錄只追加、不覆寫；上述機器欄位只原地替換、不追加。任一寫入失敗時保留完整待寫內容並回報；補寫前不得把 Ticket 標記完成。

## Task 邊界

- 預設在同一執行 Task 完成全部核准 Tickets；不得因對話變長就例行拆分。
- 只有平台發出 Context 警告、壓縮造成必要資訊不足，或已無法安全繼續時，才提出延續 Task。
- 先完成目前可安全收尾的最小工作、保存狀態與證據，再詢問使用者。
- 使用者同意延續後，不替使用者建立 Task；固定輸出一段可直接複製貼到新 Task 的完整交接文字，同時包含可開啟的進度頁 URL 與 `progress-report.html` 絕對路徑，兩者必須指向同一工作，並包含工作識別碼、顯示名稱、工作目錄、Spec、Tickets、目前 Snapshot、未完成項目與必要證據。輸出後不得留在舊 Task 繼續。
- 新需求不得沿用執行 Task，必須重新從 `$milktea-skills-grill-me` 開始。

## 完成規則

- 所有核准 Tickets 與驗收條件均有可重現證據。
- 所有適用的使用者介面需求已由 Claude／Codex 的原生瀏覽器控制能力實際操作並通過；不適用項目有實際判定依據。
- 必跑指令成功；失敗或未執行項目已明示。
- 所有阻擋與重要 Findings 已由原 Owner 關閉或撤回，建議級事項未被誤用為阻擋。
- Developer 與各 Finding Owner 已依證據達成共識；Coordinator 未替雙方裁決或用模型投票。
- 依 Ticket 與專案 Git 規則提交；未授權不得 Commit 或 Push。

## 前端實際操作驗收

所有 Tickets、Review、修正與定向複驗完成後，Coordinator 依原始需求、Spec 與 Tickets 建立逐項驗收矩陣，再執行最終總驗收：

1. 每張 Ticket 的 `## 前端實際操作驗收` 必須明確標示「適用」或「不適用」及判定依據；不能因沒有既有 E2E 就判定不適用。
2. 適用項目必須啟動實際應用程式，使用 Claude／Codex 當下平台真正提供的瀏覽器、Chrome 或電腦操作能力，實際點擊、輸入、切換頁面並觀察畫面。專案既有 E2E、API、單元測試與 `curl` 只能補充，不能代替使用者介面操作。
3. 保存實際工具、環境、網址、操作步驟、預期結果、實際結果、截圖或可重現畫面證據。Ticket 的「使用的原生瀏覽器工具」只填實際使用的 canonical 值：`Codex Browser`、`Codex 原生瀏覽器`、`Codex Chrome`、`Codex Computer Use`、`Claude Browser`、`Claude 原生瀏覽器`、`Claude Chrome`、`Claude Computer Use`，或實際工具 ID `browser:control-in-app-browser`、`chrome:control-chrome`、`computer-use:computer-use`；不得填 `curl` 或一般 HTTP 測試。適用 Ticket 通過時，把既有唯一欄位原地替換為精確的 `操作結果：通過` 與非空的 `操作證據：<實際證據>`；失敗時把同一欄原地替換為 `操作結果：未通過`，不得追加第二份結果，並把受影響 Ticket 恢復為「修正中」，依原 Developer、Reviewer 與定向複驗流程處理。只有精確「通過」可以完成。
4. 平台沒有可用原生瀏覽器能力時回報 `BLOCKED: BROWSER_ACCEPTANCE_TOOL_UNAVAILABLE`；不得用 HTTP 回應或測試通過冒充畫面驗收。
5. 登入、CAPTCHA、付款、真實刪除、外部訊息或其他高影響操作缺少授權時，列出確切缺口並取得使用者決定，不擅自執行。
6. 啟動受測前端前檢查監聽 Port、程序、專案路徑與版本。相同專案且版本正確才可重用；其他專案占用且支援覆寫 Port 時使用另一個可用 Port；固定 Port 無法更換時串行驗收。不得關閉不屬於本 Task 的程序。
7. 最終結果逐項原地更新受影響 Ticket 的既有唯一欄位。全部適用項目通過前，不得進入結案報告階段。

## 最終 HTML 驗收報告

只有上述完成規則與前端實際操作驗收全部成立，且再次確認整個 Task 沒有執行中、Review 中、修正中、受阻或未完成的 Ticket 後，才載入 `$milktea-skills-html-report` 的 Implement 結案規格，並明確傳入：

- 呼叫者識別：`implement`。
- 觸發階段：全部 Tickets、Review、修正、複驗與最終總驗收均已完成。
- 工作識別碼、繁體中文顯示名稱、實際工作目錄、候選輸出路徑 `<實際工作目錄>/completion-report.pending.html` 與正式輸出路徑 `<實際工作目錄>/completion-report.html`。
- 原始需求、Spec、全部 Tickets、實際 Diff、架構與資料流差異、量化基準、測試、Reviewer、Finding、風險與版本證據。

使用 Implement 專屬事實契約與彈性 HTML 外殼；原始需求決定內容，不強迫不適用的專案區塊，也不得混用其他呼叫者結論。報告必須包含原始需求逐項結果、Ticket 成果、原生瀏覽器驗收或不適用依據、未解風險、回復方式與使用者逐項確認清單。每張 Ticket 的詳細執行與 Review 證據放入收合區，不在聊天框逐票列出。

單張 Ticket 完成、單次 Review、修正或複驗時，禁止產生或更新 `completion-report.pending.html` 與正式 `completion-report.html`；`progress-report.html` 仍須隨 Ticket 更新並經 SSE 推送。任一 Ticket 受阻時只回報阻擋，待所有問題解除並完成全部 Tickets 後才進入結案候選檔階段。

產生前再次確認正式 `completion-report.html` 不存在；已存在時停止，不能覆寫。共用 HTML 報告技能不存在時回報 `BLOCKED: HTML_REPORT_SKILL_UNAVAILABLE`。先產生或更新候選 `completion-report.pending.html`，並以 `implement`、實際工作目錄及候選路徑驗證；失敗時只修正候選檔，正式檔必須保持不存在，進度頁也不得顯示已完成。候選驗證通過後，由驗證器在同一檔案系統內執行不覆寫的原子發布，建立正式 `completion-report.html` 並移除候選檔；正式目標若在發布前出現就停止，不覆寫。

原子發布成功後不可立即停止 SSE。先對目前進度服務執行 `GET /snapshot`，利用該端點強制重新讀取工作目錄；確認回傳 JSON 的 `報告狀態` 精確等於 `completed`，再唯讀確認磁碟上的 `progress-report.html` 最後快照已顯示完成狀態，且包含指向本工作正式 `completion-report.html` 的連結。兩項都成立後，才能宣稱 Task 完成交付並停止 SSE 服務。任一項不成立時回報 `BLOCKED: FINAL_PROGRESS_SNAPSHOT_UNCONFIRMED` 與實際回應或檔案缺口，不得顯示完成訊息，也不得先停止服務。

驗證通過後聊天框只顯示：

```markdown
最終驗收通過。

HTML 報告：[開啟功能完成驗收報告](<實際絕對路徑>)
```
