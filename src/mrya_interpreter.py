from mrya_ast import Expr, Literal, Variable, BinaryExpression, LetStatement, OutputStatement, FunctionDeclaration, FunctionCall, ReturnStatement, IfStatement, WhileStatement, Assignment, InputCall, ImportStatement, ListLiteral
from mrya_errors import MryaRuntimeError, MryaTypeError
from modules.math_equations import evaluate_binary_expression
from modules.file_io import fetch, store, append_to
from mrya_tokens import TokenType  
import os
from mrya_lexer import MryaLexer
from mrya_parser import MryaParser
from modules import arrays as arrays
from modules import maps as maps
from modules import math_utils as math_utils

class Environment:
    def __init__(self, enclosing=None):
        self.values = {}
        self.types = {} # Store type annotations
        self.functions = {}
        self.enclosing = enclosing
    
    def define_variable(self, name_token, value):
        self.values[name_token.lexeme] = value
    
    def define_typed_variable(self, name_token, value, type_token):
        self.values[name_token.lexeme] = value
        self.types[name_token.lexeme] = type_token.lexeme

    def get_type(self, name):
        if name in self.types:
            return self.types[name]
        if self.enclosing:
            return self.enclosing.get_type(name)
        return None
        
    def define_function(self, name_token, func_decl):
        self.functions[name_token.lexeme] = func_decl
        
    def get_variable(self, name_token):
        name = name_token.lexeme
        if name in self.values:
            return self.values[name]
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
    
    def assign(self, name_token, value):
        name = name_token.lexeme
        if name in self.values:
            # Check type before assigning
            expected_type = self.get_type(name)
            if expected_type:
                MryaInterpreter._check_type(expected_type, value, name_token)
            self.values[name] = value
        elif self.enclosing:
            self.enclosing.assign(name_token, value)
        else:
            raise MryaRuntimeError(name_token, f"Cannot assign to undefined variable '{name}'.")
    
     

class MryaInterpreter:
    def __init__(self):
        self.env = Environment()
        # Built in functions:
        self.builtins = {
            "to_int": self._builtin_to_int,
            "to_float": self._builtin_to_float,
            "to_bool": self._builtin_to_bool,
            "request": self._builtin_request,
            "fetch": fetch,
            "store": store,
            "append_to": append_to,
            "import": self._builtin_import,
            # List commands
            "list": arrays.create,
            "get": arrays.get,
            "set": arrays.set,
            "append": arrays.push,   
            "length": arrays.size,    
            "list_slice": arrays.slice,
            # Map commands
            "map": maps.create_map,
            "map_get": maps.get_key,
            "map_set": maps.set_key,
            "map_has": maps.has_key,
            "map_keys": maps.keys,
            "map_values": maps.values,
            "map_delete": maps.delete_key,
            # Math commands
            "abs": math_utils.absfn,
            "round": math_utils.roundfn,
            "up": math_utils.up,
            "down": math_utils.down,
            "root": math_utils.root,
            "random": math_utils.randomf,
            "randint": math_utils.randint,
            
             
}
        self.env.functions = {}
        self.imported_files = set()
    
    def interpret(self, statements):
        for stmt in statements:
            self._execute(stmt)
    
    def _execute(self, stmt):
        if isinstance(stmt, LetStatement):
            value = self._evaluate(stmt.initializer)
            if stmt.type_annotation:
                # Coerce numbers to strings if the type annotation is 'string'
                if stmt.type_annotation.lexeme == "string" and isinstance(value, (int, float)):
                    value = str(value)

                # Perform type check before defining
                self._check_type(stmt.type_annotation.lexeme, value, stmt.type_annotation)
                self.env.define_typed_variable(stmt.name, value, stmt.type_annotation)
            else:
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
                for inner_stmt in stmt.body:
                    self._execute(inner_stmt)


        elif isinstance(stmt, Assignment):
            value = self._evaluate(stmt.value)
            self.env.assign(stmt.name, value)
             
        elif isinstance(stmt, ImportStatement):
            path = self._evaluate(stmt.path_expr)
            if not isinstance(path, str):
                raise RuntimeError("Import path must be a string.")
            
            abs_path = os.path.abspath(path)
            if abs_path in self.imported_files:
                return
            
            self.imported_files.add(abs_path)

            from mrya_lexer import MryaLexer
            from mrya_parser import MryaParser

            try:
                with open(abs_path, "r", encoding="utf-8") as f:
                    source_code = f.read()
            except Exception as e:
                raise RuntimeError(f"Failed to import '{path}': {e}")
            
            tokens = MryaLexer(source_code).scan_tokens()
            imported_statements = MryaParser(tokens).parse()
            for s in imported_statements:
                self._execute(s)

        else:
            raise RuntimeError(f"Unknown statement type: {type(stmt).__name__}")
        
    def _builtin_import(self, filepath):
        if not isinstance(filepath, str):
            raise RuntimeError("import() requires a file path as a string.")
        
        if not filepath.endswith(".mrya"):
            filepath += ".mrya"
        
        if not os.path.exists(filepath):
            raise RuntimeError(f"Import failed: '{filepath}' not found.")
        
        with open(filepath, "r", encoding="utf-8") as f:
                  source = f.read()
        
        lexer = MryaLexer(source)
        tokens = lexer.scan_tokens()
        parser = MryaParser(tokens)
        statements = parser.parse()

        prev_env = self.env
        try:
            self.env = Environment(enclosing=prev_env)
            for stmt in statements:
                self._execute(stmt)
        finally:
            self.env = prev_env
        return None
                  

    
    def _call_function(self, call):
        name = call.name.lexeme
        if name in self.builtins:
            args = [self._evaluate(arg) for arg in call.arguments]
            return self.builtins[name](*args)
        
        if name not in self.env.functions:
            raise RuntimeError(f"Mrya Error: Function '{name}' is not defined.")
        
        
        declaration = self.env.functions[name]
        
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
    
    def _builtin_to_int(self, value):
        try:
            return int(value)
        except ValueError:
            raise RuntimeError(f"Cannot convert '{value}' to int.")
    
    def _builtin_to_float(self, value):
        try:
            return float(value)
        except ValueError:
            raise RuntimeError(f"Cannot convert '{value}' to float.")
    
    def _builtin_to_bool(self, value):
        if isinstance(value, str):
            val_lower = value.strip().lower()
            if val_lower in ("true", "yes", "1"):
                return True
            elif val_lower in ("false", "no", "0"):
                return False
            else:
                raise RuntimeError(f"Cannot convert '{value}' to bool.")
        return bool(value)
    
    def _builtin_request(self, prompt, validation_type=None, default=None):
        while True:
            user_input = input(str(prompt) + " ")

            if default is not None and user_input.strip() == "":
                return default
            
            if validation_type is None or validation_type == "string":
                return user_input
            
            elif validation_type == "number":
                try:
                    if '.' in user_input:
                        return float(user_input)
                    else: 
                        return int(user_input)
                except ValueError:
                    print("Invalid number, please try again.")
            
            elif validation_type == "bool":
                val = user_input.strip().lower()
                if val in ("true", "yes", "1"):
                    return True
                elif val in ("false", "no", "0"):
                    return False
                else:
                    print("Invalid boolean, please enter yes/no, true/false, or 1/0.")
            
            else:
                print(f"Unknown validation type '{validation_type}'. Please try again.")
                    
            

    def _evaluate(self, expr):
        if isinstance(expr, Literal):
            return expr.value
        
        elif isinstance(expr, Variable):
            return self.env.get_variable(expr.name)
        
        elif isinstance(expr, InputCall):
            prompt = self._evaluate(expr.prompt)
            return input(str(prompt))
        
        elif isinstance(expr, ListLiteral):
            return [self._evaluate(element) for element in expr.elements]
        
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

                    
            
        



