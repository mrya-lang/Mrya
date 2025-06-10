from mrya_ast import *
from mrya_errors import MryaRuntimeError
from modules.math_equations import evaluate_binary_expression
from mrya_tokens import TokenType  

class Environment:
    def __init__(self):
        self.variables = {}

    def define(self, name_token, value):
        # name_token is a Token object
        self.variables[name_token.lexeme] = value

    def get(self, name_token):
        # name_token is a Token object; use lexeme as key
        name = name_token.lexeme
        if name in self.variables:
            return self.variables[name]
        # Raise runtime error with token info for better error reporting
        raise MryaRuntimeError(name_token, f"Variable '{name}' is not defined.")

class MryaInterpreter:
    def __init__(self):
        self.env = Environment()

    def interpret(self, statements):
        for stmt in statements:
            self._execute(stmt)

    def _execute(self, expr):
        if isinstance(expr, Literal):
            return expr.value
        elif isinstance(expr, Variable):
            return self.env.get(expr.name)
        elif isinstance(expr, BinaryExpression):
            left = self._evaluate(expr.left)
            right = self._evaluate(expr.right)
            try:
                return evaluate_binary_expression(left, expr.operator.lexeme, right)
            except RuntimeError as e:
                raise MryaRuntimeError(expr.operator, str(e))
        else:
            raise RuntimeError(f"Mrya Error: The expression is not defined")
        
    def _evaluate(self, expr):
        if isinstance(expr, Literal):
            return expr.value
        elif isinstance(expr, Variable):
            # expr.name is a Token, so we pass it to env.get()
            return self.env.get(expr.name)
        elif isinstance(expr, BinaryExpression):
            left = self._evaluate(expr.left)
            right = self._evaluate(expr.right)
            op = expr.operator.type
            try:
            
                if op == TokenType.PLUS:
                    return left + right
                elif op == TokenType.MINUS:
                    return left - right
                elif op == TokenType.STAR:
                    return left * right
                elif op == TokenType.SLASH:
                    if right == 0:
                        raise MryaRuntimeError(expr.operator, "Division by zero is not allowed.")
                    return left / right
                else:
                    raise MryaRuntimeError(expr.operator, f"Mrya Error: Unknown operator '{op}' in expression '{expr}'")
            except TypeError:
                raise MryaRuntimeError(expr.operator, f"Mrya Error: Incompatible operatnds for '{expr.operator.lexeme}': {left} and {right}")
