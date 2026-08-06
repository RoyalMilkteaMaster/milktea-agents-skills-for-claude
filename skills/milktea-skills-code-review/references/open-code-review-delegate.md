# Reviewer B 的 Open Code Review Delegation Mode

此流程只使用 OCR 的確定性工程能力。宿主 Reviewer B 才是實際 Reviewer。

## 禁止事項

- 不執行 `ocr review`、`ocr scan`、`ocr llm test` 或 `ocr config set`。
- 不安裝或更新 OCR；安裝只可由 `milktea-skills-set-agent-roles` 的兩層確認流程處理。
- 不讀取或要求 OCR LLM API Key。
- 不把 Alibaba 官方 Agent Skill 載入目前專案。
- 不修改 `.opencodereview/`、專案檔案、Git 狀態或 Ticket。

每次 OCR 命令只在子程序設定 `OCR_NO_UPDATE=1`，防止 npm wrapper 背景更新。所有 `<ocr-command>` 都必須替換成 Task 狀態中已驗證的 OCR 絕對路徑並正確引用；命令、Git 與 repo path 都使用 Coordinator 指定的同一執行環境與 command prefix，不得重新依賴宿主 `PATH` 或另一個 WSL distribution。

## 1. Preview

依 Coordinator 的固定 Snapshot 使用其中一種模式，不得自行改成別的範圍：

| Snapshot | 命令 |
|---|---|
| 未提交工作區 | `<ocr-command> delegate preview --repo <repo>` |
| 分支或 revision 範圍 | `<ocr-command> delegate preview --repo <repo> --from <from> --to <to>` |
| 單一 commit | `<ocr-command> delegate preview --repo <repo> --commit <hash>` |

若 Ticket／Spec 有簡短背景，可加 `--background <text>`；長內容使用 `--background-file <path>`，不可把密鑰或不必要個資放入參數。

Windows PowerShell 在呼叫前暫時設定 `$env:OCR_NO_UPDATE = "1"`，完成後還原。Linux／WSL 在單一命令前加 `OCR_NO_UPDATE=1`。

保存 Preview 的：

- mode，以及 from／to／commit／merge_base
- Reviewable 檔案、狀態、增刪行數
- Excluded 檔案與排除原因

Preview 與 Coordinator 的固定檔案列表或 revision 不一致時停止並回報，不得默默改 Review 範圍。

## 2. Rule

把 Preview 的 Reviewable 路徑原樣傳給：

```text
<ocr-command> delegate rule --repo <repo> <path1> <path2> ...
```

路徑很多時可分批，但每個 Reviewable 檔案都必須取得規則結果。不得把 Excluded 檔案混入 Rule 命令以假裝 OCR 選中了它。

## 3. 取得固定 Diff

依 Preview metadata 直接用 Git：

- Range：`git diff <merge_base>..<to> -- <path>`
- Commit：`git show <commit> -- <path>`
- Workspace 已追蹤檔：`git diff HEAD -- <path>`
- Workspace 未追蹤檔：唯讀完整檔案，因整份內容都是新程式

使用 `--` 分隔 revision 與路徑，避免路徑被解讀為 option。所有命令都必須在同一 repo 與固定 Snapshot 上執行。

## 4. Milktea Standards Review

- 對每個 Reviewable 檔案，以解析到的 Rule Group 作為額外清單，只輔助 `milktea-skills-code-review` 的 Standards Review。
- `review_axis: both` 時，Spec Review 仍由 Reviewer B 依原生固定 Snapshot 執行，不使用 OCR 規則判斷規格是否達成。
- Excluded 檔案不做逐行 OCR Review，但仍列在報告；若它對驗收、資料流或 Reviewable 檔案的行為有必要影響，可唯讀檢查上下文。
- OCR 規則不得蓋過 Spec、Ticket、專案規範或安全要求。
- 使用 Milktea 原有的阻擋／重要／建議嚴重度與 Finding 格式，不把 OCR 腳手架描述成另一個模型的結論。

## 5. 回報證據

除原本報告欄位外，加入：

```yaml
review_engine: open_code_review_delegate
ocr:
  mode: delegate
  version: <實際版本>
  preview_mode: workspace | range | commit
  reviewable_files: [...]
  excluded_files:
    - path: <path>
      reason: <OCR 輸出的原因>
```

OCR 命令失敗時改回報 `OCR_DELEGATE_UNAVAILABLE`；不得聲稱已完成 Delegation Mode。
