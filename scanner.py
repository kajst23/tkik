from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TokenType(Enum):
    SLOWO_KLUCZOWE = "SLOWO_KLUCZOWE"
    NUTA = "NUTA"
    PAUZA = "PAUZA"
    LICZBA = "LICZBA"
    MODYFIKATOR_GORA = "MODYFIKATOR_GORA"
    MODYFIKATOR_DOL = "MODYFIKATOR_DOL"
    ZNAK_TAKTOWY = "ZNAK_TAKTOWY"
    NAWIAS_L = "NAWIAS_L"
    NAWIAS_P = "NAWIAS_P"
    KONIEC = "KONIEC"


@dataclass
class Token:
    type: TokenType
    value: str
    column: int

    def __str__(self) -> str:
        return f"({self.type.value}, {self.value!r})"


class ScannerError(Exception):
    def __init__(self, message: str, column: int):
        self.column = column
        super().__init__(f"Błąd skanera w kolumnie {column}: {message}")


class Scanner:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0

    @property
    def column(self) -> int:
        return self.pos + 1

    def _current(self) -> Optional[str]:
        if self.pos < len(self.text):
            return self.text[self.pos]
        return None

    def _advance(self):
        self.pos += 1

    def _skip_whitespace(self):
        while self._current() is not None and self._current().isspace():
            self._advance()

    def _scan_int(self) -> Token:
        start_col = self.column
        digits: list[str] = []
        while self._current() is not None and self._current().isdigit():
            digits.append(self._current())
            self._advance()
        return Token(TokenType.LICZBA, "".join(digits), start_col)

    def _scan_word(self) -> Token:
        start_col = self.column
        chars: list[str] = []
        
        while self._current() is not None and (self._current().isalpha() or self._current().isdigit()):
            chars.append(self._current().upper()) # Normalizujemy do wielkich liter
            self._advance()
            
        word = "".join(chars)
        
        if word in ["TEMPO", "LOOP"]:
            return Token(TokenType.SLOWO_KLUCZOWE, word, start_col)
        elif len(word) == 1 and word in "ABCDEFG":
            return Token(TokenType.NUTA, word, start_col)
        elif len(word) == 1 and word == "P":
            return Token(TokenType.PAUZA, word, start_col)
            
        raise ScannerError(f"nieznany identyfikator {word!r}", column=start_col)

    def next_token(self) -> Token:
        self._skip_whitespace()

        if self._current() is None:
            return Token(TokenType.KONIEC, "", self.column)

        ch = self._current()
        col = self.column

        if ch.isdigit():
            return self._scan_int()

        if ch.isalpha():
            return self._scan_word()

        SINGLE_CHAR_TOKENS = {
            "+": TokenType.MODYFIKATOR_GORA,
            "-": TokenType.MODYFIKATOR_DOL,
            "|": TokenType.ZNAK_TAKTOWY,
            "[": TokenType.NAWIAS_L,
            "]": TokenType.NAWIAS_P,
        }
        
        if ch in SINGLE_CHAR_TOKENS:
            self._advance()
            return Token(SINGLE_CHAR_TOKENS[ch], ch, col)

        raise ScannerError(
            f"nierozpoznany znak {ch!r}",
            column=col,
        )


def scan_to_tokens(expression: str) -> tuple[list[Token], ScannerError | None]:
    scanner = Scanner(expression)
    tokens: list[Token] = []
    while True:
        try:
            token = scanner.next_token()
        except ScannerError as e:
            return tokens, e
        if token.type == TokenType.KONIEC:
            return tokens, None
        tokens.append(token)


def scan_expression(expression: str) -> list[Token]:
    scanner = Scanner(expression)
    tokens: list[Token] = []

    print(f"Wyrażenie: {expression!r}")

    while True:
        try:
            token = scanner.next_token()
        except ScannerError as e:
            print(f"BŁĄD: {e}")
            print(expression)
            print(" " * (e.column - 1) + "^")
            break

        if token.type == TokenType.KONIEC:
            print("(KONIEC, '')")
            break

        tokens.append(token)
        print(token)

    return tokens
