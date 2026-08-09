# 功能實作結案報告契約

## 用途與產生時間

證明本次工作包的原始需求、Tickets、Review、修正、定向複驗及最終總驗收已完成。只有呼叫者識別為 `implement`，且整個工作沒有執行中、Review 中、修正中、阻擋或未完成 Ticket 時才能產生。

先寫入 `<實際工作目錄>/completion-report.pending.html`。使用 `--candidate --publish` 嚴格驗證並原子發布後，使用者才會得到 `<實際工作目錄>/completion-report.html`；正式檔已存在時必須停止，不得覆寫。

## 必要輸入

- 工作識別碼、繁體中文顯示名稱與實際工作目錄。
- 使用者全部原始需求，不以 Agent 摘要取代。
- 核准 Spec、全部 Tickets、實際差異與版本。
- 測試、Reviewer、Finding、修正、定向複驗及未解風險。
- 每張 Ticket 的前端實際操作適用性、判定依據與實際證據。
- Spec「原始需求」內每項 `R-xxx`，以及每張 Ticket 的精確完成證據：`Developer 結論`、`Reviewer 模式`、Reviewer A／B 結論、`未關閉阻擋或重要 Findings` 與 `Ticket 最終驗收`。

## 需求驅動內容

報告使用彈性 HTML 外殼，不強迫固定專案章節。至少回答：

1. 最終結論：是否全部通過；任何一項未完成就不能產生本報告。
2. 原始需求：逐項顯示原文、實際結果與可重現證據。
3. Ticket 成果：白話說明每張 Ticket 做了什麼、狀態、Review 結論及是否超出範圍。
4. 實際驗收：必跑指令、退出碼、原生瀏覽器操作或不適用依據、Findings 關閉情況。
5. 風險與回復：未解風險、觸發條件、降低方式、回復步驟及回復後驗證。
6. 使用者確認：依原始需求提供逐項可勾選清單；這是使用者清點工具，不取代 Agent 已完成的技術驗收。

專案有可靠前後基準時才增加架構、資料流、改善數據或圖表。缺少基準時使用「無法量化：缺少修改前基準」，不得為符合版型製造數字。

## 精確驗證欄位

- Spec 文件前言的 `工作識別碼` 與 `狀態` 必須各自在前言與全文件恰好出現一次，且 `狀態` 精確為「已核准」。
- 每張 Ticket 的 `狀態` 只能在文件前言出現一次且精確為「完成」。`適用性`、`判定依據`、`使用的原生瀏覽器工具`、`操作環境與實際網址`、`操作步驟與預期結果`、`操作結果`、`操作證據` 只能在「前端實際操作驗收」各出現一次；下列 Developer／Reviewer／Finding／最終驗收欄位只能在「執行與 Review 紀錄」各出現一次。每個欄位在全 Ticket 也只能出現一次。適用時操作步驟必須實填且可執行；不適用時必須精確填「不適用」。
- Ticket 草稿已預先放入上述機器欄位時，實作流程必須原地替換其值；不得保留占位值後，又在文件尾端或其他章節追加同名欄位。重複值即使相同也不能通過。
- `Developer 結論` 與 `Ticket 最終驗收` 必須精確為「通過」；`未關閉阻擋或重要 Findings` 必須精確為 `0`。
- `Reviewer 模式` 只可為 `both`、`a_only` 或 `b_only`。啟用的 Reviewer 結論必須為「通過」，未啟用者必須為「不適用」。只有單一 CLI／平台時仍要保留獨立 Reviewer 角色與證據，不能跳過 Review。
- 前端適用時，`操作結果` 必須精確為「通過」，`操作證據` 另存自由文字；工具只填明確 allowlist：`Codex Browser`、`Codex 原生瀏覽器`、`Codex Chrome`、`Codex Computer Use`、`Claude Browser`、`Claude 原生瀏覽器`、`Claude Chrome`、`Claude Computer Use`，或實際工具識別 `browser:control-in-app-browser`、`chrome:control-chrome`、`computer-use:computer-use`。網址必須是實際 `http://`、`https://` 或 `file://` URL；`curl`、一般 HTTP 測試、提示字與假網址都不能通過。
- 每個 Spec `R-xxx` 至少要被一張 Ticket 以相同原文引用；不存在的 ID、改寫原文或零 Ticket 覆蓋都拒絕。報告的每個需求 checkbox 也必須使用同一組 `R-xxx` 且恰好一次。舊工作沒有 R 編號時，先依共用規則建立 `R-LEGACY-xxx` 對照。
- 所有動態文字先 HTML escape，只能填入模板純文字槽。每個 checkbox 的 `id` 必須等於 `data-requirement-id`，且只對應一個 label；label 精確顯示 `R-ID：Spec 原始需求原文`。不得預先勾選、停用、隱藏或用 CSS 讓使用者無法逐項操作。

## 狀態用語

原始需求狀態只使用「完成、部分完成、未完成、範圍外」。本報告只有全部核准需求均完成且驗收通過時才能產生；範圍外項目必須附核准依據。

## 聊天框

只顯示「最終驗收通過」及結案報告絕對路徑連結，不逐票重述證據。
