from mrya_tokens import TokenType
from mrya_ast import Literal, Variable, Assign, Call, LetStatement, OutputStatement, BinaryExpression

class ParseError(Exception):
    pass

class MryaParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        statements = []
        while not self._is_at_end():
            stmt = self._statement()
            if stmt is not None:
                statements.append(stmt)
        return statements

    def _statement(self):
        if self._match(TokenType.LET):
            return self._let_statement()
        if self._match(TokenType.OUTPUT):
            return self._output_statement()

        # If we reach here and didn’t match anything,
        # advance to avoid infinite loop and report error.
        print(f"Mrya Parse Error: Unexpected token '{self._peek().lexeme}' on line {self._peek().line}")
        self._advance()  # skip unknown token to continue parsing
        return None

    def _let_statement(self):
        name_token = self._consume(TokenType.IDENTIFIER, "Expect variable name.")
        self._consume(TokenType.EQUAL, "Expect '=' after variable name.")
        initializer = self._expression()
        return LetStatement(name_token, initializer)

    def _output_statement(self):
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'output'.")
        expr = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after output.")
        return OutputStatement(expr)

    def _expression(self):
        return self._term()
    
    def _term(self):
        expr = self._factor()
        
        while self._match(TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH):
            operator = self._previous()
            right = self._primary()
            expr = BinaryExpression(expr, operator, right)
        return expr
    def _factor(self):
        expr = self._primary()
        
        while self._match(TokenType.STAR, TokenType.SLASH):
            operator = self._previous()
            right = self._primary()
            expr = BinaryExpression(expr, operator, right)
        return expr
    
    def _primary(self):    
        if self._check(TokenType.STRING):
            return Literal(self._advance().literal)
        elif self._check(TokenType.NUMBER):
            return Literal(self._advance().literal)
        elif self._check(TokenType.IDENTIFIER):
            return Variable(self._advance())  # Pass token, not string
        raise ParseError("Unsupported expression")

    # Utilities

    def _match(self, *types):
        for t in types:
            if self._check(t):
                self._advance()
                return True
        return False

    def _consume(self, type, message):
        if self._check(type):
            return self._advance()
        raise ParseError(message)

    def _check(self, type):
        if self._is_at_end():
            return False
        return self._peek().type == type

    def _advance(self):
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _peek(self):
        return self.tokens[self.current]

    def _previous(self):
        return self.tokens[self.current - 1]

    def _is_at_end(self):
        return self._peek().type == TokenType.EOF
