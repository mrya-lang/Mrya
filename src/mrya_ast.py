class Expr:
    pass

class Literal(Expr):
    def __init__(self, value):
        self.value = value

class HString(Expr):
    def __init__(self, parts):
        self.parts = parts # A list of string literals and expression nodes

class Splat(Expr):
    def __init__(self, expression):
        self.expression = expression

class Variable(Expr):
    def __init__(self, name_token):  # Accept token, not string
        self.name = name_token       # Store token itself here

class BinaryExpression(Expr):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class Logical(Expr):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class Get(Expr):
    def __init__(self, object, name):
        self.object = object
        self.name = name

class Unary(Expr):
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right

class This(Expr):
    def __init__(self, keyword):
        self.keyword = keyword

class Inherit(Expr):
    def __init__(self, keyword, method):
        self.keyword = keyword
        self.method = method

class Stmt:
    pass

class LetStatement(Stmt):
    def __init__(self, name, initializer, is_const, type_annotation=None):
        self.name = name
        self.initializer = initializer
        self.type_annotation = type_annotation
        self.is_const = is_const

class OutputStatement(Stmt):
    def __init__(self, expression):
        self.expression = expression

class FunctionDeclaration(Stmt):
    def __init__(self, name, params, body, decorators=None, is_variadic=False):
        self.name = name
        self.params = params
        self.body = body
        self.is_variadic = is_variadic
        self.decorators = decorators if decorators is not None else []
        self.env = None # To hold the closure environment

class FunctionCall(Expr):
    def __init__(self, callee, arguments):
        self.callee = callee
        self.arguments = arguments

class ReturnStatement(Stmt):
    def __init__(self, keyword, value):
        self.keyword = keyword  # 'return' token, for error reporting
        self.value = value  # Expr or None

class IfStatement(Stmt):
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

class WhileStatement(Stmt):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class ForStatement(Stmt):
    def __init__(self, variable, iterable, body):
        self.variable = variable
        self.iterable = iterable
        self.body = body

class BreakStatement(Stmt):
    def __init__(self, keyword):
        self.keyword = keyword

class ContinueStatement(Stmt):
    def __init__(self, keyword):
        self.keyword = keyword

class CatchClause(Stmt):
    def __init__(self, error_type, body):
        self.error_type = error_type # Optional IDENTIFIER token
        self.body = body

class TryStatement(Stmt):
    def __init__(self, try_block, catch_clauses, finally_block):
        self.try_block = try_block
        self.catch_clauses = catch_clauses
        self.finally_block = finally_block

class ClassDeclaration(Stmt):
    def __init__(self, name, superclass, methods, decorators=None):
        self.name = name
        self.methods = methods
        self.superclass = superclass
        self.decorators = decorators if decorators is not None else []

class SetProperty(Stmt):
    def __init__(self, obj, name, value):
        self.object = obj
        self.name = name
        self.value = value

class Assignment(Stmt):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class SubscriptGet(Expr):
    def __init__(self, obj, index_expr, closing_bracket):
        self.object = obj
        self.index = index_expr
        self.token = closing_bracket # For error reporting

class SubscriptSet(Stmt):
    def __init__(self, obj, index_expr, value):
        self.object = obj
        self.index = index_expr
        self.value = value

class InputCall(Expr):
    def __init__(self, prompt):
        self.prompt = prompt

class ImportStatement(Stmt):
    def __init__(self, path_expr):
        self.path_expr = path_expr

class ListLiteral(Expr):
    def __init__(self, elements):
        self.elements = elements

class MapLiteral(Expr):
    def __init__(self, pairs):
        self.pairs = pairs # List of (key_expr, value_expr) tuples