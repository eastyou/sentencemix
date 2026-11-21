"""命令行测试。"""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from sentencemix.cli import main


def run_cli(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


class SheetCommandTest(unittest.TestCase):
    def test_default_uses_builtin(self):
        code, out, _ = run_cli(["sheet"])
        self.assertEqual(code, 0)
        self.assertEqual(out.count('class="item"'), 11)

    def test_text_option(self):
        code, out, _ = run_cli(
            ["sheet", "--text", "Hello world.\n今天天气很好。", "--seed", "1"]
        )
        self.assertEqual(code, 0)
        self.assertEqual(out.count('class="item"'), 2)

    def test_count_option(self):
        code, out, _ = run_cli(["sheet", "--text", "a b\nc d\ne f", "--count", "2", "--seed", "2"])
        self.assertEqual(code, 0)
        self.assertEqual(out.count('class="item"'), 2)

    def test_writes_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "sheet.html")
            code, out, _ = run_cli(["sheet", "--text", "a b\nc d", "-o", target])
            self.assertEqual(code, 0)
            self.assertIn("已写入", out)
            with open(target, encoding="utf-8") as handle:
                html = handle.read()
            self.assertEqual(html.count('class="item"'), 2)

    def test_answers_flag(self):
        code, out, _ = run_cli(["sheet", "--text", "a b\nc d", "--answers", "--seed", "3"])
        self.assertEqual(code, 0)
        self.assertIn("参考答案", out)

    def test_input_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "sentences.txt")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("Hello world.\n今天天气很好。\n")
            code, out, _ = run_cli(["sheet", "-i", path, "--seed", "4"])
            self.assertEqual(code, 0)
            self.assertEqual(out.count('class="item"'), 2)

    def test_missing_input_file(self):
        code, _, err = run_cli(["sheet", "-i", "/no/such/file.txt"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_too_many_returns_two(self):
        code, _, err = run_cli(["sheet", "--text", "a b", "--count", "2"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_invalid_sentence_returns_two(self):
        code, _, err = run_cli(["sheet", "--text", "Hello."])
        self.assertEqual(code, 2)
        self.assertIn("至少需要两个词", err)

    def test_custom_title(self):
        code, out, _ = run_cli(["sheet", "--text", "a b", "--title", "语文小练习"])
        self.assertEqual(code, 0)
        self.assertIn("语文小练习", out)

    def test_reproducible_seed(self):
        _, first, _ = run_cli(["sheet", "--text", "a b c\nd e f", "--seed", "7"])
        _, second, _ = run_cli(["sheet", "--text", "a b c\nd e f", "--seed", "7"])
        self.assertEqual(first, second)

    def test_nested_output_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "x", "y", "sheet.html")
            code, _, _ = run_cli(["sheet", "--text", "a b", "-o", target])
            self.assertEqual(code, 0)
            self.assertTrue(os.path.exists(target))


class MixCommandTest(unittest.TestCase):
    def test_prints_scrambled(self):
        code, out, _ = run_cli(["mix", "The cat sleeps."])
        self.assertEqual(code, 0)
        parts = out.strip().split(" / ")
        self.assertEqual(len(parts), 3)
        self.assertIn("The", parts)

    def test_deterministic_with_seed(self):
        _, first, _ = run_cli(["mix", "a b c d", "--seed", "2"])
        _, second, _ = run_cli(["mix", "a b c d", "--seed", "2"])
        self.assertEqual(first, second)

    def test_invalid_sentence(self):
        code, _, err = run_cli(["mix", "Hello."])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)


class HelpTest(unittest.TestCase):
    def test_help_exits_zero(self):
        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                main(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_sheet_help(self):
        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                main(["sheet", "--help"])
        self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
