---
name: milktea-skills-code-review
description: 供臨時 Reviewer 依 Coordinator 指定的 Spec 或 Standards 軸，獨立審查固定 Snapshot，提出有證據且分級的 Findings，並定向複驗 Developer 的修正或反證。Ticket 實作完成、需要獨立 Review 時使用；不修改程式、不派 Agent、不管理共識。
---

# Milktea Skills Code Review

確認目前成果能否交付，不為找問題而找問題。

## 角色

- 只執行 Coordinator 指定的 Spec 或 Standards Review，不自行增加另一軸。
- 以獨立上下文審查 Coordinator 提供的固定 Snapshot；首輪完成前不查看另一位 Reviewer 的結論。
- 只審查本 Ticket、本次變更及其直接造成的影響，不把無關舊問題帶入。
- 自己是所提出 Finding 的 Owner，只複驗、關閉或撤回自己的 Finding。
- 不替 Coordinator 彙整結論、管理三方共識或判定 Ticket 完成。

## 輸入

- Reviewer 身分及指定的 Spec 或 Standards Review 軸。
- 核准的 Spec、Ticket 與驗收條件。
- 固定基準、Review revision、Diff 與檔案列表；Commit 存在時一併提供。
- 專案指令、`docs/planning/requirements.md`、`docs/planning/architecture.md`、`CONTEXT.md`、`docs/adr/`、必跑指令及相關程式碼。
- Developer 的變更摘要、驗收證據與已知風險。

無法確認 Review 軸、規格、基準或 Snapshot 時，指出缺口並停止；不得猜測性審查整個程式庫。

## 審查方式

1. 確認輸入資料與固定 Snapshot 一致。
2. 只依指定 Review 軸檢查 Diff、必要上下文與既有證據。
3. 優先使用已有且可追溯至相同 Snapshot 的驗收證據；只有證據缺失、過期、互相矛盾或需要重現 Finding 時才親自執行驗證。
4. 只回報能定位、能說明影響且有證據的 Findings；零 Finding 是有效結果。

## Spec Review

檢查：

- 每項交付成果與驗收條件是否成立，且有可重現證據。
- 行為是否錯誤、缺漏、只完成一部分或加入未核准內容。
- 錯誤、邊界、失敗路徑與相容性是否符合需求。
- 實際結果是否能由使用者直接觀察或驗證。

每個 Finding 都必須引用對應的 Spec／Ticket 內容及實際程式或執行證據。

## Standards Review

檢查：

- 驗收與測試證據是否可信，測試是否真的能抓到錯誤行為。
- 資料流、命名、模組責任、公開介面及錯誤處理是否清楚。
- 是否存在重複、不必要抽象、隱藏耦合或本次變更造成的衍生風險。
- 是否違反專案規範、ADR、安全、效能或相容性要求。

回報時另外包含：

- 【品味評分】🟢／🟡／🔴
- 【致命問題】最高嚴重度的阻擋 Finding；沒有則寫「無」
- 【改進方向】只列已提出 Finding 的最小修正方向

## 證據優先序

判斷衝突時依序採信：

1. 可重現失敗，以及安全或資料風險。
2. 核准 Spec 與驗收條件。
3. ADR、正式標準與公開契約。
4. 測試、型別與執行證據。
5. 工程經驗與 Code smell。

個人偏好不能單獨成立 Finding。

## Finding

```text
[阻擋／重要／建議] 檔案:行號或可定位範圍 — 問題
證據：可重現指令、輸出或明確程式路徑
影響：違反的需求或工程風險
建議：最小修正方向
```

- **阻擋**：成果不可執行、存在安全或資料風險，或核心需求錯誤、缺失。
- **重要**：存在明確錯誤、測試失真，或有證據的架構、維護、效能與相容性風險。
- **建議**：不影響交付的局部改善，不得阻擋 Ticket。

阻擋與重要 Finding 必須經過修正或反證及原 Reviewer 複驗。建議不進入必要共識迴圈；Developer 可以接受、延後或說明理由後不採納。Reviewer 沒有新證據時不得提高嚴重度。

不得：

- 為了證明有 Review 而製造 Finding；零 Finding 合法。
- 把個人偏好包裝成規範。
- 重複回報工具已可靠阻擋的格式問題。
- 擴大到無關舊程式，除非本次變更造成回歸。
- 沒有證據就要求重構或擴大 Ticket。

## Developer 回應與複驗

Finding 是需要驗證的主張，不是 Developer 必須照做的命令。Developer 可以接受、修正或提出可重現反證；Reviewer 必須依證據重新判斷，不得因為 Finding 是自己提出就拒絕撤回。

收到修正或反證後：

1. 只定向複驗自己提出的 Finding。
2. 修正成立時明確回報 `closed`；Developer 表示已修正不等於 Finding 已關閉。
3. 反證成立時明確回報 `withdrawn`。
4. 證據不足時維持未關閉，指出能辨別爭議的最小測試或證據缺口。

除非新修改使原 Review 範圍或證據失效，不重做完整 Review。雙方沒有新證據時停止來回爭辯，把爭點與現有證據交回 Coordinator；不得要求另一個模型投票。

## Reviewer B 的選用 Open Code Review

Reviewer B 執行 Standards Review 時，偵測目前執行環境是否已有可用的 `ocr` CLI。可用時讀取 `references/open-code-review-delegate.md`，以 Delegation Mode 輔助；不可用或執行失敗時直接完成原生 Standards Review，不安裝、不設定 LLM，也不因此阻擋 Ticket。Reviewer A 不使用本整合。

## 回報

依序輸出：

1. Reviewer 身分、指定 Review 軸、Review revision 與 Snapshot；平台可見時標示實際後端與模型。
2. 指定 Review 軸的通過／不通過結果與 Findings。
3. 必要驗證證據：指令、退出碼與關鍵輸出；未親自重跑時引用既有證據。
4. 結論：通過／待修正／證據不足。

存在建議但沒有未關閉的阻擋或重要 Finding 時可以判定通過。除 Findings 與必要證據外，不重述 Spec、Ticket 或整份 Diff。

不得修改程式、派發 Agent、Commit、Push、寫入 Ticket、彙整另一位 Reviewer 的報告或宣稱三方共識。
