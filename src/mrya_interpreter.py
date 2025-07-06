from mrya_ast import Expr, Literal, Variable, BinaryExpression, LetStatement, OutputStatement, FunctionDeclaration, FunctionCall, ReturnStatement, IfStatement, WhileStatement
from mrya_errors import MryaRuntimeError
from modules.math_equations import evaluate_binary_expression
from mrya_tokens import TokenType  

class Environment:
    def __init__(self, enclosing=None):
        self.variables = {}
        self.functions = {}
        self.enclosing = enclosing
    
    def define_variable(self, name_token, value):
        self.variables[name_token.lexeme] = value
        
    def define_function(self, name_token, func_decl):
        self.functions[name_token.lexeme] = func_decl
        
    def get_variable(self, name_token):
        name = name_token.lexeme
        if name in self.variables:
            return self.variables[name]
        if self.enclosing:
            return self.enclosing.get_variable(name_token)
        raise MryaRuntimeError(name_token, f"Variable '{name}' is not defined.")
    
    def get_function(self, name_token):
        name =  name_token.lexeme
        if name in self.functions:
            return self.functions[name]
        if self.enclosing:
            return self.enclosing.get_function(name_token)
        raise MryaRuntimeError(name_token, f"Function '{name}' is not defined.")
    
     

class MryaInterpreter:
    def __init__(self):
        self.env = Environment()
    
    def interpret(self, statements):
        for stmt in statements:
            self._execute(stmt)
    
    def _execute(self, stmt):
        if isinstance(stmt, LetStatement):
            value = self._evaluate(stmt.initializer)
            self.env.define_variable(stmt.name, value)
            
        elif isinstance(stmt, OutputStatement):
            value = self._evaluate(stmt.expression)
            print(value)
        
        elif isinstance(stmt, FunctionDeclaration):
            self.env.define_function(stmt.name, stmt)
        
        elif isinstance(stmt, ReturnStatement):
            value = self._evaluate(stmt.value) if stmt.value is not None else None
            raise ReturnValue(value)
        
        elif isinstance(stmt, Expr):
            self._evaluate(stmt)
        
        elif isinstance(stmt, IfStatement):
            condition = self._evaluate(stmt.condition)
            if condition:
                for s in stmt.then_branch:
                    self._execute(s)
            elif stmt.else_branch:
                for s in stmt.else_branch:
                    self._execute(s)
        
        elif isinstance(stmt, WhileStatement):
            while self._evaluate(stmt.condition):
                for s in stmt.body:
                    self._execute(s)
            
        
        else:
            raise RuntimeError(f"Unknown statement type: {type(stmt).__name__}")
    
    def _call_function(self, call):
        declaration = self.env.get_function(call.name)
        
        if len(call.arguments) != len(declaration.params):
            raise RuntimeError(f"Function '{call.name.lexeme}' expects {len(declaration.params)} arguments, got {len(call.arguments)}.")
        
        call_env = Environment(enclosing=self.env)
        
        for param_token, arg_expr in zip(declaration.params, call.arguments):
            arg_value = self._evaluate(arg_expr)
            call_env.define_variable(param_token, arg_value)
            
        previous_env = self.env
        self.env = call_env
        
        try:
            for stmt in declaration.body:
                self._execute(stmt)
        except ReturnValue as return_value:
            self.env = previous_env
            return return_value.value
        
        self.env = previous_env
        return None
            

    def _evaluate(self, expr):
        if isinstance(expr, Literal):
            return expr.value
        
        elif isinstance(expr, Variable):
            return self.env.get_variable(expr.name)
        
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
                        raise MryaRuntimeError(expr.operator, "Division by zero.")
                    return left / right
                elif op == TokenType.GREATER:
                    return left > right
                elif op == TokenType.LESS:
                    return left < right
                elif op == TokenType.GREATER_EQUAL:
                    return left >= right
                elif op == TokenType.LESS_EQUAL:
                    return left <= right
                else:
                    raise MryaRuntimeError(expr.operator, f"Unsupported operator: {expr.operator.lexeme}")
            except TypeError:
                raise MryaRuntimeError(expr.operator, f"Invalid operands for {expr.operator.lexeme}: {left}, {right}")
        
        elif isinstance(expr, FunctionCall):
            return self._call_function(expr)
        
        else:
            raise RuntimeError(f"Unsupported expression type; {type(expr).__name__}")

class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value
                    
            
        



