from dataclasses import dataclass
from typing import List


@dataclass
class QuizDTO:
    text: str
    type: str
    options: List[str]
    correct: List[int]


@dataclass
class TextDTO:
    content: str


@dataclass
class ShortAnswerDTO:
    question: str
    correct_answers: List[str]
    case_sensitive: bool = False
    trim_whitespace: bool = True


@dataclass
class VideoDTO:
    url: str
    title: str


@dataclass
class TestDTO:
    input: str


@dataclass
class CodeDTO:
    description: str
    test_cases: List[TestDTO]
    checker_code: str
    author_solve: str
    author_language: str
    test_examples_count: int
    time_limit: int = 2
    memory_limit: int = 128
