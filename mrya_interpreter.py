from mrya_ast import *
import builtins

class Environment:
    def __init__(self):
        self.variables = {}

    def define(self, name, value):
        self.variables[name] = value

    def get(self, name):
        if name in self.variables:
            return self.variables[name]
        raise RuntimeError(f"Mrya Error: The variable '{name}' is not defined")

class MryaInterpreter:
    def __init__(self):
        self.env = Environment()

    def interpret(self, statements):
        for stmt in statements:
            self._execute(stmt)

    def _execute(self, stmt):
        if isinstance(stmt, LetStatement):
            value = self._evaluate(stmt.initializer)
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
            raise RuntimeError(f"Mrya Error: The expression '{expr}' is not defined")