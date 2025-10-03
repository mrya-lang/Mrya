from mrya_tokens import TokenType
from mrya_ast import Literal, Variable, Get, LetStatement, OutputStatement, BinaryExpression, Logical, Unary, FunctionDeclaration, FunctionCall, ReturnStatement, IfStatement, WhileStatement, ForStatement, BreakStatement, ContinueStatement, Assignment, SubscriptGet, SubscriptSet, InputCall, ImportStatement, ListLiteral, MapLiteral

class ParseError(Exception):
    def __init__(self, token, message):
        self.token = token
        self.message = message
        super().__init__(f"[Line {token.line}] Error at '{token.lexeme}': {message}")

class MryaParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

        self._loop_depth = 0 # To track if we are inside a loop
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
        if self._match(TokenType.IF):
            return self._if_statement()
        if self._match(TokenType.FOR):
            return self._for_statement()
        if self._match(TokenType.WHILE):
            return self._while_statement()
        if self._match(TokenType.BREAK):
            return self._break_statement()
        if self._match(TokenType.CONTINUE):
            return self._continue_statement()
        
        return self._expression_statement()
    
    def _if_statement(self):
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'if'.")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after if condition.")
        self._consume(TokenType.LEFT_BRACE, "Expected '{' to start if block.")
        
        then_branch = []
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            stmt = self._statement()
            if stmt:
                then_branch.append(stmt)
        self._consume(TokenType.RIGHT_BRACE, "Expected '}' after if block.")
        
        else_branch = None
        if self._match(TokenType.ELSE):
            if self._match(TokenType.IF):
                # This is an 'else if'. The else branch is a list containing a single new IfStatement.
                else_branch = [self._if_statement()]
            else:
                # This is a plain 'else' block.
                self._consume(TokenType.LEFT_BRACE, "Expected '{' to start else block.")
                else_branch = []
                while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
                    stmt = self._statement()
                    if stmt:
                        else_branch.append(stmt)
                self._consume(TokenType.RIGHT_BRACE, "Expected '}' after else block.")
            
        return IfStatement(condition, then_branch, else_branch)
    
    def _while_statement(self):
        try:
            self._loop_depth += 1
            self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'while'.")
            condition = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expected ')' after while condition.")
            self._consume(TokenType.LEFT_BRACE, "Expected '{' to begin while block.")

            body = []
            while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
                stmt = self._statement()
                if stmt:
                    body.append(stmt)
            self._consume(TokenType.RIGHT_BRACE, "Expected '}' after while block.")
            return WhileStatement(condition, body)
        finally:
            self._loop_depth -= 1

    def _for_statement(self):
        try:
            self._loop_depth += 1
            self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'for'.")
            variable = self._consume(TokenType.IDENTIFIER, "Expected variable name.")
            self._consume(TokenType.IN, "Expected 'in' after variable.")
            iterable = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expected ')' after for loop clause.")
            self._consume(TokenType.LEFT_BRACE, "Expected '{' to begin for loop body.")

            body = []
            while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
                stmt = self._statement()
                if stmt:
                    body.append(stmt)
            self._consume(TokenType.RIGHT_BRACE, "Expected '}' after for loop body.")
            return ForStatement(variable, iterable, body)
        finally:
            self._loop_depth -= 1

    def _break_statement(self):
        if self._loop_depth == 0:
            raise ParseError(self._previous(), "'break' can only be used inside a loop.")
        keyword = self._previous()
        # self._consume(TokenType.SEMICOLON, "Expected ';' after 'break'.")
        return BreakStatement(keyword)

    def _continue_statement(self):
        if self._loop_depth == 0:
            raise ParseError(self._previous(), "'continue' can only be used inside a loop.")
        keyword = self._previous()
        # self._consume(TokenType.SEMICOLON, "Expected ';' after 'continue'.")
        return ContinueStatement(keyword)

    
    def _return_statement(self):
        keyword = self._previous()
        
        if not self._check(TokenType.SEMICOLON) and not self._check(TokenType.RIGHT_BRACE):
            value = self._expression()
        else:
            value = None
        return ReturnStatement(keyword, value)

    def _let_statement(self):
        is_const = self._match(TokenType.CONST)
        name_token = self._consume(TokenType.IDENTIFIER, "Expected variable name after 'let'.")
        
        type_annotation = None
        if self._match(TokenType.AS):
            type_annotation = self._consume(TokenType.IDENTIFIER, "Expected type name (e.g., 'int', 'string') after 'as'.")

        if not self._match(TokenType.EQUAL):
            raise ParseError(self._peek(), "Expected '=' after variable name in a 'let' statement.")

        initializer = self._expression()
        return LetStatement(name_token, initializer, is_const, type_annotation)

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
        return self._assignment()
    
    def _assignment(self):
        expr = self._logic_or()

        if self._match(TokenType.EQUAL):
            equals = self._previous()
            value = self._assignment()
            
            if isinstance(expr, Variable):
                name = expr.name
                return Assignment(name, value)
            elif isinstance(expr, SubscriptGet):
                return SubscriptSet(expr.object, expr.index, value)
            else: 
                raise ParseError(equals, "Invalid assignment target.")
        return expr
    
    def _logic_or(self):
        expr = self._logic_and()
        while self._match(TokenType.OR):
            operator = self._previous()
            right = self._logic_and()
            expr = Logical(expr, operator, right)
        return expr

    def _logic_and(self):
        expr = self._equality()
        while self._match(TokenType.AND):
            operator = self._previous()
            right = self._equality()
            expr = Logical(expr, operator, right)
        return expr

    def _equality(self):
        expr = self._comparison()
        while self._match(TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL):
            operator = self._previous()
            right = self._comparison()
            expr = BinaryExpression(expr, operator, right)
        return expr

    def _comparison(self):
        expr = self._addition()
        while self._match(TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL):
            operator = self._previous()
            right = self._addition()
            expr = BinaryExpression(expr, operator, right)
        return expr
    
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
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator = self._previous()
            right = self._unary()
            return Unary(operator, right)
        return self._call()

    def _call(self):
        expr = self._primary()
        while True:
            if self._match(TokenType.LEFT_PAREN):
                expr = self._finish_call(expr)
            elif self._match(TokenType.DOT):
                name = self._consume(TokenType.IDENTIFIER, "Expect property name after '.'.")
                expr = Get(expr, name)
            elif self._match(TokenType.LEFT_BRACKET):
                index_expr = self._expression()
                closing_bracket = self._consume(TokenType.RIGHT_BRACKET, "Expect ']' after index.")
                expr = SubscriptGet(expr, index_expr, closing_bracket)
            else:
                break
        return expr

    def _primary(self):
        if self._match(TokenType.TRUE): return Literal(True)
        if self._match(TokenType.FALSE): return Literal(False)

        if self._match(TokenType.NUMBER, TokenType.STRING):
           return Literal(self._previous().literal)
    
        if self._match(TokenType.IDENTIFIER):
            return Variable(self._previous())

        if self._match(TokenType.LEFT_PAREN):
            expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return expr # Grouping expression

        if self._match(TokenType.LEFT_BRACKET):  
            elements = []
            if not self._check(TokenType.RIGHT_BRACKET):
                while True:
                    elements.append(self._expression())
                    if not self._match(TokenType.COMMA):
                        break
            self._consume(TokenType.RIGHT_BRACKET, "Expected ']' after list elements.")
            return ListLiteral(elements)  
    
        if self._match(TokenType.LEFT_BRACE):
            return self._map_literal()

        raise ParseError(self._peek(), "Expected an expression.")

    def _map_literal(self):
        pairs = []
        if not self._check(TokenType.RIGHT_BRACE):
            while True:
                key = self._expression()
                self._consume(TokenType.COLON, "Expected ':' after map key.")
                value = self._expression()
                pairs.append((key, value))
                if not self._match(TokenType.COMMA):
                    break
        self._consume(TokenType.RIGHT_BRACE, "Expected '}' after map entries.")
        return MapLiteral(pairs)

    def _finish_call(self, callee):
        arguments = []
        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                arguments.append(self._expression())
                if not self._match(TokenType.COMMA):
                    break
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after function arguments.")
        
        # The 'callee' is now an expression, not just an identifier token.
        return FunctionCall(callee, arguments)
                        


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
        raise ParseError(self._peek(), message)

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
