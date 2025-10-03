from mrya_tokens import TokenType, Token
from mrya_errors import LexerError

KEYWORDS = {
    "let": TokenType.LET,
    "function": TokenType.FUNCTION,
    "return": TokenType.RETURN,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "output": TokenType.OUTPUT,
    "input": TokenType.INPUT,
    "func": TokenType.FUNC,
    "define": TokenType.DEFINE,
    "while": TokenType.WHILE,
    "request": TokenType.INPUT,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "for": TokenType.FOR,
    "const": TokenType.CONST,
    "in": TokenType.IN,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "using": TokenType.USING,
    "as": TokenType.AS,
}
class MryaLexer:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self):
        while not self._is_at_end():
            self.start = self.current
            self._scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def _scan_token(self):
        c = self._advance()
        if c == '(':
            self._add_token(TokenType.LEFT_PAREN)
        elif c == ')':
            self._add_token(TokenType.RIGHT_PAREN)
        elif c == '{':
            self._add_token(TokenType.LEFT_BRACE)
        elif c == '}':
            self._add_token(TokenType.RIGHT_BRACE)
        elif c == '[':
            self._add_token(TokenType.LEFT_BRACKET)
        elif c == ']':
            self._add_token(TokenType.RIGHT_BRACKET)
        elif c == ',':
            self._add_token(TokenType.COMMA)
        elif c == ':':
            self._add_token(TokenType.COLON)
        elif c == '.':
            self._add_token(TokenType.DOT)
        elif c == '-':
            self._add_token(TokenType.MINUS)
        elif c == '+':
            self._add_token(TokenType.PLUS)
        elif c == ';':
            self._add_token(TokenType.SEMICOLON)
        elif c == '*':
            self._add_token(TokenType.STAR)
        elif c == '!':
            self._add_token(TokenType.BANG_EQUAL if self._match('=') else TokenType.BANG)
        elif c == '=':
            self._add_token(TokenType.EQUAL_EQUAL if self._match('=') else TokenType.EQUAL)
        elif c == '<':
            self._add_token(TokenType.LESS_EQUAL if self._match('=') else TokenType.LESS)
        elif c == '>':
            self._add_token(TokenType.GREATER_EQUAL if self._match('=') else TokenType.GREATER)
        elif c == '/':
            if self._match('/'):
                while self._peek() != '\n' and not self._is_at_end():
                    self._advance()
            else:
                self._add_token(TokenType.SLASH)
        # Shebang!!
        elif c == '#':
            if self.current == 1 and self._match('!'):
                while self._peek() != '\n' and not self._is_at_end():
                    self._advance()
                # Ignore the shebang line entirelyF
        elif c in [' ', '\r', '\t']:
            pass  # Ignore whitespace
        elif c == '\n':
            self.line += 1
        elif c == '"':
            self._string()
        elif c.isdigit():
            self._number()
        elif c.isalpha() or c == '_':
            self._identifier()
        else:
            raise LexerError(f"[Line {self.line}] Unexpected character: {c}")

    def _advance(self):
        self.current += 1
        return self.source[self.current - 1]

    def _add_token(self, type, literal=None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type, text, literal, self.line))

    def _match(self, expected):
        if self._is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def _peek(self):
        if self._is_at_end():
            return '\0'
        return self.source[self.current]

    def _peek_next(self):
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def _string(self):
        value_builder = []
        while self._peek() != '"' and not self._is_at_end():
            if self._peek() == '\n':
                self.line += 1
            
            char = self._advance()
            if char == '\\':
                # Handle escape sequences
                if self._match('n'):
                    value_builder.append('\n')
                elif self._match('t'):
                    value_builder.append('\t')
                elif self._match('"'):
                    value_builder.append('"')
                elif self._match('\\'):
                    value_builder.append('\\')
                else:
                    # If not a recognized escape, treat as a literal backslash
                    value_builder.append('\\')
            else:
                value_builder.append(char)

        if self._is_at_end():
            raise LexerError(f"[Line {self.line}] Unterminated string.")

        self._advance() # Consume the closing quote
        self._add_token(TokenType.STRING, "".join(value_builder))

    def _number(self):
        while self._peek().isdigit():
            self._advance()

        if self._peek() == '.' and self._peek_next().isdigit():
            self._advance()
            while self._peek().isdigit():
                self._advance()

        num_str = self.source[self.start:self.current]
        try:
            if '.' in num_str:
                value = float(num_str)
            else:
                value = int(num_str)
        except ValueError:
            raise LexerError(f"[Line {self.line}] Invalid number: {num_str}")
        self._add_token(TokenType.NUMBER, value)

    def _identifier(self):
        while self._peek().isalnum() or self._peek() == '_':
            self._advance()

        text = self.source[self.start:self.current]
        token_type = KEYWORDS.get(text, TokenType.IDENTIFIER)
        self._add_token(token_type)

    def _is_at_end(self):
        return self.current >= len(self.source)
