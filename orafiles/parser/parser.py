"""Recursive-descent parser for Oracle NV-pair configuration format."""

from __future__ import annotations
from orafiles.parser.lexer import Lexer, Token, TokenType, LexerError
from orafiles.parser.ast_nodes import NVPair, NVList, NVValue, ConfigFile


class ParseError(Exception):
    def __init__(self, message: str, token: Token | None = None):
        if token:
            super().__init__(f"Line {token.line}, Col {token.col}: {message}")
        else:
            super().__init__(message)
        self.token = token


class Parser:
    """Recursive-descent parser for Oracle .ora files.

    Grammar (simplified):
        config_file = { nv_pair }
        nv_pair     = WORD '=' value
        value       = WORD | STRING | '(' list_items ')'
        list_items  = list_item { [','] list_item }
        list_item   = nv_pair | value
    """

    def __init__(self, text: str):
        self.tokens = Lexer(text).tokenize()
        self.pos = 0

    def _current(self) -> Token:
        return self.tokens[self.pos]

    def _peek(self) -> Token:
        return self.tokens[self.pos]

    def _advance(self) -> Token:
        token = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return token

    def _expect(self, token_type: TokenType) -> Token:
        token = self._current()
        if token.type != token_type:
            raise ParseError(
                f"Expected {token_type.name}, got {token.type.name} ({token.value!r})",
                token
            )
        return self._advance()

    def _is_at(self, *types: TokenType) -> bool:
        return self._current().type in types

    def parse(self) -> ConfigFile:
        """Parse the token stream into a ConfigFile AST."""
        entries = []
        while not self._is_at(TokenType.EOF):
            entries.append(self._parse_nv_pair())
        return ConfigFile(entries=entries)

    def _parse_nv_pair(self) -> NVPair:
        """Parse: WORD '=' value

        Handles Oracle's multi-paren format where:
            ADDRESS = (PROTOCOL = TCP)(HOST = myhost)(PORT = 1521)
        is equivalent to:
            ADDRESS = (PROTOCOL = TCP, HOST = myhost, PORT = 1521)
        Multiple consecutive parenthesized groups are merged into one NVList.
        """
        key_token = self._expect(TokenType.WORD)
        self._expect(TokenType.EQUALS)
        value = self._parse_value()

        # If value is an NVList and the next token is LPAREN, merge consecutive lists
        if isinstance(value, NVList) and self._is_at(TokenType.LPAREN):
            merged_items = list(value.items)
            while self._is_at(TokenType.LPAREN):
                next_list = self._parse_list()
                merged_items.extend(next_list.items)
            value = NVList(items=merged_items)

        return NVPair(key=key_token.value, value=value)

    def _parse_value(self):
        """Parse: WORD | STRING | '(' list_items ')'"""
        if self._is_at(TokenType.LPAREN):
            return self._parse_list()
        elif self._is_at(TokenType.WORD):
            token = self._advance()
            return NVValue(value=token.value)
        elif self._is_at(TokenType.STRING):
            token = self._advance()
            return NVValue(value=token.value)
        else:
            token = self._current()
            raise ParseError(
                f"Expected value, got {token.type.name} ({token.value!r})",
                token
            )

    def _parse_list(self) -> NVList:
        """Parse: '(' list_items ')'"""
        self._expect(TokenType.LPAREN)
        items = []
        while not self._is_at(TokenType.RPAREN, TokenType.EOF):
            # Skip commas
            if self._is_at(TokenType.COMMA):
                self._advance()
                continue

            # Look ahead to determine if this is an nv_pair or a bare value
            if self._is_at(TokenType.WORD):
                # Check if next non-whitespace token is '='
                if self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1].type == TokenType.EQUALS:
                    items.append(self._parse_nv_pair())
                else:
                    token = self._advance()
                    items.append(NVValue(value=token.value))
            elif self._is_at(TokenType.STRING):
                token = self._advance()
                items.append(NVValue(value=token.value))
            elif self._is_at(TokenType.LPAREN):
                items.append(self._parse_list())
            else:
                token = self._current()
                raise ParseError(
                    f"Unexpected token in list: {token.type.name} ({token.value!r})",
                    token
                )

        self._expect(TokenType.RPAREN)
        return NVList(items=items)


def parse_ora(text: str) -> ConfigFile:
    """Convenience function to parse Oracle .ora file text."""
    return Parser(text).parse()
