"""命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .model import (
    PuzzleError,
    build_puzzle,
    build_puzzles,
    builtin_sentences,
    format_scrambled,
    load_sentences,
    split_sentences,
)
from .render import render_worksheet


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sentencemix",
        description="句子重排练习纸：打乱词序，生成可打印 A4 题目与答案",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    sheet_parser = subparsers.add_parser("sheet", help="生成练习纸 HTML")
    source = sheet_parser.add_mutually_exclusive_group()
    source.add_argument("-i", "--input", default=None, help="句子文本文件，一行一句")
    source.add_argument("--text", default=None, help="直接给出一段句子文本")
    sheet_parser.add_argument("--count", type=int, default=None, help="题目数量，默认使用全部句子")
    sheet_parser.add_argument("--seed", type=int, default=None, help="随机种子")
    sheet_parser.add_argument("--title", default="句子重排练习", help="练习纸标题")
    sheet_parser.add_argument("--lines", type=int, default=1, help="每题书写行数，默认 1")
    sheet_parser.add_argument("--answers", action="store_true", help="追加答案页")
    sheet_parser.add_argument("-o", "--output", default=None, help="输出文件")

    mix_parser = subparsers.add_parser("mix", help="在终端查看打乱结果")
    mix_parser.add_argument("sentence", help="要打乱的句子")
    mix_parser.add_argument("--seed", type=int, default=None, help="随机种子")
    return parser


def _write_output(html_text: str, output: Optional[str]) -> None:
    if not output:
        print(html_text)
        return
    path = Path(output)
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_text, encoding="utf-8")
    print("已写入 %s" % path)


def _collect_sentences(args: argparse.Namespace) -> List[str]:
    if args.text is not None:
        return split_sentences(args.text)
    if args.input is not None:
        return load_sentences(args.input)
    return builtin_sentences()


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "mix":
            puzzle = build_puzzle(args.sentence, args.seed)
            print(format_scrambled(puzzle))
            return 0
        sentences = _collect_sentences(args)
        puzzles = build_puzzles(sentences, args.count, args.seed)
        html_text = render_worksheet(puzzles, args.title, args.answers, args.lines)
        _write_output(html_text, args.output)
        return 0
    except PuzzleError as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2
    except OSError as exc:
        print("写入失败：%s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
