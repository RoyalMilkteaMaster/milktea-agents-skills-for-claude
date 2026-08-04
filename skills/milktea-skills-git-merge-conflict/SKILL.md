---
name: milktea-skills-git-merge-conflict
description: 供執行 Git 整合的臨時開發 Agent 按需載入。當 merge、rebase 或 cherry-pick 回報 CONFLICT 或 unmerged paths 時，依 Spec、Ticket、Commit、ADR 與測試理解雙方意圖，完成合併與驗證；平時不預載。
---

# Milktea Skills Git Merge Conflict

依雙方意圖解決實際 Git 衝突。預設自行完成；只有現有證據無法裁決的需求或架構衝突才詢問使用者。

## 載入方式

- 讓臨時開發 Agent 可發現本 Skill，但不得預載完整內容。
- 臨時開發 Agent 執行 merge、rebase 或 cherry-pick 並收到衝突後，先載入本 Skill，再修改衝突。
- Skill 不可用時回報 `BLOCKED: GIT_MERGE_CONFLICT_SKILL_UNAVAILABLE`，不得自行亂解。
- `implement` 只負責路由、派工與 Review，不親自解衝突。
- Git 操作完成後才發現程式異常時，改用 `$milktea-skills-debug`。

## 前提

讀取專案 Git 規則、派工、Ticket、Spec、`docs/planning/requirements.md`、`docs/planning/architecture.md`、`CONTEXT.md`、ADR、目前操作與兩邊版本。先確認本次 Git 操作與授權範圍正確。

## 流程

1. 查看 Git 狀態、歷史、操作類型、來源版本、目標版本、既有修改與全部衝突檔案。
2. 逐個衝突讀取雙方 Diff、Commit、PR／Ticket、Spec、相關測試與歷史，確認兩邊各自要保留的行為。
3. 逐段解決：可以共存就保留雙方意圖；無法共存就依核准 Spec、ADR、架構限制與本次整合目標選擇。
4. 一般技術判斷自行完成並記錄理由，不把 Git 衝突本身丟給使用者決定。
5. 只有選擇會新增或改變需求、公開介面、資料模型或架構，且核准文件無法裁決時，才提供推薦、理由與代價請使用者決定。
6. 檢查未合併清單、衝突標記、Diff、刪除與重新命名，確認沒有遺漏或無關修改。
7. 先跑衝突範圍測試，再跑專案要求的型別、測試與格式檢查；修正本次合併造成的失敗。
8. 依派工與專案 Git 規則精確 Stage 已解決檔案，完成 merge、rebase 或 cherry-pick；需要 Commit 時建立可追溯版本。
9. 回報 `Ready for Review` 與最終 Snapshot，由 `implement` 派兩位 Reviewer 審查合併後版本。

## 規則

- 不用整批 `ours`／`theirs` 取代逐段判斷。
- 不發明雙方原本都沒有、且未經核准的行為。
- 鎖定檔先解決來源清單，再用專案既有工具重新產生。
- 二進位檔依可追溯的核准版本選擇；無法確認就停止。
- 刪除、重新命名與移動衝突必須檢查引用、資料流與相容性。
- 不因衝突困難而 Abort。只有證據顯示本次 Git 操作本身錯誤時，才停止並提出 Abort；未經授權不得執行。
- 不使用 `git add .`、`git add -A`、Reset、強制切換或清理工作目錄。
- 不覆蓋、刪除或隱藏使用者及其他 Agent 的既有修改。
- 未獲授權不得 Push、改寫歷史或擴大 Ticket 範圍。

## 完成條件

- Git 操作已依授權完成，沒有未解決檔案或殘留衝突標記。
- 每項解法都能對應雙方意圖或核准取捨。
- 相關檢查已執行，結果與退出碼已記錄。
- 無關修改保持不變；Stage 與 Commit 範圍精確可核對。
- 合併後 Snapshot 已交由 `implement` 進入雙 Reviewer 與三方共識流程。

## 回報

- 操作類型、來源版本與目標版本。
- 衝突檔案及雙方意圖。
- 各檔案解法與必要取捨。
- 測試指令、退出碼與關鍵結果。
- Stage、Commit、未解事項與目前 Git 狀態。

把回報交給執行協調者追加到對應本機 Ticket 的 `## 執行與 Review 紀錄`；不得另建衝突報告或自行修改 Ticket。
