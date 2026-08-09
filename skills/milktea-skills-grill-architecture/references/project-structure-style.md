# Milktea 專案結構偏好

這是預設思考模型，不是必建清單。只建立目前需要的目錄，不預建空架構。

## 目錄

- [優先順序](#優先順序)
- [通用骨架](#通用骨架)
- [三個根目錄](#三個根目錄)
- [文件與報告](#文件與報告)
- [程式碼結構](#程式碼結構)
- [命名](#命名)
- [建檔與重構](#建檔與重構)

## 優先順序

1. 框架強制規則。
2. 已核准需求與既有公開契約。
3. 現有專案一致性。
4. 本文件的結構偏好。
5. 最小可用結構。

新專案預設採用本文件。既有專案不得為單張 Ticket 大搬家；衝突時列出差異、風險與最小改善方案，交由使用者確認。

## 通用骨架

```text
workspace/                    # 同一專案家族的外層工作區
├─ <project>_project/         # Git：程式碼與可重現設定
│  ├─ AGENTS.md              # 長期有效的 Agent 規則
│  ├─ CONTEXT.md             # 專有名詞、關係與歧義
│  ├─ frontend/              # 使用者介面專案
│  │  └─ src/                # 前端主要原始碼
│  │     ├─ pages/            # 路由頁面
│  │     ├─ components/       # 可重用元件
│  │     ├─ features/         # 複雜功能
│  │     ├─ api/              # 後端呼叫
│  │     ├─ stores/           # 狀態
│  │     └─ styles/           # 樣式
│  ├─ backend/               # API 與後端業務程式
│  │  └─ app/                # 後端主要原始碼
│  │     ├─ api/              # 請求入口
│  │     ├─ services/         # 業務流程
│  │     ├─ repositories/     # 資料存取
│  │     └─ domain/           # 核心領域
│  ├─ execution/              # 外部工具與長任務的控制程式
│  ├─ migrations/             # Schema 與遷移，不放實際資料庫
│  ├─ shared/                 # 跨模組穩定定義
│  ├─ tests/                  # 自動化測試與測試資料
│  ├─ scripts/                # 開發、維護、部署腳本
│  ├─ config/                 # 可提交的設定與範例
│  └─ docs/                   # 規劃、架構、報告與開發文件
│     ├─ planning/            # 已核准規劃
│     │  ├─ requirements.md   # 核准需求
│     │  └─ architecture.md   # 核准架構與資料流
│     ├─ work/                # 從草稿、核准到完成的工作文件與證據
│     │  └─ <work-id>/        # 唯一工作識別碼，不靠功能名稱避免撞名
│     │     ├─ spec.md        # 本次規格、狀態與顯示名稱
│     │     ├─ tickets/       # 每票一個 Markdown，含草稿到完成狀態
│     │     ├─ implementation-plan.html # Ticket 草稿完成後的實作藍圖
│     │     ├─ progress-report.html   # 執行中非同步進度頁
│     │     └─ completion-report.html # 全部驗收後才存在的結案報告
│     ├─ adr/                 # 重大且難逆轉的架構決策
│     ├─ feasibility/         # 可行性評估 Markdown
│     ├─ architecture-reviews/ # 架構健檢工作目錄
│     │  └─ <work-id>/        # 盤點開始即建立的唯一工作識別碼
│     │     └─ architecture-review.html # 該工作的唯一架構健檢 HTML
│     └─ assets/              # 文件與報告使用的靜態資產
│        └─ feasibility/      # 可行性分級 SVG
│
├─ <project>_data/            # 不進 Git：可變資料
│  ├─ databases/              # SQLite、資料庫檔案
│  ├─ records/                # 表單與業務資料
│  ├─ uploads/                # 使用者或外部系統輸入
│  ├─ artifacts/              # 任務與生成流程產物
│  ├─ exports/                # 提供使用者取用的匯出結果
│  ├─ logs/                   # 啟用正式 Logging 時才建立
│  └─ temporary/              # 可安全清除的暫存資料
│
├─ <project>_runtime/         # 不進 Git：大型執行資源
│  ├─ applications/           # Blender、ComfyUI 等
│  ├─ models/                 # Checkpoints、模型權重
│  ├─ plugins/                # 外掛、自訂節點
│  ├─ environments/           # 應用程式執行環境
│  └─ cache/                  # 可重建快取
│
└─ backups/                   # 獨立備份
```

不需要的分支必須省略。`runtime` 是預設名稱，不是強制名稱；邏輯責任不可混淆。

## 三個根目錄

- **Code Root**：程式碼、測試、設定範例、Schema 與 migrations。
- **Data Root**：實際資料庫、表單資料、上傳、輸出、產物，以及已啟用的正式 Log。
- **Runtime Root**：Blender、ComfyUI、模型、外掛、大型環境與可重建快取。
- `execution/` 只放呼叫與控制外部工具的程式，不放工具本體。
- 多個 Worktree 可共用 Data／Runtime Root，不得各自複製；並行寫入必須有鎖或單一寫入者。
- 測試不得修改正式 Data Root；使用暫存目錄或測試專用資料。
- 備份不放進 Code、Data 或 Runtime Root。
- 刪除或遷移前，必須確認解析後的實際路徑與所有權；不得從 workspace 根目錄遞迴操作。

路徑由本機設定提供，不寫死在程式碼：

```env
PROJECT_DATA_ROOT=D:/workspace/<project>_data
PROJECT_RUNTIME_ROOT=D:/workspace/<project>_runtime
```

實際 `.env` 不提交；`.env.example` 只放變數與範例。使用 junction、symlink 或 mount 時必須記錄真實目標並排除版本控制。

## 文件與報告

- `CONTEXT.md`：只記錄已確認的專有名詞、關係與歧義。
- `docs/planning/requirements.md`：核准需求。
- `docs/planning/architecture.md`：核准架構與資料流。
- `docs/work/<工作識別碼>/spec.md`：新工作的本機 Spec、工作識別碼與繁體中文顯示名稱。
- `docs/work/<工作識別碼>/tickets/`：新工作的本機 Tickets、狀態與執行證據。
- `docs/work/<工作識別碼>/implementation-plan.html`：Spec 已核准且全部 Tickets 仍為草稿時產生的唯一實作藍圖；HTML `data-work-id` 必須與工作識別碼一致。
- 舊的 `docs/work/<功能名稱>/` 仍是合法既有工作目錄；只沿用實際交接路徑，不搬移、不改名、不覆寫。
- `docs/adr/`：ADR；需要寫入時才建立。
- `docs/feasibility/`：可行性報告；需要寫入時才建立。
- `docs/architecture-reviews/<工作識別碼>/architecture-review.html`：每次 Brownfield 盤點的唯一架構健檢 HTML；工作識別碼在盤點開始時建立，不使用日期或範圍名稱避免同名覆寫。
- `docs/assets/`：報告資產；不得連回 Skill 安裝目錄。
- Spec 與 Tickets：只存 `docs/work/`，維持單一真相。
- 執行、Debug、Git 衝突與 Review 證據：追加到對應本機 Ticket 的 `## 執行與 Review 紀錄`。
- 以上路徑固定；不得把需求、架構或報告正文複製到 `CONTEXT.md`。
- 長期文件放 Code Root；業務資料放 Data Root；模型與大型應用程式放 Runtime Root。
- 只在實際產出時建立所需目錄，不預建空骨架。

## 程式碼結構

- 目錄名稱應讓人不開檔就能判斷職責。
- 同一概念只保留一個正式位置；禁止同時存在 `pages/` 與 `src/pages/`。
- 前端頁面負責組合；元件、API、狀態、驗證與樣式依複雜度拆分。
- 功能簡單時按技術分層；功能變多後才建立 `features/`。
- 後端 Route 只處理輸入、呼叫與輸出；業務流程放 Service，資料存取放 Repository。
- 簡單需求不得為形式強制建立 Service、Repository、Domain 等全部層級。
- 長時間任務、CLI、模型與外部程式不得混進 API Route。
- `shared/` 只放真正跨模組共用且穩定的定義。
- `integrations/` 只放第三方服務介接，並依服務名稱拆分。

## 命名

使用「領域＋角色或行為」，例如：

- `character_repository.py`
- `task_progress_reporter.py`
- `comfyui_api_client.py`
- `blender_process_runner.py`

避免單獨使用 `utils`、`helpers`、`common`、`worker`、`handler`、`manager`、`processor`、`integration`、`core`、`base`。確實需要時補足用途，例如 `cli_session_manager.py`。

禁止永久保留 `new_frontend/`、`frontend_v2/`、`final2.py`，或在 `temp/`、`scratch/` 放正式程式碼。

## 建檔與重構

建檔前確認：

1. 現有目錄是否已有正確位置？
2. 名稱能否直接說明領域與用途？
3. 是否正在建立模糊垃圾桶或重複來源？
4. 新增頂層目錄是否真的必要？

無法回答時停止建檔，先確認架構。

搬動架構前，先提出目前問題、新目錄樹、責任、遷移順序與驗證方法；完成後更新 import、測試與架構文件，刪除舊的重複來源。
