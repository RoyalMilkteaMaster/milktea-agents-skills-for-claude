# Open Code Review 可選整合契約

本契約只適用 Alibaba Open Code Review CLI（命令為 `ocr`）。它不是圖片 OCR，也不是 Milktea Skills 的必要相依。

## 固定邊界

- 預設關閉；只有使用者在目前 Task 明確開啟才生效。
- 只提供 Reviewer B 的 Standards Review 使用；Reviewer A 與所有 Spec Review 永遠使用原生流程。
- 只使用 Delegation Mode：`ocr delegate preview` 與 `ocr delegate rule`。
- OCR 只負責 Git 變更檔案篩選、排除原因與 Review 規則解析；實際推理與 Findings 由 Reviewer B 的宿主模型完成。
- 不執行 `ocr review`、`ocr scan`、`ocr llm test` 或 `ocr config set`，不索取、不儲存 LLM API Key。
- 不下載或複製 Alibaba 的完整原始碼到使用者專案，不加入專案依賴，不建立專案級 Skill。
- 不自行建立 `.opencodereview/rule.json`。專案已存在此檔案時可由 OCR 唯讀解析；要新增規則必須是另一個明確需求。

## 兩層確認

### 第一層：功能同意

先用白話說明：

> Open Code Review 可以替 Reviewer B 的 Standards Review 整理這次 Git 變更中應審查與被排除的檔案，並解析適用的 Review 規則。真正讀程式、判斷問題及產生報告的仍是 Reviewer B；Spec Review 不交給 OCR，因此不需要另外提供 OCR 的 LLM API Key。要為目前 Task 開啟嗎？

未取得肯定回答時停止 OCR 流程，不得連偵測命令都執行。

### 第二層：安裝同意

只有第一層已開啟且檢查結果顯示 OCR 不可用時才出現。先揭露：

- 安裝套件：`@alibaba-group/open-code-review@1.8.6`
- 安裝範圍：Windows 的目前 npm 全域目錄；Linux／WSL 的使用者層級 `~/.local`
- 網路：npm registry 與 GitHub Releases；套件安裝器會驗證下載的二進位 checksum
- 可能寫入：npm 全域目錄，以及使用 OCR 時的 `~/.opencodereview/`
- 不會寫入：目前 Git 專案（除非使用者日後另外要求建立專案規則）
- 不會做：設定 LLM、詢問 API Key、執行 Review

使用者未肯定同意時不得安裝。使用者同意後，安裝腳本仍必須收到 `-Confirmed` 或 `--confirmed`；少此旗標時腳本應拒絕執行。

## 環境與必要條件

- Windows 與每個 WSL distribution 都是獨立環境；只在目前 Task 已解析的 `execution_environment` 檢查或安裝，不得因為另一個環境已安裝就標記可用。
- 唯讀檢查與安裝共用 `scripts/open-code-review.js`。Windows PowerShell、cmd、Bash、sh 都是呼叫同一個 Node.js 核心，不各自維護安裝邏輯。
- Windows 宿主選擇 WSL 時，使用已解析的 `wsl.exe -d <distribution> --` 前綴、Linux Node 路徑、Linux 專案路徑與 Linux 腳本路徑。不得用 Windows Node 處理 WSL 的 OCR 狀態。
- OCR 官方 Quick Start 要求 Git ≥ 2.41、Node.js ≥ 18。npm 安裝還需要 npm 可用。
- 已安裝靜態 OCR 且 `ocr delegate --help` 成功時，執行階段只要求 Git 與有效的 Git 工作樹；Node.js 只屬於 npm 安裝必要條件。
- 檢查或執行 OCR 命令時，僅對該子程序設定 `OCR_NO_UPDATE=1`，避免 npm wrapper 在未確認時背景更新。
- Milktea 不自動安裝或升級 Git、Node.js、npm，也不使用 `sudo`、winget 或系統套件管理器。

標準命令：

```text
node <environment-script-path>/open-code-review.js check --repo <environment-project-path>
node <environment-script-path>/open-code-review.js install --confirmed --repo <environment-project-path>
```

第二個命令只有通過第二層確認才能執行。舊的 `.ps1` 與 `.sh` 檔案只是薄 wrapper，不能繞過 `--confirmed`。

## 檢查結果

檢查腳本輸出 JSON，至少包含：

- `environment.kind`、實際 WSL `distribution`
- `git`、`node`、`npm`、`ocr` 的存在狀態、路徑與版本
- `inside_git_worktree`
- `delegate_ready`
- `npm_install_ready`
- `reason_codes`

`delegate_ready: true` 才能在 Task 狀態中啟用 `open_code_review_delegate`。同時保存解析後的 environment 值與 OCR 在該環境內的絕對路徑，Reviewer B 必須透過同一環境使用該路徑，不依賴之後的 Shell 是否剛好具有相同 `PATH`。其他情況一律以原生 Reviewer B 繼續，除非使用者明確要求先排除安裝問題。

## 安裝後

安裝腳本成功不等於可用；必須再跑檢查腳本。保存實際版本與環境，不把憑證、家目錄完整內容或其他敏感環境變數寫入 Task 狀態。

版本來源與行為依據：

- <https://github.com/alibaba/open-code-review/releases/tag/v1.8.6>
- <https://open-codereview.ai/docs/delegate>
- <https://open-codereview.ai/docs/installation>
- <https://open-codereview.ai/docs/agent-skill>
