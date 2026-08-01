---
name: milktea-skills-to-ticket
description: 將已核准中文規格拆成可獨立派工、驗證與 Review 的 Tickets，標示依賴、執行順序、Agent 角色、驗收條件與三角色共識規則，並發布到專案 issue tracker。由 milktea-skills-grill-me 在拆票階段調用，或在使用者要求把規格拆成 Tickets 時使用；不開始實作。
---

# Milktea Skills To Ticket

把核准規格拆成最小、可驗證的垂直切片。不得重新設計需求或架構。

## 前提

- Spec 已核准並可直接開啟。
- 可行性關卡允許執行。
- `docs/agents/issue-tracker.md` 的正式 Tracker、標籤與 Ticket 連結方式可用。

Spec 或可行性前提缺少時停止，不猜測。Tracker 設定不存在、不完整或無法操作時，呼叫 `/milktea-agents-army-claude:milktea-skills-setup-issue-tracker`；只在收到 `TRACKER_READY` 後繼續。設定 Skill 不可用或設定失敗時停止並回報實際缺口。

## 流程

1. 讀取 Spec、`docs/agents/issue-tracker.md`、`docs/planning/requirements.md`、`docs/planning/architecture.md`、可行性報告、專案指令、`CONTEXT.md`、ADR 與程式庫現況。
2. 依使用者價值切成可獨立驗證的 Tickets；避免純分層或模糊雜務票。
3. 標示依賴、阻擋關係、建議順序與可安全平行的工作。
4. 為每張 Ticket 指定執行角色、兩個隔離 Reviewer 與驗收證據；實際後端由執行階段偵測。
5. 發布到設定檔指定的 Repository 與 issue tracker，套用 `ready-for-agent`，並使用原生 blocking links；不支援時在 Ticket 內明列。不得依目前工作目錄猜 Repository。
6. 顯示完整拆分與關係，要求使用者核准；不派工、不實作。

## Ticket 格式

```markdown
# 〈Ticket 標題〉

## 目標

## 使用者價值

## 範圍

## 已確認實作決策

## 驗收條件

- 每條都必須可觀察、可判定。

## 測試與證據

- 測試接縫：
- 必跑指令：
- 必交證據：測試結果、必要的執行輸出與變更摘要。
- 保存位置：對應 Ticket comments。

## 依賴

- Depends on：無／Ticket
- Blocks：無／Ticket

## Agent 分工

- 執行：優先 Claude 開發 Agent；不可用時使用 Codex 開發 Agent
- Reviewer A：優先使用臨時 Claude Agent；不可用時使用隔離的臨時 Codex Agent
- Reviewer B：優先使用臨時 Codex Agent；不可用時使用另一個隔離的臨時 Agent
- Reviewer 標準：兩者都載入 `/milktea-agents-army-claude:milktea-skills-code-review`，並同時執行 Standards 與 Spec Review
- 後端選擇：由 `/milktea-agents-army-claude:milktea-skills-implement` 完成能力偵測後決定

## 完成規則

- 三個角色已處理所有可重現且有證據的問題。
- 沒有未解決的正確性、可執行性、可讀性、架構或衍生風險。
- 三個角色對完成狀態達成共識。
```

## 拆票規則

- 每張 Ticket 只交付一個可驗證結果。
- 每張 Ticket 必須有明確驗收條件，不以「完成實作」作為驗收。
- 優先建立能端到端驗證的最小切片，再逐步擴充。
- 不把相依工作偽裝成可平行；平行 Tickets 必須有清楚的檔案或模組所有權。
- Ticket 只引用已核准決策；發現缺口時退回對應階段。

## Review 共識

- Reviewer 的目標是驗證能跑、符合 Spec、可讀、架構清楚且無明顯衍生問題，不是強迫找錯。
- 開發 Agent 不得照單全收 Reviewer 建議；必須重現、查證或以測試驗證。
- 建議不正確時，開發 Agent 應提出證據並維持立場；Reviewer 也必須依證據修正判斷。
- 有合理分歧時繼續交換證據，直到三個角色同意修改、接受現況或明確回報使用者裁決。
- 未達共識前，Ticket 不得標記完成，開發 Agent 不得休息或接下一張 Ticket。

若 Claude 不可用，改用彼此隔離的 Codex 角色並明示缺少跨模型獨立性；不得假裝已建立 Claude Agent，也不得因此跳過 Review。

## 完成條件

- 每項 Spec 驗收條件至少由一張 Ticket 覆蓋。
- 所有 Tickets 皆有依賴、角色、驗收、測試與證據要求。
- Review 共識規則已納入每張 Ticket 或父規格。
- 執行、Debug、Git 衝突與 Review 證據的保存位置已寫入 Ticket。
- Tickets 已發布、套用 `ready-for-agent` 並由使用者核准。
- 尚未開始實作。

核准後把實際 Spec 連結、Ticket 連結與執行順序交回 `/milktea-agents-army-claude:milktea-skills-grill-me`。本 Skill 不建立 Task，也不啟動實作。
