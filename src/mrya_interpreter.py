from mrya_ast import Literal, Variable, BinaryExpression, LetStatement, OutputStatement, FunctionDeclaration, FunctionCall
from mrya_errors import MryaRuntimeError
from modules.math_equations import evaluate_binary_expression
from mrya_tokens import TokenType  

class Environment:
    def __init__(self):
        self.variables = {}
        self.functions = {}

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
            self.env.define(stmt.name, value)
        elif isinstance(stmt, OutputStatement):
            value = self._evaluate(stmt.expression)
            print(value)
        elif isinstance(stmt, FunctionDeclaration):
            self.functions[stmt.name.lexeme] = stmt
        else:
            # Log what statement type is being processed for debugging
            print(f"Debug: Unknown statement type: {type(stmt).__name__}")
            raise RuntimeError("Mrya Error: The expression is not defined")
    
    def _call_function(self, call):
        name = call.name.lexeme
        if name not in self.functions:
            raise RuntimeError(f"Mrya Error: Function '{name}' is not defined.")
        
        declaration = self.functions[name]
        
        if len(call.arguments) != len(declaration.params):
            raise RuntimeError(f"Mrya Error: Function '{name}' expects {len(declaration.params)} arguments, but got {len(call.arguments)}.")
        
        previous_env = self.environment.copy()
        self.environment = {}
        
        for i in range(len(call.arguments)):
            param_name = declaration.params[i].lexeme
            arg_value = self._evaluate(call.arguments[i])
            self.environment[param_name] = arg_value
        
        for stmt in declaration.body:
            self._execute(stmt)
        
        self.environment = previous_env

    def _evaluate(self, expr):
        if isinstance(expr, Literal):
            return expr.value

        elif isinstance(expr, Variable):
            return self.env.get(expr.name)

        elif isinstance(expr, BinaryExpression):
            left = self._evaluate(expr.left)
            right = self._evaluate(expr.right)
            operator = expr.operator.type

            try:
                if operator == TokenType.PLUS:
                    return left + right
                elif operator == TokenType.MINUS:
                    return left - right
                elif operator == TokenType.STAR:
                    return left * right
                elif operator == TokenType.SLASH:
                    if right == 0:
                        raise MryaRuntimeError(expr.operator, "Division by zero is not allowed.")
                    return left / right
                else:
                    raise MryaRuntimeError(expr.operator, f"Unsupported operator: {expr.operator.lexeme}")
            except TypeError:
                raise MryaRuntimeError(expr.operator, f"Invalid operands for {expr.operator.lexeme}: {left}, {right}")
        elif isinstance(expr, FunctionCall):
            return self._call_function(expr)
        else:
            raise RuntimeError(f"Mrya Error: The expression is not defined")


