from mrya_tokens import TokenType
from mrya_ast import Literal, Variable, Assign, Call

class ParseError(Exception):
    pass

class MryaParser:
    def __init__(self,tokens):
        self.tokens - tokens
        self.current = 0
    
    def parse(self):
        statements = []
        while not self._is_at_end():
            stmt = self._statement()
            if stmt:
                statements.append(stmt)
        return statements
    
    def _statement(self):
        if self_match(TokenType.LET):
            return self._variable_declaration()
        if self._match(TokenType.OUTPUT):
            return self._print_statement()
        return None
    
    def _var_decleration(self):
        name = self._consume(TokenType.IDENTIFIER, "Expect variable name.")
        self._consume(TokenType.EQUAL, "Expect '=' after variable name.")
        value = self._expression()
        return Assign(name, value)
    
    def _print_statement(self):
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'output'.")
        value = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after value.")
        return Call("Output", [value])
    
    def _expression(self):
        if self._check(TokenType.STRING):
            return Literal(self._advance().literal)
        elif self._check(TokenType.NUMBER):
            return Literal(self._advance().literal)
        elif self._check(TokenType.IDENTIFIER):
            return Variable(self._advance())
        raise ParseError("Unsupported expression")
    
    #Utilities
    
    