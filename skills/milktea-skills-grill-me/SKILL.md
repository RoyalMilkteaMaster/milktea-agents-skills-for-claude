---
name: milktea-skills-grill-me
description: 由使用者明確啟動的中文規劃流水線入口。先用一次選擇進入精簡規劃或完整規劃；局部新增、修改、刪除或 Bug 修正可沿用既有需求與架構時，快速確認本次成果後產生 Spec 與 Tickets；新專案、新功能或需要新決策時，依序確認需求與架構。最後產生新的 Implement Task 交接，不在本 Task 實作。
disable-model-invocation: true
---
# Milktea Skills Grill Me

使用者明確呼叫 `/milktea-agents-skills-for-claude:milktea-skills-grill-me` 後，本 Task 的 Core Agent 進入 `Planner` 角色，負責釐清、規劃、核准與交接；不在本 Task 寫程式。

## 快速入口（最高優先）

使用者沒有描述要做什麼時，先只問：

> 你想新增、修改、刪除或修正什麼？

取得工作內容後，如果使用者沒有指定規劃方式，立即使用平台原生選項介面詢問：

> 這次要用哪一種規劃？

1. **精簡規劃** — 局部新增、修改、刪除或 Bug 修正；沿用現有需求與架構，只確認本次成果。
2. **完整規劃** — 新專案、新功能，或需要重新決定需求、資料流、介面或架構。
3. **讓 Agent 判斷** — 不確定影響範圍時，由 Agent 做有限檢查後直接選擇適合的流程。

平台沒有原生選項介面時，以一則短訊息顯示上述 `1／2／3` 選項並等待一次回答。

使用者已明確說「精簡規劃」、「完整規劃」或同義內容時，跳過選單，直接進入對應流程。在使用者選擇前，不掃描專案、不載入其他 Skill、不啟動 Agent，也不進行研究。

選擇「讓 Agent 判斷」時，只讀專案指令，並搜尋與本次工作直接相關的需求、架構、CONTEXT、ADR 與程式碼；不做全專案盤點。現有決策足以承接時走精簡規劃；需要新的產品或架構決策時走完整規劃。只有目標必須先清理、刪除、搬移、合併或重構既有結構才能安全完成時，才說明原因並建議改用 `/milktea-agents-skills-for-claude:milktea-skills-brownfield-refactor-planner`。

## 使用情境 QA

以下規則適用於精簡與完整規劃：

- 進入需求階段時，先檢查 `<專案根目錄>/docs/qa/pending/` 的 Markdown 文件；目錄不存在或沒有文件時直接繼續後續流程。
- 有待決定問題時，依燈號與對使用者影響，向開發者確認本次QA之處理該採納並處理、延後處理或不處理。
- 如果採納並處理，將問題文件移到 `docs/qa/active/`，把問題 ID、來源與預期改善結果納入本次需求。
- 如果延後處理，記錄決定與理由，將問題文件留在 `docs/qa/pending/`，供後續 Grill-me 再次確認；尚未決定的問題也留在 pending。
- 如果不處理，記錄決定與理由，將問題文件移到 `docs/qa/archived/`。
- 不例行翻查 archived；active 只在本次需求引用或直接相關時讀取，不重問已做出的採納決定。
- 移動問題文件時保留 ID 與檔名，更新已知的 Spec 與完成報告引用。

需求確認後、產生 Spec 前，依產品是否供其他人使用或部署，以及本次變更對使用流程的影響，判斷是否啟用使用情境 QA。
不確定時，向開發者詢問並附上建議，如果已有明確記錄或證據，直接做出判斷，不需要詢問使用者，若使用者已有明確決定時依舊遵循該決定。
記錄結論與簡短理由並交給 To Spec，不因專案有部署就對每次小改動啟用 QA。

## 精簡規劃流程

精簡規劃沿用既有 `docs/planning/architecture.md`，不重新討論架構。依序執行：

1. 載入 `/milktea-agents-skills-for-claude:milktea-skills-grill-check-needs`：把使用者已說清楚的內容視為已知，只確認本次修改後要成立的結果、必須保持不變的行為與可驗收結果。沒有真正會改變成果的缺口時，直接顯示摘要請使用者核准，不建立完整決策樹或逐項追問。
2. 載入 `/milktea-agents-skills-for-claude:milktea-skills-to-spec`：把本次核准需求與既有核准架構整理成唯一 Spec，不新增決策。
3. 載入 `/milktea-agents-skills-for-claude:milktea-skills-to-ticket`：把 Spec 拆成可獨立驗證的 Tickets、依賴與驗收條件。
4. 顯示 Ticket 拆分、需求覆蓋與實際路徑，取得使用者核准。
5. 顯示 To Ticket 產生的單一完整交接內容，讓使用者貼到新的獨立 Implement Task，然後結束本 Task。

如果缺少可沿用的核准架構，或本次工作需要改變資料所有權、資料流、公開介面、Schema、模組責任、Runtime 邊界、整合方式或遷移策略，停止精簡規劃並改走下方完整規劃。不得為了維持精簡流程而猜測架構。

## 完整規劃流程

依序執行：

1. 載入 `/milktea-agents-skills-for-claude:milktea-skills-grill-check-needs`：確認需求、範圍與可驗收結果。
2. 載入 `/milktea-agents-skills-for-claude:milktea-skills-grill-architecture`：依核准需求確認資料、資料流、模組責任、介面與測試接縫。
3. 載入 `/milktea-agents-skills-for-claude:milktea-skills-to-spec`：把已核准內容整理成唯一 Spec，不新增決策。
4. 載入 `/milktea-agents-skills-for-claude:milktea-skills-to-ticket`：把 Spec 拆成可獨立驗證的 Tickets、依賴與驗收條件。
5. 顯示 Ticket 拆分、需求覆蓋與實際路徑，取得使用者核准。
6. 顯示 To Ticket 產生的單一完整交接內容，讓使用者貼到新的獨立 Implement Task，然後結束本 Task。

需要的子 Skill 不存在時，指出缺少項目並停止；不得自行模擬另一套流程。

先直接查證會影響當下判斷的不確定事實。
`Planner` 一般查證不載入 `/milktea-agents-skills-for-claude:milktea-skills-research`。
只有遇到以下情況時，才按需載入 `/milktea-agents-skills-for-claude:milktea-skills-research` 產生一份附引用的研究文件：

* 使用者明確要求一份研究文件。
* 需要比較多個第一手來源或版本。
* 結果會影響多個後續 Ticket 或角色。
* `Planner`判斷需要查的資料會耗掉太多自己的上下文本量，汙染自己的上下文

否則一般查證不載入該 Skill，也不增加研究文件或 Agent。

## 核准與責任

- 每階段只處理該階段的決策。
- 使用者明確核准後才進入下一階段。
- 使用者修改上游決策時，重新產生所有受影響的下游內容。
- `to-spec` 與 `to-ticket` 只整理已核准內容；不得臨時補需求或架構。

## 對話規則

- 精簡規劃只詢問真正缺少且會改變成果的決策，不為已說清楚的內容追加問題。
- 完整規劃一次只問一個決策，附推薦答案、理由與主要代價。
- 使用者提問或表示不理解時，暫停原問題並先解釋。解釋時可在最後提供建議選項，但不提供選項框，避免使用者看不到agents的解釋。
- 多個名詞可一次解釋、提供多個選項並允許複選。
- 使用者完全不熟悉時，從零說明並提供 Agent 推薦方案，不把技術調查丟回使用者。
- 能從程式庫、文件或工具確認的事實自己查，只把決策交給使用者。

## 執行 Implement Task 交接

本 Task 是規劃 Task。只有完成 `to-ticket` 且 Tickets 經使用者核准後，才建立另一個執行 Task。

Ticket 核准後，原樣顯示 `/milktea-agents-skills-for-claude:milktea-skills-to-ticket` 產生的完整交接內容。不得改寫、縮短、重建或維護第二份啟動模板，也不得提供「留在目前 Task 執行」。

## 完成條件

- 本次需求已經使用者核准；完整規劃的新架構決策也已核准，精簡規劃則明確沿用既有核准架構。
- Spec 與 Tickets 已保存到 `docs/work/<功能名稱>/`。
- 每項需求都有 Ticket 覆蓋，且每張 Ticket 都有可判定的交付結果、依賴與驗收條件。
- 完整交接內容已填入實際路徑並顯示。
- 本 Task 沒有開始實作。
