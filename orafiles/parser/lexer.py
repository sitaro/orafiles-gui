"""Tokenizer for Oracle NV-pair configuration format."""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    WORD = auto()       # Unquoted identifier or value
    STRING = auto()     # Quoted string
    LPAREN = auto()     # (
    RPAREN = auto()     # )
    EQUALS = auto()     # =
    COMMA = auto()      # ,
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    col: int

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.col})"


class LexerError(Exception):
    def __init__(self, message: str, line: int, col: int):
        super().__init__(f"Line {line}, Col {col}: {message}")
        self.line = line
        self.col = col


class Lexer:
    """Tokenizer for Oracle .ora NV-pair format.

    Handles:
    - Parenthesized lists: ( )
    - Key = Value pairs
    - Quoted strings (single and double)
    - Comments: # line comments
    - Comma separators
    """

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.col = 1

    def _advance(self):
        if self.pos < len(self.text):
            if self.text[self.pos] == '\n':
                self.line += 1
                self.col = 1
            else:
                self.col += 1
            self.pos += 1

    def _peek(self) -> str | None:
        if self.pos < len(self.text):
            return self.text[self.pos]
        return None

    def _skip_whitespace_and_comments(self):
        while self.pos < len(self.text):
            ch = self.text[self.pos]
            if ch in (' ', '\t', '\r', '\n'):
                self._advance()
            elif ch == '#':
                while self.pos < len(self.text) and self.text[self.pos] != '\n':
                    self._advance()
            else:
                break

    def _read_quoted_string(self, quote_char: str) -> Token:
        start_line = self.line
        start_col = self.col
        self._advance()  # skip opening quote
        result = []
        while self.pos < len(self.text):
            ch = self.text[self.pos]
            if ch == quote_char:
                self._advance()  # skip closing quote
                return Token(TokenType.STRING, ''.join(result), start_line, start_col)
            result.append(ch)
            self._advance()
        raise LexerError(f"Unterminated string starting with {quote_char}", start_line, start_col)

    def _read_word(self) -> Token:
        start_line = self.line
        start_col = self.col
        result = []
        while self.pos < len(self.text):
            ch = self.text[self.pos]
            if ch in ('(', ')', '=', ',', '#', ' ', '\t', '\r', '\n', '"', "'"):
                break
            result.append(ch)
            self._advance()
        return Token(TokenType.WORD, ''.join(result), start_line, start_col)

    def tokenize(self) -> list[Token]:
        tokens = []
        while True:
            self._skip_whitespace_and_comments()
            if self.pos >= len(self.text):
                tokens.append(Token(TokenType.EOF, '', self.line, self.col))
                break

            ch = self.text[self.pos]
            if ch == '(':
                tokens.append(Token(TokenType.LPAREN, '(', self.line, self.col))
                self._advance()
            elif ch == ')':
                tokens.append(Token(TokenType.RPAREN, ')', self.line, self.col))
                self._advance()
            elif ch == '=':
                tokens.append(Token(TokenType.EQUALS, '=', self.line, self.col))
                self._advance()
            elif ch == ',':
                tokens.append(Token(TokenType.COMMA, ',', self.line, self.col))
                self._advance()
            elif ch in ('"', "'"):
                tokens.append(self._read_quoted_string(ch))
            else:
                tokens.append(self._read_word())

        return tokens
