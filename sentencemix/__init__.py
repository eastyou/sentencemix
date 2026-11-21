"""sentencemix：句子重排练习纸。"""

from .model import (
    Puzzle,
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
from .render import render_worksheet

__all__ = [
    "Puzzle",
    "PuzzleError",
    "build_puzzle",
    "build_puzzles",
    "builtin_sentences",
    "check_answer",
    "format_scrambled",
    "load_sentences",
    "normalize_text",
    "render_worksheet",
    "shuffle_tokens",
    "split_sentences",
    "tokenize",
]

__version__ = "0.1.0"
