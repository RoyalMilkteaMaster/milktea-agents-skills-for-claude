---
name: milktea-skills-html-report
description: 依明確呼叫者識別，為 Brownfield Planner、Grill-me、Implement 或 Brownfield Implement 產生各自不同的繁體中文 HTML 報告。四個流程只有在規定階段才可呼叫；本技能負責快速路由到單一專屬規格與模板，不新增事實、不修改需求、不進行架構決策或實作。
---
# Milktea HTML 報告

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
| grill-me             | Spec 與全部 Tickets 已完成，等待使用者核准實作           | references/grill-me.md             | assets/grill-me.html             |
| implement            | 全部 Tickets、Review、修正、複驗與最終驗收均已完成       | references/implement.md            | assets/implement.html            |
| brownfield-implement | 全部重構 Tickets、Review、原有功能確認與最終驗收均已完成 | references/brownfield-implement.md | assets/brownfield-implement.html |

呼叫者不得讀取或混用另外三份專屬規格與模板。

## 執行順序

1. 驗證呼叫者識別與觸發階段。
2. 讀取共用規則與唯一對應的專屬規格。
3. 檢查必要輸入與證據；不足時回傳缺口，不補造內容。
4. 依平台規則選擇設計輔助。
5. 使用唯一對應模板產生 HTML。
6. 執行 scripts/validate_report.py，傳入相同呼叫者識別。
7. 驗證失敗時修正同一份報告；通過後才回傳路徑給呼叫者。

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

- 只寫入呼叫者提供的單一報告路徑。
- 同一階段修訂時覆寫同一檔案，不建立 final、new、v2 等副本。
- Reviewer A 與 Reviewer B 保持唯讀；報告由呼叫流程的 Coordinator 寫入。
- 不因單張 Ticket 完成、單次 Review、修正或複驗而產生報告。
- 報告驗證失敗時不得宣稱該階段已完成。

## 回傳格式

只把下列資料交回呼叫者：

- 驗證結果。
- HTML 絕對路徑。
- 若失敗，最重要的缺口或錯誤。

由呼叫者依自己的專屬規格向使用者顯示連結與必要選項；本技能不在聊天框重述整份報告。
