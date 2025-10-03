from mrya_ast import Expr, Literal, Variable, Get, BinaryExpression, Logical, LetStatement, OutputStatement, FunctionDeclaration, FunctionCall, ReturnStatement, IfStatement, WhileStatement, ForStatement, BreakStatement, ContinueStatement, Assignment, SubscriptGet, SubscriptSet, InputCall, ImportStatement, ListLiteral, MapLiteral
from mrya_errors import MryaRuntimeError, MryaTypeError
from modules.math_equations import evaluate_binary_expression
from modules.file_io import fetch, store, append_to
from mrya_tokens import TokenType  
import os
from modules import arrays as arrays
from modules import maps as maps
from modules import math_utils as math_utils
from modules import time as time_module

class MryaModule:
    """A simple class to represent a Mrya module with methods."""
    def __init__(self, name):
        self.name = name
        self.methods = {}

    def get(self, name_token):
        if name_token.lexeme in self.methods:
            return self.methods[name_token.lexeme]
        raise MryaRuntimeError(name_token, f"Module '{self.name}' has no attribute '{name_token.lexeme}'.")

class MryaBox:
    """A mutable box to hold a variable's value, enabling reference semantics."""
    def __init__(self, value, is_const=False):
        self.value = value
        self.is_const = is_const

class Environment:
    def __init__(self, enclosing=None):
        self.values = {}
        self.types = {} # Store type annotations
        self.constants = set() # Store names of constant variables
        self.functions = {}
        self.enclosing = enclosing
    
    def define_variable(self, name, value):
        # This method now expects 'value' to be a MryaBox
        if isinstance(name, str):
            self.values[name] = value
        else: # It's a Token
            self.values[name.lexeme] = value
    
    def define_typed_variable(self, name_token, value, type_token):
        # This method also expects 'value' to be a MryaBox
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
            return self.values[name].value
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
            box = self.values[name]
            if box.is_const:
                raise MryaRuntimeError(name_token, f"Cannot assign to constant variable '{name}'.")
            expected_type = self.get_type(name)
            if expected_type:
                MryaInterpreter._check_type(expected_type, value, name_token)
            box.value = value
        elif self.enclosing:
            self.enclosing.assign(name_token, value)
        else:
            raise MryaRuntimeError(name_token, f"Cannot assign to undefined variable '{name}'.")

class MryaInterpreter:
    def __init__(self):
        self.env = Environment()

        # Native Modules
        time_mod = MryaModule("time")
        time_mod.methods = {
            "sleep": time_module.sleep,
            "time": time_module.time,
            "datetime": time_module.datetime_now,
        }

        string_mod = MryaModule("string")
        string_mod.methods = {
            "upper": lambda s: str(s).upper(),
            "lower": lambda s: str(s).lower(),
            "trim": lambda s: str(s).strip(),
            "replace": lambda s, old, new: str(s).replace(str(old), str(new)),
        }

        builtins = {
            "to_int": self._builtin_to_int,
            "to_float": self._builtin_to_float,
            "to_bool": self._builtin_to_bool,
            "request": self._builtin_request,
            "fetch": fetch,
            "store": store,
            "append_to": append_to, 
            "import": self._builtin_import,
            "length": self._builtin_length,
            # List commands
            "list": arrays.create,
            "get": arrays.get,
            "set": arrays.set,
            "append": arrays.push,
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
        for name, fn in builtins.items():
            self.env.define_variable(name, fn)

        self.native_modules = {
            "time": time_mod,
            "string": string_mod,
}
        self.imported_files = set()
    
    def interpret(self, statements):
        for stmt in statements:
            self._execute(stmt)
    
    def _execute(self, stmt):
        if isinstance(stmt, LetStatement):
            if stmt.is_const:
                # For const, we always want the final value, not a reference.
                # So we evaluate with unbox=True to get the raw value.
                value = self._evaluate(stmt.initializer, unbox=True)
                # Then we create a new, constant box for it.
                box = MryaBox(value, is_const=True)
            else:
                # For non-const, we want reference semantics.
                init_value = self._evaluate(stmt.initializer, unbox=False)
                # If the initializer was another variable, we get its box.
                # Otherwise, we create a new non-constant box.
                box = init_value if isinstance(init_value, MryaBox) else MryaBox(init_value, is_const=False)

            if stmt.type_annotation:
                self._check_type(stmt.type_annotation.lexeme, box.value, stmt.type_annotation)
                self.env.define_typed_variable(stmt.name, box, stmt.type_annotation)
            else:
                self.env.define_variable(stmt.name, box)
            
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
            try:
                while self._evaluate(stmt.condition):
                    try:
                        for inner_stmt in stmt.body:
                            self._execute(inner_stmt)
                    except ContinueInterrupt:
                        continue # Python's continue, to continue the while loop
            except BreakInterrupt:
                pass # Exit the loop
        
        elif isinstance(stmt, ForStatement):
            iterable = self._evaluate(stmt.iterable)
            if not isinstance(iterable, (list, str)):
                raise MryaRuntimeError(stmt.variable, "For loop can only iterate over lists and strings.")

            try:
                for item in iterable:
                    try:
                        # Create a new environment for each iteration to properly scope the loop variable
                        loop_env = Environment(enclosing=self.env)
                        loop_env.define_variable(stmt.variable, item)
                        
                        # Execute the body in the new environment
                        self._execute_block(stmt.body, loop_env)
                    except ContinueInterrupt:
                        continue # Python's continue, to continue the for loop
            except BreakInterrupt:
                pass # Exit the loop

        elif isinstance(stmt, BreakStatement):
            raise BreakInterrupt()
        elif isinstance(stmt, ContinueStatement):
            raise ContinueInterrupt()



        elif isinstance(stmt, Assignment):
            value = self._evaluate(stmt.value)
            self.env.assign(stmt.name, value)

        elif isinstance(stmt, SubscriptSet):
            obj = self._evaluate(stmt.object)
            index = self._evaluate(stmt.index)
            value = self._evaluate(stmt.value)

            if isinstance(obj, list):
                if not isinstance(index, int):
                    raise MryaRuntimeError(stmt.index.name if hasattr(stmt.index, 'name') else stmt.object.name, "List index must be an integer.")
                try:
                    obj[index] = value
                except IndexError:
                    raise MryaRuntimeError(stmt.index.name if hasattr(stmt.index, 'name') else stmt.object.name, f"List index {index} out of range.")
            elif isinstance(obj, dict):
                # In Mrya, map keys can be strings or numbers
                if not isinstance(index, (str, int, float)):
                     raise MryaRuntimeError(stmt.index.name if hasattr(stmt.index, 'name') else stmt.object.name, "Map keys must be strings or numbers.")
                obj[index] = value
            else:
                raise MryaRuntimeError(stmt.object.name, "Can only set items on lists and maps.")
             
        elif isinstance(stmt, ImportStatement):
            path = self._evaluate(stmt.path_expr)
            if not isinstance(path, str):
                raise RuntimeError("Import path must be a string.")
            
            abs_path = os.path.abspath(path)
            if abs_path in self.imported_files:
                return
            
            try:
                with open(abs_path, "r", encoding="utf-8") as f:
                    source_code = f.read()
            except Exception as e:
                raise RuntimeError(f"Failed to import '{path}': {e}")
            
            self.imported_files.add(abs_path)

            from mrya_lexer import MryaLexer
            from mrya_parser import MryaParser
            tokens = MryaLexer(source_code).scan_tokens()
            imported_statements = MryaParser(tokens).parse()

            # Execute in a new environment to prevent scope pollution
            self._execute_block(imported_statements, Environment(enclosing=self.env))

        else:
            raise RuntimeError(f"Unknown statement type: {type(stmt).__name__}")
        
    def _builtin_import(self, filepath):
        if not isinstance(filepath, str):
            raise RuntimeError("import() requires a file path as a string.")
        
        # Check for native modules first
        if filepath in self.native_modules:
            return self.native_modules[filepath]

        # Fallback to file-based import
        if not filepath.endswith(".mrya"):
            filepath += ".mrya"
        
        if not os.path.exists(filepath):
            raise RuntimeError(f"Import failed: '{filepath}' not found.")
        
        with open(filepath, "r", encoding="utf-8") as f:
                  source = f.read()
        
        from mrya_lexer import MryaLexer
        from mrya_parser import MryaParser
        lexer = MryaLexer(source)
        tokens = lexer.scan_tokens()
        parser = MryaParser(tokens)
        statements = parser.parse()

        # Create a new module-like object to return
        module_env = Environment(enclosing=self.env)
        self._execute_block(statements, module_env)
        
        module_obj = MryaModule(os.path.basename(filepath))
        module_obj.methods = {**module_env.values, **module_env.functions}
        return module_obj

    def _call_function(self, call):
        callee = self._evaluate(call.callee)

        if isinstance(callee, FunctionDeclaration):
            declaration = callee
            args = [self._evaluate(arg) for arg in call.arguments]
            if len(args) != len(declaration.params):
                raise MryaRuntimeError(call.callee.name, f"Function '{declaration.name.lexeme}' expects {len(declaration.params)} arguments, but got {len(args)}.") # This might fail if callee is not a simple variable
        elif callable(callee): # For built-ins and native module methods
            try:
                args = [self._evaluate(arg) for arg in call.arguments]
                return callee(*args)
            except TypeError as e:
                # When a built-in is called with the wrong number of arguments, it raises a TypeError.
                # We catch it and raise a Mrya-native error that the REPL can handle.
                callee_token = call.callee.name if isinstance(call.callee, Variable) else call.callee
                raise MryaRuntimeError(callee_token, f"Error calling built-in function: {e}")
            except Exception as e:
                callee_token = call.callee.name if isinstance(call.callee, Variable) else call.callee
                raise MryaRuntimeError(callee_token, f"Error inside built-in function: {e}")
        else:
            raise RuntimeError("Can only call functions and methods.")
        
        call_env = Environment(enclosing=self.env)
        for param_token, arg_expr in zip(declaration.params, call.arguments):
            arg_value = self._evaluate(arg_expr)
            call_env.define_variable(param_token, arg_value)
            
        try:
            self._execute_block(declaration.body, call_env)
        except ReturnValue as return_value:
            return return_value.value
        
        return None
    
    def _execute_block(self, statements, environment):
        previous_env = self.env
        try:
            self.env = environment
            for statement in statements:
                self._execute(statement)
        finally:
            self.env = previous_env

    @staticmethod
    def _check_type(expected_type, value, token):
        type_map = {
            "int": int,
            "float": float,
            "string": str,
            "bool": bool,
            "list": list,
            "map": dict
        }
        mrya_type = next((t for t, py_t in type_map.items() if isinstance(value, py_t)), None)

        if expected_type not in type_map or mrya_type != expected_type:
            actual_type = mrya_type or type(value).__name__
            raise MryaTypeError(token, f"Type mismatch for '{token.lexeme}'. Expected '{expected_type}', but got value of type '{actual_type}'.")

    def _builtin_length(self, collection):
        if isinstance(collection, (str, list, dict)):
            return len(collection)
        else:
            # We need a token for error reporting. This is a limitation of built-ins.
            raise RuntimeError(f"Cannot get length of type '{type(collection).__name__}'.")

    def _builtin_to_int(self, value):
        try:
            # First convert to float to handle "123.45", then to int to truncate.
            return int(float(value))
        except (ValueError, TypeError):
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
                if val in ("true", "yes", "1", "y"):
                    return True
                elif val in ("false", "no", "0", "n"):
                    return False
                else:
                    print("Invalid boolean, please enter yes/no, true/false, or 1/0.")
            else:
                print(f"Unknown validation type '{validation_type}'. Please try again.")
                    
            
    def _evaluate(self, expr, unbox=True):
        if isinstance(expr, Literal):
            return expr.value
        
        elif isinstance(expr, Variable):
            name = expr.name.lexeme
            if name in self.env.values:
                box = self.env.values[name]
                return box.value if unbox else box
            if self.env.enclosing:
                return self.env.get_variable(expr.name) # Fallback for built-ins
            return self.env.get_variable(expr.name)
        
        elif isinstance(expr, ListLiteral):
            return [self._evaluate(element) for element in expr.elements]
        
        elif isinstance(expr, Get):
            obj = self._evaluate(expr.object)
            if isinstance(obj, MryaModule):
                return obj.get(expr.name)
            # Allow property access on strings via the string module
            if isinstance(obj, str):
                string_mod = self.native_modules["string"]
                method = string_mod.get(expr.name)
                # Return a new function that has the string instance pre-filled as the first argument
                return lambda *args: method(obj, *args)

            raise MryaRuntimeError(expr.name, f"Only modules and strings can have properties. Got {type(obj).__name__}.")

        elif isinstance(expr, SubscriptGet):
            obj = self._evaluate(expr.object)
            index = self._evaluate(expr.index)

            if isinstance(obj, (list, str)):
                if not isinstance(index, int):
                    raise MryaRuntimeError(expr.token, "List or string index must be an integer.")
                try:
                    return obj[index]
                except IndexError:
                    raise MryaRuntimeError(expr.token, f"Index {index} out of range.")
            elif isinstance(obj, dict):
                if not isinstance(index, (str, int, float)):
                    raise MryaRuntimeError(expr.token, "Map key must be a string or number.")
                return obj.get(index) # Use .get() to return None for missing keys

            raise MryaRuntimeError(expr.name, f"Only modules and strings can have properties. Got {type(obj).__name__}.")
        
        elif isinstance(expr, BinaryExpression):
            left = self._evaluate(expr.left)
            right = self._evaluate(expr.right)
            op = expr.operator.type
            
            try:
                if op == TokenType.PLUS:
                    # If one operand is a string, treat it as concatenation
                    if isinstance(left, str) or isinstance(right, str):
                        return str(left) + str(right)
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
                elif op == TokenType.EQUAL_EQUAL:
                    return left == right
                elif op == TokenType.BANG_EQUAL:
                    return left != right
                else:
                    raise MryaRuntimeError(expr.operator, f"Unsupported operator: {expr.operator.lexeme}")
            except TypeError:
                raise MryaRuntimeError(expr.operator, f"Invalid operands for {expr.operator.lexeme}: {left}, {right}")
        
        elif isinstance(expr, FunctionCall):
            return self._call_function(expr)
        
        elif isinstance(expr, Logical):
            left = self._evaluate(expr.left)
            if expr.operator.type == TokenType.OR:
                # Short-circuit: if left is true, the whole expression is true
                if left:
                    return True
            elif expr.operator.type == TokenType.AND:
                # Short-circuit: if left is false, the whole expression is false
                if not left:
                    return False
            return bool(self._evaluate(expr.right))
        
        elif isinstance(expr, MapLiteral):
            map_obj = {}
            for key_expr, value_expr in expr.pairs:
                key = self._evaluate(key_expr)
                value = self._evaluate(value_expr)
                map_obj[key] = value
            return map_obj

        else:
            raise RuntimeError(f"Unsupported expression type; {type(expr).__name__}")

class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value

class BreakInterrupt(Exception):
    """Used to signal a 'break' statement."""
    pass

class ContinueInterrupt(Exception):
    """Used to signal a 'continue' statement."""
    pass
                    
            
        
