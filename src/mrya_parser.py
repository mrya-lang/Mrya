from mrya_tokens import TokenType, Token
from mrya_ast import Literal, HString, Splat, Variable, Get, LetStatement, OutputStatement, BinaryExpression, Logical, Unary, FunctionDeclaration, FunctionCall, ReturnStatement, IfStatement, WhileStatement, ForStatement, BreakStatement, ContinueStatement, TryStatement, CatchClause, ClassDeclaration, SetProperty, This, Inherit, Assignment, SubscriptGet, SubscriptSet, InputCall, ImportStatement, ListLiteral, MapLiteral

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
        # If the expression is a call to 'import', treat it as an ImportStatement.
        if isinstance(expr, FunctionCall) and isinstance(expr.callee, Variable) and expr.callee.name.lexeme == "import":
            if len(expr.arguments) != 1:
                raise ParseError(expr.callee.name, "import() expects exactly one argument (the file path).")
            return ImportStatement(expr.arguments[0])
        # Otherwise, if it's any other function call, wrap it in OutputStatement to print its result.
        elif isinstance(expr, FunctionCall):
            return OutputStatement(expr)
        return expr

    def _statement(self):
        decorators = []
        while self._match(TokenType.PERCENT):
            decorators.append(self._expression())

        if self._match(TokenType.LET):
            if decorators:
                raise ParseError(self._previous(), "Decorators can only be applied to functions and classes.")
            return self._let_statement()
        if self._match(TokenType.OUTPUT):
            if decorators:
                raise ParseError(self._previous(), "Decorators can only be applied to functions and classes.")
            return self._output_statement()
        if self._match(TokenType.FUNC):  
            return self._function_statement(decorators)
        if self._match(TokenType.RETURN):
            if decorators:
                raise ParseError(self._previous(), "Decorators can only be applied to functions and classes.")
            return self._return_statement()
        if self._match(TokenType.IF):
            if decorators:
                raise ParseError(self._previous(), "Decorators can only be applied to functions and classes.")
            return self._if_statement()
        if self._match(TokenType.FOR):
            return self._for_statement()
        if self._match(TokenType.WHILE):
            return self._while_statement()
        if self._match(TokenType.BREAK):
            return self._break_statement()
        if self._match(TokenType.CONTINUE):
            return self._continue_statement()
        if self._match(TokenType.TRY):
            return self._try_statement()
        if self._match(TokenType.CLASS):
            return self._class_declaration(decorators)
        
        expr_stmt = self._expression_statement()
        if decorators and not isinstance(expr_stmt, (FunctionDeclaration, ClassDeclaration)):
            raise ParseError(self._peek(), "Decorators can only be applied to functions and classes.")
        return expr_stmt
    
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

    def _try_statement(self):
        self._consume(TokenType.LEFT_BRACE, "Expected '{' after 'try'.")
        try_block = self._block()

        catch_clauses = []
        while self._match(TokenType.CATCH):
            error_type = None
            if self._check(TokenType.IDENTIFIER):
                error_type = self._advance()

            self._consume(TokenType.LEFT_BRACE, "Expected '{' after 'catch'.")
            catch_body = self._block()
            catch_clauses.append(CatchClause(error_type, catch_body))

        finally_block = None
        if self._match(TokenType.END):
            self._consume(TokenType.LEFT_BRACE, "Expected '{' after 'end'.")
            finally_block = self._block()

        if not catch_clauses and not finally_block:
            raise ParseError(self._previous(), "Expected 'catch' or 'end' after 'try' block.")

        return TryStatement(try_block, catch_clauses, finally_block)

    def _class_declaration(self, decorators):
        name = self._consume(TokenType.IDENTIFIER, "Expect class name.")

        superclass = None
        if self._match(TokenType.LESS):
            self._consume(TokenType.IDENTIFIER, "Expect superclass name.")
            superclass = Variable(self._previous())

        self._consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")

        methods = []
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            self._consume(TokenType.FUNC, "Expect 'func' to define a method.")
            methods.append(self._function_statement(is_method=True))

        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")
        return ClassDeclaration(name, superclass, methods, decorators)

    def _block(self):
        """Helper to parse a block of statements inside braces."""
        statements = []
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            stmt = self._statement()
            if stmt:
                statements.append(stmt)
        self._consume(TokenType.RIGHT_BRACE, "Expected '}' after block.")
        return statements


    
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
        # self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'output'.")
        expr = self._expression()
        # self._consume(TokenType.RIGHT_PAREN, "Expected ')' after output expression.")
        return OutputStatement(expr)

    
    def _function_statement(self, decorators=None, is_method=False):
        if self._peek().type in [TokenType.THIS, TokenType.INHERIT]:
            token = self._peek()
            raise ParseError(token, f"Cannot use reserved keyword '{token.lexeme}' as a function name.")
        name_token = self._consume(TokenType.IDENTIFIER, "Expected function name after 'func'.")

        self._consume(TokenType.EQUAL, "Expected '=' after function name.")
        self._consume(TokenType.DEFINE, "Expected 'define' after '=' in function declaration.")
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'define'.")

        parameters = []
        is_variadic = False
        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                if self._match(TokenType.ELLIPSIS):
                    if is_variadic: # Should not happen if we break
                        raise ParseError(self._previous(), "Cannot have multiple variadic '...' parameters.")
                    parameters.append(self._consume(TokenType.IDENTIFIER, "Expected parameter name after '...'.") )
                    is_variadic = True
                    break # Variadic parameter must be the last one

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
        return FunctionDeclaration(name_token, parameters, body, decorators, is_variadic)
    
    # --- Expressions ---
    def _expression(self):
        return self._assignment()
    
    def _assignment(self):
        expr = self._logic_or()

        if self._match(TokenType.EQUAL, TokenType.PLUS_EQUAL, TokenType.MINUS_EQUAL, TokenType.STAR_EQUAL, TokenType.SLASH_EQUAL):
            operator_token = self._previous()
            right_value = self._assignment()

            if isinstance(expr, Variable):
                name = expr.name
                # If it's a compound assignment, transform it.
                if operator_token.type != TokenType.EQUAL:
                    # Map compound token to binary operator token
                    op_map = {
                        TokenType.PLUS_EQUAL: TokenType.PLUS,
                        TokenType.MINUS_EQUAL: TokenType.MINUS,
                        TokenType.STAR_EQUAL: TokenType.STAR,
                        TokenType.SLASH_EQUAL: TokenType.SLASH,
                    }
                    binary_op_token = Token(op_map[operator_token.type], operator_token.lexeme[:-1], None, operator_token.line)
                    # Create `x = x + value`
                    new_value = BinaryExpression(expr, binary_op_token, right_value)
                    return Assignment(name, new_value)
                else:
                    # It's a simple assignment: x = value
                    return Assignment(name, right_value)

            elif isinstance(expr, SubscriptGet):
                if operator_token.type != TokenType.EQUAL:
                    op_map = { TokenType.PLUS_EQUAL: TokenType.PLUS, TokenType.MINUS_EQUAL: TokenType.MINUS, TokenType.STAR_EQUAL: TokenType.STAR, TokenType.SLASH_EQUAL: TokenType.SLASH }
                    binary_op_token = Token(op_map[operator_token.type], operator_token.lexeme[:-1], None, operator_token.line)
                    new_value = BinaryExpression(expr, binary_op_token, right_value)
                    return SubscriptSet(expr.object, expr.index, new_value)
                else:
                    return SubscriptSet(expr.object, expr.index, right_value)

            elif isinstance(expr, Get):
                if operator_token.type != TokenType.EQUAL:
                    op_map = {
                        TokenType.PLUS_EQUAL: TokenType.PLUS,
                        TokenType.MINUS_EQUAL: TokenType.MINUS,
                        TokenType.STAR_EQUAL: TokenType.STAR,
                        TokenType.SLASH_EQUAL: TokenType.SLASH,
                    }
                    binary_op_token = Token(op_map[operator_token.type], operator_token.lexeme[:-1], None, operator_token.line)
                    new_value = BinaryExpression(expr, binary_op_token, right_value)
                    return SetProperty(expr.object, expr.name, new_value)
                else:
                    return SetProperty(expr.object, expr.name, right_value)
            else: 
                raise ParseError(operator_token, "Invalid assignment target.")
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
        if self._match(TokenType.NIL): return Literal(None)

        if self._match(TokenType.THIS):
            return This(self._previous())

        if self._match(TokenType.INHERIT):
            keyword = self._previous()
            self._consume(TokenType.DOT, "Expect '.' after 'inherit'.")
            method = self._consume(TokenType.IDENTIFIER, "Expect superclass method name.")
            return Inherit(keyword, method)

        if self._match(TokenType.NUMBER, TokenType.STRING):
           return Literal(self._previous().literal)
    
        if self._match(TokenType.H_STRING):
            return self._parse_h_string(self._previous())

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
                if self._match(TokenType.ELLIPSIS):
                    # A splat argument is usually the last one.
                    arguments.append(Splat(self._expression())) 
                    if not self._match(TokenType.COMMA):
                        break # Exit loop if no comma follows the splat.
                arguments.append(self._expression())
                if not self._match(TokenType.COMMA):
                    break
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after function arguments.")

        # The 'callee' is now an expression, not just an identifier token.
        return FunctionCall(callee, arguments)
                        
    def _parse_h_string(self, h_string_token):
        """
        Parses the content of a H_STRING token into a list of literals and expressions.
        This is a mini-parser that operates on the string content.
        """
        content = h_string_token.literal
        parts = []
        last_index = 0
        current_index = 0

        while current_index < len(content):
            if content[current_index] == '<':
                # Add the preceding literal part
                if current_index > last_index:
                    parts.append(Literal(content[last_index:current_index]))
                
                # Find the closing '>'
                start_expr = current_index + 1
                end_expr = content.find('>', start_expr)
                if end_expr == -1:
                    raise ParseError(h_string_token, "Unterminated expression in h-string.")
                
                expr_content = content[start_expr:end_expr]
                
                # Re-tokenize and re-parse the expression
                from mrya_lexer import MryaLexer
                expr_tokens = MryaLexer(expr_content).scan_tokens()
                expr_node = MryaParser(expr_tokens)._expression()
                parts.append(expr_node)
                
                current_index = end_expr + 1
                last_index = current_index
            else:
                current_index += 1
        
        # Add any remaining literal part
        if last_index < len(content):
            parts.append(Literal(content[last_index:]))
            
        return HString(parts)


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
