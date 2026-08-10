# Reviewer B 的 Open Code Review Delegation Mode

只在目前執行環境已能直接呼叫 `ocr` 時使用。Open Code Review 只負責選擇檔案與解析規則；Reviewer B 仍以自己的能力完成 Standards Review 並對結論負責。

## 邊界

- 不安裝或更新 OCR，不執行 `ocr review`，不設定 LLM，也不要求 API Key。
- 不修改 `.opencodereview/`、專案檔案、Git 狀態或 Ticket。
- OCR 不可用、版本不支援 Delegation Mode 或命令失敗時，記錄實際錯誤並改用原生 Standards Review。
- OCR 的檔案選擇與規則不能縮小 Coordinator 指定的固定 Snapshot，也不能取代 Spec、Ticket、專案規範或 ADR。

## 流程

1. 在與固定 Snapshot 相同的專案與執行環境確認 `ocr` 可用，並執行 `ocr version` 記錄實際版本。
2. 依 Snapshot 執行其中一種 Preview：
   - 工作區：`ocr delegate preview --repo <專案根目錄>`
   - Revision 範圍：`ocr delegate preview --repo <專案根目錄> --from <來源> --to <目標>`
   - 單一 Commit：`ocr delegate preview --repo <專案根目錄> --commit <SHA>`
3. 確認 Preview 的模式、Revision、Reviewable 與 Excluded 檔案沒有偏離固定 Snapshot；不一致時停止使用 OCR，改回原生 Review。
4. 對 Reviewable 檔案執行 `ocr delegate rule --repo <專案根目錄> <路徑...>`，把規則結果當成額外檢查清單。
5. Reviewer B 親自閱讀固定 Diff 與必要上下文，驗證問題並使用 Milktea 的阻擋／重要／建議格式。OCR 輸出本身不是 Finding。

回報時附上 OCR 版本、實際命令，以及 Reviewable／Excluded 檔案；Excluded 檔案仍依 Ticket 影響使用原生方式檢查。
