"""管理者向け確認表（Markdown）を PDF 化用の HTML に変換する。

使い方: python build-admin-html.py  → admin-verification-sheet.html を生成（build-pdf.js が読む）
依存: pip install markdown
"""
import re
from pathlib import Path
from urllib.parse import quote

import markdown

HERE = Path(__file__).parent
src = (HERE / "admin-verification-sheet.md").read_text(encoding="utf-8")
src = re.sub(r"^---\n.*?\n---\n", "", src, flags=re.S)  # frontmatter を除去
body = markdown.markdown(src, extensions=["tables"])


def repository_link(match):
    """Keep PDF links portable without embedding the author's local file path."""
    target = match.group(1)
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
        return match.group(0)
    relative_path, separator, fragment = target.partition("#")
    repository_path = (HERE / relative_path).resolve().relative_to(HERE.parents[1])
    url = "https://github.com/yukiworkspace/EleKnowledge-AI/blob/develop/"
    url += quote(repository_path.as_posix(), safe="/")
    if separator:
        url += "#" + quote(fragment, safe="-")
    return f'href="{url}"'


body = re.sub(r'href="([^"]+)"', repository_link, body)
css = """<style>
@page{size:A4 landscape;margin:14mm}
body{font-family:"BIZ UDPGothic","Yu Gothic UI","Yu Gothic","Meiryo",sans-serif;font-size:9.5pt;line-height:1.6;color:#1a1a1a;margin:0}
h1{font-size:16pt;border-left:6px solid #1d4ed8;padding:1mm 3mm;background:#eff6ff}
h2{font-size:12.5pt;border-bottom:2px solid #93c5fd;margin-top:6mm;break-after:avoid}
h3{font-size:11pt;color:#1e3a8a;margin-top:4mm;break-after:avoid}
table{border-collapse:collapse;width:100%;margin:2mm 0 4mm;font-size:8.8pt}
th,td{border:1px solid #cbd5e1;padding:1.2mm 2mm;vertical-align:top;text-align:left}
th{background:#eff6ff}
tr{break-inside:avoid}
code{font-family:Consolas,monospace;background:#f1f5f9;padding:0 1mm;font-size:8.5pt}
li{margin-bottom:0.8mm}
</style>"""
html = (
    '<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">'
    "<title>EleKnowledge 管理者向け確認表</title>" + css + "</head><body>" + body + "</body></html>"
)
(HERE / "admin-verification-sheet.html").write_text(html, encoding="utf-8")
print("wrote admin-verification-sheet.html")
