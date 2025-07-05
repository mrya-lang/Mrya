from mrya_tokens import TokenType
import mrya_interpreter
from mrya_ast import Literal, Variable, LetStatement, OutputStatement, BinaryExpression, FunctionDeclaration, FunctionCall, ReturnStatement

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
    
    def _expression_statement(self):
        expr = self._expression()
        return expr

    def _statement(self):
        if self._match(TokenType.LET):
            return self._let_statement()
        if self._match(TokenType.OUTPUT):
            return self._output_statement()
        if self._match(TokenType.FUNC):  
            return self._function_statement()
        if self._match(TokenType.RETURN):
            return self._return_statement()
        
        return self._expression_statement()

        print(f"Mrya Parse Error: Unexpected token '{self._peek().lexeme}' on line {self._peek().line}")
        self._advance()
        return None
    
    def _return_statement(self):
        keyword = self._previous()
        
        if not self._check(TokenType.SEMICOLON) and not self._check(TokenType.RIGHT_BRACE):
            value = self._expression()
        else:
            value = None
        return ReturnStatement(keyword, value)

    def _let_statement(self):
        name_token = self._consume(TokenType.IDENTIFIER, "Expected variable name after 'let'.")
        self._consume(TokenType.EQUAL, "Expected '=' after variable name.")
        initializer = self._expression()
        return LetStatement(name_token, initializer)

    def _output_statement(self):
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'output'.")
        expr = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after output expression.")
        return OutputStatement(expr)

    
    def _function_statement(self):
        name_token = self._consume(TokenType.IDENTIFIER, "Expected function name after 'func'.")
        self._consume(TokenType.EQUAL, "Expected '=' after function name.")
        self._consume(TokenType.DEFINE, "Expected 'define' after '=' in function declaration.")
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'define'.")

        parameters = []
        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                parameters.append(self._consume(TokenType.IDENTIFIER, "Expected parameter name."))
                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters.")
        self._consume(TokenType.LEFT_BRACE, "Expected '{' to start function body.")

        body = []
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            stmt = self._statement()
            if stmt:
                body.append(stmt)

        self._consume(TokenType.RIGHT_BRACE, "Expected '}' after function body.")
        return FunctionDeclaration(name_token, parameters, body)

    # --- Expressions ---
    def _expression(self):
        return self._addition()

    def _addition(self):
        expr = self._multiplication()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            operator = self._previous()
            right = self._multiplication()
            expr = BinaryExpression(expr, operator, right)
        return expr

    def _multiplication(self):
        expr = self._unary()
        while self._match(TokenType.STAR, TokenType.SLASH):
            operator = self._previous()
            right = self._unary()
            expr = BinaryExpression(expr, operator, right)
        return expr

    def _unary(self):
        if self._match(TokenType.MINUS):
            operator = self._previous()
            right = self._unary()
            return BinaryExpression(Literal(0), operator, right)
        return self._primary()

    def _primary(self):
        if self._match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self._previous().literal)
        if self._match(TokenType.IDENTIFIER):
            name = self._previous()
            if self._match(TokenType.LEFT_PAREN):
                arguments = []
                if not self._check(TokenType.RIGHT_PAREN):
                    while True:
                        arguments.append(self._expression())
                        if not self._match(TokenType.COMMA):
                            break
                self._consume(TokenType.RIGHT_PAREN, "Expected ')' after function arguments.")
                return FunctionCall(name, arguments)
            return Variable(name)
                        


    # --- Token Helpers ---
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
