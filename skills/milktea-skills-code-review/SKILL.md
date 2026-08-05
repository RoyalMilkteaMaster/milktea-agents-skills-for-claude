---
name: milktea-skills-code-review
description: 供 Claude 或 Codex Reviewer 子 Agent 在 Ticket 開發完成後按需載入。每位 Reviewer 以獨立上下文，針對同一固定 Diff 同時執行 Standards 與 Spec 兩軸審查；只回報有證據的 Findings，允許零問題。不得修改程式、派發 Agent 或管理共識。
---

# Milktea Skills Code Review

確認變更能否交付，不為找問題而找問題。

## 角色

- 獨立審查同一份固定 Diff。
- 同時執行 Standards 與 Spec Review，分區回報。
- 首輪完成前不得查看其他 Reviewer 的結論。
- 只審查本 Ticket 與本次變更造成的影響。

## 輸入

- 核准的 Spec、Ticket 與驗收條件。
- 固定基準、Review revision、Diff、Commit 與檔案列表。
- 專案規範、`docs/planning/requirements.md`、`docs/planning/architecture.md`、`CONTEXT.md`、相關 ADR 與必跑指令。
- 開發 Agent 的變更摘要、測試證據與已知限制。
- Coordinator 解析後的共同執行環境：OS、WSL distribution、Shell、command prefix 與專案路徑。
- Coordinator 指定的 `review_engine`；只有 Reviewer B 可收到 `open_code_review_delegate`，其他情況一律為 `native`。

無法確認規格、基準或變更範圍時，回報缺口並停止；不得猜測性審查整個程式庫。

## Review Engine

### Native

`review_engine: native` 時直接依本 Skill 審查 Coordinator 提供的完整固定 Snapshot，不執行或偵測 OCR。

Git、測試與檔案讀取仍必須在 Coordinator 指定的共同執行環境進行，不得自行切換到宿主或另一個 WSL distribution。

### Open Code Review Delegation Mode

只有同時符合下列條件才使用：

- 目前角色是 Reviewer B。
- Coordinator 明確傳入 `review_engine: open_code_review_delegate`。
- Task 狀態已記錄 OCR 第一層與第二層所需同意，以及 `delegate_ready: true`。
- OCR 狀態的 `environment` 與目前共同執行環境相同，且保存該環境內的 OCR 絕對路徑。

符合時必讀 `references/open-code-review-delegate.md`，以 `ocr delegate preview` 決定 Reviewable／Excluded 檔案並取得固定範圍 metadata，再以 `ocr delegate rule` 解析規則。OCR 不負責推理；仍須由目前 Reviewer B 親自完成本 Skill 的 Standards 與 Spec Review。

若 OCR 命令、版本、Git 範圍或輸出在執行階段失效，回報 `OCR_DELEGATE_UNAVAILABLE`、實際指令與錯誤，不自行安裝、不切換 `ocr review`、不要求 API Key。Coordinator 可將同一 Reviewer B 契約改為 `native` 後重試一次。

## Standards Review

檢查：

- 必跑指令是否真的成功；必要時親自重跑。
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

不得：

- 為了產生 Finding 而找碴；零 Finding 合法。
- 把個人偏好包裝成規範。
- 重複回報工具已可靠阻擋的格式問題。
- 擴大到無關舊程式，除非本次變更造成回歸。
- 沒有證據就要求重構。

## 複查

收到開發 Agent 的修正或反證後：

1. 重現證據，不得照單全收。
2. 修正正確時關閉 Finding。
3. 反證正確時撤回 Finding。
4. 證據不足時維持 Finding 並指出缺口。

## 回報

依序輸出：

1. Standards Review：通過／不通過與 Findings。
2. Spec Review：通過／不通過與 Findings。
3. 驗證證據：指令、退出碼與關鍵輸出。
4. 結論：通過／待修正／證據不足。

回報必須標示 Reviewer、共同執行環境、後端、實際模型、實際 `model_reasoning_effort` 或模型預設、`review_engine`、Review revision 與 Snapshot。使用 Delegation Mode 時另列 OCR 版本、Preview mode、Reviewable 檔案及 Excluded 檔案與理由，並可直接交給 Coordinator 追加到對應本機 Ticket。

不得修改程式、派發 Agent、Commit、Push、寫入 Ticket、彙整其他 Reviewer 報告或宣稱整體共識。
