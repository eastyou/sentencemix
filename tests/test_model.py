"""模型层测试。"""

import os
import tempfile
import unittest

from sentencemix.model import (
    PuzzleError,
    build_puzzle,
    build_puzzles,
    builtin_sentences,
    check_answer,
    format_scrambled,
    load_sentences,
    normalize_text,
    shuffle_tokens,
    split_sentences,
    tokenize,
)


class SplitTest(unittest.TestCase):
    def test_basic_lines(self):
        text = "Hello world.\nGood morning class."
        self.assertEqual(split_sentences(text), ["Hello world.", "Good morning class."])

    def test_skips_blank_lines(self):
        text = "First line.\n\n\nSecond line.\n"
        self.assertEqual(split_sentences(text), ["First line.", "Second line."])

    def test_skips_comments(self):
        text = "# 标题\nHello world.\n"
        self.assertEqual(split_sentences(text), ["Hello world."])

    def test_strips_whitespace(self):
        self.assertEqual(split_sentences("  Hello world.  "), ["Hello world."])

    def test_empty_rejected(self):
        with self.assertRaises(PuzzleError):
            split_sentences("  \n# only comment\n")

    def test_non_string(self):
        with self.assertRaises(PuzzleError):
            split_sentences(None)


class TokenizeTest(unittest.TestCase):
    def test_english_words(self):
        self.assertEqual(tokenize("The quick fox"), ["The", "quick", "fox"])

    def test_strips_trailing_punctuation(self):
        self.assertEqual(tokenize("Hello, world!"), ["Hello", "world"])

    def test_strips_quotes(self):
        self.assertEqual(tokenize('"Stop!" she said.'), ["Stop", "she", "said"])

    def test_keeps_internal_apostrophe(self):
        self.assertEqual(tokenize("It's a test."), ["It's", "a", "test"])

    def test_chinese_characters(self):
        self.assertEqual(tokenize("你好，世界！"), ["你", "好", "世", "界"])

    def test_chinese_without_punctuation(self):
        self.assertEqual(tokenize("我们学习"), ["我", "们", "学", "习"])

    def test_extra_spaces(self):
        self.assertEqual(tokenize("  a   b  "), ["a", "b"])

    def test_single_token_rejected(self):
        with self.assertRaises(PuzzleError):
            tokenize("Word")

    def test_punctuation_only_rejected(self):
        with self.assertRaises(PuzzleError):
            tokenize("...!!!")

    def test_empty_rejected(self):
        with self.assertRaises(PuzzleError):
            tokenize("   ")

    def test_non_string(self):
        with self.assertRaises(PuzzleError):
            tokenize(42)


class NormalizeTest(unittest.TestCase):
    def test_lowercase_and_spaces(self):
        self.assertEqual(normalize_text("Hello World"), "helloworld")

    def test_removes_english_punctuation(self):
        self.assertEqual(normalize_text("Hi, there!"), "hithere")

    def test_removes_chinese_punctuation(self):
        self.assertEqual(normalize_text("你好，世界！"), "你好世界")

    def test_non_string(self):
        self.assertEqual(normalize_text(None), "")


class ShuffleTest(unittest.TestCase):
    def test_preserves_tokens(self):
        tokens = ["a", "b", "c", "d"]
        self.assertEqual(sorted(shuffle_tokens(tokens, seed=1)), tokens)

    def test_changes_order(self):
        tokens = ["a", "b", "c", "d"]
        self.assertNotEqual(shuffle_tokens(tokens, seed=1), tokens)

    def test_deterministic(self):
        tokens = ["a", "b", "c", "d", "e"]
        self.assertEqual(shuffle_tokens(tokens, seed=3), shuffle_tokens(tokens, seed=3))

    def test_single_token(self):
        self.assertEqual(shuffle_tokens(["only"]), ["only"])

    def test_empty(self):
        self.assertEqual(shuffle_tokens([]), [])

    def test_identical_tokens(self):
        tokens = ["the", "the"]
        self.assertEqual(shuffle_tokens(tokens, seed=2), tokens)

    def test_two_tokens(self):
        self.assertEqual(shuffle_tokens(["a", "b"], seed=1), ["b", "a"])


class BuildPuzzleTest(unittest.TestCase):
    def test_fields(self):
        puzzle = build_puzzle("The cat sleeps.", seed=1)
        self.assertEqual(puzzle.answer, "The cat sleeps.")
        self.assertEqual(puzzle.token_count, 3)
        self.assertEqual(sorted(puzzle.scrambled), sorted(puzzle.tokens))

    def test_scrambled_differs(self):
        puzzle = build_puzzle("We read books.", seed=2)
        self.assertNotEqual(list(puzzle.scrambled), list(puzzle.tokens))

    def test_deterministic(self):
        first = build_puzzle("We read books.", seed=4)
        second = build_puzzle("We read books.", seed=4)
        self.assertEqual(first.scrambled, second.scrambled)

    def test_chinese(self):
        puzzle = build_puzzle("今天天气很好。", seed=1)
        self.assertEqual(puzzle.token_count, 6)

    def test_duplicate_tokens_rejected(self):
        with self.assertRaises(PuzzleError):
            build_puzzle("the the", seed=1)

    def test_single_token_rejected(self):
        with self.assertRaises(PuzzleError):
            build_puzzle("Hello.")

    def test_format_scrambled(self):
        puzzle = build_puzzle("a b c", seed=5)
        text = format_scrambled(puzzle)
        self.assertEqual(len(text.split(" / ")), 3)


class BuildPuzzlesTest(unittest.TestCase):
    def test_default_uses_all(self):
        sentences = builtin_sentences()
        self.assertEqual(len(build_puzzles(sentences, seed=1)), len(sentences))

    def test_count(self):
        sentences = builtin_sentences()
        self.assertEqual(len(build_puzzles(sentences, 4, seed=1)), 4)

    def test_deterministic(self):
        sentences = builtin_sentences()
        first = [p.answer for p in build_puzzles(sentences, 5, seed=2)]
        second = [p.answer for p in build_puzzles(sentences, 5, seed=2)]
        self.assertEqual(first, second)

    def test_different_seeds(self):
        sentences = builtin_sentences()
        first = [p.answer for p in build_puzzles(sentences, 5, seed=2)]
        second = [p.answer for p in build_puzzles(sentences, 5, seed=3)]
        self.assertNotEqual(first, second)

    def test_too_many(self):
        with self.assertRaises(PuzzleError):
            build_puzzles(["a b"], 2)

    def test_zero(self):
        with self.assertRaises(PuzzleError):
            build_puzzles(["a b"], 0)

    def test_empty_list(self):
        with self.assertRaises(PuzzleError):
            build_puzzles([])

    def test_non_list(self):
        with self.assertRaises(PuzzleError):
            build_puzzles("a b")

    def test_invalid_sentence_in_list(self):
        with self.assertRaises(PuzzleError):
            build_puzzles(["fine sentence", "bad"])

    def test_builtin_sentences(self):
        sentences = builtin_sentences()
        self.assertEqual(len(sentences), 11)
        self.assertTrue(all(sentence.strip() for sentence in sentences))


class CheckAnswerTest(unittest.TestCase):
    def setUp(self):
        self.puzzle = build_puzzle("The cat sleeps.", seed=1)

    def test_exact(self):
        self.assertTrue(check_answer(self.puzzle, "The cat sleeps."))

    def test_lowercase_and_punctuation(self):
        self.assertTrue(check_answer(self.puzzle, "the cat sleeps"))

    def test_extra_spaces(self):
        self.assertTrue(check_answer(self.puzzle, "  The   cat   sleeps  "))

    def test_wrong_order(self):
        self.assertFalse(check_answer(self.puzzle, "cat the sleeps"))

    def test_missing_word(self):
        self.assertFalse(check_answer(self.puzzle, "The cat"))

    def test_empty(self):
        self.assertFalse(check_answer(self.puzzle, "   "))

    def test_chinese_answer(self):
        puzzle = build_puzzle("我们学习中文。", seed=1)
        self.assertTrue(check_answer(puzzle, "我们学习中文"))
        self.assertFalse(check_answer(puzzle, "中文学习我们"))


class LoadSentencesTest(unittest.TestCase):
    def test_reads_utf8(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "sentences.txt")
            with open(path, "w", encoding="utf-8-sig") as handle:
                handle.write("Hello world.\n\n今天天气很好。\n")
            sentences = load_sentences(path)
            self.assertEqual(len(sentences), 2)
            self.assertEqual(sentences[1], "今天天气很好。")

    def test_missing_file(self):
        with self.assertRaises(PuzzleError):
            load_sentences("/no/such/file.txt")

    def test_empty_path(self):
        with self.assertRaises(PuzzleError):
            load_sentences("  ")

    def test_empty_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "empty.txt")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("\n\n")
            with self.assertRaises(PuzzleError):
                load_sentences(path)


if __name__ == "__main__":
    unittest.main()
