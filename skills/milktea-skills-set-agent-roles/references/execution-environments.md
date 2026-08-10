# 執行環境選擇契約

執行環境是目前專案所有執行 Task 的共同工作位置。Developer、Reviewer A、Reviewer B、Git、測試與可選 OCR 必須使用同一個已解析環境。

## 選項

1. **Windows PowerShell**：使用 Windows 內已可執行的 PowerShell 與 Windows 專案路徑。
2. **WSL**：使用實際存在的 distribution；不得假設是 Ubuntu。有多個可用 distribution 且沒有明確預設時，再詢問一次。
3. **其他已安裝 CLI 的環境**：依目前可安全探測的環境，尋找已能執行所需 CLI 並讀寫同一專案的位置。

終端機品牌不是執行環境。Windows Terminal 可能承載 PowerShell、cmd 或 WSL，必須記錄實際結果。

## 偵測邊界

- 只做版本、`PATH`、WSL 清單、專案路徑與 Git 工作樹等唯讀檢查。
- 只驗證使用者選中的環境；不遞迴掃描磁碟、不安裝、不更新、不登入，也不接受任意 CLI 字串。
- 多個環境會改變實際結果時才詢問使用者。

## 記錄方式

把解析結果寫入 `<專案根目錄>/.milktea/agent-settings.yaml`：

```yaml
agent_settings:
  execution_environment:
    preference: wsl
    kind: wsl
    distribution: Debian
    shell: /bin/bash
    command_prefix: [wsl.exe, -d, Debian, --]
    project_path: /mnt/d/project
```

Windows PowerShell 的 `distribution` 為 `null`。沒有使用者指定時保留 `preference: auto`，由執行 Skill 使用目前唯一可行的環境。

## 執行規則

- WSL 從 Windows 啟動時，所有專案命令都使用記錄的 WSL 前綴與 Linux 專案路徑。
- PowerShell 選項只使用 Windows 工具與 Windows 專案路徑。
- 其他環境只能使用已解析的單一位置，不讓不同角色各自選擇工作目錄。
- 派工前確認設定環境仍可用；失效時回報，不偷偷改用另一個環境。
- 新設定適用於所有後續 Task 尚未派發的 Tickets；進行中的 Ticket 不換環境。

若某張 Ticket 必須改用另一個作業系統，先取得使用者核准；該 Ticket 的 Developer、兩位 Reviewer、測試與 OCR 仍使用同一個例外環境。
