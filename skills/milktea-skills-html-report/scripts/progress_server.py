#!/usr/bin/env python3
"""從 Milktea Ticket 讀取進度，透過本機 SSE 非同步推送到進度頁。"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import threading
import time
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, unquote, urlparse
from urllib.request import urlopen


合法狀態 = {"草稿", "已核准", "執行中", "Review 中", "修正中", "完成", "阻擋"}
目前狀態順序 = {"阻擋": 0, "修正中": 1, "Review 中": 2, "執行中": 3, "已核准": 4, "草稿": 5, "完成": 6}
下一步對照 = {
    "草稿": "等待規劃核准",
    "已核准": "等待進入 Ready Queue",
    "執行中": "Developer 繼續實作與快速檢查",
    "Review 中": "等待 Reviewer 結論或定向複驗",
    "修正中": "Developer 處理已確認的 Finding",
    "完成": "本 Ticket 已完成",
    "阻擋": "依阻擋與裁決紀錄等待必要決定",
}


def 讀取文字(路徑: Path) -> str:
    try:
        return 路徑.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as 錯誤:
        return f"讀取失敗：{錯誤}"


def 拆解章節(內容: str) -> dict[str, str]:
    章節: dict[str, list[str]] = {}
    目前章節 = ""
    for 原始行 in 內容.splitlines():
        標題 = re.match(r"^##\s+(.+?)\s*$", 原始行)
        if 標題:
            目前章節 = 標題.group(1)
            章節.setdefault(目前章節, [])
            continue
        if 目前章節:
            章節[目前章節].append(原始行)
    return {名稱: "\n".join(行).strip() for 名稱, 行 in 章節.items()}


def 清理區段(內容: str, 上限: int = 420) -> str:
    行列 = []
    for 原始行 in 內容.splitlines():
        行 = 原始行.strip()
        if not 行:
            continue
        行 = re.sub(r"^[-*]\s+", "", 行)
        行列.append(行)
    合併 = "\n".join(行列)
    if len(合併) <= 上限:
        return 合併
    return f"…{合併[-上限:]}"


def 尋找欄位(內容: str, 名稱: str, 預設: str = "") -> str:
    結果 = re.search(rf"^-\s*{re.escape(名稱)}[：:]\s*(.+?)\s*$", 內容, re.MULTILINE)
    return 結果.group(1).strip() if 結果 else 預設


def 讀取最近證據(內容: str) -> str:
    關鍵行 = [
        行.strip()
        for 行 in 內容.splitlines()
        if re.search(r"通過|失敗|退出碼|Review|Finding|驗收|測試", 行, re.IGNORECASE)
    ]
    return 清理區段("\n".join(關鍵行[-6:]), 360) or "尚未記錄測試或 Review 結果"


def 讀取品味評分(內容: str) -> str:
    結果 = re.findall(r"【品味評分】\s*([^\r\n]+)", 內容)
    return 結果[-1].strip() if 結果 else "尚未完成 Standards Review"


def 讀取範圍警示(內容: str) -> str:
    關鍵行 = [
        行.strip()
        for 行 in 內容.splitlines()
        if re.search(r"範圍外|超出範圍|不必要抽象|不必要依賴|過度複雜|複雜度警示", 行)
    ]
    return 清理區段("\n".join(關鍵行[-4:]), 320) or "尚無範圍或複雜度警示"


def 解析_ticket(路徑: Path) -> dict[str, str]:
    內容 = 讀取文字(路徑)
    章節 = 拆解章節(內容)
    標題 = re.search(r"^#\s+(.+?)\s*$", 內容, re.MULTILINE)
    狀態 = 尋找欄位(內容, "狀態", "未知")
    編號 = re.match(r"^(\d+)", 路徑.stem)
    執行紀錄 = 章節.get("執行與 Review 紀錄", "")
    阻擋紀錄 = 章節.get("阻擋與裁決紀錄", "") if 狀態 == "阻擋" else ""
    前端驗收 = 清理區段(章節.get("前端實際操作驗收", ""), 360)
    驗收摘要 = 讀取最近證據(執行紀錄)
    if 前端驗收:
        驗收摘要 = f"{驗收摘要}\n前端操作：{前端驗收}"
    return {
        "編號": 編號.group(1) if 編號 else 路徑.stem,
        "名稱": 標題.group(1).strip() if 標題 else 路徑.stem,
        "狀態": 狀態 if 狀態 in 合法狀態 else 狀態,
        "原始需求": 清理區段(章節.get("對應原始需求", "")) or "Ticket 尚未記錄對應原始需求",
        "目標": 清理區段(章節.get("目標", "")) or "Ticket 尚未記錄目標",
        "目前紀錄": 清理區段(執行紀錄, 420) or "尚未開始執行",
        "驗收摘要": 驗收摘要,
        "品味評分": 讀取品味評分(執行紀錄),
        "範圍警示": 讀取範圍警示(執行紀錄),
        "下一步": 下一步對照.get(狀態, "查閱 Ticket 實際紀錄"),
        "阻擋內容": 清理區段(阻擋紀錄, 1200),
        "路徑": str(路徑.resolve()),
    }


def 推定專案根目錄(工作目錄: Path) -> Path:
    if 工作目錄.parent.name == "work" and 工作目錄.parent.parent.name == "docs":
        return 工作目錄.parent.parent.parent
    return 工作目錄.parent


def 讀取工作資料(工作目錄: Path, 專案根目錄: Path) -> dict[str, object]:
    規格內容 = 讀取文字(工作目錄 / "spec.md")
    工作識別碼 = 尋找欄位(規格內容, "工作識別碼", 工作目錄.name)
    顯示名稱 = 尋找欄位(規格內容, "顯示名稱")
    if not 顯示名稱:
        規格標題 = re.search(r"^#\s+(.+?)\s*$", 規格內容, re.MULTILINE)
        顯示名稱 = 規格標題.group(1).strip() if 規格標題 else 工作目錄.name

    Ticket目錄 = 工作目錄 / "tickets"
    Tickets = [解析_ticket(路徑) for 路徑 in sorted(Ticket目錄.glob("*.md"))]
    完成數 = sum(1 for Ticket in Tickets if Ticket["狀態"] == "完成")
    排序後 = sorted(Tickets, key=lambda Ticket: (目前狀態順序.get(str(Ticket["狀態"]), 9), str(Ticket["編號"])))
    目前 = 排序後[0] if 排序後 else None
    阻擋 = [
        f"{Ticket['編號']}｜{Ticket['名稱']}\n{Ticket['阻擋內容']}"
        for Ticket in Tickets
        if Ticket["狀態"] == "阻擋" and Ticket["阻擋內容"]
    ]

    歷史報告 = []
    工作根目錄 = 專案根目錄 / "docs" / "work"
    if 工作根目錄.is_dir():
        for 報告路徑 in sorted(工作根目錄.glob("*/completion-report.html"), reverse=True):
            相對工作 = 報告路徑.parent.name
            歷史報告.append(
                {
                    "名稱": f"{相對工作}｜結案報告",
                    "連結": f"/history/{quote(相對工作)}",
                    "本機連結": 報告路徑.resolve().as_uri(),
                }
            )

    結案已存在 = (工作目錄 / "completion-report.html").is_file()
    報告狀態 = "completed" if 結案已存在 else ("blocked" if 阻擋 else "in-progress")
    總數 = len(Tickets)
    return {
        "報告狀態": 報告狀態,
        "顯示名稱": 顯示名稱,
        "工作識別碼": 工作識別碼,
        "完成數": 完成數,
        "總數": 總數,
        "完成比例": round((完成數 / 總數) * 100) if 總數 else 0,
        "目前工作": f"{目前['編號']}｜{目前['名稱']}" if 目前 else "沒有 Ticket",
        "目前階段": str(目前["狀態"]) if 目前 else "尚未開始",
        "最後更新": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z"),
        "Tickets": Tickets,
        "阻擋": 阻擋,
        "歷史報告": 歷史報告,
    }


def 安全_json(資料: object) -> str:
    return (
        json.dumps(資料, ensure_ascii=False, separators=(",", ":"))
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
    )


def 產生進度頁(模板路徑: Path, 輸出路徑: Path, 資料: dict[str, object]) -> None:
    模板 = 模板路徑.read_text(encoding="utf-8")
    顯示名稱 = str(資料.get("顯示名稱", "未命名工作"))
    安全標題 = (
        顯示名稱.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )
    內容 = (
        模板.replace("{{報告狀態}}", str(資料.get("報告狀態", "in-progress")))
        .replace("{{顯示名稱}}", 安全標題)
        .replace("{{初始資料}}", 安全_json(資料))
    )
    暫存路徑 = 輸出路徑.with_name(f".{輸出路徑.name}.{os.getpid()}.tmp")
    暫存路徑.write_text(內容, encoding="utf-8")
    暫存路徑.replace(輸出路徑)


def 狀態簽章(工作目錄: Path, 專案根目錄: Path) -> tuple[tuple[str, int, int], ...]:
    路徑列表 = [工作目錄 / "spec.md", *sorted((工作目錄 / "tickets").glob("*.md"))]
    路徑列表.extend(sorted((專案根目錄 / "docs" / "work").glob("*/completion-report.html")))
    簽章 = []
    for 路徑 in 路徑列表:
        try:
            狀態 = 路徑.stat()
        except OSError:
            continue
        簽章.append((str(路徑.resolve()), 狀態.st_mtime_ns, 狀態.st_size))
    return tuple(簽章)


class 共享進度:
    def __init__(self, 工作目錄: Path, 專案根目錄: Path, 模板路徑: Path) -> None:
        self.工作目錄 = 工作目錄
        self.專案根目錄 = 專案根目錄
        self.模板路徑 = 模板路徑
        self.輸出路徑 = 工作目錄 / "progress-report.html"
        self.條件 = threading.Condition()
        self.版本 = 0
        self.資料: dict[str, object] = {}
        self.簽章: tuple[tuple[str, int, int], ...] = ()
        self.重新讀取(force=True)

    def 重新讀取(self, force: bool = False) -> bool:
        新簽章 = 狀態簽章(self.工作目錄, self.專案根目錄)
        if not force and 新簽章 == self.簽章:
            return False
        新資料 = 讀取工作資料(self.工作目錄, self.專案根目錄)
        產生進度頁(self.模板路徑, self.輸出路徑, 新資料)
        with self.條件:
            self.簽章 = 新簽章
            self.資料 = 新資料
            self.版本 += 1
            self.條件.notify_all()
        return True

    def 快照(self) -> tuple[int, dict[str, object]]:
        with self.條件:
            return self.版本, self.資料

    def 等待更新(self, 版本: int, 秒數: float) -> tuple[int, dict[str, object]]:
        with self.條件:
            if self.版本 == 版本:
                self.條件.wait(timeout=秒數)
            return self.版本, self.資料


def 建立處理器(共享: 共享進度):
    class 進度處理器(BaseHTTPRequestHandler):
        server_version = "MilkteaProgress/1.0"

        def do_GET(self) -> None:  # noqa: N802
            路徑 = urlparse(self.path).path
            if 路徑 in {"/", "/progress-report.html"}:
                self.回傳檔案(共享.輸出路徑, "text/html; charset=utf-8")
                return
            if 路徑 == "/snapshot":
                _, 資料 = 共享.快照()
                self.回傳內容(安全_json(資料).encode("utf-8"), "application/json; charset=utf-8")
                return
            if 路徑 == "/events":
                self.回傳事件()
                return
            if 路徑.startswith("/history/"):
                工作名稱 = unquote(路徑.removeprefix("/history/"))
                if not 工作名稱 or Path(工作名稱).name != 工作名稱:
                    self.send_error(HTTPStatus.BAD_REQUEST)
                    return
                報告 = 共享.專案根目錄 / "docs" / "work" / 工作名稱 / "completion-report.html"
                工作根 = (共享.專案根目錄 / "docs" / "work").resolve()
                try:
                    已解析 = 報告.resolve(strict=True)
                    已解析.relative_to(工作根)
                except (OSError, ValueError):
                    self.send_error(HTTPStatus.NOT_FOUND)
                    return
                self.回傳檔案(已解析, "text/html; charset=utf-8")
                return
            self.send_error(HTTPStatus.NOT_FOUND)

        def 回傳檔案(self, 路徑: Path, 類型: str) -> None:
            try:
                內容 = 路徑.read_bytes()
            except OSError:
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            self.回傳內容(內容, 類型)

        def 回傳內容(self, 內容: bytes, 類型: str) -> None:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", 類型)
            self.send_header("Content-Length", str(len(內容)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(內容)

        def 回傳事件(self) -> None:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Connection", "keep-alive")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()
            版本, 資料 = 共享.快照()
            try:
                while True:
                    事件 = f"event: progress\ndata: {安全_json(資料)}\n\n".encode("utf-8")
                    self.wfile.write(事件)
                    self.wfile.flush()
                    新版本, 新資料 = 共享.等待更新(版本, 15.0)
                    if 新版本 == 版本:
                        self.wfile.write(b": keep-alive\n\n")
                        self.wfile.flush()
                        continue
                    版本, 資料 = 新版本, 新資料
            except (BrokenPipeError, ConnectionResetError, OSError):
                return

        def log_message(self, 格式: str, *參數: object) -> None:
            return

    return 進度處理器


def 監看檔案(共享: 共享進度, 停止: threading.Event, 間隔秒數: float) -> None:
    while not 停止.wait(間隔秒數):
        try:
            共享.重新讀取()
        except Exception as 錯誤:  # 保留既有快照，下一輪再試
            print(f"進度讀取失敗：{錯誤}", file=sys.stderr, flush=True)


def 建立伺服器(共享: 共享進度, 主機: str, 埠號: int) -> ThreadingHTTPServer:
    伺服器 = ThreadingHTTPServer((主機, 埠號), 建立處理器(共享))
    伺服器.daemon_threads = True
    return 伺服器


def 執行自我測試() -> int:
    模板路徑 = Path(__file__).resolve().parent.parent / "assets" / "progress.html"
    with tempfile.TemporaryDirectory() as 暫存目錄:
        專案 = Path(暫存目錄) / "project"
        工作 = 專案 / "docs" / "work" / "wp-20260809-120000-a1b2c3d4"
        Tickets = 工作 / "tickets"
        Tickets.mkdir(parents=True)
        (工作 / "spec.md").write_text(
            "# 測試規格\n\n- 工作識別碼：wp-20260809-120000-a1b2c3d4\n- 顯示名稱：繁體中文測試工作\n",
            encoding="utf-8",
        )
        (Tickets / "01-first.md").write_text(
            "# 第一張 Ticket\n\n- 狀態：執行中\n\n## 目標\n\n建立可驗證功能。\n\n"
            "## 對應原始需求\n\n- 使用者要求實際功能。\n\n## 執行與 Review 紀錄\n\n測試尚在執行。\n\n"
            "## 阻擋與裁決紀錄\n",
            encoding="utf-8",
        )
        舊工作 = 專案 / "docs" / "work" / "older-work"
        舊工作.mkdir()
        (舊工作 / "completion-report.html").write_text("<html lang=\"zh-Hant\"><title>舊報告</title></html>", encoding="utf-8")

        共享 = 共享進度(工作, 專案, 模板路徑)
        內容 = 共享.輸出路徑.read_text(encoding="utf-8")
        if "http-equiv=\"refresh\"" in 內容.lower() or "setInterval" in 內容:
            print("自我測試失敗：進度頁不得自動重新整理或前端輪詢。")
            return 1
        if "繁體中文測試工作" not in 內容 or "第一張 Ticket" not in 內容:
            print("自我測試失敗：進度頁缺少工作或 Ticket 快照。")
            return 1

        伺服器 = 建立伺服器(共享, "127.0.0.1", 0)
        埠號 = int(伺服器.server_address[1])
        執行緒 = threading.Thread(target=伺服器.serve_forever, daemon=True)
        執行緒.start()
        try:
            with urlopen(f"http://127.0.0.1:{埠號}/snapshot", timeout=3) as 回應:
                資料 = json.loads(回應.read().decode("utf-8"))
            if 資料["工作識別碼"] != "wp-20260809-120000-a1b2c3d4":
                print("自我測試失敗：SSE 服務讀到錯誤工作。")
                return 1
            with urlopen(f"http://127.0.0.1:{埠號}/events", timeout=3) as 回應:
                事件行 = []
                for _ in range(4):
                    行 = 回應.readline().decode("utf-8").strip()
                    if not 行:
                        break
                    事件行.append(行)
            if "event: progress" not in 事件行 or not any(行.startswith("data: ") for 行 in 事件行):
                print("自我測試失敗：SSE 沒有送出初始進度事件。")
                return 1
            with urlopen(f"http://127.0.0.1:{埠號}/history/older-work", timeout=3) as 回應:
                if "舊報告" not in 回應.read().decode("utf-8"):
                    print("自我測試失敗：歷史報告路由錯誤。")
                    return 1
        finally:
            伺服器.shutdown()
            伺服器.server_close()
            執行緒.join(timeout=3)

    print("自我測試通過：唯一工作、靜態快照、動態 Port、SSE 資料與歷史報告皆正常。")
    return 0


def 建立參數解析器() -> argparse.ArgumentParser:
    解析器 = argparse.ArgumentParser(description="啟動 Milktea 本機 SSE 工作進度頁。")
    解析器.add_argument("work_dir", nargs="?", type=Path, help="包含 spec.md 與 tickets/ 的實際工作目錄")
    解析器.add_argument("--project-root", type=Path, help="專案根目錄；省略時由 docs/work 推定")
    解析器.add_argument("--host", default="127.0.0.1", help="只允許使用 127.0.0.1")
    解析器.add_argument("--port", type=int, default=0, help="監聽 Port；預設 0 由作業系統配置")
    解析器.add_argument("--watch-seconds", type=float, default=1.0, help="後端檢查 Ticket 變更的間隔")
    解析器.add_argument("--self-test", action="store_true", help="執行內建自我測試")
    return 解析器


def main() -> int:
    參數 = 建立參數解析器().parse_args()
    if 參數.self_test:
        return 執行自我測試()
    if 參數.work_dir is None:
        print("錯誤：必須提供實際工作目錄。", file=sys.stderr)
        return 2
    if 參數.host != "127.0.0.1":
        print("錯誤：進度服務只能綁定 127.0.0.1。", file=sys.stderr)
        return 2

    工作目錄 = 參數.work_dir.resolve()
    if not (工作目錄 / "spec.md").is_file() or not (工作目錄 / "tickets").is_dir():
        print("錯誤：工作目錄必須包含 spec.md 與 tickets/。", file=sys.stderr)
        return 2
    專案根目錄 = 參數.project_root.resolve() if 參數.project_root else 推定專案根目錄(工作目錄)
    模板路徑 = Path(__file__).resolve().parent.parent / "assets" / "progress.html"
    if not 模板路徑.is_file():
        print(f"錯誤：找不到進度頁模板：{模板路徑}", file=sys.stderr)
        return 2

    共享 = 共享進度(工作目錄, 專案根目錄, 模板路徑)
    停止 = threading.Event()
    監看執行緒 = threading.Thread(target=監看檔案, args=(共享, 停止, max(參數.watch_seconds, 0.2)), daemon=True)
    監看執行緒.start()
    伺服器 = 建立伺服器(共享, 參數.host, 參數.port)
    實際埠號 = int(伺服器.server_address[1])
    print(f"進度頁：http://127.0.0.1:{實際埠號}/progress-report.html", flush=True)
    print(f"本機快照：{共享.輸出路徑}", flush=True)
    try:
        伺服器.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        停止.set()
        伺服器.server_close()
        監看執行緒.join(timeout=3)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
