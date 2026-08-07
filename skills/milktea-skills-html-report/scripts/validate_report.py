#!/usr/bin/env python3
"""驗證四種 Milktea 繁體中文 HTML 報告是否使用正確規格。"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path


報告規格 = {
    "brownfield-planner": {
        "status": "ready-for-decision",
        "sections": {
            "決策摘要",
            "現況架構與資料流",
            "問題與清理候選",
            "改善方案",
            "相容性與決策",
        },
    },
    "grill-me": {
        "status": "ready-for-approval",
        "sections": {
            "原始需求與範圍",
            "目標架構與資料流",
            "Ticket執行藍圖",
            "Agent與驗收設計",
            "風險與核准",
        },
    },
    "implement": {
        "status": "pass",
        "sections": {
            "原始要求完成狀態",
            "實際修改內容",
            "架構與資料流前後對比",
            "改善數據",
            "最終驗收",
        },
    },
    "brownfield-implement": {
        "status": "pass",
        "sections": {
            "原始重構目標",
            "清理與修改結果",
            "架構與資料流前後差異",
            "改善與相容性數據",
            "最終安全驗收",
        },
    },
}

中文模式 = re.compile(r"[\u3400-\u9fff]")
模板殘留模式 = re.compile(r"\{\{.*?\}\}|(?:^|\W)TODO(?:\W|$)", re.IGNORECASE | re.DOTALL)
合法設計輔助 = {
    "Claude Design",
    "內建模板（Claude Design 無法使用）",
    "內建模板",
}


class 報告解析器(HTMLParser):
    """只收集驗證所需結構，不執行任何網頁內容。"""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.根屬性: dict[str, str] = {}
        self.有_utf8 = False
        self.有標題 = False
        self.有主內容 = False
        self.有設計輔助 = False
        self.設計輔助文字: list[str] = []
        self.章節文字: dict[str, list[str]] = {}
        self.標題文字: list[str] = []
        self._章節堆疊: list[str] = []
        self._標題層數 = 0
        self._設計輔助標籤: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        屬性 = {名稱: 值 or "" for 名稱, 值 in attrs}

        if tag == "html":
            self.根屬性 = 屬性
        elif tag == "meta":
            if 屬性.get("charset", "").lower() == "utf-8":
                self.有_utf8 = True
        elif tag == "title":
            self.有標題 = True
        elif tag == "main":
            self.有主內容 = True

        if 屬性.get("id") == "design-assist":
            self.有設計輔助 = True
            self._設計輔助標籤 = tag

        if tag == "section" and 屬性.get("id"):
            章節 = 屬性["id"]
            self._章節堆疊.append(章節)
            self.章節文字.setdefault(章節, [])

        if tag in {"h1", "h2", "h3"}:
            self._標題層數 += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "section" and self._章節堆疊:
            self._章節堆疊.pop()
        if tag in {"h1", "h2", "h3"} and self._標題層數:
            self._標題層數 -= 1
        if tag == self._設計輔助標籤:
            self._設計輔助標籤 = None

    def handle_data(self, data: str) -> None:
        文字 = data.strip()
        if not 文字:
            return
        if self._章節堆疊:
            self.章節文字[self._章節堆疊[-1]].append(文字)
        if self._標題層數:
            self.標題文字.append(文字)
        if self._設計輔助標籤:
            self.設計輔助文字.append(文字)


def 驗證內容(內容: str, 呼叫者: str) -> list[str]:
    問題: list[str] = []
    規格 = 報告規格[呼叫者]
    解析器 = 報告解析器()

    try:
        解析器.feed(內容)
    except Exception as 錯誤:
        return [f"HTML 無法解析：{錯誤}"]

    if 解析器.根屬性.get("lang") != "zh-Hant":
        問題.append('html 的 lang 必須是 "zh-Hant"')

    實際呼叫者 = 解析器.根屬性.get("data-report-profile")
    if 實際呼叫者 != 呼叫者:
        問題.append(
            f"模板用錯：呼叫者是 {呼叫者}，HTML 使用 {實際呼叫者 or '未設定'}"
        )

    實際狀態 = 解析器.根屬性.get("data-report-status")
    if 實際狀態 != 規格["status"]:
        問題.append(
            f"觸發狀態不符：預期 {規格['status']}，實際 {實際狀態 or '未設定'}"
        )

    if not 解析器.有_utf8:
        問題.append("缺少 UTF-8 charset")
    if not 解析器.有標題:
        問題.append("缺少 title")
    if not 解析器.有主內容:
        問題.append("缺少 main")
    if not 解析器.有設計輔助:
        問題.append('缺少 id="design-assist" 的設計輔助欄位')
    elif " ".join(解析器.設計輔助文字) not in 合法設計輔助:
        問題.append("設計輔助標記不合法或與平台規則不符")
    if 模板殘留模式.search(內容):
        問題.append("發現尚未替換的模板欄位或未完成提示")

    for 章節 in sorted(規格["sections"]):
        if 章節 not in 解析器.章節文字:
            問題.append(f"缺少必要章節：{章節}")
            continue
        合併文字 = " ".join(解析器.章節文字[章節])
        if len(合併文字) < 12:
            問題.append(f"必要章節內容過少：{章節}")

    if not any(中文模式.search(文字) for 文字 in 解析器.標題文字):
        問題.append("標題必須包含繁體中文內容")

    return 問題


def 驗證檔案(路徑: Path, 呼叫者: str) -> list[str]:
    if not 路徑.is_file():
        return [f"找不到報告：{路徑}"]

    try:
        內容 = 路徑.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ["報告不是有效的 UTF-8 檔案"]

    return 驗證內容(內容, 呼叫者)


def 建立測試文件(呼叫者: str) -> str:
    規格 = 報告規格[呼叫者]
    章節 = "".join(
        f'<section id="{名稱}"><h2>繁體中文章節</h2>'
        '<p>這是足夠長度且可驗證的繁體中文內容。</p></section>'
        for 名稱 in sorted(規格["sections"])
    )
    return (
        f'<!doctype html><html lang="zh-Hant" data-report-profile="{呼叫者}" '
        f'data-report-status="{規格["status"]}"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>繁體中文測試報告</title></head><body>'
        f'<div id="design-assist">內建模板</div><main>{章節}</main></body></html>'
    )


def 執行自我測試() -> int:
    with tempfile.TemporaryDirectory() as 暫存目錄:
        根目錄 = Path(暫存目錄)

        for 呼叫者 in 報告規格:
            路徑 = 根目錄 / f"{呼叫者}.html"
            路徑.write_text(建立測試文件(呼叫者), encoding="utf-8")
            問題 = 驗證檔案(路徑, 呼叫者)
            if 問題:
                print(f"自我測試失敗（{呼叫者}）：")
                for 項目 in 問題:
                    print(f"- {項目}")
                return 1

        錯誤內容 = 建立測試文件("implement").replace(
            'data-report-profile="implement"',
            'data-report-profile="brownfield-planner"',
        )
        if not 驗證內容(錯誤內容, "implement"):
            print("自我測試失敗：驗證器沒有攔截錯用模板。")
            return 1

        殘留內容 = 建立測試文件("grill-me").replace(
            "繁體中文測試報告",
            "{{尚未替換}}",
        )
        if not 驗證內容(殘留內容, "grill-me"):
            print("自我測試失敗：驗證器沒有攔截模板殘留。")
            return 1

        設計錯誤內容 = 建立測試文件("brownfield-planner").replace(
            "內建模板",
            "未知設計工具",
        )
        if not 驗證內容(設計錯誤內容, "brownfield-planner"):
            print("自我測試失敗：驗證器沒有攔截錯誤的設計輔助標記。")
            return 1

    print("自我測試通過：四種報告與三個錯誤案例均符合預期。")
    return 0


def 建立參數解析器() -> argparse.ArgumentParser:
    解析器 = argparse.ArgumentParser(description="驗證 Milktea 繁體中文 HTML 報告。")
    解析器.add_argument("report", nargs="?", type=Path, help="要驗證的 HTML 報告路徑")
    解析器.add_argument(
        "--caller",
        choices=sorted(報告規格),
        help="呼叫者固定識別",
    )
    解析器.add_argument("--self-test", action="store_true", help="執行驗證器自我測試")
    return 解析器


def main() -> int:
    參數 = 建立參數解析器().parse_args()

    if 參數.self_test:
        return 執行自我測試()

    if 參數.report is None or 參數.caller is None:
        print("錯誤：一般驗證必須同時提供 --caller 與報告路徑。", file=sys.stderr)
        return 2

    問題 = 驗證檔案(參數.report, 參數.caller)
    if 問題:
        print(f"報告驗證失敗：{參數.report}")
        for 項目 in 問題:
            print(f"- {項目}")
        return 1

    print(f"報告驗證通過：{參數.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
