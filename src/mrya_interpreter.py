from mrya_ast import Expr, Literal, HString, Splat, Variable, Get, BinaryExpression, Logical, Unary, LetStatement, OutputStatement, FunctionDeclaration, FunctionCall, ReturnStatement, IfStatement, WhileStatement, ForStatement, BreakStatement, ContinueStatement, TryStatement, CatchClause, ClassDeclaration, SetProperty, This, Inherit, Assignment, SubscriptGet, SubscriptSet, InputCall, ImportStatement, ListLiteral, MapLiteral
from mrya_errors import LexerError, MryaRuntimeError, MryaTypeError, MryaRaisedError, ClassFunctionError
from modules.math_equations import evaluate_binary_expression
from modules.file_io import fetch, store, append_to
from mrya_tokens import TokenType, Token
import os
from modules import arrays as arrays
from modules import maps as maps
from modules import math_utils as math_utils
from modules import fs_utils as fs_utils
from modules import time as time_module
from modules import errors as error_module
from modules import window_module as window_module
from modules import http_server as http_server_module
from modules import html_renderer as html_renderer_module

import __main__

class MryaModule:
    """A simple class to represent a Mrya module with methods."""
    def __init__(self, name):
        self.name = name
        self.methods = {}
        self.env = None

    def get(self, name_token):
        if name_token.lexeme in self.methods:
            value = self.methods[name_token.lexeme]
            # If it's a function, wrap it to use the module's environment
            if isinstance(value, FunctionDeclaration) and hasattr(self, 'env') and self.env:
                return MryaModuleMethod(self, value)
            return value
        raise MryaRuntimeError(name_token, f"Module '{self.name}' has no attribute '{name_token.lexeme}'.")

class MryaBox:
    """A mutable box to hold a variable's value, enabling reference semantics."""
    def __init__(self, value, is_const=False):
        self.value = value
        self.is_const = is_const

class MryaModuleMethod:
    """A bound method for module functions that preserves the module's environment."""
    def __init__(self, module, func_decl):
        self.module = module
        self.func_decl = func_decl
    
    def __call__(self, interpreter, arguments):
        # Use the module's environment as the enclosing environment
        call_env = Environment(enclosing=self.module.env)
        
        # Bind parameters
        for i, param in enumerate(self.func_decl.params):
            call_env.define_variable(param.lexeme, MryaBox(arguments[i]))
        
        # Execute the function body in the module's environment
        try:
            interpreter._execute_block(self.func_decl.body, call_env)
            return None
        except ReturnValue as return_value:
            return return_value.value

class MryaClass:
    def __init__(self, name, superclass, methods):
        self.name = name
        self.methods = methods
        self.superclass = superclass

    def __call__(self, interpreter, arguments):
        instance = MryaInstance(self)
        initializer = self.find_method("_start_")
        if initializer: # The initializer is a FunctionDeclaration
            bound_initializer = MryaBoundMethod(instance, initializer)
            bound_initializer(interpreter, arguments)
        return instance

    def find_method(self, name):
        if name in self.methods:
            return self.methods[name]
        if self.superclass:
            return self.superclass.find_method(name)
        return None

    def __str__(self):
        return f"<class {self.name}>"

class MryaBoundMethod:
    def __init__(self, instance, method_declaration):
        self.instance = instance
        self.method = method_declaration
    def __call__(self, interpreter, arguments):
        return interpreter.call_function_or_method(self.method, arguments, self.instance)

class MryaInstance:
    def __init__(self, klass):
        self._klass = klass
        self.fields = {}

    def get(self, name_token):
        name = name_token.lexeme
        if name in self.fields:
            return self.fields[name]
        
        # Look for a class-level attribute (method or static property)
        class_attr = self._klass.find_method(name)
        if class_attr is not None:
            # If it's a function, bind it to the instance as a method
            if isinstance(class_attr, FunctionDeclaration):
                return MryaBoundMethod(self, class_attr)
            # Otherwise, it's a static-like property, return it directly
            return class_attr

        raise MryaRuntimeError(name_token, f"Undefined property '{name}'.")

    def __str__(self):
        return f"<Instance of {self._klass.name}>"

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
        if name in self.functions: # Fallback to check global functions
            return self.functions[name]
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
        # Native Modules
        time_mod = MryaModule("time")
        time_mod.methods = {
            "sleep": time_module.sleep,
            "time": time_module.time,
            "datetime": time_module.datetime_now,
        }

        fs_mod = MryaModule("fs")
        fs_mod.methods = {
            "exists": fs_utils.exists,
            "is_file": fs_utils.is_file,
            "is_dir": fs_utils.is_dir,
            "list_dir": fs_utils.list_dir,
            "get_size": fs_utils.get_size,
            "make_dir": fs_utils.make_dir,
            "remove_file": fs_utils.remove_file,
            "remove_dir": fs_utils.remove_dir,
        }

        string_mod = MryaModule("string")
        string_mod.methods = {
            "upper": lambda s: str(s).upper(),
            "lower": lambda s: str(s).lower(),
            "trim": lambda s: str(s).strip(),
            "replace": lambda s, old, new: str(s).replace(str(old), str(new)),
            "split": lambda s, sep: str(s).split(str(sep)),
            "startsWith": lambda s, prefix: str(s).startswith(str(prefix)),
            "endsWith": lambda s, suffix: str(s).endswith(str(suffix)),
            "contains": lambda s, sub: str(sub) in str(s),
            "slice": lambda s, start, end=None: str(s)[int(start):int(end) if end is not None else None],
            "join": lambda sep, lst: str(sep).join([str(i) for i in lst]),
        }

        math_mod = MryaModule("math")
        math_mod.methods = {
            "abs": math_utils.absfn,
            "randint": math_utils.randint,
        }

        window_mod = MryaModule("window")
        window_mod.methods = {
            "init": window_module.init,
            "create_display": window_module.create_display,
            "update": window_module.update,
            "get_events": window_module.get_events,
            "get_event_type": window_module.get_event_type,
            "get_const": window_module.get_const,
            "rect": window_module.rect,
            "text": window_module.text,
            "fill": window_module.fill,
            "circle": window_module.circle,
            "get_event_key": window_module.get_event_key,
            "get_key_state": window_module.get_key_state,
            "update_key_states": window_module.update_key_states
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
            "raise": error_module.mrya_raise,
            "assert": error_module.mrya_assert,
            
             
}
        for name, fn in builtins.items():
            # Wrap built-in functions in a constant box
            self.env.define_variable(name, MryaBox(fn, is_const=True))

        self.native_modules = {
            "time": time_mod,
            "fs": fs_mod,
            "string": string_mod,
            "math": math_mod,
            "window": window_mod
        }

        http_mod = MryaModule("http_server")
        http_mod.methods = {
            "run": http_server_module.run_server
        }
        self.native_modules["http_server"] = http_mod

        html_mod = MryaModule("html_renderer")
        html_mod.methods = {
            "render": html_renderer_module.render
        }
        self.native_modules["html_renderer"] = html_mod

        self.imported_files = set()
        self.module_cache = {} # Add a cache for module objects
        self.current_directory = os.getcwd()
    
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
            
            # Handle custom output for class instances
            if isinstance(value, MryaInstance):
                out_method = value._klass.find_method("_out_")
                if out_method:
                    bound_method = MryaBoundMethod(value, out_method)
                    # Call the _out_ method to get the string representation
                    output_value = str(bound_method(self, []))
                else:
                    output_value = str(value) # Use default representation
            else:
                output_value = value
            if os.path.basename(getattr(__main__, "__file__", "")) != "mrya_suite.py": # Avoid output during test suite
                print(output_value)
        
        elif isinstance(stmt, ClassDeclaration):
            superclass = None
            if stmt.superclass:
                superclass = self._evaluate(stmt.superclass)
                if not isinstance(superclass, MryaClass):
                    raise MryaRuntimeError(stmt.superclass.name, "Superclass must be a class.")

            methods = {method.name.lexeme: method for method in stmt.methods}
            
            # The initial class object
            klass_obj = MryaClass(stmt.name.lexeme, superclass, methods)

            # Apply decorators
            decorated_obj = klass_obj
            if stmt.decorators:
                # Decorators are applied from the bottom up
                for decorator_expr in reversed(stmt.decorators):
                    decorator_func = self._evaluate(decorator_expr)
                    # Check if it's a Mrya function, a bound method, or a Python callable
                    is_mrya_callable = isinstance(decorator_func, (FunctionDeclaration, MryaBoundMethod, MryaModuleMethod))
                    if not is_mrya_callable and not callable(decorator_func):
                        # This needs a token for better error reporting.
                        raise MryaRuntimeError(decorator_expr.name, f"Decorator must be a callable function.")
                    decorated_obj = self.call_function_or_method(decorator_func, [decorated_obj])

            self.env.define_variable(stmt.name, MryaBox(decorated_obj, is_const=True))

        elif isinstance(stmt, FunctionDeclaration):
            # The function object itself
            # Capture the current environment to create a closure.
            stmt.env = self.env

            func_obj = stmt

            # Apply decorators
            decorated_obj = func_obj
            if stmt.decorators:
                # Decorators are applied from the bottom up
                for decorator_expr in reversed(stmt.decorators):
                    decorator_func = self._evaluate(decorator_expr)
                    is_mrya_callable = isinstance(decorator_func, (FunctionDeclaration, MryaBoundMethod, MryaModuleMethod))
                    if not is_mrya_callable and not callable(decorator_func):
                        # This needs a token for better error reporting.
                        raise MryaRuntimeError(decorator_expr.name, f"Decorator must be a callable function.")
                    # Use the interpreter's call mechanism
                    decorated_obj = self.call_function_or_method(decorator_func, [decorated_obj])

            self.env.define_variable(stmt.name, MryaBox(decorated_obj, is_const=True))

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
                        loop_env.define_variable(stmt.variable, MryaBox(item)) # This was incorrect, should be a new box
                        
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
        
        elif isinstance(stmt, TryStatement):
            try:
                self._execute_block(stmt.try_block, self.env)
            except (MryaRuntimeError, MryaTypeError, MryaRaisedError) as e:
                caught = False
                for clause in stmt.catch_clauses:
                    # Check if the clause can handle this error type.
                    can_handle = False
                    if clause.error_type:  # Specific catch like `catch MryaRuntimeError`
                        error_name = type(e).__name__
                        if clause.error_type.lexeme == error_name:
                            can_handle = True
                    else: # Generic catch {}
                        can_handle = True

                    if can_handle:
                        self._execute_block(clause.body, Environment(enclosing=self.env))
                        caught = True
                        break # Only execute the first matching catch block
                
                if not caught:
                    raise e # Re-raise the exception if no catch block handled it
            finally:
                if stmt.finally_block:
                    self._execute_block(stmt.finally_block, self.env)









        elif isinstance(stmt, Assignment):
            value = self._evaluate(stmt.value)
            self.env.assign(stmt.name, value)

        elif isinstance(stmt, SetProperty):
            obj = self._evaluate(stmt.object)
            value = self._evaluate(stmt.value)

            if isinstance(obj, MryaInstance):
                obj.fields[stmt.name.lexeme] = value
            elif isinstance(obj, MryaClass):
                # Allow setting "static" properties on a class.
                # We can store them in the `methods` dict, which acts as the class's attribute store.
                obj.methods[stmt.name.lexeme] = value
            else:
                raise MryaRuntimeError(stmt.name, "Only instances and classes can have properties set.")
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
            elif isinstance(obj, MryaInstance):
                set_method = obj._klass.find_method("_set_")
                if not set_method:
                    raise ClassFunctionError(stmt.object.name, f"Class '{obj._klass.name}' does not define a '_set_' method and cannot be assigned to with [].")
                bound_method = MryaBoundMethod(obj, set_method)
                bound_method(self, [index, value])
            else:
                raise MryaRuntimeError(stmt.object.name, "Can only set items on lists and maps.")
             
        elif isinstance(stmt, ImportStatement):
            # This handles standalone `import("filename")` statements.
            path_str = self._evaluate(stmt.path_expr)
            module_obj = self._builtin_import(path_str)
 
            # Create a variable in the current environment with the module's name.
            module_name = os.path.splitext(os.path.basename(path_str))[0]
            # The token is for error reporting; line number isn't critical here.
            module_name_token = Token(TokenType.IDENTIFIER, module_name, None, 0)
            self.env.define_variable(module_name_token, MryaBox(module_obj, is_const=True))

        else:
            raise RuntimeError(f"Unknown statement type: {type(stmt).__name__}")
        
    def set_current_directory(self, path):
        self.current_directory = path

    def _builtin_import(self, filepath):
        if not isinstance(filepath, str):
            raise RuntimeError("import() requires a file path as a string.")

        is_package = False
        full_path = ""

        # Check if external package
        if filepath.startswith("package:"):
            is_package = True
            current_script_path = os.path.abspath(__file__)
            current_dir = os.path.dirname(current_script_path)
            package_name = filepath.removeprefix("package:")
            suffix = "main.mrya" if not package_name.endswith((".mrya", ".mr")) and not os.path.splitext(package_name)[1] else ""
            full_path = os.path.abspath(os.path.join(current_dir, "..", "packages", package_name, suffix))

        # Check for native modules first
        if filepath in self.native_modules:
            return self.native_modules[filepath]

        previous_directory = self.current_directory

        # For non-packages, resolve the path relative to the current script's directory.
        if not is_package:
            if not filepath.endswith((".mrya", ".mr")) and not os.path.splitext(filepath)[1]:
                filepath += ".mrya"
            full_path = os.path.abspath(os.path.join(self.current_directory, filepath))

        # Check cache first to handle circular imports
        if full_path in self.module_cache:
            return self.module_cache[full_path]

        if not os.path.exists(full_path):
            # Restore directory before raising error
            self.current_directory = previous_directory
            raise RuntimeError(f"Import failed: '{full_path}' not found.")
        
        # Create and cache the module object BEFORE executing its code
        module_obj = MryaModule(os.path.basename(filepath))
        self.module_cache[full_path] = module_obj

        with open(full_path, "r", encoding="utf-8") as f:
                  source = f.read()

        # Set the directory context for the new module
        self.current_directory = os.path.dirname(full_path)
        
        from mrya_lexer import MryaLexer
        from mrya_parser import MryaParser
        lexer = MryaLexer(source)
        tokens = lexer.scan_tokens() # This might need error handling
        parser = MryaParser(tokens)
        statements = parser.parse()

        # Create a new module-like object to return
        module_env = Environment(enclosing=self.env)
        # Store the environment on the module object so its functions can access it,
        # but only after it's populated
        module_obj.env = module_env

        try:
            self._execute_block(statements, module_env)
        except ReturnValue as return_value:
            # If the file has a top-level return, return that value directly.
            self.module_cache[full_path] = return_value.value
            return return_value.value
        finally:
            # --- Restore the previous directory context ---
            self.current_directory = previous_directory

        # If no top-level return, populate the module object with all defined variables/functions.
        module_obj.methods = {name: box.value for name, box in module_env.values.items()}
        module_obj.methods.update(module_env.functions)
        return module_obj

    def _call_function(self, call):
        callee = self._evaluate(call.callee)

        # Check for class instantiation
        if isinstance(callee, MryaClass):
            # Class initializers also support argument unpacking
            args = []
            for arg_expr in call.arguments:
                if isinstance(arg_expr, Splat):
                    value_to_unpack = self._evaluate(arg_expr.expression)
                    if not isinstance(value_to_unpack, list):
                        raise MryaRuntimeError(None, "The '...' operator can only be used to unpack lists in function calls.")
                    args.extend(value_to_unpack)
                else:
                    args.append(self._evaluate(arg_expr))
            return callee(self, args)
        
        if isinstance(callee, MryaModule):
            # This provides a helpful error when a user forgets to `return` a class from an imported file.
            callee_token = call.callee.name if isinstance(call.callee, Variable) else call.callee
            raise MryaRuntimeError(callee_token, f"Cannot call a module. If you intended to import a class, make sure the imported file ends with a 'return' statement.")
        
        # Centralize argument evaluation and unpacking
        arguments = []
        for arg_expr in call.arguments:
            if isinstance(arg_expr, Splat):
                value_to_unpack = self._evaluate(arg_expr.expression)
                if not isinstance(value_to_unpack, list):
                    raise MryaRuntimeError(None, "The '...' operator can only be used to unpack lists in function calls.")
                arguments.extend(value_to_unpack)
            else:
                arguments.append(self._evaluate(arg_expr))

        if isinstance(callee, (MryaBoundMethod, MryaModuleMethod, FunctionDeclaration)):
            return self.call_function_or_method(callee, arguments)

        elif callable(callee): # For built-ins
            try:
                # Check if the callable is a method of one of the native modules.
                # This is a bit of a heuristic, but it works for our case.
                # We only pass the interpreter instance to native module functions.
                # We also exclude the interpreter's own _builtin_ methods.
                is_internal_builtin = hasattr(callee, '__name__') and callee.__name__.startswith('_builtin_') # e.g. _builtin_import
                is_simple_lambda = callee.__name__ == '<lambda>' # For string methods
                is_native_module_func = any(callee in mod.methods.values() for mod in self.native_modules.values()) and not is_internal_builtin and not is_simple_lambda
                if is_native_module_func:
                    return callee(self, *arguments)
                else:
                    return callee(*arguments)
            except (MryaRuntimeError, MryaTypeError, MryaRaisedError) as e:
                # Let Mrya's own errors pass through without being wrapped.
                # This MUST be the first handler to prevent our errors from being re-wrapped.
                raise e
            except TypeError as e:
                # When a built-in is called with the wrong number of arguments, it raises a TypeError.
                # We catch it and raise a Mrya-native error that the REPL can handle.
                callee_token = call.callee.name if isinstance(call.callee, Variable) else call.callee
                raise MryaRuntimeError(callee_token, f"Error calling built-in function: {e}") from e
            except Exception as e:
                callee_token = call.callee.name if isinstance(call.callee, Variable) else call.callee
                raise MryaRuntimeError(callee_token, f"Error inside built-in function: {e}")
        else:
            if isinstance(call.callee, Get):
                callee_token = call.callee.name
            elif isinstance(call.callee, Variable):
                callee_token = call.callee.name
            else:
                callee_token = call.callee
            raise MryaRuntimeError(callee_token, f"'{callee_token.lexeme}' is not a function or class and cannot be called.")
    
    def call_function_or_method(self, callee, arguments, instance=None):
        if isinstance(callee, MryaBoundMethod):
            # A bound method already has its instance, so we can call it directly.
            return callee(self, arguments)
        if isinstance(callee, MryaModuleMethod):
            # A module method has its own calling logic to use the module's environment.
            return callee(self, arguments)

        declaration = callee
        # When calling a function, its new environment should enclose the one
        # it was defined in (its closure), not the one it is being called from.
        closure_env = declaration.env if declaration.env is not None else self.env
        call_env = Environment(enclosing=closure_env)

        if instance: # If it's a method call, bind 'this'
            current_class = instance._klass
            if declaration not in current_class.methods.values(): # Search up the chain
                while current_class.superclass and declaration not in current_class.methods.values():
                    current_class = current_class.superclass
            call_env.define_variable("inherit", MryaBox(current_class.superclass, is_const=True))
            call_env.define_variable("this", MryaBox(instance, is_const=True))
        
        if declaration.is_variadic:
            num_fixed_params = len(declaration.params) - 1
            if len(arguments) < num_fixed_params:
                raise MryaRuntimeError(declaration.name, f"Function '{declaration.name.lexeme}' expects at least {num_fixed_params} arguments, but got {len(arguments)}.")

            # Bind fixed parameters
            for i in range(num_fixed_params):
                call_env.define_variable(declaration.params[i], MryaBox(arguments[i]))

            # Bind variadic parameter to a list of remaining arguments
            variadic_args = arguments[num_fixed_params:]
            variadic_param_name = declaration.params[-1]
            call_env.define_variable(variadic_param_name, MryaBox(variadic_args))
        else:
            if len(arguments) != len(declaration.params):
                raise MryaRuntimeError(declaration.name, f"Function '{declaration.name.lexeme}' expects {len(declaration.params)} arguments, but got {len(arguments)}.")

            for param_token, arg_value in zip(declaration.params, arguments):
                call_env.define_variable(param_token, MryaBox(arg_value))
            
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
        elif isinstance(collection, MryaInstance):
            len_method = collection._klass.find_method("_len_")
            if not len_method:
                # This needs a token, but built-ins don't have one. This is a known limitation.
                raise ClassFunctionError(None, f"Class '{collection._klass.name}' does not define a '_len_' method.")
            bound_method = MryaBoundMethod(collection, len_method)
            return bound_method(self, [])
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

        elif isinstance(expr, HString):
            result_parts = []
            for part in expr.parts:
                result_parts.append(str(self._evaluate(part)))
            return "".join(result_parts)
        
        elif isinstance(expr, Get):
            obj = self._evaluate(expr.object)
            if isinstance(obj, MryaModule):
                return obj.get(expr.name)
            if isinstance(obj, MryaInstance):
                return obj.get(expr.name)
            # Allow property access on strings via the string module
            if isinstance(obj, str):
                string_mod = self.native_modules["string"]
                method = string_mod.get(expr.name)
                # Check if it's a raw Python function from the module
                if callable(method) and not isinstance(method, (MryaClass, FunctionDeclaration)):
                    # Return a new function that has the string instance pre-filled as the first argument.
                    # Unlike other native functions, these simple lambdas don't need the interpreter instance. We pass the object and the rest of the arguments.
                    return lambda *args: method(obj, *args) # The `obj` is the string itself.
                return method

            raise MryaRuntimeError(expr.name, f"Only modules, instances, and strings can have properties. Got {type(obj).__name__}.")

        elif isinstance(expr, Inherit):
            superclass = self.env.get_variable(expr.keyword)
            instance = self.env.get_variable(Token(TokenType.THIS, "this", None, expr.keyword.line))

            method = superclass.find_method(expr.method.lexeme)
            if method is None:
                raise MryaRuntimeError(expr.method, f"Undefined method '{expr.method.lexeme}' in superclass.")
            
            return MryaBoundMethod(instance, method)

        elif isinstance(expr, This):
            return self.env.get_variable(expr.keyword)

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
            elif isinstance(obj, MryaInstance):
                get_method = obj._klass.find_method("_get_")
                if not get_method:
                    raise ClassFunctionError(expr.token, f"Class '{obj._klass.name}' does not define a '_get_' method and is not subscriptable.")
                bound_method = MryaBoundMethod(obj, get_method)
                return bound_method(self, [index])

            raise MryaRuntimeError(expr.token, "Can only use [] on lists, strings, and maps.")
        
        elif isinstance(expr, Unary):
            right = self._evaluate(expr.right)
            op = expr.operator.type

            if op == TokenType.MINUS:
                if not isinstance(right, (int, float)):
                    raise MryaRuntimeError(expr.operator, "Operand must be a number for negation.")
                return -right
            if op == TokenType.BANG:
                return not bool(right)
            return None # Unreachable

        elif isinstance(expr, BinaryExpression):
            left = self._evaluate(expr.left)
            right = self._evaluate(expr.right)
            op = expr.operator.type
            
            # Check for operator overloading on classes
            if isinstance(left, MryaInstance):
                method_map = {
                    TokenType.PLUS: "_plus_",
                    TokenType.MINUS: "_minus_",
                    TokenType.STAR: "_times_",
                    TokenType.SLASH: "_divide_",
                    TokenType.EQUAL_EQUAL: "_equals_",
                    TokenType.BANG_EQUAL: "_equals_", # Uses _equals_ and negates the result
                }
                if op in method_map:
                    method_name = method_map[op]
                    method = left._klass.find_method(method_name)
                    if method:
                        bound_method = MryaBoundMethod(left, method)
                        result = bound_method(self, [right])
                        if op == TokenType.BANG_EQUAL:
                            return not result
                        return result

            # Default behavior for built-in types
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
        
        elif isinstance(expr, Splat):
            # A splat expression should not be evaluated on its own. It's a syntax marker for function calls.
            # If it's encountered here, it's a programming error in the interpreter or a syntax error in the language.
            # We need a token for this error.
            raise MryaRuntimeError(None, "The '...' operator can only be used inside a function call.")
        
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
                    
            
        
