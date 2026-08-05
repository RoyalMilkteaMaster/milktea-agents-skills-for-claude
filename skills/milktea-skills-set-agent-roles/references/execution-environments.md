# 執行環境選擇契約

執行環境是目前 Task 的共同工作位置。Developer、所有啟用 Reviewer、Git、測試與可選 OCR 必須使用同一個已解析環境。

## 固定三個選項

1. **Windows PowerShell**：使用 Windows 內已可執行的 PowerShell 與 Windows 專案路徑。
2. **WSL**：使用目前 WSL，或由 `wsl.exe --list --verbose` 唯讀找到的實際 distribution。不得假設是 Ubuntu；有多個可用 distribution 且沒有明確預設時，再詢問一次。
3. **其他已安裝 CLI 的環境（AI 偵測）**：AI 依專案指令與目前可安全探測的執行環境，尋找已可執行所需 CLI 且可讀寫同一專案的環境，例如 cmd、Git Bash、Container 或原生 Linux／macOS。

選項介面可把本 Task 目前值設為預選值，但不要另加第四個「保持目前設定」。

## 偵測邊界

- 只做版本、`PATH`、WSL 清單、專案路徑與 Git 工作樹等唯讀檢查。
- 不遞迴掃描磁碟，不安裝、不更新、不登入工具，也不接受任意 CLI 字串。
- 第三項若找到一個可用環境就直接採用；若有多個會明顯改變行為的環境，再請使用者選擇；找不到時回報 `BLOCKED: EXECUTION_ENVIRONMENT_UNAVAILABLE`。
- 終端機品牌不是執行環境。Windows Terminal 可能承載 PowerShell、cmd 或 WSL，必須記錄實際結果。
- 不把個人電腦的選擇寫入公開專案 `AGENTS.md`、README 或 Git 設定。

## Task 狀態

保存使用者選項與解析結果：

```yaml
execution_environment:
  preference: wsl
  kind: wsl
  distribution: Debian
  shell: /bin/bash
  command_prefix: [wsl.exe, -d, Debian, --]
  project_path: /mnt/d/project
  source: user_choice
```

Windows PowerShell 的 `distribution` 為 `null`，`command_prefix` 記錄實際 PowerShell 執行檔與固定參數。第三項的 `preference` 為 `auto_detect_other`，其餘欄位仍必須填入實測結果。

## 執行規則

- WSL 從 Windows 啟動時，所有專案命令都使用已記錄的 `wsl.exe -d <distribution> --` 前綴與 Linux 專案路徑。
- PowerShell 選項只使用 Windows 工具與 Windows 專案路徑。
- 第三項只能使用已解析的單一環境，不得讓啟用角色各自找不同位置。
- 派工前重新驗證環境仍可用；失效時停止，不得偷偷換環境。
- 設定從下一張尚未派發的 Ticket 生效；進行中的 Ticket 不換環境。

若某張 Ticket 必須使用另一 OS，先取得使用者核准。該 Ticket 的所有啟用角色、測試與 OCR 仍共同使用同一個例外環境，完成後下一張 Ticket 回到 Task 設定。
