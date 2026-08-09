---
name: milktea-skills-html-report
description: 提供 Milktea 的繁體中文 HTML 報告能力：Implement 執行中以 Ticket 為唯一來源提供 SSE 非同步進度頁；Brownfield Planner、Grill-me、Implement 與 Brownfield Implement 則依明確呼叫者及生命週期產生報告。結案內容先寫候選檔，嚴格驗證後才原子發布不可覆寫的正式報告。
---
# Milktea HTML 報告

## 進度頁入口

Implement 或 Brownfield Implement 啟動後可以立即讀取 `references/progress.md`，使用 `assets/progress.html` 與 `scripts/progress_server.py` 建立 `<實際工作目錄>/progress-report.html`。

- 進度頁只讀 Spec、Tickets 與既有結案報告，不新增需求或結論。
- Ticket 是唯一進度來源，不接受另一份手動維護狀態。
- 使用 SSE 非同步推送；前端禁止輪詢、自動重新整理或整頁重載。
- 進度頁不是下列結案報告入口，不需要假裝已到達完成階段。

## 唯一入口

呼叫者必須同時提供：

- 呼叫者識別。
- 已到達的觸發階段。
- 專案或功能名稱。
- 輸出路徑。
- 內容證據及其來源。

缺少呼叫者識別、使用未知識別，或尚未到達指定階段時，立即停止並回報實際缺口；不得從對話猜測，也不得改用其他報告。

## 快速路由

先讀 references/共用規則.md，再依呼叫者只讀一份專屬報告原則與一份專屬模板：

| 呼叫者識別           | 呼叫階段                                                 | 報告原則                           | 報告模板                         |
| -------------------- | -------------------------------------------------------- | ---------------------------------- | -------------------------------- |
| brownfield-planner   | 唯讀架構盤點完成，等待使用者決定是否繼續                 | references/brownfield-planner.md   | assets/brownfield-planner.html   |
| grill-me             | Spec 已核准且全部 Ticket 草稿文件已完整，等待使用者核准實作 | references/grill-me.md             | assets/grill-me.html             |
| implement            | 全部 Tickets、Review、修正、複驗、原生瀏覽器操作與最終驗收均已完成       | references/implement.md            | assets/completion.html           |
| brownfield-implement | 全部重構 Tickets、Review、原有功能、原生瀏覽器操作與最終驗收均已完成 | references/brownfield-implement.md | assets/completion.html           |

呼叫者不得讀取或混用另外三份專屬規格與模板。

## 執行順序

1. 驗證呼叫者識別與觸發階段。
2. 讀取共用規則與唯一對應的專屬規格。
3. 檢查必要輸入與證據；不足時回傳缺口，不補造內容。
4. 依平台規則選擇設計輔助。
5. 使用唯一對應模板產生 HTML。Implement 或 Brownfield Implement 只能先寫入 `<實際工作目錄>/completion-report.pending.html`。
6. Grill-me 與 Brownfield Planner 都必須傳入 `--project-root <專案根目錄> --work-id <工作識別碼>` 執行 `scripts/validate_report.py`，強制核對唯一報告路徑、HTML 識別與對應工作包。結案報告執行 `scripts/validate_report.py <候選檔> --caller <呼叫者> --work-dir <實際工作目錄> --candidate --publish`；這會使用同一批已驗證位元組原子建立正式檔，且永不覆寫既有正式檔。
7. 驗證失敗時只修正候選檔；通過並發布後刪除候選檔，才回傳正式 `completion-report.html` 路徑。

## 平台規則

### Claude Code

預設使用目前環境已提供的官方 frontend-design 技能協助視覺設計，但不得讓它改寫事實、需求、數據或結論。成功使用時，在報告中標示「設計輔助：Claude Design」。

若 frontend-design 不存在或無法使用：

- 不自動安裝。
- 改用對應的內建模板。
- 在報告中標示「設計輔助：內建模板（Claude Design 無法使用）」。

### Codex

- 不搜尋、不呼叫、不安裝 Claude Design 或 frontend-design。
- 固定使用對應的內建模板。
- 在報告中標示「設計輔助：內建模板」。

## 寫入邊界

- 進度階段只寫入 `<實際工作目錄>/progress-report.html`；它可以依 Ticket 更新，不能宣告完成。
- Brownfield Planner 與 Grill-me 在同一核准階段修訂時覆寫同一檔案，不建立 final、new、v2 等副本。
- Implement 與 Brownfield Implement 在全部 Tickets、Review、修正、複驗及最終驗收完成前，不得產生 `completion-report.pending.html` 或正式報告。到達結案觸發階段後才先寫候選檔；正式 `completion-report.html` 只能由驗證器在全部嚴格閘門通過後原子發布，且不得覆寫。目標已存在時停止。
- Reviewer A 與 Reviewer B 保持唯讀；報告由呼叫流程的 Coordinator 寫入。
- 單張 Ticket 完成、單次 Review、修正或複驗只更新進度頁，不產生結案報告。
- 報告驗證失敗時不得宣稱該階段已完成。

## 回傳格式

只把下列資料交回呼叫者：

- 驗證結果。
- HTML 絕對路徑。
- 若失敗，最重要的缺口或錯誤。

由呼叫者依自己的專屬規格向使用者顯示連結與必要選項；本技能不在聊天框重述整份報告。
