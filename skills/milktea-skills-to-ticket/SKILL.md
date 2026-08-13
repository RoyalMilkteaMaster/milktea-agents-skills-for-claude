---
name: milktea-skills-to-ticket
description: 將已核准的中文 Spec 拆成可獨立派工與驗證的垂直 Tickets，確認需求覆蓋、阻擋關係及必要寫入邊界，經使用者核准後固定寫入 docs/work/功能名稱/tickets/，並產生可貼到新 Implement Task 的交接文字。由 milktea-skills-grill-me 在拆票階段調用，或在使用者要求把已核准 Spec 拆成 Tickets 時使用；不決定模型、Reviewer、執行環境或實作方式，不開始實作。
---
# Milktea Skills To Ticket

把已核准 Spec 拆成短小、完整、可獨立驗證的垂直切片。Ticket 只描述要交付什麼，不承擔執行狀態、Agent 設定或 Review 紀錄，也不得重新設計需求或架構。

## 前提

- Spec 已核准並可直接開啟。
- 需求或架構仍有缺口時，指出應回到哪個規劃階段；不得在拆票時自行補決策。

## 儲存位置

- 沿用 Spec 所在的 `docs/work/<功能名稱>/`，把 Tickets 寫入 `tickets/<NN>-<slug>.md`。
- Ticket 從 `01` 依建議執行順序連續編號，不另建工作目錄。
- 核准前只在對話中顯示拆分；核准後才寫入 Ticket 檔案，不建立草稿、已核准、final 或其他平行版本。
- 不為拆票或交接執行 Git 操作。

## 流程

1. 讀取已核准 Spec、專案指令和相關程式碼；其他文件只在需要時讀取。
2. 把工作拆成多張 Tickets；每張都要交付一個完整、可驗證的結果，並能在一個新的執行 Task 內完成。
3. 標明每張 Ticket 必須等待哪些 Ticket 完成；沒有就寫「無」。
4. 多張 Ticket 可能同時修改相同位置時，標明衝突範圍；沒有風險就省略。
5. 確認 Spec 的每項需求與驗收條件都有 Ticket 負責，且沒有多加未核准工作。
6. 用編號清單顯示每張 Ticket 的名稱、交付成果、前置 Ticket 與需求覆蓋，讓使用者調整拆分、順序或依賴。
7. 使用者核准後，寫入 Tickets 並顯示全部實際路徑。
8. 產生填妥路徑的 Implement Task 交接文字；不建立 Task，也不開始實作。

## Ticket 格式

```markdown
# <NN> — <Ticket 標題>

- Spec：`../spec.md`
- Blocked by：無／<Ticket 編號與名稱>

## 交付成果

從使用者或系統行為描述這張 Ticket 完成後實際成立的結果。

## 驗收條件

- 使用可觀察、可操作或可重現的方式判定通過或失敗。

## 必要寫入範圍

- 只有存在實際平行衝突風險時才保留本節；否則省略。
```

## 拆票規則

- 優先拆成端到端可展示或驗證的垂直切片，不建立只完成單一技術層、沒有獨立成果的 Tickets。
- 每張 Ticket 只交付一個清楚結果；過大就拆分，無法獨立驗證的小票就合併。
- 不得因 Ticket 編號、建議順序、共用唯讀程式碼或尚未查證的可能衝突建立 `Blocked by`；拆票完成前必須最大化初始 Ready Tickets，只有後一張確實需要前一張產物或決策時才能建立依賴。
- 必要寫入範圍只在多張 Ticket 可能同時修改相同檔案、模組、資料或共用資源時填寫，用來提醒 Implement 避免衝突。它不是檔案白名單，也不規定模型、Agent、工具、執行順序或實作方法。
- 驗收條件必須描述可以直接觀察或重現的完成結果。「完成實作」只是在宣稱做完；「測試通過」可以作為證據，但不能取代功能本身應達成的結果。
- Ticket 只引用 Spec 已核准的內容；實作決策、研究資料或限制已在 Spec 中清楚說明時，不在每張 Ticket 重複抄寫。

## Implement Task 交接

由 Brownfield Refactor Planner 呼叫時，使用 `/milktea-agents-skills-for-claude:milktea-skills-brownfield-refactor-implement`，並在交接中加入 Planner 提供的 HTML 架構報告實際路徑。其他呼叫來源，包括 Grill-me 或使用者直接呼叫本 Skill，使用 `/milktea-agents-skills-for-claude:milktea-skills-implement`，並省略 HTML 架構報告一行。

Tickets 寫入後，以實際資料填妥並顯示以下唯一交接文字：

```text
請將以下內容完整貼到新的獨立 Task：

<Implement Skill>

專案根目錄：<實際路徑>
HTML 架構報告：<只有 Brownfield Refactor Planner 呼叫時填入實際路徑；其他情況省略此行>
Spec：<已核准 Spec 的實際路徑>
Tickets（依建議順序）：<全部 Ticket 實際路徑>

依已核准 Spec 與 Tickets 完成實作及驗收，不得自行擴大核准範圍。
```

不要改寫成另一份模板，也不要要求規劃 Task 繼續實作。

## 完成條件

- 使用者已核准 Ticket 粒度、依賴與需求覆蓋。
- Tickets 已寫入 Spec 所在工作目錄，且每張都有可判定的交付成果與驗收條件。
- 只有真正需要的 Ticket 包含必要寫入範圍。
- 已顯示實際 Ticket 路徑與完整交接文字。
- 尚未開始實作。
