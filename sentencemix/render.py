"""句子重排练习纸的 HTML 渲染。"""

from __future__ import annotations

import html
from typing import Sequence

from .model import Puzzle

STYLE = """
@page { size: A4 portrait; margin: 14mm 13mm; }
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
  color: #1b2430;
  font-size: 11pt;
  line-height: 1.55;
}
h1 { font-size: 20pt; margin: 0 0 2mm; }
.sub { color: #6b7280; font-size: 10pt; margin: 0 0 6mm; }
ol.items { margin: 0; padding-left: 7mm; }
li.item { margin-bottom: 7mm; page-break-inside: avoid; }
.chips { display: flex; flex-wrap: wrap; gap: 1.6mm; margin-bottom: 2.5mm; }
.chip {
  display: inline-block;
  padding: 0.7mm 2.4mm;
  border: 0.6pt solid #94a3b8;
  border-radius: 1.4mm;
  background: #f8fafc;
  font-size: 10.5pt;
}
.lines .line {
  border-bottom: 0.6pt solid #c7cdd4;
  height: 8mm;
}
.answers { page-break-before: always; }
.answers h2 { font-size: 15pt; margin: 0 0 4mm; }
.answers ol { padding-left: 8mm; }
.answers li { margin-bottom: 2.4mm; page-break-inside: avoid; }
.note { color: #6b7280; font-size: 9.5pt; }
@media print { li.item, .answers li { break-inside: avoid; } }
"""


def _escape(text: str) -> str:
    return html.escape(str(text), quote=True)


def render_worksheet(
    puzzles: Sequence[Puzzle],
    title: str = "句子重排练习",
    include_answers: bool = False,
    lines: int = 1,
) -> str:
    """生成重排练习纸；include_answers 为真时追加答案页。"""
    if isinstance(lines, bool) or not isinstance(lines, int) or lines < 1:
        raise ValueError("书写行数必须是正整数")
    safe_title = _escape(title)
    items = []
    for index, puzzle in enumerate(puzzles, start=1):
        chips = "".join('<span class="chip">%s</span>' % _escape(token) for token in puzzle.scrambled)
        write_lines = "".join('<div class="line"></div>' for _ in range(lines))
        items.append(
            '<li class="item">'
            '<div class="chips">%s</div>'
            '<div class="lines">%s</div>'
            "</li>" % (chips, write_lines)
        )
    body = "".join(items) or '<p class="note">暂无题目。</p>'
    parts = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % safe_title,
        "<style>%s</style>" % STYLE,
        "</head>",
        "<body>",
        "<h1>%s</h1>" % safe_title,
        '<p class="sub">姓名：__________　班级：__________　日期：__________</p>',
        "<p>把下面的词卡重新排列，组成一个通顺的句子，写在横线上。</p>",
        '<ol class="items">%s</ol>' % body,
    ]
    if include_answers:
        answers = "".join(
            "<li>%s</li>" % _escape(puzzle.answer) for puzzle in puzzles
        )
        parts.extend(
            [
                '<section class="answers">',
                "<h2>参考答案</h2>",
                "<ol>%s</ol>" % answers,
                "</section>",
            ]
        )
    parts.extend(["</body>", "</html>"])
    return "\n".join(parts)
