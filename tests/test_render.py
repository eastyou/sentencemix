"""渲染层测试。"""

import unittest

from sentencemix.model import build_puzzle, build_puzzles, builtin_sentences
from sentencemix.render import render_worksheet


class WorksheetRenderTest(unittest.TestCase):
    def test_skeleton(self):
        html = render_worksheet(build_puzzles(builtin_sentences(), 2, seed=1))
        self.assertTrue(html.startswith("<!DOCTYPE html>"))
        self.assertIn('<meta charset="utf-8">', html)
        self.assertIn('<html lang="zh-CN">', html)

    def test_item_count(self):
        html = render_worksheet(build_puzzles(builtin_sentences(), 3, seed=1))
        self.assertEqual(html.count('class="item"'), 3)

    def test_chips_match_tokens(self):
        puzzles = build_puzzles(builtin_sentences(), 2, seed=2)
        html = render_worksheet(puzzles)
        total = sum(puzzle.token_count for puzzle in puzzles)
        self.assertEqual(html.count('class="chip"'), total)

    def test_answers_hidden_by_default(self):
        html = render_worksheet(build_puzzles(builtin_sentences(), 2, seed=3))
        self.assertNotIn("参考答案", html)

    def test_answers_included(self):
        puzzles = build_puzzles(builtin_sentences(), 2, seed=3)
        html = render_worksheet(puzzles, include_answers=True)
        self.assertIn("参考答案", html)
        for puzzle in puzzles:
            self.assertIn(puzzle.answer, html)

    def test_title_escaped(self):
        html = render_worksheet([], title="<重排> & 练习")
        self.assertIn("&lt;重排&gt; &amp; 练习", html)

    def test_empty(self):
        html = render_worksheet([])
        self.assertIn("暂无题目", html)

    def test_lines_parameter(self):
        puzzle = build_puzzle("The cat sleeps.", seed=1)
        html = render_worksheet([puzzle], lines=2)
        self.assertEqual(html.count('class="line"'), 2)

    def test_invalid_lines(self):
        with self.assertRaises(ValueError):
            render_worksheet([], lines=0)

    def test_a4_style(self):
        html = render_worksheet(build_puzzles(builtin_sentences(), 1, seed=4))
        self.assertIn("size: A4", html)
        self.assertIn("@media print", html)

    def test_chinese_sentence(self):
        puzzle = build_puzzle("今天天气很好。", seed=1)
        html = render_worksheet([puzzle], include_answers=True)
        self.assertIn("今天天气很好。", html)
        self.assertIn('class="chip"', html)


if __name__ == "__main__":
    unittest.main()
