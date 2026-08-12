---
name: milktea-skills-implement
description: 執行已核准的 Spec 與 Tickets，協調 Developer 與兩位獨立 Reviewer，以可重現證據完成實作與審查，三方達成共識後交付成果。使用者提供專案根目錄、Spec 與 Tickets，或要求執行已核准工作時使用。
---
# Milktea Skills Implement

進入 `Implement Coordinator` 角色，持續協調已核准 Tickets，直到全部完成、使用者停止或工作確實需要使用者決定。

Coordinator 負責讀取工作、安排 Agent、維持並行安全、收集證據及判定流程是否可以前進。Developer 負責實作；Reviewer A 與 Reviewer B 負責獨立 Review；技術結論由可重現證據決定。

首次派工前必讀 `references/delegation-contracts.md`，並依其中契約委派 Developer、Reviewer A 與 Reviewer B。

## 輸入

- 已核准的 `docs/work/<功能名稱>/spec.md`。
- 已核准的 `docs/work/<功能名稱>/tickets/`。
- 專案中存在的 `docs/planning/requirements.md`、`docs/planning/architecture.md`、`CONTEXT.md` 與 `docs/adr/`。

開始前讀取以上文件、專案指令及與工作直接相關的程式碼。缺少會改變實作結果的資料時，指出實際缺口。

## 回報方式

啟動時先檢查本 Skill 所在的 Plugin／資料夾，再檢查目前平台的全域 Skill／Plugin 環境，找到 `i-have-adhd` 後為 Coordinator 呼叫。Coordinator 的使用者回報遵循以下方式：

- 省略思考過程、重複說明及逐步操作紀錄。
- 每張 Ticket 完成後，用一至兩句說明成立的結果及下一張工作。
- 工作受阻、需要使用者決定、使用者詢問進度或全部完成時，提供當下需要的細節。
- 詳細變更與驗證集中在最終 HTML 報告。

以上兩處都確認找不到 `i-have-adhd` 時，沿用本節格式繼續執行。

## 執行環境

每張尚未派發的 Ticket 開始派工前，只檢查 `<專案根目錄>/.milktea/agent-settings.yaml`，不搜尋其他位置。檔案不存在時，執行環境使用 `auto`，Developer 使用 `claude`，Reviewer A 與 Reviewer B 使用 `codex`；檔案存在時，使用其中明確設定的共同執行環境，以及三個角色的 Agent、CLI、模型與推理強度，未設定的角色 CLI 仍使用上述預設。只有設定檔明確寫入 `cli: auto` 時才自動選擇該角色的 Agent／CLI。後來更新的設定只影響尚未派發的 Tickets。

確認設定或自動選定的環境可讀寫、必要命令可執行，並盤點可建立的 Agent 與可用並行數。預設或明確設定的 `claude`／`codex` 無法使用時，說明原因並停止派發受影響的 Ticket，不自行換到其他 Agent、CLI、模型或推理強度；只有明確的 `auto` 模式可以在可用選項中自動選擇。自動環境有多個可行選項，且選擇會實際改變工具、相依套件或執行結果時，才詢問使用者。

保留工作樹中既有的使用者變更。Git Commit、Push、Merge、Rebase 或其他會改變遠端或分支歷史的操作，依使用者授權及專案指令執行。

## 角色與 Developer 路由

每張 Ticket 使用一個新的 Developer、Reviewer A 與 Reviewer B。三個角色使用彼此隔離的 Agent 上下文；Reviewer A 與 Reviewer B 都必須完成各自 Review。

- Developer：完成 Ticket，開始前呼叫目前平台可用的 Ponytail `full` 模式；適用時使用 `milktea-skills-tdd`，遇到非預期錯誤時使用 `milktea-skills-debug`，實際發生 Git 衝突時使用 `milktea-skills-git-merge-conflict`。
- Reviewer A：使用 `milktea-skills-code-review` 執行 Spec Review，檢查成果與驗收條件是否成立。
- Reviewer B：使用 `milktea-skills-code-review` 執行 Standards Review，檢查正確性、可讀性、架構、安全與衍生問題；Open Code Review 可作為 Reviewer B 的選用輔助。

使用者明確設定的三個角色配置優先。角色 CLI 未設定時，Developer 固定使用 `claude`，Reviewer A 與 Reviewer B 固定使用 `codex`；Reviewer 未明確指定模型或推理強度時，使用 Codex 後端預設值，不依 Ticket 難度換 Reviewer。Developer 的 CLI 與模型路由分開處理：CLI 依設定或上述預設決定；未明確指定 Developer 模型時，仍在每張 Ticket 派工前依 Ticket、Spec 與相關程式碼選擇模型：

- 工作明確、局部、低風險，有相鄰實作可沿用及快速驗證，且不涉及跨模組設計、Schema、Migration、權限、安全、資料風險或公開介面：使用較快的可用開發模型；Claude 使用 Sonnet 5／high。
- 其他工作或難度無法確定：使用能力最強的可用開發模型；Claude 使用 Opus 5／high。

明確指定 Developer 模型時，不套用難度選模；首次派工前簡短提醒可移除模型設定以恢復自動難度分派，但不等待回覆，仍依使用者設定繼續。只固定 Developer CLI 不會關閉難度選模。

每次派發 Developer 或 Reviewer 前，記錄設定來源（預設或設定檔路徑）、角色、實際 Agent／CLI、實際模型、實際推理強度。Developer 另記錄難度判定（低風險或高／不確定）、判定依據及選模理由；Reviewer 記錄「不適用難度路由」。無法取得實際模型或推理強度時如實記錄 `unknown`，不得把預期值當成執行證據。

Developer 提供可重現的能力不足證據、核心實作方法被有效 Finding 證明不可行，或同一有效 Finding 經修正仍無法解決時，改由新的更強 Developer 接手相同 Ticket 與既有證據；Claude 使用 Opus 5／xhigh。已使用最強配置時，依實際阻擋繼續查證或請使用者決定。

外部 Skill 不可用時簡短標示實際狀態，使用目前可用能力完成相同責任；Code Review 無法由兩個隔離 Reviewer 完成時，回報實際阻擋。

## 證據共識

每張 Ticket 的三方是 Developer、Reviewer A 與 Reviewer B。Coordinator 不加入投票，而是中立檢查三方是否根據同一個 Snapshot、Spec 與可重現證據作出結論。

- Reviewer 的 Finding 是需要驗證的主張，不是 Developer 必須直接照做的命令。
- Developer 必須重現 Finding；成立就修正，不成立就以測試、程式行為、Spec 或正式文件提出反證。
- Reviewer 必須針對修正或反證定向複驗，依證據關閉、撤回或保留 Finding。
- 結論衝突時，Coordinator 檢查雙方證據，要求最小辨別測試或執行必要的唯讀驗證；證據不足的一方必須補充證據或修正結論。
- 只有缺少產品選擇、需求範圍、公開行為或不可逆風險的決定時，才交由使用者裁決。

## 安全並行

讀取全部 Tickets，將 `Blocked by` 已完成的 Ticket 放入 Ready Queue。

派工前依必要寫入範圍及相關程式碼確認預期修改位置與排他資源。互不衝突的 Tickets 同時派發；存在重疊或無法安全判定時依序執行。使用平台目前實際可用的 Agent 數量，不固定並行數，也不為填滿空位建立沒有獨立成果的 Agent。

每張 Ticket 完成、受阻或釋放修改範圍後，重新計算 Ready Queue，立即安排新解鎖且可安全執行的工作。

## Ticket 執行流程

1. 為 Ready Ticket 記錄基準版本及本次預期修改範圍，選擇 Developer 配置。
2. 把 Spec、Ticket、相關程式碼、專案指令、基準、修改範圍及驗收條件交給新的 Developer。
3. Developer 完成最小且完整的實作，執行與風險相稱的驗證，回報變更摘要、實際 Diff、驗收證據及已知風險。
4. 固定該 Ticket 的 Review snapshot，將相同 Snapshot 同時交給 Reviewer A 與 Reviewer B；並行數不足時依序派發，兩位 Reviewer 的首輪結論彼此獨立。
5. Reviewer 只回報有證據的 Findings；沒有 Finding 也是有效結果。Coordinator 將 Findings 逐項交回原 Developer。
6. Developer 重現每個 Finding，成立時修正並提供新證據，不成立時提出可重現反證。原 Reviewer 只複查自己提出的 Finding，直到確認關閉或撤回。
7. 交付成果與驗收條件成立、必要驗證完成，且兩位 Reviewer 都沒有未解決的阻擋或重要 Finding 後，完成該 Ticket，釋放修改範圍並更新 Ready Queue。

需要外部事實時先直接查證；只有成果需要保留一份可重用的正式研究文件時，才呼叫 `milktea-skills-research`。

## 需要使用者決定的情況

在核准範圍內持續處理一般錯誤、測試失敗與 Review Findings。下列情況以實際證據說明目前結果、選項與建議，再請使用者決定：

- 需求或驗收條件存在多種會產生不同可觀察結果的合理解讀。
- 下一步會改變已核准範圍、公開介面、資料模型或使用流程。
- 下一步涉及不可逆資料處置、安全接受程度或缺少必要外部權限。

## Context 與 Task 交接

預設在同一 Task 完成全部 Tickets。平台顯示 context 接近上限，或壓縮後繼續執行可能遺失必要資訊時，在目前 Ticket 完成後簡短告知：

```text
這張 Ticket 已完成。Context 已接近上限，建議從下一張改用新 Task；我會先繼續執行。需要交接時請回覆「換 Task」。
```

告知後直接繼續下一張 Ready Ticket。使用者沒有回應時維持目前 Task；使用者回覆「換 Task」時，完成正在執行的 Ticket，再輸出一份可直接貼到新 Task 的提示詞：

```text
請在新的獨立 Task 繼續以下工作：

/milktea-agents-skills-for-claude:milktea-skills-implement

專案根目錄：<實際路徑>
Spec：<實際路徑>
Tickets：<全部實際路徑>
目前 Branch／SHA：<實際值>
已完成 Tickets：<編號、成果與主要驗證>
尚未完成 Tickets：<編號與 Blocked by 判定>
目前工作樹：<實際 Diff 或修改檔案>
未解決 Findings／阻擋：<實際內容或無>
下一步：<下一個可直接執行的行動>

先讀取以上檔案與目前工作樹，再依原 Spec 與 Tickets 繼續；保留既有變更，不重做已完成工作。
```

## 最終驗收與報告

全部 Tickets 完成後，依原始需求、Spec 與 Tickets 進行一次總驗收。使用者介面需求使用實際可用的瀏覽器或電腦操作能力驗證主要操作流程；其他需求使用適合該成果的測試、命令或可重現操作驗證。

成果包含可操作的使用者介面時，Coordinator 必須啟動實際系統，使用目前平台可用的瀏覽器或電腦操作能力，依 Spec 實際點擊、輸入並走完主要操作流程；自動化測試、API 呼叫或 `curl` 只能作為補充。Agent 驗證通過後，開啟實際頁面並提供網址與簡短檢查項目，請使用者進行一次最終視覺確認。使用者尚未回應時，先完成所有仍可繼續的工作，只在整個 Task 結束時等待確認。平台沒有可用的瀏覽器操作能力時，直接說明無法完成這項驗收，不宣稱通過。

在 `docs/work/<功能名稱>/completion-report.html` 產生一份簡潔的繁體中文完成報告，依實際專案內容組織，讓使用者可以直接看到：

- 本次實際使用的執行環境，以及每張 Ticket 的 Developer、Reviewer A、Reviewer B 實際 Agent、CLI、模型與推理強度。
- 原始需求逐項為「完成」、「部分完成」、「未完成」或「範圍外」。
- 實際修改內容及使用者可感受到的結果。
- 驗收方式、實際結果與兩位 Reviewer 結論。
- 未完成項目、已知風險、回復方式及建議檢查步驟。
- 需要使用者確認的畫面、實際網址與簡短檢查步驟。

報告只使用可重現證據；缺少修改前基準時不建立虛構數字。完成後在聊天中顯示總體結果與 HTML 的實際路徑。

## 完成條件

- Spec 的核准範圍已由 Tickets 完整交付。
- 每張 Ticket 的驗收條件都有可重現證據。
- Developer、Reviewer A 與 Reviewer B 已對最終 Snapshot、驗收結果，以及所有阻擋或重要 Findings 達成有證據的共識。
- 適用的使用者操作流程已實際驗證。
- 最終 HTML 報告已產生並可直接開啟。
