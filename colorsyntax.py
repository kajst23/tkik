import html as _html
from scanner import TokenType, ScannerError, scan_to_tokens

COLORS = {
    TokenType.SLOWO_KLUCZOWE:   "purple",
    TokenType.NUTA:             "blue",
    TokenType.PAUZA:            "gray",
    TokenType.LICZBA:           "green",
    TokenType.MODYFIKATOR_GORA: "red",
    TokenType.MODYFIKATOR_DOL:  "red",
    TokenType.ZNAK_TAKTOWY:     "black",
    TokenType.NAWIAS_L:         "orange",
    TokenType.NAWIAS_P:         "orange",
}


def _highlight(expression: str, tokens, error) -> str:
    pos_to_token = {}
    for token in tokens:
        start = token.column - 1
        for i in range(start, start + len(token.value)):
            pos_to_token[i] = token

    parts = []
    i = 0
    while i < len(expression):
        if i in pos_to_token:
            token = pos_to_token[i]
            color = COLORS.get(token.type, "black")
            val = _html.escape(token.value)
            
            if token.type == TokenType.SLOWO_KLUCZOWE:
                val = f"<b>{val}</b>"
            
            parts.append(f'<font color="{color}">{val}</font>')
            i += len(token.value)
        elif error and i == error.column - 1:
            parts.append(f'<font color="red"><u>{_html.escape(expression[i])}</u></font>')
            i += 1
        else:
            parts.append(_html.escape(expression[i]))
            i += 1

    return "".join(parts)


def generate_html(expressions: list[str]) -> str:
    lines = []
    for expr in expressions:
        tokens, error = scan_to_tokens(expr)
        lines.append(f"<p><code>{_highlight(expr, tokens, error)}</code></p>")
        if error:
            lines.append(f'<p><font color="red">{_html.escape(str(error))}</font></p>')

    return "<html><body style='font-family: monospace; font-size: 16px;'>\n" + "\n".join(lines) + "\n</body></html>"
