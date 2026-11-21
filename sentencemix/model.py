"""句子分词、打乱与重排题生成。"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

PUNCTUATION = set(".,!?;:\"'()[]{}<>，。！？；：、“”‘’（）【】《》…—·")
CJK_PATTERN = re.compile(r"[\u4e00-\u9fff]")


class PuzzleError(ValueError):
    """句子、文件或题目参数不合法。"""


@dataclass(frozen=True)
class Puzzle:
    """一道重排题。"""

    sentence: str
    tokens: Tuple[str, ...]
    scrambled: Tuple[str, ...]

    @property
    def answer(self) -> str:
        return self.sentence

    @property
    def token_count(self) -> int:
        return len(self.tokens)


BUILTIN_SENTENCES = (
    "The quick brown fox jumps over the lazy dog.",
    "I like to read books before bedtime.",
    "My teacher gave us a challenging puzzle.",
    "We should finish our homework before dinner.",
    "今天的天气非常适合去公园散步。",
    "我们在实验室里观察了水的沸腾。",
    "请把课桌上的书本整理整齐。",
    "小明每天坚持跑步锻炼身体。",
    "这本书讲述了一个关于勇气的故事。",
    "音乐可以让人放松心情。",
    "周末我们一起去博物馆参观展览。",
)


def builtin_sentences() -> List[str]:
    return list(BUILTIN_SENTENCES)


def check_count(count: int) -> int:
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        raise PuzzleError("题目数量必须是正整数")
    return count


def split_sentences(text: str) -> List[str]:
    """按行拆分句子，跳过空行与 # 注释。"""
    if not isinstance(text, str):
        raise PuzzleError("句子文本必须是字符串")
    sentences = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        sentences.append(line)
    if not sentences:
        raise PuzzleError("没有可用的句子")
    return sentences


def load_sentences(path: str) -> List[str]:
    """读取 UTF-8 文本文件，兼容 BOM。"""
    if not isinstance(path, str) or not path.strip():
        raise PuzzleError("文件路径不能为空")
    try:
        content = Path(path).read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise PuzzleError("无法读取文件 %s：%s" % (path, exc))
    return split_sentences(content)


def _strip_edges(token: str) -> str:
    while token and token[0] in PUNCTUATION:
        token = token[1:]
    while token and token[-1] in PUNCTUATION:
        token = token[:-1]
    return token


def tokenize(sentence: str) -> List[str]:
    """中文按字拆分，英文按词拆分，去掉标点与空白。"""
    if not isinstance(sentence, str):
        raise PuzzleError("句子必须是字符串")
    cleaned = sentence.strip()
    if not cleaned:
        raise PuzzleError("句子不能为空")
    if CJK_PATTERN.search(cleaned):
        tokens = [char for char in cleaned if not char.isspace() and char not in PUNCTUATION]
    else:
        tokens = []
        for word in cleaned.split():
            token = _strip_edges(word)
            if token:
                tokens.append(token)
    if len(tokens) < 2:
        raise PuzzleError("句子至少需要两个词：%s" % sentence)
    return tokens


def normalize_text(text: str) -> str:
    """去掉大小写、空白与标点，用于答案比对。"""
    if not isinstance(text, str):
        return ""
    return "".join(char.lower() for char in text if not char.isspace() and char not in PUNCTUATION)


def shuffle_tokens(tokens: Sequence[str], seed: Optional[int] = None) -> List[str]:
    """确定性打乱，并保证顺序与原句不同。"""
    if len(tokens) < 2:
        return list(tokens)
    rng = random.Random(seed)
    result = list(tokens)
    for _ in range(20):
        rng.shuffle(result)
        if result != list(tokens):
            return result
    result = list(tokens[1:]) + [tokens[0]]
    return result


def build_puzzle(sentence: str, seed: Optional[int] = None) -> Puzzle:
    """把一句话变成一道重排题。"""
    tokens = tokenize(sentence)
    if len(set(tokens)) < 2:
        raise PuzzleError("句子至少需要两个不同的词：%s" % sentence)
    scrambled = shuffle_tokens(tokens, seed)
    return Puzzle(sentence.strip(), tuple(tokens), tuple(scrambled))


def build_puzzles(
    sentences: Sequence[str],
    count: Optional[int] = None,
    seed: Optional[int] = None,
) -> List[Puzzle]:
    """从句子列表中抽取并生成题目。"""
    if not isinstance(sentences, (list, tuple)):
        raise PuzzleError("句子必须是列表")
    source = list(sentences)
    if not source:
        raise PuzzleError("句子列表不能为空")
    total = len(source) if count is None else check_count(count)
    if total > len(source):
        raise PuzzleError("只有 %d 个句子，无法生成 %d 道题" % (len(source), total))
    rng = random.Random(seed)
    chosen = rng.sample(source, total)
    return [build_puzzle(sentence, None if seed is None else seed + index) for index, sentence in enumerate(chosen)]


def check_answer(puzzle: Puzzle, text: str) -> bool:
    """判断重排后的句子是否正确，忽略标点、大小写与空白。"""
    if not isinstance(text, str) or not text.strip():
        return False
    return normalize_text(text) == normalize_text(puzzle.sentence)


def format_scrambled(puzzle: Puzzle, separator: str = " / ") -> str:
    return separator.join(puzzle.scrambled)
