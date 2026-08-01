---
name: milktea-skills-to-spec
description: 將已核准的需求與架構整理成完整中文規格，預設寫入 docs/work/功能名稱/spec.md；只有使用者明確啟用遠端 Tracker 時才發布到遠端。由 milktea-skills-grill-me 在規格階段調用，或在使用者要求把已確認內容轉成 Spec、PRD 或可拆票規格時使用；不訪談、不新增決策、不拆票。
---

# Milktea Skills To Spec

把已核准內容整理成唯一規格來源。全程使用繁體中文；程式識別字保留原文。

## 前提

下列內容必須已核准：

- `docs/planning/requirements.md` 的需求與驗收結果。
- `docs/planning/architecture.md` 的架構、資料流與測試接縫。

需求或架構缺少或互相衝突時停止，指出應回到哪個階段；不得自行補問或猜測。

## 儲存模式

- 預設使用本機 Markdown：`docs/work/<功能名稱>/spec.md`。
- `<功能名稱>` 使用簡短、可辨識的 kebab-case；同一工作沿用既有目錄，不同工作撞名時追加 `-02`、`-03`。
- 只有 `docs/agents/issue-tracker.md` 明確包含 `模式：remote` 且設定可用時，才發布到指定遠端 Tracker。
- 設定不存在、缺少模式或仍是舊格式時，一律使用本機；不詢問、不自動設定遠端。
- 不為了儲存或交接執行 `git add`、Commit、Push、建立 Repository 或修改 remote。

## 流程

1. 讀取 `docs/planning/requirements.md`、`docs/planning/architecture.md`、專案指令、`CONTEXT.md`、相關 ADR 與程式庫現況。
2. 依下方格式撰寫規格，不加入未確認內容。
3. 本機模式建立工作目錄並寫入固定路徑；遠端模式發布到設定的 Repository，套用 Spec 標籤且不得套用 `ready-for-agent`。
4. 顯示完整規格與實際路徑或連結，等待使用者核准；修改後更新同一來源，不建立副本。

## 規格格式

```markdown
# 〈規格名稱〉

## 問題

## 目標

## User Stories

1. 身為〈角色〉，我希望〈能力或行為〉，以便〈價值〉。

## 需求與行為

## 實作決策

- 資料與所有權
- 模組責任與公開介面
- Schema、API contract 與系統互動
- 相容、遷移與技術限制

## 驗收條件

- 使用可觀察、可判定的結果。

## 測試決策

- 公開行為
- 測試接縫
- 既有測試模式
- 不應耦合的實作細節

## 不在範圍內

## 補充
```

## 規則

- User Stories 描述誰需要什麼及原因；驗收條件描述怎樣才算完成。
- 使用專案術語並遵守 ADR。
- 寫模組與介面名稱；省略易過期的檔案路徑、行號與大段程式碼。
- 原型已驗證的狀態機、Schema 或型別只保留決策所需片段並標記來源。
- 不實作、不拆 Ticket、不修改來源碼。

## 完成條件

- 規格只包含核准內容。
- User Stories 與驗收條件完整。
- 架構與測試決策可供拆票。
- 規格已寫入本機固定路徑；遠端模式則已發布並套用 Spec 標籤。
- 使用者核准規格。
