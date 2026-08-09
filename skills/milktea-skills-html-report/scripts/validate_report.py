#!/usr/bin/env python3
"""驗證 Milktea HTML 報告，並以候選檔原子發布不可變結案報告。"""

from __future__ import annotations

import argparse
import html
import os
import re
import sys
import tempfile
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


報告規格 = {
    "brownfield-planner": {
        "status": "ready-for-decision",
        "sections": {"決策摘要", "現況架構與資料流", "問題與清理候選", "改善方案", "相容性與決策"},
        "需要工作目錄": False,
        "template": "brownfield-planner.html",
    },
    "grill-me": {
        "status": "ready-for-approval",
        "sections": {"原始需求與範圍", "目標架構與資料流", "Ticket執行藍圖", "Agent與驗收設計", "風險與核准"},
        "需要工作目錄": False,
        "template": "grill-me.html",
    },
    "implement": {
        "status": "pass",
        "sections": {"原始需求", "Ticket成果", "實際驗收", "風險與回復", "使用者確認"},
        "需要工作目錄": True,
        "template": "completion.html",
    },
    "brownfield-implement": {
        "status": "pass",
        "sections": {"原始需求", "Ticket成果", "實際驗收", "風險與回復", "使用者確認"},
        "需要工作目錄": True,
        "template": "completion.html",
    },
}

結案呼叫者 = {"implement", "brownfield-implement"}
中文模式 = re.compile(r"[\u3400-\u9fff]")
模板殘留模式 = re.compile(r"\{\{.*?\}\}|(?:^|\W)TODO(?:\W|$)", re.IGNORECASE | re.DOTALL)
新工作識別碼模式 = re.compile(r"wp-\d{8}-\d{6}-[0-9a-f]{8}")
需求識別碼模式 = re.compile(r"R-\d{3}")
舊需求識別碼模式 = re.compile(r"R-LEGACY-\d{3}")
合法設計輔助 = {"Claude Design", "內建模板（Claude Design 無法使用）", "內建模板"}
合法Ticket狀態 = {"草稿", "已核准", "執行中", "Review 中", "修正中", "完成", "阻擋"}
合法Reviewer模式 = {"both", "a_only", "b_only"}
合法原生瀏覽器工具 = {
    "Codex Browser",
    "Codex 原生瀏覽器",
    "Codex Chrome",
    "Codex Computer Use",
    "Claude Browser",
    "Claude 原生瀏覽器",
    "Claude Chrome",
    "Claude Computer Use",
    "browser:control-in-app-browser",
    "chrome:control-chrome",
    "computer-use:computer-use",
}
未填提示 = {
    "",
    "執行階段填寫",
    "適用時逐項列出",
    "對應哪項使用者介面需求；不適用時寫明理由",
    "尚待執行",
    "尚未執行",
    "待填",
}
失敗或未驗證模式 = re.compile(r"未通過|不通過|失敗|尚未驗證|未驗證|尚待|沒有反應")
不可靠證據模式 = re.compile(r"無法確認|假設|推測|不確定|尚未驗證|未驗證")
未完成占位模式 = re.compile(r"執行階段填寫|規劃階段填寫|適用／不適用|必填|待補|待確認")
允許標籤 = {
    "html", "head", "meta", "title", "style", "body", "main", "header", "section", "article",
    "div", "span", "p", "h1", "h2", "h3", "h4", "small", "strong", "em", "b", "i",
    "table", "thead", "tbody", "tr", "th", "td", "ul", "ol", "li", "dl", "dt", "dd",
    "details", "summary", "pre", "code", "blockquote", "time", "a", "input", "label", "br", "hr", "script",
}
危險URL模式 = re.compile(r"^\s*(?:javascript|vbscript|data):", re.IGNORECASE)
危險CSS模式 = re.compile(r"@import|url\s*\(|expression\s*\(|javascript:|vbscript:|behavior\s*:|-moz-binding", re.IGNORECASE)
清單禁用CSS模式 = re.compile(
    r"(?:display\s*:\s*none|visibility\s*:\s*hidden|pointer-events\s*:\s*none|opacity\s*:\s*0(?:\.0*)?)(?:\s*!important)?",
    re.IGNORECASE,
)
清單CSS目標 = (
    "#使用者確認", "[data-user-checklist]", "[data-requirement-id]", "[type=checkbox]",
    ".確認清單", ".確認項目", "html", "body", "main", "section", "div", "input", "label", "*",
)
Grill必要章節 = (
    "目標", "對應原始需求", "使用者價值", "範圍", "已確認實作決策", "驗收條件", "測試與證據",
    "前端實際操作驗收", "依賴", "並行與所有權", "初始執行配置", "Agent 分工", "完成規則",
    "執行與 Review 紀錄", "阻擋與裁決紀錄",
)
Grill必填文字章節 = ("目標", "使用者價值", "範圍", "已確認實作決策", "驗收條件", "完成規則")
Grill不允許規劃值 = {
    "無／Ticket", "parallel-safe／serialized", "實際檔案或模組", "無／實際資源",
    "符合的具體條件", "無／實際 Markdown 路徑", "每條都必須可觀察、可判定。",
}


def URL屬性不安全(值: str) -> bool:
    if any(ord(字元) < 32 or ord(字元) == 127 for 字元 in 值):
        return True
    正規化值 = re.sub(r"[\t\r\n]", "", 值)
    return bool(危險URL模式.search(正規化值))


class 報告解析器(HTMLParser):
    """收集結構與安全屬性；不執行 HTML。"""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.根屬性: dict[str, str] = {}
        self.文件宣告: list[str] = []
        self.元素: list[tuple[str, dict[str, str]]] = []
        self.所有ID: list[str] = []
        self.html開始數 = 0
        self.有_utf8 = False
        self.有標題 = False
        self.有主內容 = False
        self.有設計輔助 = False
        self.設計輔助文字: list[str] = []
        self.章節文字: dict[str, list[str]] = {}
        self.標題文字: list[str] = []
        self.需求識別碼: list[str] = []
        self.有瀏覽器證據標記 = False
        self.有最終驗收標記 = False
        self.安全問題: list[str] = []
        self.腳本內容: list[list[str]] = []
        self.腳本屬性: list[dict[str, str]] = []
        self.樣式內容: list[list[str]] = []
        self.確認輸入: list[dict[str, str]] = []
        self.確認標籤: list[dict[str, object]] = []
        self._章節堆疊: list[str] = []
        self._標題層數 = 0
        self._設計輔助標籤: str | None = None
        self._腳本索引: int | None = None
        self._樣式索引: int | None = None
        self._動態文字標籤: str | None = None
        self._目前確認標籤: dict[str, object] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        屬性名稱 = [名稱.lower() for 名稱, _ in attrs]
        重複屬性 = sorted(名稱 for 名稱, 次數 in Counter(屬性名稱).items() if 次數 > 1)
        if 重複屬性:
            self.安全問題.append(f"同一個 <{tag}> 不得重複屬性名稱：{', '.join(重複屬性)}")
        屬性: dict[str, str] = {}
        for 名稱, 值 in attrs:
            屬性.setdefault(名稱.lower(), 值 or "")
        self.元素.append((tag, 屬性))
        if 屬性.get("id"):
            self.所有ID.append(屬性["id"])
        位於確認區 = "使用者確認" in self._章節堆疊 or (
            tag == "section" and 屬性.get("id") == "使用者確認"
        )
        if tag not in 允許標籤:
            self.安全問題.append(f"不允許的 HTML 標籤：<{tag}>")
        if self._動態文字標籤 is not None:
            self.安全問題.append(f"動態文字必須先跳脫，不能插入 <{tag}>")
        if self._目前確認標籤 is not None:
            self.安全問題.append(f"需求 label 必須是純文字，不能插入 <{tag}>")
        for 名稱, 值 in 屬性.items():
            if 名稱.startswith("on"):
                self.安全問題.append(f"不允許事件屬性：{名稱}")
            if 名稱 in {"href", "src", "action", "formaction"} and URL屬性不安全(值):
                self.安全問題.append(f"不允許可執行 URL：{名稱}")
            if 名稱 == "style":
                self.安全問題.append("動態內容不得加入 style 屬性")
        if tag == "meta" and 屬性.get("http-equiv"):
            self.安全問題.append("不允許 meta http-equiv；報告不能重新整理或重新導向")
        if tag == "html":
            self.html開始數 += 1
            if self.html開始數 == 1:
                self.根屬性 = 屬性
        elif tag == "meta" and 屬性.get("charset", "").lower() == "utf-8":
            self.有_utf8 = True
        elif tag == "title":
            self.有標題 = True
        elif tag == "main":
            self.有主內容 = True
        elif tag == "script":
            self.腳本內容.append([])
            self.腳本屬性.append(屬性)
            self._腳本索引 = len(self.腳本內容) - 1
            if 屬性:
                self.安全問題.append("固定 script 不得有任何屬性（包含 src）")
        elif tag == "style":
            self.樣式內容.append([])
            self._樣式索引 = len(self.樣式內容) - 1

        if 屬性.get("data-dynamic-text"):
            self._動態文字標籤 = tag
        if 屬性.get("id") == "design-assist":
            self.有設計輔助 = True
            self._設計輔助標籤 = tag
        if 屬性.get("data-evidence") == "browser-acceptance":
            self.有瀏覽器證據標記 = True
        if 屬性.get("data-evidence") == "final-acceptance" and 屬性.get("data-result") == "通過":
            self.有最終驗收標記 = True
        if tag == "input" and 位於確認區:
            if 屬性.get("type", "").lower() != "checkbox" or not 屬性.get("data-requirement-id"):
                self.安全問題.append("使用者確認區的 input 必須是具有 data-requirement-id 的 checkbox")
            else:
                self.需求識別碼.append(屬性["data-requirement-id"])
                self.確認輸入.append(屬性)
        elif tag == "input" and 屬性.get("data-requirement-id"):
            self.安全問題.append("需求 checkbox 必須位於使用者確認區")
        if tag == "label" and 位於確認區:
            標籤資料: dict[str, object] = {"for": 屬性.get("for", ""), "文字": []}
            self.確認標籤.append(標籤資料)
            self._目前確認標籤 = 標籤資料
        if tag == "section" and 屬性.get("id"):
            章節 = 屬性["id"]
            self._章節堆疊.append(章節)
            self.章節文字.setdefault(章節, [])
        if tag in {"h1", "h2", "h3"}:
            self._標題層數 += 1

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "section" and self._章節堆疊:
            self._章節堆疊.pop()
        if tag in {"h1", "h2", "h3"} and self._標題層數:
            self._標題層數 -= 1
        if tag == self._設計輔助標籤:
            self._設計輔助標籤 = None
        if tag == self._動態文字標籤:
            self._動態文字標籤 = None
        if tag == "label":
            self._目前確認標籤 = None
        if tag == "script":
            self._腳本索引 = None
        if tag == "style":
            self._樣式索引 = None

    def handle_data(self, data: str) -> None:
        if self._腳本索引 is not None:
            self.腳本內容[self._腳本索引].append(data)
        if self._樣式索引 is not None:
            self.樣式內容[self._樣式索引].append(data)
        if self._目前確認標籤 is not None:
            文字列表 = self._目前確認標籤["文字"]
            assert isinstance(文字列表, list)
            文字列表.append(data)
        文字 = data.strip()
        if not 文字:
            return
        if self._章節堆疊:
            self.章節文字[self._章節堆疊[-1]].append(文字)
        if self._標題層數:
            self.標題文字.append(文字)
        if self._設計輔助標籤:
            self.設計輔助文字.append(文字)

    def handle_decl(self, decl: str) -> None:
        self.文件宣告.append(decl.strip().lower())


def 解析HTML(內容: str) -> tuple[報告解析器, list[str]]:
    解析器 = 報告解析器()
    try:
        解析器.feed(內容)
        解析器.close()
    except Exception as 錯誤:
        return 解析器, [f"HTML 無法解析：{錯誤}"]
    return 解析器, list(dict.fromkeys(解析器.安全問題))


def 驗證Completion元素契約(解析器: 報告解析器) -> list[str]:
    問題: list[str] = []
    無屬性標籤 = {"head", "title", "style", "body", "main", "h1", "article", "small", "strong", "h2", "script"}
    動態文字槽 = {"結論內容", "原始需求內容", "Ticket成果內容", "實際驗收內容", "詳細證據", "風險與回復內容"}
    需求模式 = re.compile(r"(?:R-\d{3}|R-LEGACY-\d{3})")

    def 規則名稱(tag: str, 屬性: dict[str, str]) -> str | None:
        if tag in 無屬性標籤 and not 屬性:
            return tag
        if tag == "html" and set(屬性) == {"lang", "data-report-profile", "data-report-status", "data-work-id"}:
            return "html"
        if tag == "meta":
            if 屬性 == {"charset": "utf-8"}:
                return "meta-charset"
            if 屬性 == {"name": "viewport", "content": "width=device-width, initial-scale=1"}:
                return "meta-viewport"
        if tag == "header" and 屬性 == {"id": "結論"}:
            return "header-結論"
        if tag == "p":
            if 屬性 in ({"class": "眉題"}, {"class": "識別"}):
                return f"p-{屬性['class']}"
            if 屬性 == {"id": "確認進度", "class": "確認摘要", "role": "status", "aria-live": "polite"}:
                return "p-確認進度"
        if tag == "div":
            for 類別 in ("通過", "摘要", "證據", "確認清單", "確認項目"):
                if 屬性 == {"class": 類別}:
                    return f"div-{類別}"
            if 屬性 == {"class": "驗收狀態", "data-evidence": "final-acceptance", "data-result": "通過"}:
                return "div-最終驗收"
            if 屬性 == {"id": "design-assist"}:
                return "div-design-assist"
        if tag == "section":
            if 屬性 in ({"id": "原始需求"}, {"id": "Ticket成果"}, {"id": "風險與回復"}):
                return f"section-{屬性['id']}"
            if 屬性 == {"id": "實際驗收", "data-evidence": "browser-acceptance"}:
                return "section-實際驗收"
            if 屬性 == {"id": "使用者確認", "data-user-checklist": ""}:
                return "section-使用者確認"
        if tag == "pre" and set(屬性) == {"class", "data-dynamic-text"} and 屬性["class"] == "動態文字":
            槽 = 屬性["data-dynamic-text"]
            if 槽 in 動態文字槽:
                return f"pre-{槽}"
        if tag == "input" and set(屬性) == {"id", "type", "data-requirement-id"}:
            if 屬性["type"].lower() == "checkbox" and 屬性["id"] == 屬性["data-requirement-id"] and 需求模式.fullmatch(屬性["id"]):
                return "input-需求"
        if tag == "label" and set(屬性) == {"for"} and 需求模式.fullmatch(屬性["for"]):
            return "label-需求"
        return None

    計數: Counter[str] = Counter()
    for tag, 屬性 in 解析器.元素:
        規則 = 規則名稱(tag, 屬性)
        if 規則 is None:
            問題.append(f"completion 元素不符合固定模板 allowlist：<{tag}>")
        else:
            計數[規則] += 1

    固定計數 = {
        "html": 1, "head": 1, "meta-charset": 1, "meta-viewport": 1, "title": 1, "style": 1,
        "body": 1, "main": 1, "header-結論": 1, "p-眉題": 1, "h1": 1, "p-識別": 1,
        "div-通過": 1, "div-摘要": 1, "article": 3, "small": 3, "strong": 3,
        "pre-結論內容": 1, "section-原始需求": 1, "h2": 5, "pre-原始需求內容": 1,
        "section-Ticket成果": 1, "pre-Ticket成果內容": 1, "section-實際驗收": 1,
        "div-最終驗收": 1, "pre-實際驗收內容": 1, "div-證據": 1, "pre-詳細證據": 1,
        "section-風險與回復": 1, "pre-風險與回復內容": 1, "section-使用者確認": 1,
        "p-確認進度": 1, "div-確認清單": 1, "div-design-assist": 1, "script": 1,
    }
    for 規則, 預期 in 固定計數.items():
        if 計數[規則] != 預期:
            問題.append(f"completion 關鍵結構「{規則}」必須恰好出現 {預期} 次，實際 {計數[規則]} 次")
    需求項目數 = 計數["input-需求"]
    if 計數["label-需求"] != 需求項目數 or 計數["div-確認項目"] != 需求項目數:
        問題.append("completion 每個需求必須恰好有一個確認項目、一個 checkbox 與一個 label")
    if 解析器.html開始數 != 1:
        問題.append(f"completion 的 <html> 根 start tag 必須恰好出現一次，實際 {解析器.html開始數} 次")
    if 解析器.文件宣告 != ["doctype html"]:
        問題.append("completion 必須恰好有一個 <!doctype html>")
    重複ID = sorted(識別碼 for 識別碼, 次數 in Counter(解析器.所有ID).items() if 次數 != 1)
    if 重複ID:
        問題.append(f"completion 全文件 id 必須唯一：{', '.join(重複ID)}")
    return 問題


def 取得模板固定區塊(呼叫者: str, 標籤: str) -> list[str]:
    模板路徑 = Path(__file__).resolve().parent.parent / "assets" / str(報告規格[呼叫者]["template"])
    try:
        模板 = 模板路徑.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    return [
        區塊.replace("\r\n", "\n").replace("\r", "\n").strip()
        for 區塊 in re.findall(rf"<{標籤}(?:\s[^>]*)?>(.*?)</{標籤}>", 模板, re.IGNORECASE | re.DOTALL)
    ]


def 驗證固定程式與樣式(解析器: 報告解析器, 呼叫者: str) -> list[str]:
    問題: list[str] = []
    def 正規化(值: str) -> str:
        return 值.replace("\r\n", "\n").replace("\r", "\n").strip()

    實際腳本 = [正規化("".join(區塊)) for 區塊 in 解析器.腳本內容]
    實際樣式 = [正規化("".join(區塊)) for 區塊 in 解析器.樣式內容]
    固定樣式 = 取得模板固定區塊(呼叫者, "style")
    if 實際腳本 != 取得模板固定區塊(呼叫者, "script"):
        問題.append("報告包含新增或被改寫的 script；只允許固定模板程式")
    if len(實際樣式) != len(固定樣式):
        問題.append("報告不得新增或移除 style 區塊")
    elif any(危險CSS模式.search(樣式) for 樣式 in 實際樣式):
        問題.append("style 包含外部載入或可執行 CSS")
    if 呼叫者 in 結案呼叫者:
        for 樣式 in 實際樣式:
            for 選擇器, 宣告 in re.findall(r"([^{}]+)\{([^{}]*)\}", 樣式, re.DOTALL):
                if any(目標 in 選擇器 for 目標 in 清單CSS目標) and 清單禁用CSS模式.search(宣告):
                    問題.append("completion CSS 不得隱藏使用者確認清單或停用互動")
                    return 問題
        if 實際樣式 != 固定樣式:
            問題.append("completion style 必須與固定模板完全一致，不得新增 selector 或改寫 CSS")
    return 問題


def 驗證內容(內容: str, 呼叫者: str) -> list[str]:
    問題: list[str] = []
    規格 = 報告規格[呼叫者]
    解析器, 解析問題 = 解析HTML(內容)
    問題.extend(解析問題)
    問題.extend(驗證固定程式與樣式(解析器, 呼叫者))
    if 呼叫者 in 結案呼叫者:
        問題.extend(驗證Completion元素契約(解析器))

    if 解析器.根屬性.get("lang") != "zh-Hant":
        問題.append('html 的 lang 必須是 "zh-Hant"')
    實際呼叫者 = 解析器.根屬性.get("data-report-profile")
    if 實際呼叫者 != 呼叫者:
        問題.append(f"模板用錯：呼叫者是 {呼叫者}，HTML 使用 {實際呼叫者 or '未設定'}")
    實際狀態 = 解析器.根屬性.get("data-report-status")
    if 實際狀態 != 規格["status"]:
        問題.append(f"觸發狀態不符：預期 {規格['status']}，實際 {實際狀態 or '未設定'}")
    if (規格["需要工作目錄"] or 呼叫者 in {"brownfield-planner", "grill-me"}) and not 解析器.根屬性.get("data-work-id"):
        問題.append("報告缺少 data-work-id")
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
        if not 解析器.有最終驗收標記:
            問題.append("實際驗收區缺少精確的最終總驗收通過標記")
        if not 解析器.需求識別碼:
            問題.append("使用者確認區缺少可逐項勾選的原始需求")

    if not any(中文模式.search(文字) for 文字 in 解析器.標題文字):
        問題.append("標題必須包含繁體中文內容")
    return 問題


def 取得章節(內容: str, 名稱: str) -> str:
    結果 = re.search(rf"^##\s+{re.escape(名稱)}\s*$\n(.*?)(?=^##\s+|\Z)", 內容, re.MULTILINE | re.DOTALL)
    return 結果.group(1).strip() if 結果 else ""


def 章節存在(內容: str, 名稱: str) -> bool:
    return bool(re.search(rf"^##\s+{re.escape(名稱)}\s*$", 內容, re.MULTILINE))


def 取得欄位(內容: str, 名稱: str) -> str:
    結果 = re.search(rf"^-\s*{re.escape(名稱)}[：:]\s*(.*?)\s*$", 內容, re.MULTILINE)
    return 結果.group(1).strip() if 結果 else ""


def 取得欄位列表(內容: str, 名稱: str) -> list[str]:
    return [
        結果.strip()
        for 結果 in re.findall(rf"^-\s*{re.escape(名稱)}[：:]\s*(.*?)\s*$", 內容, re.MULTILINE)
    ]


def 取得前言(內容: str) -> str:
    return re.split(r"^##\s+", 內容, maxsplit=1, flags=re.MULTILINE)[0]


def 取得唯一機器欄位(
    全文: str,
    指定區段: str,
    名稱: str,
    區段名稱: str,
    問題: list[str],
    文件名稱: str,
) -> str:
    全部值 = 取得欄位列表(全文, 名稱)
    區段值 = 取得欄位列表(指定區段, 名稱)
    if len(區段值) != 1:
        問題.append(f"{文件名稱} 的「{名稱}」必須在{區段名稱}恰好出現一次，實際 {len(區段值)} 次")
    if len(全部值) != 1:
        問題.append(f"{文件名稱} 的機器欄位「{名稱}」全文件必須恰好出現一次，實際 {len(全部值)} 次")
    return 區段值[0] if len(區段值) == 1 else ""


def 是未完成占位(值: str) -> bool:
    return 值 in 未填提示 or bool(未完成占位模式.search(值))


def 是未完成Grill規劃值(值: str) -> bool:
    值 = 值.strip()
    return (
        是未完成占位(值)
        or 值 in Grill不允許規劃值
        or bool(re.fullmatch(r"〈[^〉]+〉", 值))
    )


def 取得唯一欄位組(
    全文: str,
    指定區段: str,
    欄位名稱: tuple[str, ...],
    區段名稱: str,
    問題: list[str],
    文件名稱: str,
) -> dict[str, str]:
    return {
        名稱: 取得唯一機器欄位(全文, 指定區段, 名稱, 區段名稱, 問題, 文件名稱)
        for 名稱 in 欄位名稱
    }


def 實際網址合法(網址: str) -> bool:
    if 網址 in 未填提示 or 失敗或未驗證模式.search(網址):
        return False
    try:
        結果 = urlsplit(網址)
    except ValueError:
        return False
    if 結果.scheme in {"http", "https"}:
        return bool(結果.hostname) and 結果.hostname not in {"example.com", "example.org", "example.net"}
    if 結果.scheme == "file":
        return bool(結果.path and 結果.path not in {"/", "."})
    return False


def 解析需求對照(內容: str, 模式: re.Pattern[str]) -> tuple[dict[str, str], set[str]]:
    對照: dict[str, str] = {}
    重複或衝突: set[str] = set()
    行模式 = re.compile(rf"^\s*-\s*({模式.pattern})\s*[：:]\s*(\S.*?)\s*$", re.MULTILINE)
    for 結果 in 行模式.finditer(內容):
        識別碼, 原文 = 結果.group(1), 結果.group(2).strip()
        if 識別碼 in 對照:
            重複或衝突.add(識別碼)
        else:
            對照[識別碼] = 原文
    return 對照, 重複或衝突


def HTML包含精確需求對照(HTML文字: str, 識別碼: str, 原文: str) -> bool:
    正規化HTML = re.sub(r"\s+", " ", HTML文字).strip()
    正規化原文 = re.sub(r"\s+", " ", 原文).strip()
    原文模式 = re.escape(正規化原文).replace(r"\ ", r"\s+")
    return bool(re.search(rf"{re.escape(識別碼)}\s*[：:]\s*{原文模式}", 正規化HTML))


def 驗證Reviewer證據(Ticket名稱: str, 內容: str) -> list[str]:
    問題: list[str] = []
    紀錄 = 取得章節(內容, "執行與 Review 紀錄")
    if not 紀錄:
        問題.append(f"Ticket 缺少執行與 Review 紀錄：{Ticket名稱}")
    取值 = lambda 名稱: 取得唯一機器欄位(內容, 紀錄, 名稱, "「執行與 Review 紀錄」", 問題, Ticket名稱)
    Developer結論 = 取值("Developer 結論")
    Reviewer模式 = 取值("Reviewer 模式")
    ReviewerA = 取值("Reviewer A 結論")
    ReviewerB = 取值("Reviewer B 結論")
    未關閉 = 取值("未關閉阻擋或重要 Findings")
    最終驗收 = 取值("Ticket 最終驗收")

    if Developer結論 != "通過":
        問題.append(f"Ticket Developer 結論必須精確為通過：{Ticket名稱}")
    if Reviewer模式 not in 合法Reviewer模式:
        問題.append(f"Ticket Reviewer 模式不合法：{Ticket名稱}：{Reviewer模式 or '未設定'}")
    else:
        預期A = "不適用" if Reviewer模式 == "b_only" else "通過"
        預期B = "不適用" if Reviewer模式 == "a_only" else "通過"
        if ReviewerA != 預期A:
            問題.append(f"Ticket Reviewer A 結論應為{預期A}：{Ticket名稱}")
        if ReviewerB != 預期B:
            問題.append(f"Ticket Reviewer B 結論應為{預期B}：{Ticket名稱}")
    if 未關閉 != "0":
        問題.append(f"Ticket 仍有未關閉的阻擋或重要 Findings：{Ticket名稱}：{未關閉 or '未設定'}")
    if 最終驗收 != "通過":
        問題.append(f"Ticket 最終驗收必須精確為通過：{Ticket名稱}")
    return 問題


def 驗證Ticket(路徑: Path, 呼叫者: str) -> tuple[list[str], str]:
    問題: list[str] = []
    try:
        內容 = 路徑.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as 錯誤:
        return [f"Ticket 無法讀取：{路徑.name}：{錯誤}"], ""

    狀態 = 取得唯一機器欄位(內容, 取得前言(內容), "狀態", "文件前言", 問題, 路徑.name)
    if 狀態 not in 合法Ticket狀態:
        問題.append(f"Ticket 狀態不合法：{路徑.name}：{狀態 or '未設定'}")
    elif 狀態 != "完成":
        問題.append(f"Ticket 尚未完成：{路徑.name}：{狀態}")

    前端驗收 = 取得章節(內容, "前端實際操作驗收")
    前端欄位 = lambda 名稱: 取得唯一機器欄位(
        內容, 前端驗收, 名稱, "「前端實際操作驗收」", 問題, 路徑.name
    )
    適用性 = 前端欄位("適用性")
    判定依據 = 前端欄位("判定依據")
    工具 = 前端欄位("使用的原生瀏覽器工具")
    網址 = 前端欄位("操作環境與實際網址")
    步驟 = 前端欄位("操作步驟與預期結果")
    結果 = 前端欄位("操作結果")
    證據 = 前端欄位("操作證據")
    if 適用性 not in {"適用", "不適用"}:
        問題.append(f"Ticket 缺少前端操作適用性：{路徑.name}")
    elif 是未完成占位(判定依據) or 判定依據 == "不適用":
        問題.append(f"Ticket 缺少前端操作判定依據：{路徑.name}")
    elif 適用性 == "適用":
        if 工具 not in 合法原生瀏覽器工具:
            問題.append(f"Ticket 使用的不是允許的 Claude／Codex 原生瀏覽器工具：{路徑.name}：{工具 or '未設定'}")
        if not 實際網址合法(網址):
            問題.append(f"Ticket 缺少真實 http／https／file 前端網址：{路徑.name}")
        if 步驟 == "不適用" or 是未完成占位(步驟):
            問題.append(f"Ticket 缺少可執行的前端操作步驟與預期結果：{路徑.name}")
        if 結果 != "通過":
            問題.append(f"Ticket 的前端操作結果必須精確為通過：{路徑.name}")
        if 證據 == "不適用" or 是未完成占位(證據) or 失敗或未驗證模式.search(證據):
            問題.append(f"Ticket 缺少已通過的前端操作證據：{路徑.name}")
    elif any(值 != "不適用" for 值 in {工具, 網址, 步驟, 結果, 證據}):
        問題.append(f"Ticket 前端不適用時，工具、網址、操作步驟、操作結果與操作證據都必須精確填「不適用」：{路徑.name}")

    問題.extend(驗證Reviewer證據(路徑.name, 內容))

    if 呼叫者 == "brownfield-implement":
        原有功能 = 取得章節(內容, "原有功能確認")
        原有欄位 = lambda 名稱: 取得唯一機器欄位(
            內容, 原有功能, 名稱, "「原有功能確認」", 問題, 路徑.name
        )
        共用方法 = 原有欄位("共用驗證方法")
        修改前基準 = 原有欄位("修改前基準")
        修改後結果 = 原有欄位("修改後結果")
        原有功能結果 = 原有欄位("原有功能驗收")
        原有功能證據 = 原有欄位("驗收證據")
        for 名稱, 值 in {"共用驗證方法": 共用方法, "修改前基準": 修改前基準, "修改後結果": 修改後結果}.items():
            if 值 == "不適用" or 是未完成占位(值) or 不可靠證據模式.search(值):
                問題.append(f"Brownfield Ticket 的{名稱}必須是可確認的非占位內容：{路徑.name}")
        if 原有功能結果 != "通過":
            問題.append(f"Brownfield Ticket 原有功能驗收必須精確為通過：{路徑.name}")
        if 原有功能證據 == "不適用" or 是未完成占位(原有功能證據) or 失敗或未驗證模式.search(原有功能證據) or 不可靠證據模式.search(原有功能證據):
            問題.append(f"Brownfield Ticket 缺少已通過的原有功能證據：{路徑.name}")
    return 問題, 內容


def 驗證工作目錄(
    工作目錄: Path,
    呼叫者: str,
    報告路徑: Path,
    報告內容: str,
    候選模式: bool,
) -> list[str]:
    問題: list[str] = []
    try:
        實際工作目錄 = 工作目錄.resolve(strict=True)
    except OSError:
        return [f"找不到實際工作目錄：{工作目錄}"]

    預期檔名 = "completion-report.pending.html" if 候選模式 else "completion-report.html"
    if 報告路徑.name != 預期檔名 or 報告路徑.parent.resolve() != 實際工作目錄:
        問題.append(f"結案報告必須位於實際工作目錄的 {預期檔名}")
    if 報告路徑.is_symlink():
        問題.append("結案報告不能是指向其他位置的符號連結")
    正式路徑 = 實際工作目錄 / "completion-report.html"
    if 候選模式 and 正式路徑.exists():
        問題.append("正式 completion-report.html 已存在；不得覆寫或重新發布")

    Spec路徑 = 實際工作目錄 / "spec.md"
    try:
        Spec內容 = Spec路徑.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as 錯誤:
        return 問題 + [f"Spec 無法讀取：{錯誤}"]
    Spec前言 = 取得前言(Spec內容)
    Spec工作識別碼 = 取得唯一機器欄位(
        Spec內容, Spec前言, "工作識別碼", "文件前言", 問題, "spec.md"
    )
    Spec狀態 = 取得唯一機器欄位(Spec內容, Spec前言, "狀態", "文件前言", 問題, "spec.md")
    if Spec狀態 != "已核准":
        問題.append(f"Spec 狀態必須精確為已核准，實際為：{Spec狀態 or '未設定'}")
    HTML解析器, _ = 解析HTML(報告內容)
    HTML工作識別碼 = HTML解析器.根屬性.get("data-work-id", "")
    目錄工作識別碼 = 實際工作目錄.name
    if 目錄工作識別碼.startswith("wp-") and not 新工作識別碼模式.fullmatch(目錄工作識別碼):
        問題.append("新工作識別碼必須符合 wp-YYYYMMDD-HHmmss-xxxxxxxx")
    if 新工作識別碼模式.fullmatch(目錄工作識別碼):
        if 實際工作目錄.parent.name != "work" or 實際工作目錄.parent.parent.name != "docs":
            問題.append("新工作目錄必須位於專案的 docs/work/<工作識別碼>/")
    if not Spec工作識別碼:
        問題.append("Spec 缺少工作識別碼")
    if Spec工作識別碼 and Spec工作識別碼 != 目錄工作識別碼:
        問題.append(f"Spec 與工作目錄的工作識別碼不一致：{Spec工作識別碼} != {目錄工作識別碼}")
    if HTML工作識別碼 != 目錄工作識別碼:
        問題.append(f"HTML 與工作目錄的工作識別碼不一致：{HTML工作識別碼 or '未設定'} != {目錄工作識別碼}")

    Ticket目錄 = 實際工作目錄 / "tickets"
    Ticket路徑 = sorted(Ticket目錄.glob("*.md")) if Ticket目錄.is_dir() else []
    if not Ticket路徑:
        return 問題 + ["實際工作目錄沒有 Ticket"]
    Ticket內容列表: list[tuple[Path, str]] = []
    for 路徑 in Ticket路徑:
        Ticket問題, Ticket內容 = 驗證Ticket(路徑, 呼叫者)
        問題.extend(Ticket問題)
        if Ticket內容:
            Ticket內容列表.append((路徑, Ticket內容))

    原始需求章節 = 取得章節(Spec內容, "原始需求") or Spec內容
    需求對照, 重複需求 = 解析需求對照(原始需求章節, 需求識別碼模式)
    使用舊需求對照 = False
    if 重複需求:
        問題.append(f"Spec 原始需求識別碼重複：{', '.join(sorted(重複需求))}")
    if not 需求對照:
        if 新工作識別碼模式.fullmatch(目錄工作識別碼):
            問題.append("新工作 Spec 的原始需求缺少 R-001 起的穩定識別碼")
        else:
            使用舊需求對照 = True
            舊對照: dict[str, str] = {}
            衝突: set[str] = set()
            for Ticket路徑, Ticket內容 in Ticket內容列表:
                對應章節 = 取得章節(Ticket內容, "對應原始需求")
                當前對照, 當前重複 = 解析需求對照(對應章節, 舊需求識別碼模式)
                if not 當前對照:
                    問題.append(f"舊工作 Ticket 缺少 R-LEGACY-001 起的原始需求對照：{Ticket路徑.name}")
                衝突.update(當前重複)
                for 識別碼, 原文 in 當前對照.items():
                    if 識別碼 in 舊對照 and 舊對照[識別碼] != 原文:
                        衝突.add(識別碼)
                    舊對照.setdefault(識別碼, 原文)
            if 衝突:
                問題.append(f"舊工作需求識別碼重複或對應原文不一致：{', '.join(sorted(衝突))}")
            需求對照 = 舊對照
            if not 需求對照:
                問題.append("舊工作必須先建立 R-LEGACY-001 起的明確需求對照，不能退回只檢查一個勾選框")

    if 需求對照 and not 使用舊需求對照:
        已覆蓋需求: set[str] = set()
        for Ticket路徑, Ticket內容 in Ticket內容列表:
            對應章節 = 取得章節(Ticket內容, "對應原始需求")
            Ticket對照, Ticket重複 = 解析需求對照(對應章節, 需求識別碼模式)
            if Ticket重複:
                問題.append(f"Ticket 對應原始需求識別碼重複：{Ticket路徑.name}：{', '.join(sorted(Ticket重複))}")
            if not Ticket對照:
                問題.append(f"Ticket 沒有以 R-xxx 對應任何 Spec 原始需求：{Ticket路徑.name}")
                continue
            for 識別碼, 原文 in Ticket對照.items():
                if 識別碼 not in 需求對照:
                    問題.append(f"Ticket 引用 Spec 不存在的原始需求：{Ticket路徑.name}：{識別碼}")
                    continue
                if 原文 != 需求對照[識別碼]:
                    問題.append(f"Ticket 的原始需求原文與 Spec 不一致：{Ticket路徑.name}：{識別碼}")
                    continue
                已覆蓋需求.add(識別碼)
        未被Ticket覆蓋 = sorted(set(需求對照) - 已覆蓋需求)
        if 未被Ticket覆蓋:
            問題.append(f"Spec 原始需求沒有任何 Ticket 負責：{', '.join(未被Ticket覆蓋)}")

    報告計數 = Counter(HTML解析器.需求識別碼)
    非法報告識別碼 = sorted(識別碼 for 識別碼 in 報告計數 if 識別碼 not in 需求對照)
    遺漏 = sorted(識別碼 for 識別碼 in 需求對照 if 報告計數[識別碼] == 0)
    重複 = sorted(識別碼 for 識別碼, 次數 in 報告計數.items() if 次數 != 1)
    if 遺漏:
        問題.append(f"使用者確認清單遺漏原始需求：{', '.join(遺漏)}")
    if 非法報告識別碼:
        問題.append(f"使用者確認清單包含 Spec／舊工作對照沒有的需求：{', '.join(非法報告識別碼)}")
    if 重複:
        問題.append(f"使用者確認清單的需求識別碼必須恰好出現一次：{', '.join(重複)}")

    全文件ID計數 = Counter(HTML解析器.所有ID)
    for 需求ID in 需求對照:
        if 全文件ID計數[需求ID] != 1:
            問題.append(f"需求 ID 在 completion 全文件必須恰好出現一次，且唯一節點必須是對應 checkbox：{需求ID}")

    輸入ID計數 = Counter(屬性.get("id", "") for 屬性 in HTML解析器.確認輸入)
    標籤for計數 = Counter(str(標籤.get("for", "")) for 標籤 in HTML解析器.確認標籤)
    for 屬性 in HTML解析器.確認輸入:
        需求識別碼 = 屬性.get("data-requirement-id", "")
        輸入ID = 屬性.get("id", "")
        if not 輸入ID or 輸入ID != 需求識別碼:
            問題.append(f"需求 checkbox 的 id 必須與 data-requirement-id 相同：{需求識別碼 or '未設定'}")
        if 輸入ID計數[輸入ID] != 1:
            問題.append(f"需求 checkbox id 必須唯一：{輸入ID or '未設定'}")
        if 標籤for計數[輸入ID] != 1:
            問題.append(f"每個需求 checkbox 必須恰好有一個對應 label：{輸入ID or '未設定'}")
    for 標籤 in HTML解析器.確認標籤:
        對應ID = str(標籤.get("for", ""))
        文字片段 = 標籤.get("文字", [])
        標籤文字 = "".join(文字片段).strip() if isinstance(文字片段, list) else ""
        if 輸入ID計數[對應ID] != 1:
            問題.append(f"需求 label 必須恰好對應一個 checkbox：{對應ID or '未設定'}")
            continue
        if 對應ID in 需求對照:
            預期文字 = f"{對應ID}：{需求對照[對應ID]}"
            if 標籤文字 != 預期文字:
                問題.append(f"需求 label 必須顯示 exact R-ID 與 Spec 原始需求原文：{對應ID}")
    return 問題


def 驗證GrillTicket(
    路徑: Path,
    內容: str,
    Spec需求: dict[str, str],
) -> tuple[list[str], set[str]]:
    問題: list[str] = []
    文件名稱 = 路徑.name
    標題 = re.search(r"^#\s+(\S.*?)\s*$", 內容, re.MULTILINE)
    if not 標題 or 是未完成Grill規劃值(標題.group(1)):
        問題.append(f"Grill-me Ticket 缺少實際標題：{文件名稱}")

    for 章節 in Grill必要章節:
        if not 章節存在(內容, 章節):
            問題.append(f"Grill-me Ticket 缺少必要章節「{章節}」：{文件名稱}")
    for 章節 in Grill必填文字章節:
        章節內容 = 取得章節(內容, 章節)
        if not 章節內容 or 是未完成Grill規劃值(章節內容):
            問題.append(f"Grill-me Ticket 的「{章節}」缺少已完成規劃內容：{文件名稱}")

    前言 = 取得前言(內容)
    前言欄位 = 取得唯一欄位組(
        內容, 前言, ("狀態", "Spec", "Blocked by"), "文件前言", 問題, 文件名稱
    )
    if 前言欄位["狀態"] != "草稿":
        問題.append(f"Grill-me 產生實作藍圖時 Ticket 狀態必須精確為草稿：{文件名稱}：{前言欄位['狀態'] or '未設定'}")
    for 名稱 in ("Spec", "Blocked by"):
        if 是未完成Grill規劃值(前言欄位[名稱]):
            問題.append(f"Grill-me Ticket 的「{名稱}」仍是空值或規劃占位：{文件名稱}")

    對應章節 = 取得章節(內容, "對應原始需求")
    Ticket需求, Ticket重複 = 解析需求對照(對應章節, 需求識別碼模式)
    if Ticket重複:
        問題.append(f"Grill-me Ticket 的 R-ID 重複：{文件名稱}：{', '.join(sorted(Ticket重複))}")
    if not Ticket需求:
        問題.append(f"Grill-me Ticket 沒有對應任何 Spec R-ID：{文件名稱}")
    有效覆蓋: set[str] = set()
    for 識別碼, 原文 in Ticket需求.items():
        if 識別碼 not in Spec需求:
            問題.append(f"Grill-me Ticket 引用 Spec 不存在的 R-ID：{文件名稱}：{識別碼}")
        elif 原文 != Spec需求[識別碼]:
            問題.append(f"Grill-me Ticket 的 R-ID 原文與 Spec 不一致：{文件名稱}：{識別碼}")
        else:
            有效覆蓋.add(識別碼)

    測試欄位 = 取得唯一欄位組(
        內容,
        取得章節(內容, "測試與證據"),
        ("測試接縫", "迭代期快速檢查", "Ready for Review 完整驗收", "Findings 修正後", "必交證據", "保存位置"),
        "「測試與證據」",
        問題,
        文件名稱,
    )
    for 名稱, 值 in 測試欄位.items():
        if 是未完成Grill規劃值(值):
            問題.append(f"Grill-me Ticket 的測試欄位「{名稱}」仍是空值或規劃占位：{文件名稱}")

    前端欄位 = 取得唯一欄位組(
        內容,
        取得章節(內容, "前端實際操作驗收"),
        ("適用性", "判定依據", "操作環境與實際網址", "使用的原生瀏覽器工具", "操作步驟與預期結果", "操作結果", "操作證據"),
        "「前端實際操作驗收」",
        問題,
        文件名稱,
    )
    適用性 = 前端欄位["適用性"]
    if 適用性 not in {"適用", "不適用"}:
        問題.append(f"Grill-me Ticket 前端適用性必須在規劃階段決定：{文件名稱}")
    if 是未完成Grill規劃值(前端欄位["判定依據"]) or 前端欄位["判定依據"] == "不適用":
        問題.append(f"Grill-me Ticket 缺少前端適用性判定依據：{文件名稱}")
    if 適用性 == "適用" and 是未完成Grill規劃值(前端欄位["操作步驟與預期結果"]):
        問題.append(f"Grill-me Ticket 缺少規劃完成的前端操作步驟與預期結果：{文件名稱}")
    if 適用性 == "不適用" and 前端欄位["操作步驟與預期結果"] != "不適用":
        問題.append(f"Grill-me Ticket 前端不適用時操作步驟必須精確填「不適用」：{文件名稱}")
    for 名稱 in ("操作環境與實際網址", "使用的原生瀏覽器工具", "操作結果", "操作證據"):
        if not 前端欄位[名稱]:
            問題.append(f"Grill-me Ticket 缺少預建的前端執行欄位「{名稱}」：{文件名稱}")

    依賴欄位 = 取得唯一欄位組(
        內容, 取得章節(內容, "依賴"), ("Depends on", "Blocks"), "「依賴」", 問題, 文件名稱
    )
    所有權欄位 = 取得唯一欄位組(
        內容,
        取得章節(內容, "並行與所有權"),
        ("Dispatch", "Exclusive write scope", "Shared resource locks", "Can run with"),
        "「並行與所有權」",
        問題,
        文件名稱,
    )
    if 所有權欄位["Dispatch"] not in {"parallel-safe", "serialized"}:
        問題.append(f"Grill-me Ticket Dispatch 必須精確為 parallel-safe 或 serialized：{文件名稱}")
    for 名稱, 值 in {**依賴欄位, **所有權欄位}.items():
        if 是未完成Grill規劃值(值):
            問題.append(f"Grill-me Ticket 的依賴／所有權欄位「{名稱}」仍是空值或規劃占位：{文件名稱}")

    配置欄位 = 取得唯一欄位組(
        內容,
        取得章節(內容, "初始執行配置"),
        ("Developer model", "model_reasoning_effort", "路由理由", "升級路徑", "執行時覆寫", "Research 證據"),
        "「初始執行配置」",
        問題,
        文件名稱,
    )
    模型值 = 配置欄位["Developer model"]
    if sum(模型 in 模型值 for 模型 in ("claude-sonnet-5", "claude-opus-5")) != 1:
        問題.append(f"Grill-me Ticket 必須選定一個 Developer 相容預設模型：{文件名稱}")
    if "high" not in 配置欄位["model_reasoning_effort"] or "xhigh" in 配置欄位["model_reasoning_effort"]:
        問題.append(f"Grill-me Ticket 初始 model_reasoning_effort 必須選定 high：{文件名稱}")
    for 名稱, 值 in 配置欄位.items():
        if 是未完成Grill規劃值(值):
            問題.append(f"Grill-me Ticket 的初始配置欄位「{名稱}」仍是空值或規劃占位：{文件名稱}")

    Agent欄位 = 取得唯一欄位組(
        內容,
        取得章節(內容, "Agent 分工"),
        ("Developer", "Reviewer A", "Reviewer B", "Reviewer 啟用規則", "Reviewer 標準", "CLI 與模型"),
        "「Agent 分工」",
        問題,
        文件名稱,
    )
    for 名稱, 值 in Agent欄位.items():
        if 是未完成Grill規劃值(值):
            問題.append(f"Grill-me Ticket 的 Agent 分工欄位「{名稱}」仍是空值或規劃占位：{文件名稱}")

    執行欄位 = 取得唯一欄位組(
        內容,
        取得章節(內容, "執行與 Review 紀錄"),
        ("Developer 結論", "Reviewer 模式", "Reviewer A 結論", "Reviewer B 結論", "未關閉阻擋或重要 Findings", "Ticket 最終驗收"),
        "「執行與 Review 紀錄」",
        問題,
        文件名稱,
    )
    for 名稱, 值 in 執行欄位.items():
        if not 值:
            問題.append(f"Grill-me Ticket 缺少預建的執行欄位「{名稱}」：{文件名稱}")
    return 問題, 有效覆蓋


def 驗證Grill工作包(
    報告路徑: Path,
    報告內容: str,
    專案根目錄: Path | None,
    工作識別碼: str | None,
) -> list[str]:
    問題: list[str] = []
    if 專案根目錄 is None or 工作識別碼 is None:
        return ["Grill-me 報告驗證必須提供 --project-root 與 --work-id"]
    if not 工作識別碼 or Path(工作識別碼).name != 工作識別碼 or 工作識別碼 in {".", ".."}:
        return ["Grill-me 工作識別碼不是安全的單一目錄名稱"]
    if 工作識別碼.startswith("wp-") and not 新工作識別碼模式.fullmatch(工作識別碼):
        問題.append("Grill-me 新工作識別碼必須符合 wp-YYYYMMDD-HHmmss-xxxxxxxx")
    try:
        實際專案根目錄 = 專案根目錄.resolve(strict=True)
    except OSError:
        return 問題 + [f"找不到專案根目錄：{專案根目錄}"]
    工作目錄 = 實際專案根目錄 / "docs" / "work" / 工作識別碼
    預期報告 = 工作目錄 / "implementation-plan.html"
    if 報告路徑.name != 預期報告.name or 報告路徑.parent.resolve() != 工作目錄.resolve():
        問題.append("Grill-me 報告路徑必須是 docs/work/<工作識別碼>/implementation-plan.html")
    if 報告路徑.is_symlink():
        問題.append("Grill-me 報告不能是指向其他位置的符號連結")
    HTML解析器, _ = 解析HTML(報告內容)
    if HTML解析器.根屬性.get("data-work-id") != 工作識別碼:
        問題.append("Grill-me HTML data-work-id 與傳入工作識別碼不一致")

    Spec路徑 = 工作目錄 / "spec.md"
    try:
        Spec內容 = Spec路徑.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as 錯誤:
        return 問題 + [f"Grill-me Spec 無法讀取：{錯誤}"]
    Spec前言 = 取得前言(Spec內容)
    SpecID = 取得唯一機器欄位(Spec內容, Spec前言, "工作識別碼", "文件前言", 問題, "spec.md")
    Spec狀態 = 取得唯一機器欄位(Spec內容, Spec前言, "狀態", "文件前言", 問題, "spec.md")
    if SpecID != 工作識別碼:
        問題.append(f"Grill-me Spec 工作識別碼不一致：{SpecID or '未設定'} != {工作識別碼}")
    if Spec狀態 != "已核准":
        問題.append(f"Grill-me Spec 狀態必須精確為已核准，實際為：{Spec狀態 or '未設定'}")
    Spec原始需求 = 取得章節(Spec內容, "原始需求")
    Spec需求, Spec重複需求 = 解析需求對照(Spec原始需求, 需求識別碼模式)
    if Spec重複需求:
        問題.append(f"Grill-me Spec 原始需求 R-ID 重複：{', '.join(sorted(Spec重複需求))}")
    if not Spec需求:
        問題.append("Grill-me Spec 的「原始需求」缺少唯一 R-xxx 與原始需求原文")

    Ticket目錄 = 工作目錄 / "tickets"
    Ticket路徑 = sorted(Ticket目錄.glob("*.md")) if Ticket目錄.is_dir() else []
    if not Ticket路徑:
        問題.append("Grill-me 工作包沒有 Ticket 草稿")
    已覆蓋需求: set[str] = set()
    for 路徑 in Ticket路徑:
        try:
            內容 = 路徑.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as 錯誤:
            問題.append(f"Grill-me Ticket 無法讀取：{路徑.name}：{錯誤}")
            continue
        Ticket問題, Ticket覆蓋 = 驗證GrillTicket(路徑, 內容, Spec需求)
        問題.extend(Ticket問題)
        已覆蓋需求.update(Ticket覆蓋)
    未覆蓋需求 = sorted(set(Spec需求) - 已覆蓋需求)
    if 未覆蓋需求:
        問題.append(f"Grill-me Spec 原始需求沒有任何 Ticket 覆蓋：{', '.join(未覆蓋需求)}")

    HTML需求文字 = " ".join(HTML解析器.章節文字.get("原始需求與範圍", []))
    for 識別碼, 原文 in Spec需求.items():
        if not HTML包含精確需求對照(HTML需求文字, 識別碼, 原文):
            問題.append(f"Grill-me HTML 的「原始需求與範圍」未逐字顯示 Spec 需求：{識別碼}")
    return 問題


def 驗證已讀內容(
    內容: str,
    路徑: Path,
    呼叫者: str,
    工作目錄: Path | None = None,
    候選模式: bool = False,
    專案根目錄: Path | None = None,
    工作識別碼: str | None = None,
) -> list[str]:
    問題 = 驗證內容(內容, 呼叫者)
    if 報告規格[呼叫者]["需要工作目錄"]:
        if 工作目錄 is None:
            問題.append("Implement 結案驗證必須提供 --work-dir")
        else:
            問題.extend(驗證工作目錄(工作目錄, 呼叫者, 路徑, 內容, 候選模式))
    elif 候選模式:
        問題.append("--candidate 只適用於 Implement 或 Brownfield Implement 結案報告")
    if 呼叫者 == "brownfield-planner":
        HTML解析器, _ = 解析HTML(內容)
        if 專案根目錄 is None or 工作識別碼 is None:
            問題.append("Brownfield Planner 報告驗證必須提供 --project-root 與 --work-id")
        else:
            try:
                實際專案根目錄 = 專案根目錄.resolve(strict=True)
            except OSError:
                問題.append(f"找不到專案根目錄：{專案根目錄}")
            else:
                預期路徑 = 實際專案根目錄 / "docs" / "architecture-reviews" / 工作識別碼 / "architecture-review.html"
                if 路徑.name != 預期路徑.name or 路徑.parent.resolve() != 預期路徑.parent.resolve():
                    問題.append("Brownfield Planner 報告路徑必須是 docs/architecture-reviews/<工作識別碼>/architecture-review.html")
                if 路徑.is_symlink():
                    問題.append("Brownfield Planner 報告不能是指向其他位置的符號連結")
            if not 新工作識別碼模式.fullmatch(工作識別碼):
                問題.append("Brownfield Planner 工作識別碼必須符合 wp-YYYYMMDD-HHmmss-xxxxxxxx")
            if HTML解析器.根屬性.get("data-work-id") != 工作識別碼:
                問題.append("Brownfield Planner HTML data-work-id 與傳入工作識別碼不一致")
    if 呼叫者 == "grill-me":
        問題.extend(驗證Grill工作包(路徑, 內容, 專案根目錄, 工作識別碼))
    return 問題


def 驗證檔案(
    路徑: Path,
    呼叫者: str,
    工作目錄: Path | None = None,
    候選模式: bool = False,
    專案根目錄: Path | None = None,
    工作識別碼: str | None = None,
) -> list[str]:
    if not 路徑.is_file():
        return [f"找不到報告：{路徑}"]
    try:
        內容 = 路徑.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ["報告不是有效的 UTF-8 檔案"]
    except OSError as 錯誤:
        return [f"報告無法讀取：{錯誤}"]
    return 驗證已讀內容(內容, 路徑, 呼叫者, 工作目錄, 候選模式, 專案根目錄, 工作識別碼)


def 正式結案報告有效(路徑: Path, 工作目錄: Path) -> bool:
    """供進度服務判斷：只接受位於工作目錄且完整通過驗證的正式報告。"""
    try:
        內容 = 路徑.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    呼叫者結果 = re.search(r'<html\b[^>]*\bdata-report-profile=["\']([^"\']+)["\']', 內容, re.IGNORECASE)
    if not 呼叫者結果 or 呼叫者結果.group(1) not in 結案呼叫者:
        return False
    return not 驗證已讀內容(內容, 路徑, 呼叫者結果.group(1), 工作目錄, 候選模式=False)


def 發布候選報告(候選路徑: Path, 呼叫者: str, 工作目錄: Path) -> list[str]:
    """驗證同一批位元組後，以 hard-link 原子建立正式檔；永不覆寫既有正式檔。"""
    try:
        內容位元 = 候選路徑.read_bytes()
        內容 = 內容位元.decode("utf-8")
    except UnicodeDecodeError:
        return ["候選報告不是有效的 UTF-8 檔案"]
    except OSError as 錯誤:
        return [f"候選報告無法讀取：{錯誤}"]
    問題 = 驗證已讀內容(內容, 候選路徑, 呼叫者, 工作目錄, 候選模式=True)
    if 問題:
        return 問題

    實際工作目錄 = 工作目錄.resolve()
    正式路徑 = 實際工作目錄 / "completion-report.html"
    try:
        暫存描述符, 暫存名稱 = tempfile.mkstemp(
            prefix=".completion-report.", suffix=".verified.tmp", dir=實際工作目錄
        )
    except OSError as 錯誤:
        return [f"無法建立原子發布暫存檔：{錯誤}"]
    驗證暫存 = Path(暫存名稱)
    try:
        with os.fdopen(暫存描述符, "wb") as 檔案:
            檔案.write(內容位元)
            檔案.flush()
            os.fsync(檔案.fileno())
        os.link(驗證暫存, 正式路徑)
        候選路徑.unlink()
    except FileExistsError:
        return ["正式 completion-report.html 已存在；原子發布已停止，沒有覆寫"]
    except OSError as 錯誤:
        try:
            正式路徑.unlink(missing_ok=True)
        except OSError:
            pass
        return [f"原子發布失敗：{錯誤}"]
    finally:
        try:
            驗證暫存.unlink(missing_ok=True)
        except OSError:
            pass

    if not 正式結案報告有效(正式路徑, 實際工作目錄):
        try:
            正式路徑.unlink(missing_ok=True)
        except OSError:
            pass
        return ["發布後複驗失敗；已移除未通過的正式報告"]
    return []


def 建立一般測試文件(
    呼叫者: str,
    工作識別碼: str | None = None,
    章節內容: dict[str, str] | None = None,
) -> str:
    規格 = 報告規格[呼叫者]
    章節內容 = 章節內容 or {}
    章節 = "".join(
        f'<section id="{名稱}"><h2>繁體中文章節</h2><p>{html.escape(章節內容.get(名稱, "這是足夠長度且可驗證的繁體中文內容。"))}</p></section>'
        for 名稱 in sorted(規格["sections"])
    )
    模板路徑 = Path(__file__).resolve().parent.parent / "assets" / str(規格["template"])
    樣式 = 取得模板固定區塊(呼叫者, "style")
    樣式HTML = f"<style>{樣式[0]}</style>" if 樣式 else ""
    工作屬性 = f' data-work-id="{工作識別碼}"' if 工作識別碼 else ""
    return (
        f'<!doctype html><html lang="zh-Hant" data-report-profile="{呼叫者}" '
        f'data-report-status="{規格["status"]}"{工作屬性}><head><meta charset="utf-8">'
        f'<title>繁體中文測試報告</title>{樣式HTML}</head><body><div id="design-assist">內建模板</div>'
        f'<main>{章節}</main></body></html>'
    )


def 建立結案測試文件(
    呼叫者: str,
    工作識別碼: str,
    需求對照: dict[str, str] | None = None,
) -> str:
    模板 = (Path(__file__).resolve().parent.parent / "assets" / "completion.html").read_text(encoding="utf-8")
    if 需求對照 is None:
        需求對照 = {"R-001": "使用者要求實際功能。"}
    原有功能 = "原有功能修改前後驗收通過。" if 呼叫者 == "brownfield-implement" else "不適用。"
    確認項目 = "".join(
        f'<div class="確認項目"><input id="{識別碼}" type="checkbox" data-requirement-id="{識別碼}">'
        f'<label for="{識別碼}">{識別碼}：{html.escape(原文)}</label></div>'
        for 識別碼, 原文 in 需求對照.items()
    )
    替換 = {
        "{{呼叫者識別}}": 呼叫者,
        "{{工作識別碼}}": 工作識別碼,
        "{{顯示名稱}}": "繁體中文測試工作",
        "{{報告類型}}": "重構結案報告" if 呼叫者 == "brownfield-implement" else "功能結案報告",
        "{{最終結論}}": "全部驗收通過",
        "{{需求完成摘要}}": f"{len(需求對照)}／{len(需求對照)} 項完成",
        "{{Ticket完成摘要}}": "一／一張完成",
        "{{瀏覽器驗收摘要}}": "原生瀏覽器操作通過",
        "{{結論內容}}": html.escape("所有核准內容均已完成並保存可重現證據。"),
        "{{原始需求標題}}": "原始重構目標" if 呼叫者 == "brownfield-implement" else "原始需求",
        "{{原始需求內容}}": html.escape("核准的原始需求已逐項完成並保存證據。"),
        "{{Ticket成果內容}}": html.escape("全部 Ticket 與 Review 已完成。"),
        "{{實際驗收內容}}": html.escape(f"原生瀏覽器操作與最終總驗收通過。{原有功能}"),
        "{{詳細證據}}": html.escape("退出碼 0，原生瀏覽器畫面操作通過。"),
        "{{風險與回復內容}}": html.escape("沒有已知未解風險，回復步驟已有記錄。"),
        "{{使用者確認項目}}": 確認項目,
        "{{設計輔助}}": "內建模板",
    }
    for 欄位, 值 in 替換.items():
        模板 = 模板.replace(欄位, 值)
    return 模板


def 建立測試工作(根目錄: Path, 呼叫者: str, reviewer_mode: str = "both", legacy: bool = False) -> tuple[Path, Path]:
    測試尾碼 = "b1c2d3e4" if 呼叫者 == "brownfield-implement" else "a1b2c3d4"
    工作識別碼 = "legacy-feature" if legacy else f"wp-20260809-120000-{測試尾碼}"
    工作目錄 = 根目錄 / 呼叫者 / "docs" / "work" / 工作識別碼
    Ticket目錄 = 工作目錄 / "tickets"
    Ticket目錄.mkdir(parents=True)
    if legacy:
        Spec需求 = "- 舊版沒有需求識別碼的原始需求。"
        Ticket需求 = "- R-LEGACY-001：舊版沒有需求識別碼的原始需求。"
        報告需求 = {"R-LEGACY-001": "舊版沒有需求識別碼的原始需求。"}
    else:
        Spec需求 = "- R-001：使用者要求實際功能。\n- R-002：使用者要求第二項功能。"
        Ticket需求 = "- R-001：使用者要求實際功能。\n- R-002：使用者要求第二項功能。"
        報告需求 = {"R-001": "使用者要求實際功能。", "R-002": "使用者要求第二項功能。"}
    (工作目錄 / "spec.md").write_text(
        f"# 測試規格\n\n- 工作識別碼：{工作識別碼}\n- 顯示名稱：繁體中文測試工作\n- 狀態：已核准\n\n## 原始需求\n\n{Spec需求}\n",
        encoding="utf-8",
    )
    預期A = "不適用" if reviewer_mode == "b_only" else "通過"
    預期B = "不適用" if reviewer_mode == "a_only" else "通過"
    Ticket內容 = (
        "# 測試 Ticket\n\n- 狀態：完成\n\n## 對應原始需求\n\n"
        f"{Ticket需求}\n\n## 前端實際操作驗收\n\n"
        "- 適用性：適用\n- 判定依據：這是使用者介面需求。\n"
        "- 操作環境與實際網址：http://127.0.0.1:4567\n"
        "- 使用的原生瀏覽器工具：Codex Browser\n"
        "- 操作步驟與預期結果：實際點擊並觀察畫面。\n"
        "- 操作結果：通過\n- 操作證據：按鈕與結果畫面皆符合需求，截圖已保存。\n\n"
        "## 執行與 Review 紀錄\n\n- Developer 結論：通過\n"
        f"- Reviewer 模式：{reviewer_mode}\n- Reviewer A 結論：{預期A}\n- Reviewer B 結論：{預期B}\n"
        "- 未關閉阻擋或重要 Findings：0\n- Ticket 最終驗收：通過\n"
    )
    if 呼叫者 == "brownfield-implement":
        Ticket內容 += (
            "\n## 原有功能確認\n\n- 共用驗證方法：執行相同的回歸測試與使用者操作。\n"
            "- 修改前基準：回歸測試與使用者操作全部通過。\n"
            "- 修改後結果：以相同方法驗證，結果與修改前一致。\n"
            "- 原有功能驗收：通過\n- 驗收證據：修改前後輸出與畫面證據均已保存。\n"
        )
    (Ticket目錄 / "01-test.md").write_text(Ticket內容, encoding="utf-8")
    候選 = 工作目錄 / "completion-report.pending.html"
    候選.write_text(建立結案測試文件(呼叫者, 工作識別碼, 報告需求), encoding="utf-8")
    return 工作目錄, 候選


def 建立完整Grill測試Ticket() -> str:
    return """# 建立可驗證功能

- 狀態：草稿
- Spec：`../spec.md`
- Blocked by：無

## 目標

建立兩項可由使用者觀察並驗證的功能。

## 對應原始需求

- R-001：使用者要求實際功能。
- R-002：使用者要求第二項功能。

## 使用者價值

使用者可以直接完成需求並確認畫面結果。

## 範圍

只修改功能模組與對應測試，不改公開資料格式。

## 已確認實作決策

沿用既有模組邊界與公開介面。

## 驗收條件

- 兩項操作均顯示正確結果，且既有測試維持通過。

## 測試與證據

- 測試接縫：`tests/test_feature.py`
- 迭代期快速檢查：`pytest tests/test_feature.py -q`
- Ready for Review 完整驗收：`pytest -q`
- Findings 修正後：依受影響案例重跑對應 pytest 節點。
- 必交證據：完整驗收退出碼、輸出與畫面操作紀錄。
- 保存位置：本 Ticket 的「執行與 Review 紀錄」。

## 前端實際操作驗收

- 適用性：適用
- 判定依據：兩項需求都必須由使用者在畫面實際操作。
- 操作環境與實際網址：執行階段填寫
- 使用的原生瀏覽器工具：執行階段填寫
- 操作步驟與預期結果：依序開啟頁面、點擊兩項功能並確認各自顯示成功結果。
- 操作結果：執行階段填寫
- 操作證據：執行階段填寫

## 依賴

- Depends on：無
- Blocks：無

## 並行與所有權

- Dispatch：serialized
- Exclusive write scope：`src/feature.py`、`tests/test_feature.py`
- Shared resource locks：無
- Can run with：無

## 初始執行配置

- Developer model：`claude-opus-5`（相容預設偏好）
- model_reasoning_effort：`high`（相容預設偏好）
- 路由理由：包含前端與測試的跨檔案垂直切片。
- 升級路徑：Claude 使用 `claude-opus-5`／`xhigh`；其他後端使用已驗證可用的升級設定。
- 執行時覆寫：最新使用者角色設定優先；後端不可用時回退並留下紀錄。
- Research 證據：無

## Agent 分工

- Developer：負責實作、驗證與處理 Findings。
- Reviewer A：both 時執行 Spec Review；a_only 時執行兩軸。
- Reviewer B：both 時執行 Standards Review；b_only 時執行兩軸。
- Reviewer 啟用規則：依執行 Task 最新 reviewer 設定，預設 both。
- Reviewer 標準：載入 code review 技能並只執行指定 review axis。
- CLI 與模型：依最新角色設定與可用後端決定並保存實際證據。

## 完成規則

- 所有可重現 Findings 均已處理，驗收通過且沒有未解阻擋。

## 執行與 Review 紀錄

- Developer 結論：執行階段填寫
- Reviewer 模式：執行階段填寫
- Reviewer A 結論：執行階段填寫
- Reviewer B 結論：執行階段填寫
- 未關閉阻擋或重要 Findings：執行階段填寫
- Ticket 最終驗收：執行階段填寫

## 阻擋與裁決紀錄
"""


def 建立Grill測試工作(
    根目錄: Path,
    工作識別碼: str = "wp-20260809-120000-c1d2e3f4",
    Spec狀態: str = "已核准",
    Ticket內容: str | None = None,
    HTML工作識別碼: str | None = None,
    Spec需求: str = "- R-001：使用者要求實際功能。\n- R-002：使用者要求第二項功能。",
    HTML需求內容: str | None = None,
) -> tuple[Path, Path]:
    Ticket內容 = Ticket內容 or 建立完整Grill測試Ticket()
    HTML需求內容 = HTML需求內容 or "R-001：使用者要求實際功能。 R-002：使用者要求第二項功能。"
    專案根目錄 = 根目錄 / "project"
    工作目錄 = 專案根目錄 / "docs" / "work" / 工作識別碼
    (工作目錄 / "tickets").mkdir(parents=True)
    (工作目錄 / "spec.md").write_text(
        f"# 規格\n\n- 工作識別碼：{工作識別碼}\n- 狀態：{Spec狀態}\n\n## 原始需求\n\n{Spec需求}\n",
        encoding="utf-8",
    )
    (工作目錄 / "tickets" / "01-draft.md").write_text(Ticket內容, encoding="utf-8")
    報告路徑 = 工作目錄 / "implementation-plan.html"
    報告路徑.write_text(
        建立一般測試文件(
            "grill-me",
            HTML工作識別碼 or 工作識別碼,
            {"原始需求與範圍": HTML需求內容},
        ),
        encoding="utf-8",
    )
    return 專案根目錄, 報告路徑


def 執行自我測試() -> int:
    with tempfile.TemporaryDirectory() as 暫存目錄:
        根目錄 = Path(暫存目錄)
        for 呼叫者 in {"brownfield-planner", "grill-me"}:
            if 呼叫者 == "brownfield-planner":
                工作識別碼 = "wp-20260809-120000-a1b2c3d4"
                專案根目錄 = 根目錄 / "planner-project"
                路徑 = 專案根目錄 / "docs" / "architecture-reviews" / 工作識別碼 / "architecture-review.html"
                路徑.parent.mkdir(parents=True)
                路徑.write_text(建立一般測試文件(呼叫者, 工作識別碼), encoding="utf-8")
                問題 = 驗證檔案(路徑, 呼叫者, 專案根目錄=專案根目錄, 工作識別碼=工作識別碼)
            else:
                工作識別碼 = "wp-20260809-120000-c1d2e3f4"
                專案根目錄, 路徑 = 建立Grill測試工作(根目錄 / "grill-project", 工作識別碼)
                問題 = 驗證檔案(
                    路徑,
                    呼叫者,
                    專案根目錄=專案根目錄,
                    工作識別碼=工作識別碼,
                )
            if 問題:
                print(f"自我測試失敗（{呼叫者}）：{'；'.join(問題)}")
                return 1

        Planner工作識別碼 = "wp-20260809-120000-a1b2c3d4"
        Planner專案 = 根目錄 / "planner-negative"
        Planner專案.mkdir()
        錯誤路徑 = Planner專案 / "wrong.html"
        錯誤路徑.write_text(建立一般測試文件("brownfield-planner", Planner工作識別碼), encoding="utf-8")
        if not any(
            "報告路徑必須" in 項目
            for 項目 in 驗證檔案(
                錯誤路徑,
                "brownfield-planner",
                專案根目錄=Planner專案,
                工作識別碼=Planner工作識別碼,
            )
        ):
            print("自我測試失敗：沒有攔截 Brownfield Planner 錯誤報告路徑。")
            return 1
        正確Planner路徑 = Planner專案 / "docs" / "architecture-reviews" / Planner工作識別碼 / "architecture-review.html"
        正確Planner路徑.parent.mkdir(parents=True)
        正確Planner路徑.write_text(建立一般測試文件("brownfield-planner", "wp-20260809-120000-deadbeef"), encoding="utf-8")
        if not any(
            "data-work-id" in 項目
            for 項目 in 驗證檔案(
                正確Planner路徑,
                "brownfield-planner",
                專案根目錄=Planner專案,
                工作識別碼=Planner工作識別碼,
            )
        ):
            print("自我測試失敗：沒有攔截 Brownfield Planner 工作識別碼不一致。")
            return 1

        LegacyGrillID = "legacy-feature"
        LegacyGrill專案, LegacyGrill報告 = 建立Grill測試工作(
            根目錄 / "grill-legacy", 工作識別碼=LegacyGrillID
        )
        if 驗證檔案(
            LegacyGrill報告,
            "grill-me",
            專案根目錄=LegacyGrill專案,
            工作識別碼=LegacyGrillID,
        ):
            print("自我測試失敗：Grill-me 沒有相容舊工作實際路徑。")
            return 1

        完整GrillTicket = 建立完整Grill測試Ticket()
        Grill反例 = [
            ("Spec未核准", {"Spec狀態": "草稿"}, "Spec 狀態必須"),
            ("Spec重複狀態", {"Spec狀態": "已核准\n- 狀態：草稿"}, "恰好出現一次"),
            ("Ticket非草稿", {"Ticket內容": 完整GrillTicket.replace("- 狀態：草稿", "- 狀態：已核准")}, "必須精確為草稿"),
            ("Ticket重複狀態", {"Ticket內容": 完整GrillTicket.replace("- 狀態：草稿", "- 狀態：草稿\n- 狀態：完成")}, "恰好出現一次"),
            ("HTML識別錯誤", {"HTML工作識別碼": "wp-20260809-120000-deadbeef"}, "data-work-id"),
            ("新識別格式錯誤", {"工作識別碼": "wp-bad"}, "新工作識別碼"),
            ("空Ticket", {"Ticket內容": "# 空 Ticket\n\n- 狀態：草稿\n"}, "缺少必要章節"),
            ("Spec缺少R", {"Spec需求": "使用者要求未編號的功能。"}, "缺少唯一 R-xxx"),
            ("Spec重複R", {"Spec需求": "- R-001：使用者要求實際功能。\n- R-001：重複需求。"}, "R-ID 重複"),
            ("Ticket需求不符", {"Ticket內容": 完整GrillTicket.replace("R-002：使用者要求第二項功能。", "R-002：被改寫的需求。")}, "原文與 Spec 不一致"),
            ("Ticket未覆蓋", {"Ticket內容": 完整GrillTicket.replace("- R-002：使用者要求第二項功能。\n", "")}, "沒有任何 Ticket 覆蓋"),
            ("HTML未顯示R", {"HTML需求內容": "R-001：使用者要求實際功能。"}, "未逐字顯示 Spec 需求"),
            ("HTML需求錯配", {"HTML需求內容": "R-001：使用者要求第二項功能。 R-002：使用者要求實際功能。"}, "未逐字顯示 Spec 需求"),
            ("規劃欄位占位", {"Ticket內容": 完整GrillTicket.replace("- Dispatch：serialized", "- Dispatch：parallel-safe／serialized")}, "Dispatch 必須精確"),
        ]
        for 名稱, 參數, 關鍵字 in Grill反例:
            Grill專案, Grill報告 = 建立Grill測試工作(根目錄 / f"grill-{名稱}", **參數)
            GrillID = str(參數.get("工作識別碼", "wp-20260809-120000-c1d2e3f4"))
            結果 = 驗證檔案(
                Grill報告,
                "grill-me",
                專案根目錄=Grill專案,
                工作識別碼=GrillID,
            )
            if not any(關鍵字 in 項目 for 項目 in 結果):
                print(f"自我測試失敗：沒有攔截 Grill-me 反例：{名稱}")
                return 1

        Grill路徑專案, Grill正確報告 = 建立Grill測試工作(根目錄 / "grill-wrong-path")
        Grill錯誤報告 = Grill正確報告.with_name("wrong.html")
        Grill正確報告.rename(Grill錯誤報告)
        if not any(
            "報告路徑必須" in 項目
            for 項目 in 驗證檔案(
                Grill錯誤報告,
                "grill-me",
                專案根目錄=Grill路徑專案,
                工作識別碼="wp-20260809-120000-c1d2e3f4",
            )
        ):
            print("自我測試失敗：沒有攔截 Grill-me 錯誤報告路徑。")
            return 1

        for 呼叫者 in 結案呼叫者:
            for reviewer_mode in 合法Reviewer模式:
                工作目錄, 候選 = 建立測試工作(根目錄 / reviewer_mode, 呼叫者, reviewer_mode)
                問題 = 驗證檔案(候選, 呼叫者, 工作目錄, 候選模式=True)
                if 問題:
                    print(f"自我測試失敗（{呼叫者}/{reviewer_mode}）：{'；'.join(問題)}")
                    return 1

        不適用工作, 不適用候選 = 建立測試工作(根目錄 / "frontend-not-applicable", "implement")
        不適用Ticket = 不適用工作 / "tickets" / "01-test.md"
        不適用內容 = 不適用Ticket.read_text(encoding="utf-8")
        不適用內容 = 不適用內容.replace("- 適用性：適用", "- 適用性：不適用")
        不適用內容 = 不適用內容.replace("- 判定依據：這是使用者介面需求。", "- 判定依據：此 Ticket 沒有使用者介面。")
        不適用內容 = 不適用內容.replace("- 操作環境與實際網址：http://127.0.0.1:4567", "- 操作環境與實際網址：不適用")
        不適用內容 = 不適用內容.replace("- 使用的原生瀏覽器工具：Codex Browser", "- 使用的原生瀏覽器工具：不適用")
        不適用內容 = 不適用內容.replace("- 操作步驟與預期結果：實際點擊並觀察畫面。", "- 操作步驟與預期結果：不適用")
        不適用內容 = 不適用內容.replace("- 操作結果：通過", "- 操作結果：不適用")
        不適用內容 = 不適用內容.replace("- 操作證據：按鈕與結果畫面皆符合需求，截圖已保存。", "- 操作證據：不適用")
        不適用Ticket.write_text(不適用內容, encoding="utf-8")
        不適用問題 = 驗證檔案(不適用候選, "implement", 不適用工作, 候選模式=True)
        if 不適用問題:
            print(f"自我測試失敗（前端不適用精確欄位）：{'；'.join(不適用問題)}")
            return 1

        舊工作, 舊候選 = 建立測試工作(根目錄 / "legacy", "implement", legacy=True)
        if 驗證檔案(舊候選, "implement", 舊工作, 候選模式=True):
            print("自我測試失敗：明確 R-LEGACY 對照的舊工作應可通過。")
            return 1

        錯誤工作目錄, _ = 建立測試工作(根目錄 / "wrong-work-path", "implement")
        錯誤父目錄 = 根目錄 / "wrong-work-path" / "not-docs-work"
        錯誤父目錄.mkdir(parents=True)
        搬移後工作目錄 = 錯誤父目錄 / 錯誤工作目錄.name
        錯誤工作目錄.rename(搬移後工作目錄)
        搬移後候選 = 搬移後工作目錄 / "completion-report.pending.html"
        if not any(
            "docs/work" in 項目
            for 項目 in 驗證檔案(搬移後候選, "implement", 搬移後工作目錄, 候選模式=True)
        ):
            print("自我測試失敗：沒有攔截新工作放在 docs/work 以外的位置。")
            return 1

        def 反例(
            名稱: str,
            修改Ticket=None,
            修改報告=None,
            呼叫者: str = "implement",
            關鍵字: str = "",
            修改Spec=None,
        ) -> bool:
            安全名稱 = re.sub(r'[<>:"/\\|?*]', "_", 名稱)
            工作, 候選路徑 = 建立測試工作(根目錄 / f"negative-{安全名稱}", 呼叫者)
            Ticket = 工作 / "tickets" / "01-test.md"
            Spec = 工作 / "spec.md"
            if 修改Ticket:
                Ticket.write_text(修改Ticket(Ticket.read_text(encoding="utf-8")), encoding="utf-8")
            if 修改報告:
                候選路徑.write_text(修改報告(候選路徑.read_text(encoding="utf-8")), encoding="utf-8")
            if 修改Spec:
                Spec.write_text(修改Spec(Spec.read_text(encoding="utf-8")), encoding="utf-8")
            結果 = 驗證檔案(候選路徑, 呼叫者, 工作, 候選模式=True)
            return bool(結果) and (not 關鍵字 or any(關鍵字 in 項目 for 項目 in 結果))

        反例組 = [
            ("未通過", lambda s: s.replace("- 操作結果：通過", "- 操作結果：未通過"), None, "implement", "精確為通過"),
            ("curl", lambda s: s.replace("Codex Browser", "curl"), None, "implement", "原生瀏覽器工具"),
            ("假網址", lambda s: s.replace("http://127.0.0.1:4567", "尚待執行"), None, "implement", "真實"),
            ("無reviewer", lambda s: s.replace("- Reviewer A 結論：通過\n", ""), None, "implement", "Reviewer A"),
            ("ID不符", None, lambda s: s.replace('data-work-id="wp-', 'data-work-id="wrong-'), "implement", "工作識別碼不一致"),
            ("Brownfield未驗證", lambda s: s.replace("- 原有功能驗收：通過", "- 原有功能驗收：尚未驗證"), None, "brownfield-implement", "原有功能驗收"),
            ("缺R", None, lambda s: s.replace('data-requirement-id="R-002"', 'data-requirement-id="R-999"'), "implement", "遺漏"),
            ("重複R", None, lambda s: s.replace('data-requirement-id="R-002"', 'data-requirement-id="R-001"'), "implement", "恰好出現一次"),
            ("Ticket缺需求覆蓋", lambda s: s.replace("- R-002：使用者要求第二項功能。\n", ""), None, "implement", "沒有任何 Ticket 負責"),
            ("Ticket非法需求", lambda s: s.replace("- R-002：使用者要求第二項功能。", "- R-999：使用者要求第二項功能。"), None, "implement", "Spec 不存在"),
            ("Ticket需求原文不符", lambda s: s.replace("- R-002：使用者要求第二項功能。", "- R-002：被改寫的需求。"), None, "implement", "原文與 Spec 不一致"),
            ("危險script", None, lambda s: s.replace("所有核准內容均已完成", "</pre><script>alert(1)</script><pre>所有核准內容均已完成"), "implement", "script"),
            ("危險iframe", None, lambda s: s.replace("所有核准內容均已完成", '<iframe src="https://example.com"></iframe>所有核准內容均已完成'), "implement", "iframe"),
            ("危險事件", None, lambda s: s.replace("<main>", '<main onmouseover="alert(1)">'), "implement", "事件屬性"),
            ("危險CSS", None, lambda s: s.replace("<style>", '<style>@import url("https://example.com/x.css");'), "implement", "CSS"),
            ("script-src", None, lambda s: s.replace("<script>", '<script src="https://example.com/x.js">'), "implement", "script 不得有任何屬性"),
            ("label原文錯誤", None, lambda s: s.replace("R-001：使用者要求實際功能。", "R-001：被改寫的顯示文字。", 1), "implement", "exact R-ID"),
            ("label缺失", None, lambda s: s.replace('<label for="R-001">R-001：使用者要求實際功能。</label>', ""), "implement", "對應 label"),
            ("label重複", None, lambda s: s.replace('<label for="R-001">R-001：使用者要求實際功能。</label>', '<label for="R-001">R-001：使用者要求實際功能。</label><label for="R-001">R-001：使用者要求實際功能。</label>'), "implement", "對應 label"),
            ("label錯誤for", None, lambda s: s.replace('label for="R-001"', 'label for="R-999"'), "implement", "對應 label"),
            ("input-id不符", None, lambda s: s.replace('input id="R-001"', 'input id="wrong"'), "implement", "id 必須"),
        ]
        for 名稱, 修改Ticket, 修改報告, 呼叫者, 關鍵字 in 反例組:
            if not 反例(名稱, 修改Ticket, 修改報告, 呼叫者, 關鍵字):
                print(f"自我測試失敗：沒有攔截反例：{名稱}")
                return 1

        def 重複機器欄位(內容: str, 名稱: str, 替代值: str | None = None) -> str:
            模式 = re.compile(rf"^-\s*{re.escape(名稱)}[：:]\s*.*$", re.MULTILINE)
            return 模式.sub(
                lambda 結果: f"{結果.group(0)}\n- {名稱}：{替代值 if 替代值 is not None else 結果.group(0).split('：', 1)[-1]}",
                內容,
                count=1,
            )

        Ticket唯一欄位 = [
            "狀態", "適用性", "判定依據", "操作環境與實際網址", "使用的原生瀏覽器工具",
            "操作步驟與預期結果", "操作結果", "操作證據",
            "Developer 結論", "Reviewer 模式", "Reviewer A 結論", "Reviewer B 結論",
            "未關閉阻擋或重要 Findings", "Ticket 最終驗收",
        ]
        for 欄位 in Ticket唯一欄位:
            if not 反例(
                f"重複欄位-{欄位}",
                修改Ticket=lambda s, 欄位=欄位: 重複機器欄位(s, 欄位),
                關鍵字="全文件必須恰好出現一次",
            ):
                print(f"自我測試失敗：沒有攔截重複 Ticket 機器欄位：{欄位}")
                return 1

        for 欄位 in ["共用驗證方法", "修改前基準", "修改後結果", "原有功能驗收", "驗收證據"]:
            if not 反例(
                f"Brownfield重複欄位-{欄位}",
                修改Ticket=lambda s, 欄位=欄位: 重複機器欄位(s, 欄位),
                呼叫者="brownfield-implement",
                關鍵字="全文件必須恰好出現一次",
            ):
                print(f"自我測試失敗：沒有攔截重複 Brownfield 機器欄位：{欄位}")
                return 1

        for 欄位 in ["工作識別碼", "狀態"]:
            if not 反例(
                f"Spec重複欄位-{欄位}",
                修改Spec=lambda s, 欄位=欄位: 重複機器欄位(s, 欄位),
                關鍵字="全文件必須恰好出現一次",
            ):
                print(f"自我測試失敗：沒有攔截重複 Spec 機器欄位：{欄位}")
                return 1

        其他欄位反例 = [
            ("Spec未核准結案", None, lambda s: s.replace("- 狀態：已核准", "- 狀態：草稿"), "Spec 狀態必須精確為已核准"),
            ("Reviewer模式矛盾", lambda s: 重複機器欄位(s, "Reviewer 模式", "a_only"), None, "全文件必須恰好出現一次"),
            ("判定依據占位", lambda s: s.replace("- 判定依據：這是使用者介面需求。", "- 判定依據：執行階段填寫"), None, "判定依據"),
            ("操作步驟缺失", lambda s: s.replace("- 操作步驟與預期結果：實際點擊並觀察畫面。\n", ""), None, "操作步驟與預期結果"),
            ("操作步驟占位", lambda s: s.replace("- 操作步驟與預期結果：實際點擊並觀察畫面。", "- 操作步驟與預期結果：執行階段填寫"), None, "缺少可執行的前端操作步驟"),
            ("操作結果占位", lambda s: s.replace("- 操作結果：通過", "- 操作結果：執行階段填寫"), None, "精確為通過"),
            ("Developer占位", lambda s: s.replace("- Developer 結論：通過", "- Developer 結論：執行階段填寫"), None, "Developer 結論"),
        ]
        for 名稱, 修改Ticket, 修改Spec, 關鍵字 in 其他欄位反例:
            if not 反例(名稱, 修改Ticket=修改Ticket, 修改Spec=修改Spec, 關鍵字=關鍵字):
                print(f"自我測試失敗：沒有攔截欄位反例：{名稱}")
                return 1

        for 屬性 in ["hidden", "disabled", "checked", 'aria-hidden="true"', "inert"]:
            if not 反例(
                f"清單禁用-{屬性}",
                修改報告=lambda s, 屬性=屬性: s.replace('<input id="R-001"', f'<input {屬性} id="R-001"'),
                關鍵字="allowlist",
            ):
                print(f"自我測試失敗：沒有攔截清單禁用屬性：{屬性}")
                return 1

        if not 反例(
            "巢狀清單隱藏",
            修改報告=lambda s: s.replace(
                '<div class="確認清單">',
                '<div class="確認清單"><section id="巢狀區"><div hidden></div></section>',
            ),
            關鍵字="allowlist",
        ):
            print("自我測試失敗：沒有攔截巢狀區段內的清單隱藏屬性。")
            return 1

        if not 反例(
            "祖先節點隱藏清單",
            修改報告=lambda s: s.replace(
                '<section id="使用者確認" data-user-checklist>',
                '<div hidden><section id="使用者確認" data-user-checklist>',
            ).replace(
                '    </section>\n\n    <div id="design-assist">',
                '    </section></div>\n\n    <div id="design-assist">',
                1,
            ),
            關鍵字="allowlist",
        ):
            print("自我測試失敗：沒有攔截以 hidden 祖先節點隱藏整份確認清單。")
            return 1

        Completion結構反例 = [
            (
                "重複html根",
                lambda s: s.replace(
                    "<!doctype html>",
                    '<!doctype html><html lang="en" data-report-profile="evil" data-report-status="in-progress" data-work-id="evil">',
                    1,
                ),
                "根 start tag 必須恰好出現一次",
            ),
            (
                "重複lang屬性",
                lambda s: s.replace('lang="zh-Hant"', 'lang="en" lang="zh-Hant"', 1),
                "不得重複屬性名稱",
            ),
            (
                "外部重複需求ID",
                lambda s: s.replace("<main>", '<input id="R-001" type="text"><main>', 1),
                "全文件 id 必須唯一",
            ),
            (
                "inert祖先",
                lambda s: s.replace(
                    '<section id="使用者確認" data-user-checklist>',
                    '<div inert><section id="使用者確認" data-user-checklist>',
                    1,
                ).replace(
                    '    </section>\n\n    <div id="design-assist">',
                    '    </section></div>\n\n    <div id="design-assist">',
                    1,
                ),
                "allowlist",
            ),
            (
                "closed-details祖先",
                lambda s: s.replace(
                    '<section id="使用者確認" data-user-checklist>',
                    '<details><summary>確認清單</summary><section id="使用者確認" data-user-checklist>',
                    1,
                ).replace(
                    '    </section>\n\n    <div id="design-assist">',
                    '    </section></details>\n\n    <div id="design-assist">',
                    1,
                ),
                "allowlist",
            ),
            (
                "URL控制字元",
                lambda s: s.replace("<main>", '<a href="java&#x0A;script:alert(1)">連結</a><main>', 1),
                "可執行 URL",
            ),
        ]
        for 名稱, 修改報告, 關鍵字 in Completion結構反例:
            if not 反例(名稱, 修改報告=修改報告, 關鍵字=關鍵字):
                print(f"自我測試失敗：沒有攔截 completion 結構反例：{名稱}")
                return 1

        CSS反例 = [
            ".確認清單{display:none}",
            "[data-user-checklist]{visibility:hidden}",
            ".確認項目{pointer-events:none}",
            "input{opacity:0}",
        ]
        for CSS in CSS反例:
            if not 反例(
                f"清單CSS-{CSS}",
                修改報告=lambda s, CSS=CSS: s.replace("<style>", f"<style>{CSS}"),
                關鍵字="不得隱藏使用者確認清單",
            ):
                print(f"自我測試失敗：沒有攔截清單隱藏 CSS：{CSS}")
                return 1

        if not 反例(
            "需求ID隱藏CSS",
            修改報告=lambda s: s.replace("<style>", "<style>#R-001{opacity:0}"),
            關鍵字="固定模板完全一致",
        ):
            print("自我測試失敗：沒有攔截以需求 ID selector 隱藏單一 checkbox 的 CSS。")
            return 1

        for 不可靠文字 in ["無法確認", "假設通過", "推測通過", "不確定", "未驗證"]:
            if not 反例(
                f"Brownfield不可靠證據-{不可靠文字}",
                修改Ticket=lambda s, 不可靠文字=不可靠文字: re.sub(
                    r"^- 驗收證據：.*$", f"- 驗收證據：{不可靠文字}", s, count=1, flags=re.MULTILINE
                ),
                呼叫者="brownfield-implement",
                關鍵字="原有功能證據",
            ):
                print(f"自我測試失敗：沒有攔截 Brownfield 不可靠證據：{不可靠文字}")
                return 1

        for 欄位 in ["共用驗證方法", "修改前基準", "修改後結果", "驗收證據"]:
            if not 反例(
                f"Brownfield占位-{欄位}",
                修改Ticket=lambda s, 欄位=欄位: re.sub(
                    rf"^- {re.escape(欄位)}：.*$", f"- {欄位}：執行階段填寫", s, count=1, flags=re.MULTILINE
                ),
                呼叫者="brownfield-implement",
                關鍵字=欄位 if 欄位 != "驗收證據" else "原有功能證據",
            ):
                print(f"自我測試失敗：沒有攔截 Brownfield 占位欄位：{欄位}")
                return 1

        工作目錄, 候選 = 建立測試工作(根目錄 / "publish", "implement")
        發布問題 = 發布候選報告(候選, "implement", 工作目錄)
        正式 = 工作目錄 / "completion-report.html"
        if 發布問題 or 候選.exists() or not 正式結案報告有效(正式, 工作目錄):
            print(f"自我測試失敗：候選報告沒有原子發布：{'；'.join(發布問題)}")
            return 1
        原內容 = 正式.read_bytes()
        候選.write_text(
            建立結案測試文件(
                "implement",
                工作目錄.name,
                {"R-001": "使用者要求實際功能。", "R-002": "使用者要求第二項功能。"},
            ),
            encoding="utf-8",
        )
        if not 發布候選報告(候選, "implement", 工作目錄) or 正式.read_bytes() != 原內容:
            print("自我測試失敗：原子發布覆寫了既有正式報告。")
            return 1

    print("自我測試通過：候選發布、工作識別、需求清單、Reviewer、瀏覽器、Brownfield 與 HTML 安全反例皆符合預期。")
    return 0


def 建立參數解析器() -> argparse.ArgumentParser:
    解析器 = argparse.ArgumentParser(description="驗證 Milktea 繁體中文 HTML 報告並發布結案候選檔。")
    解析器.add_argument("report", nargs="?", type=Path, help="要驗證的 HTML 報告路徑")
    解析器.add_argument("--caller", choices=sorted(報告規格), help="呼叫者固定識別")
    解析器.add_argument("--work-dir", type=Path, help="Implement 結案報告的實際工作目錄")
    解析器.add_argument("--project-root", type=Path, help="Brownfield Planner 或 Grill-me 的專案根目錄")
    解析器.add_argument("--work-id", help="Brownfield Planner 或 Grill-me 的唯一工作識別碼")
    解析器.add_argument("--candidate", action="store_true", help="驗證 completion-report.pending.html 候選檔")
    解析器.add_argument("--publish", action="store_true", help="嚴格驗證候選檔後原子發布 completion-report.html")
    解析器.add_argument("--self-test", action="store_true", help="執行驗證器自我測試")
    return 解析器


def main() -> int:
    參數 = 建立參數解析器().parse_args()
    if 參數.self_test:
        return 執行自我測試()
    if 參數.report is None or 參數.caller is None:
        print("錯誤：一般驗證必須同時提供 --caller 與報告路徑。", file=sys.stderr)
        return 2
    if 參數.publish and not 參數.candidate:
        print("錯誤：--publish 必須與 --candidate 一起使用。", file=sys.stderr)
        return 2
    if 參數.publish:
        if 參數.work_dir is None or 參數.caller not in 結案呼叫者:
            print("錯誤：發布結案候選檔必須使用 Implement 呼叫者並提供 --work-dir。", file=sys.stderr)
            return 2
        問題 = 發布候選報告(參數.report, 參數.caller, 參數.work_dir)
    else:
        問題 = 驗證檔案(
            參數.report,
            參數.caller,
            參數.work_dir,
            候選模式=參數.candidate,
            專案根目錄=參數.project_root,
            工作識別碼=參數.work_id,
        )
    if 問題:
        print(f"報告驗證失敗：{參數.report}")
        for 項目 in 問題:
            print(f"- {項目}")
        return 1
    if 參數.publish:
        print(f"結案報告已原子發布：{參數.work_dir.resolve() / 'completion-report.html'}")
    else:
        print(f"報告驗證通過：{參數.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
