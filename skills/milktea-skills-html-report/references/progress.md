# 實作進度頁

## 用途

在 Implement 或 Brownfield Implement 尚未完成時，只依工作目錄中的 Spec、Tickets 與既有執行證據，向使用者顯示現在做到哪裡。進度頁不是完成證明，也不能用來提前宣告驗收通過。

## 固定路徑

- 新工作：`docs/work/<工作識別碼>/progress-report.html`。
- 舊工作：沿用實際交接工作目錄下的 `progress-report.html`。

## 資料來源

- Spec 的工作識別碼、顯示名稱與核准需求。
- 每張 Ticket 的標題、狀態、目標、對應原始需求、執行與 Review 紀錄、阻擋與裁決紀錄。
- 同一專案 `docs/work/*/completion-report.html` 的既有結案報告。

不得另外建立第二套工作狀態、推測缺少的 Ticket 內容或把進度頁當成需求來源。

## 非同步更新

- 使用 `scripts/progress_server.py` 綁定 `127.0.0.1`，Port 傳入 `0` 讓作業系統配置可用 Port。
- 瀏覽器透過同源 SSE `/events` 接收更新；禁止前端輪詢、定時重新整理或整頁重新載入。
- 服務只提供唯讀的進度頁、快照與 SSE，不接受修改專案的 HTTP 請求。
- Ticket 更新後由服務重新讀取實際檔案並推送；HTML 同時保存最後快照，服務停止後仍可直接開啟。

## 阻擋顯示

一般 Bug 修正、測試失敗、Review Finding 與同一方案內的正常迭代不顯示成需要使用者裁決。只有需求存在多種合理解讀、驗收標準不明、多個有證據的方案都遇到相同根因，或下一步必須改變功能方向、範圍或使用體驗時，才顯示 Ticket 的完整「阻擋與裁決紀錄」。

## 完成邊界

進度頁可以顯示完成狀態及最終報告連結，但不能產生結論。`completion-report.html` 仍由 Implement 在全部完成規則成立後另行產生。
