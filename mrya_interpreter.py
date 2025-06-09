from mrya_ast import *
from mrya_errors import MryaRuntimeError

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

    def _execute(self, stmt):
        if isinstance(stmt, LetStatement):
            value = self._evaluate(stmt.initializer)
            # stmt.name should be a Token object now
            self.env.define(stmt.name, value)
        elif isinstance(stmt, OutputStatement):
            value = self._evaluate(stmt.expression)
            print(value)
        else:
            raise RuntimeError(f"Mrya Error: The statement '{stmt}' is not defined")

    def _evaluate(self, expr):
        if isinstance(expr, Literal):
            return expr.value
        elif isinstance(expr, Variable):
            # expr.name is a Token, so we pass it to env.get()
            return self.env.get(expr.name)
        elif isinstance(expr, BinaryExpression):
            left = self._evaluate(expr.left)
            right = self._evaluate(expr.right)
            if expr.operator == '+':
                return left + right
            elif expr.operator == '-':
                return left - right
            elif expr.operator == '*':
                return left * right
            elif expr.operator == '/':
                return left / right
            else:
                raise RuntimeError(f"Unsupported operator '{expr.operator}'")
        else:
            raise RuntimeError(f"Mrya Error: The expression '{expr}' is not defined")
