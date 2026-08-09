#!/usr/bin/env python3
"""驗證 Milktea 繁體中文 HTML 報告、兩頁生命週期與結案證據。"""

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
        "sections": {"決策摘要", "現況架構與資料流", "問題與清理候選", "改善方案", "相容性與決策"},
        "需要工作目錄": False,
    },
    "grill-me": {
        "status": "ready-for-approval",
        "sections": {"原始需求與範圍", "目標架構與資料流", "Ticket執行藍圖", "Agent與驗收設計", "風險與核准"},
        "需要工作目錄": False,
    },
    "implement": {
        "status": "pass",
        "sections": {"原始需求", "Ticket成果", "實際驗收", "風險與回復", "使用者確認"},
        "需要工作目錄": True,
    },
    "brownfield-implement": {
        "status": "pass",
        "sections": {"原始需求", "Ticket成果", "實際驗收", "風險與回復", "使用者確認"},
        "需要工作目錄": True,
    },
}

中文模式 = re.compile(r"[\u3400-\u9fff]")
模板殘留模式 = re.compile(r"\{\{.*?\}\}|(?:^|\W)TODO(?:\W|$)", re.IGNORECASE | re.DOTALL)
合法設計輔助 = {"Claude Design", "內建模板（Claude Design 無法使用）", "內建模板"}
合法Ticket狀態 = {"草稿", "已核准", "執行中", "Review 中", "修正中", "完成", "阻擋"}
未填提示 = {"", "執行階段填寫", "適用時逐項列出", "對應哪項使用者介面需求；不適用時寫明理由"}


class 報告解析器(HTMLParser):
    """只收集驗證所需結構，不執行 HTML。"""

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
        self.需求勾選數 = 0
        self.有瀏覽器證據標記 = False
        self._章節堆疊: list[str] = []
        self._標題層數 = 0
        self._設計輔助標籤: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        屬性 = {名稱: 值 or "" for 名稱, 值 in attrs}
        if tag == "html":
            self.根屬性 = 屬性
        elif tag == "meta" and 屬性.get("charset", "").lower() == "utf-8":
            self.有_utf8 = True
        elif tag == "title":
            self.有標題 = True
        elif tag == "main":
            self.有主內容 = True

        if 屬性.get("id") == "design-assist":
            self.有設計輔助 = True
            self._設計輔助標籤 = tag
        if 屬性.get("data-evidence") == "browser-acceptance":
            self.有瀏覽器證據標記 = True
        if tag == "input" and 屬性.get("type", "").lower() == "checkbox" and 屬性.get("data-requirement-id"):
            self.需求勾選數 += 1
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
        問題.append(f"模板用錯：呼叫者是 {呼叫者}，HTML 使用 {實際呼叫者 or '未設定'}")
    實際狀態 = 解析器.根屬性.get("data-report-status")
    if 實際狀態 != 規格["status"]:
        問題.append(f"觸發狀態不符：預期 {規格['status']}，實際 {實際狀態 or '未設定'}")
    if 規格["需要工作目錄"] and not 解析器.根屬性.get("data-work-id"):
        問題.append("結案報告缺少 data-work-id")
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
            問題.append(f"缺少必要事實區塊：{章節}")
            continue
        合併文字 = " ".join(解析器.章節文字[章節])
        if len(合併文字) < 12:
            問題.append(f"必要事實區塊內容過少：{章節}")

    if 規格["需要工作目錄"]:
        驗收文字 = " ".join(解析器.章節文字.get("實際驗收", []))
        if not 解析器.有瀏覽器證據標記:
            問題.append("實際驗收區缺少原生瀏覽器證據標記")
        if "瀏覽器" not in 驗收文字 and "不適用" not in 驗收文字:
            問題.append("實際驗收區沒有原生瀏覽器操作結果或不適用依據")
        if 解析器.需求勾選數 < 1:
            問題.append("使用者確認區缺少可逐項勾選的原始需求")
        if 呼叫者 == "brownfield-implement" and "原有功能" not in 驗收文字:
            問題.append("Brownfield 結案報告缺少原有功能確認證據")

    if not any(中文模式.search(文字) for 文字 in 解析器.標題文字):
        問題.append("標題必須包含繁體中文內容")
    return 問題


def 取得章節(內容: str, 名稱: str) -> str:
    結果 = re.search(rf"^##\s+{re.escape(名稱)}\s*$\n(.*?)(?=^##\s+|\Z)", 內容, re.MULTILINE | re.DOTALL)
    return 結果.group(1).strip() if 結果 else ""


def 取得欄位(內容: str, 名稱: str) -> str:
    結果 = re.search(rf"^-\s*{re.escape(名稱)}[：:]\s*(.*?)\s*$", 內容, re.MULTILINE)
    return 結果.group(1).strip() if 結果 else ""


def 驗證工作目錄(工作目錄: Path, 呼叫者: str, 報告路徑: Path) -> list[str]:
    問題: list[str] = []
    try:
        實際工作目錄 = 工作目錄.resolve(strict=True)
    except OSError:
        return [f"找不到實際工作目錄：{工作目錄}"]
    if 報告路徑.resolve() != (實際工作目錄 / "completion-report.html").resolve():
        問題.append("結案報告必須位於實際工作目錄的 completion-report.html")

    Ticket目錄 = 實際工作目錄 / "tickets"
    Ticket路徑 = sorted(Ticket目錄.glob("*.md")) if Ticket目錄.is_dir() else []
    if not Ticket路徑:
        return 問題 + ["實際工作目錄沒有 Ticket"]

    for 路徑 in Ticket路徑:
        try:
            內容 = 路徑.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as 錯誤:
            問題.append(f"Ticket 無法讀取：{路徑.name}：{錯誤}")
            continue
        狀態 = 取得欄位(內容, "狀態")
        if 狀態 not in 合法Ticket狀態:
            問題.append(f"Ticket 狀態不合法：{路徑.name}：{狀態 or '未設定'}")
        elif 狀態 != "完成":
            問題.append(f"Ticket 尚未完成：{路徑.name}：{狀態}")

        前端驗收 = 取得章節(內容, "前端實際操作驗收")
        適用性 = 取得欄位(前端驗收, "適用性")
        判定依據 = 取得欄位(前端驗收, "判定依據")
        if 適用性 not in {"適用", "不適用"}:
            問題.append(f"Ticket 缺少前端操作適用性：{路徑.name}")
            continue
        if 判定依據 in 未填提示:
            問題.append(f"Ticket 缺少前端操作判定依據：{路徑.name}")
        if 適用性 == "適用":
            工具 = 取得欄位(前端驗收, "使用的原生瀏覽器工具")
            網址 = 取得欄位(前端驗收, "操作環境與實際網址")
            結果 = 取得欄位(前端驗收, "操作結果與證據")
            if 工具 in 未填提示:
                問題.append(f"Ticket 缺少原生瀏覽器工具證據：{路徑.name}")
            if 網址 in 未填提示:
                問題.append(f"Ticket 缺少實際前端網址：{路徑.name}")
            if 結果 in 未填提示 or "通過" not in 結果:
                問題.append(f"Ticket 的前端實際操作尚未通過：{路徑.name}")

    if 呼叫者 == "brownfield-implement":
        合併內容 = "\n".join(路徑.read_text(encoding="utf-8") for 路徑 in Ticket路徑)
        if "原有功能" not in 合併內容:
            問題.append("Brownfield Tickets 缺少原有功能確認紀錄")
    return 問題


def 驗證檔案(路徑: Path, 呼叫者: str, 工作目錄: Path | None = None) -> list[str]:
    if not 路徑.is_file():
        return [f"找不到報告：{路徑}"]
    try:
        內容 = 路徑.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ["報告不是有效的 UTF-8 檔案"]
    問題 = 驗證內容(內容, 呼叫者)
    if 報告規格[呼叫者]["需要工作目錄"]:
        if 工作目錄 is None:
            問題.append("Implement 結案驗證必須提供 --work-dir")
        else:
            問題.extend(驗證工作目錄(工作目錄, 呼叫者, 路徑))
    return 問題


def 建立一般測試文件(呼叫者: str) -> str:
    規格 = 報告規格[呼叫者]
    章節 = "".join(
        f'<section id="{名稱}"><h2>繁體中文章節</h2><p>這是足夠長度且可驗證的繁體中文內容。</p></section>'
        for 名稱 in sorted(規格["sections"])
    )
    return (
        f'<!doctype html><html lang="zh-Hant" data-report-profile="{呼叫者}" '
        f'data-report-status="{規格["status"]}"><head><meta charset="utf-8">'
        '<title>繁體中文測試報告</title></head><body><div id="design-assist">內建模板</div>'
        f'<main>{章節}</main></body></html>'
    )


def 建立結案測試文件(呼叫者: str, 工作識別碼: str) -> str:
    模板 = (Path(__file__).resolve().parent.parent / "assets" / "completion.html").read_text(encoding="utf-8")
    原有功能 = "原有功能修改前後皆通過。" if 呼叫者 == "brownfield-implement" else ""
    替換 = {
        "{{呼叫者識別}}": 呼叫者,
        "{{工作識別碼}}": 工作識別碼,
        "{{顯示名稱}}": "繁體中文測試工作",
        "{{報告類型}}": "重構結案報告" if 呼叫者 == "brownfield-implement" else "功能結案報告",
        "{{最終結論}}": "全部驗收通過",
        "{{需求完成摘要}}": "一／一項完成",
        "{{Ticket完成摘要}}": "一／一張完成",
        "{{瀏覽器驗收摘要}}": "原生瀏覽器操作通過",
        "{{結論內容}}": "<p>所有核准內容均已完成並保存可重現證據。</p>",
        "{{原始需求標題}}": "原始重構目標" if 呼叫者 == "brownfield-implement" else "原始需求",
        "{{原始需求內容}}": "<p>核准的原始需求已逐項完成並保存證據。</p>",
        "{{Ticket成果內容}}": "<p>全部 Ticket 與 Review 已完成。</p>",
        "{{實際驗收內容}}": f"<p>原生瀏覽器操作通過。{原有功能}</p>",
        "{{詳細證據}}": "<details><summary>查看證據</summary><p>退出碼零，畫面操作通過。</p></details>",
        "{{風險與回復內容}}": "<p>沒有已知未解風險，回復步驟已有記錄。</p>",
        "{{使用者確認項目}}": '<div class="確認項目"><input id="R-01" type="checkbox" data-requirement-id="R-01"><label for="R-01">確認第一項原始需求。</label></div>',
        "{{設計輔助}}": "內建模板",
    }
    for 欄位, 內容 in 替換.items():
        模板 = 模板.replace(欄位, 內容)
    return 模板


def 執行自我測試() -> int:
    with tempfile.TemporaryDirectory() as 暫存目錄:
        根目錄 = Path(暫存目錄)
        for 呼叫者 in {"brownfield-planner", "grill-me"}:
            路徑 = 根目錄 / f"{呼叫者}.html"
            路徑.write_text(建立一般測試文件(呼叫者), encoding="utf-8")
            問題 = 驗證檔案(路徑, 呼叫者)
            if 問題:
                print(f"自我測試失敗（{呼叫者}）：{'；'.join(問題)}")
                return 1

        for 呼叫者 in {"implement", "brownfield-implement"}:
            工作識別碼 = f"wp-20260809-120000-{呼叫者[:4]}"
            工作目錄 = 根目錄 / 呼叫者 / "docs" / "work" / 工作識別碼
            Ticket目錄 = 工作目錄 / "tickets"
            Ticket目錄.mkdir(parents=True)
            Ticket內容 = (
                "# 測試 Ticket\n\n- 狀態：完成\n\n## 前端實際操作驗收\n\n"
                "- 適用性：適用\n- 判定依據：這是使用者介面需求。\n"
                "- 操作環境與實際網址：http://127.0.0.1:4567\n"
                "- 使用的原生瀏覽器工具：Codex Browser\n"
                "- 操作步驟與預期結果：實際點擊並觀察畫面。\n"
                "- 操作結果與證據：通過，截圖已保存。\n"
            )
            if 呼叫者 == "brownfield-implement":
                Ticket內容 += "\n## 原有功能確認\n\n原有功能修改前後皆通過。\n"
            (Ticket目錄 / "01-test.md").write_text(Ticket內容, encoding="utf-8")
            報告 = 工作目錄 / "completion-report.html"
            報告.write_text(建立結案測試文件(呼叫者, 工作識別碼), encoding="utf-8")
            問題 = 驗證檔案(報告, 呼叫者, 工作目錄)
            if 問題:
                print(f"自我測試失敗（{呼叫者}）：{'；'.join(問題)}")
                return 1

            未完成Ticket = Ticket內容.replace("- 狀態：完成", "- 狀態：修正中")
            (Ticket目錄 / "01-test.md").write_text(未完成Ticket, encoding="utf-8")
            if not any("尚未完成" in 項目 for 項目 in 驗證檔案(報告, 呼叫者, 工作目錄)):
                print("自我測試失敗：驗證器沒有攔截未完成 Ticket。")
                return 1

        錯誤內容 = 建立一般測試文件("grill-me").replace("data-report-profile=\"grill-me\"", "data-report-profile=\"implement\"")
        if not 驗證內容(錯誤內容, "grill-me"):
            print("自我測試失敗：驗證器沒有攔截錯用模板。")
            return 1
        殘留內容 = 建立一般測試文件("brownfield-planner").replace("繁體中文測試報告", "{{尚未替換}}")
        if not 驗證內容(殘留內容, "brownfield-planner"):
            print("自我測試失敗：驗證器沒有攔截模板殘留。")
            return 1

    print("自我測試通過：規劃報告、需求驅動結案報告、工作目錄閘門與錯誤案例皆符合預期。")
    return 0


def 建立參數解析器() -> argparse.ArgumentParser:
    解析器 = argparse.ArgumentParser(description="驗證 Milktea 繁體中文 HTML 報告。")
    解析器.add_argument("report", nargs="?", type=Path, help="要驗證的 HTML 報告路徑")
    解析器.add_argument("--caller", choices=sorted(報告規格), help="呼叫者固定識別")
    解析器.add_argument("--work-dir", type=Path, help="Implement 結案報告的實際工作目錄")
    解析器.add_argument("--self-test", action="store_true", help="執行驗證器自我測試")
    return 解析器


def main() -> int:
    參數 = 建立參數解析器().parse_args()
    if 參數.self_test:
        return 執行自我測試()
    if 參數.report is None or 參數.caller is None:
        print("錯誤：一般驗證必須同時提供 --caller 與報告路徑。", file=sys.stderr)
        return 2
    問題 = 驗證檔案(參數.report, 參數.caller, 參數.work_dir)
    if 問題:
        print(f"報告驗證失敗：{參數.report}")
        for 項目 in 問題:
            print(f"- {項目}")
        return 1
    print(f"報告驗證通過：{參數.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
