# Open Code Review 可選整合契約

本契約只適用 Alibaba Open Code Review CLI（命令為 `ocr`）。它不是圖片 OCR，也不是 Milktea Skills 的必要相依。

## 使用邊界

- 安裝前必須取得使用者確認；安裝完成且 Delegation Mode 可用後，Reviewer B 自動使用，不另設開關。
- 只提供 Reviewer B 的 Standards Review 使用；Reviewer A 永遠使用原生流程。
- 只使用 Delegation Mode：`ocr delegate preview` 與 `ocr delegate rule`。
- OCR 只整理 Git 變更檔案與解析 Review 規則；Findings 仍由 Reviewer B 判斷。
- 不執行 `ocr review`、`ocr scan`、`ocr llm test` 或 `ocr config set`，不索取或保存 LLM API Key。
- 不把 OCR 加入專案依賴，不下載完整原始碼，也不自行建立 `.opencodereview/rule.json`。

## 安裝確認

OCR 不可用時，必須在安裝前揭露：

- 套件：`@alibaba-group/open-code-review@1.8.6`
- Windows 安裝到目前 npm 全域目錄；Linux／WSL 安裝到使用者層級 `~/.local`
- 需要連線 npm registry 與 GitHub Releases
- 可能寫入 npm 安裝位置及使用 OCR 時的 `~/.opencodereview/`
- 不會設定 LLM、要求 API Key 或執行 Review

只有使用者肯定同意後才能執行安裝，而且命令必須包含 `--confirmed`。未確認時腳本必須拒絕。

## 環境與檢查

- Windows 與每個 WSL distribution 是不同環境，只檢查專案設定檔指定的位置。
- Windows 選擇 WSL 時，使用該 distribution 的 Linux Node、Linux 專案路徑與 Linux Skill 路徑。
- OCR 要求 Git ≥ 2.41；npm 安裝要求 Node.js ≥ 18 與 npm。
- 已安裝且 `ocr delegate --help` 成功時，實際使用只要求 Git 與有效 Git 工作樹。
- 檢查 OCR 時只對該子程序設定 `OCR_NO_UPDATE=1`。
- 未經使用者確認不得安裝或升級；取得確認後，可以依目前環境的正式安裝方式補足 OCR 必要工具。

標準命令：

```text
node <本 Skill 實際路徑>/scripts/open-code-review.js check --repo <專案實際路徑>
node <本 Skill 實際路徑>/scripts/open-code-review.js install --confirmed --repo <專案實際路徑>
```

第二個命令只有通過安裝確認才能執行。PowerShell 與 Shell wrapper 不能繞過 `--confirmed`。

## 可用條件

檢查結果中的 `delegate_ready: true` 才能使用 Delegation Mode。Reviewer B 每次使用前依實際環境確認 OCR 仍可執行；不可用時直接改用原生 Review，不阻擋 Ticket。

OCR 是否可用以安裝環境的實際狀態為準，不在 `agent-settings.yaml` 保存 `enabled`、`disabled` 或另一份可用狀態。

行為依據：

- <https://github.com/alibaba/open-code-review/releases/tag/v1.8.6>
- <https://open-codereview.ai/docs/delegate>
- <https://open-codereview.ai/docs/installation>
