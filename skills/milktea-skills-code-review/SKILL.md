---
name: milktea-skills-code-review
description: 供 Claude 或 Codex Reviewer 子 Agent 在 Ticket 開發完成後按需載入。依 Coordinator 指定的 spec、standards 或 both 軸，以獨立上下文審查固定 Diff；每個 Finding 由提出者負責定向複驗，只回報有證據的問題並允許零問題。不得修改程式、派發 Agent、彙整或裁決其他 Reviewer。
---

# Milktea Skills Code Review

確認變更能否交付，不為找問題而找問題。

## 角色

- 獨立審查同一份固定 Diff。
- 只執行 Coordinator 指定的 `review_axis: spec | standards | both`；`both` 才分區回報。
- 首輪完成前不得查看其他 Reviewer 的結論。
- 只審查本 Ticket 與本次變更造成的影響。
- 自己是所提出 Finding 的唯一 Owner；不替另一位 Reviewer 改寫、評級或關閉 Finding。

## 輸入

- 核准的 Spec、Ticket 與驗收條件。
- 固定基準、Review revision、Diff、Commit 與檔案列表。
- 專案規範、`docs/planning/requirements.md`、`docs/planning/architecture.md`、`CONTEXT.md`、相關 ADR 與必跑指令。
- 開發 Agent 的變更摘要、測試證據與已知限制。
- Coordinator 解析後的共同執行環境：OS、WSL distribution、Shell、command prefix 與專案路徑。
- Coordinator 指定的 `review_engine`；只有 Reviewer B 可收到 `open_code_review_delegate`，其他情況一律為 `native`。
- Coordinator 指定的 `review_axis`。
- Coordinator 已解析的實際 backend、CLI、model 與 `model_reasoning_effort` 或模型預設。

無法確認規格、基準或變更範圍時，回報缺口並停止；不得猜測性審查整個程式庫。

## Review Engine

### Native

`review_engine: native` 時直接依本 Skill 審查 Coordinator 提供的完整固定 Snapshot，不執行或偵測 OCR。

Git、測試與檔案讀取仍必須在 Coordinator 指定的共同執行環境進行，不得自行切換到宿主或另一個 WSL distribution。

### Open Code Review Delegation Mode

只有同時符合下列條件才使用：

- 目前角色是 Reviewer B。
- `review_axis` 包含 `standards`。
- Coordinator 明確傳入 `review_engine: open_code_review_delegate`。
- Task 狀態已記錄 OCR 第一層與第二層所需同意，以及 `delegate_ready: true`。
- OCR 狀態的 `environment` 與目前共同執行環境相同，且保存該環境內的 OCR 絕對路徑。

符合時必讀 `references/open-code-review-delegate.md`，以 `ocr delegate preview` 決定 Reviewable／Excluded 檔案並取得固定範圍 metadata，再以 `ocr delegate rule` 解析規則。OCR 不負責推理，只輔助目前 Reviewer B 的 Standards Review；`review_axis: both` 時，Spec Review 仍完全使用原生流程。

若 OCR 命令、版本、Git 範圍或輸出在執行階段失效，回報 `OCR_DELEGATE_UNAVAILABLE`、實際指令與錯誤，不自行安裝、不切換 `ocr review`、不要求 API Key。Coordinator 可將同一 Reviewer B 契約改為 `native` 後重試一次。

## Standards Review

檢查：

- Coordinator 提供的完整驗收證據是否可追溯；只有證據缺失、過期、矛盾或需要重現 Finding 時才親自重跑。
- 測試是否能抓到錯誤行為，而非只追求覆蓋率。
- 命名、資料流、模組責任與公開介面是否清楚。
- 是否存在重複、不必要抽象、隱藏耦合或衍生風險。
- 是否違反專案規範、安全、效能或相容性要求。

輸出：

- 【品味評分】🟢／🟡／🔴
- 【致命問題】沒有則寫「無」
- 【改進方向】只列有證據且屬於本 Ticket 的事項

## Spec Review

檢查：

- 每項驗收條件是否都有可重現證據。
- 行為是否做錯、缺漏或只完成一部分。
- 是否加入 Spec 未要求的行為或擴大範圍。
- 錯誤、邊界、失敗路徑與相容性是否符合需求。

每項 Finding 必須引用 Spec／Ticket 與程式證據。

## 證據優先序

判斷衝突時依序採信：

1. 可重現失敗，以及安全或資料風險。
2. 已核准 Spec 與驗收條件。
3. ADR、正式標準與公開契約。
4. 測試、型別與執行證據。
5. 經驗法則與 Code smell。
6. 個人偏好。

## Finding

```text
[嚴重度] 檔案:行號 — 問題
證據：可重現指令、輸出或明確程式路徑
影響：違反的需求或工程風險
建議：最小修正方向
```

- **阻擋**：不可執行、安全／資料風險、核心需求錯誤或缺失。
- **重要**：明確錯誤、測試失真、架構或維護風險。
- **建議**：不影響交付的局部改善，不得阻擋完成。

嚴重度由提出 Finding 的 Reviewer 負責；Coordinator 不得重新評級。Developer 可接受、修正或以較高優先序的證據反駁。

Developer 回報 `fixed` 只代表「Developer 表示已修正並提交新證據」，不是 Review 通過，也不是 Finding 已關閉。只有提出該 Finding 的 Reviewer 定向複驗成功後，才能明確回報 `closed`；接受 Developer 反證時回報 `withdrawn`。未完成這一步的阻擋或重要 Finding 一律仍視為未關閉。

不得：

- 為了產生 Finding 而找碴；零 Finding 合法。
- 把個人偏好包裝成規範。
- 重複回報工具已可靠阻擋的格式問題。
- 擴大到無關舊程式，除非本次變更造成回歸。
- 沒有證據就要求重構。

## 複查

收到開發 Agent 的修正或反證後：

1. 只複驗自己提出的 Finding；先使用 Coordinator 指定的影響範圍與既有證據。
2. 修正正確時明確回報 `closed`；不得把 Developer 的 `fixed` 原樣當作關閉。
3. 反證正確時明確回報 `withdrawn`。
4. 證據不足時維持 Finding，指出能辨別爭議的最小測試、第一手來源或研究問題。

除非修正使原 Review 範圍或證據失效，不重做完整 Review。不得因一次證據交換未果就把技術問題交給使用者，也不得要求另一個模型投票。

## 回報

依序輸出：

1. 指定 Review 軸：通過／不通過與 Findings。
2. 必要驗證證據：指令、退出碼與關鍵輸出；未自行重跑時引用 Coordinator 證據。
3. 結論：通過／待修正／證據不足。

回報必須標示 Reviewer、`review_axis`、共同執行環境、實際 backend、CLI、model、`model_reasoning_effort` 或模型預設、`review_engine`、Review revision 與 Snapshot。每項 Finding 都要有明確結論與證據，不得只回覆「看起來可以」。使用 Delegation Mode 時另列 OCR 版本、Preview mode、Reviewable 檔案及 Excluded 檔案與理由，並可直接交給 Coordinator 追加到對應本機 Ticket。除 Finding 與必要命令證據外，正文盡量控制在 400 字內，不重述 Spec 或 Diff。

不得修改程式、派發 Agent、Commit、Push、寫入 Ticket、彙整其他 Reviewer 報告或宣稱整體共識。
