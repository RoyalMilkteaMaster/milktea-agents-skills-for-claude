# Task 交接

只在實作藍圖 HTML 已通過驗證、使用者已核准、Tickets 已更新為「已核准」，且 `$milktea-skills-to-ticket` 已產生完整交接內容後讀取。交接內容是唯一 Task prompt；不得改寫或產生另一版本。

## 交付規則

1. 原樣顯示 `$milktea-skills-to-ticket` 產生的單一可複製文字區塊。
2. 文字區塊第一行必須是已核准實作藍圖的可開啟 HTML URL，第二行必須是同一份報告的 HTML 絕對路徑。
3. HTML URL 使用已實際驗證可開啟的報告 URL；沒有報告伺服器時使用由絕對路徑轉成的 `file:///` URL。URL 與絕對路徑必須指向同一檔案。
4. 所有平台一律讓使用者手動複製並貼到新的獨立 Task。
5. 不呼叫建立、開啟或切換 Task 的工具，不顯示自動建立選項，也不回報 `TASK_CREATION_UNAVAILABLE`。
6. 不啟動巢狀 CLI、不建立 Subagent 冒充新的 Core Task，也不留在 Planner Task 實作。
