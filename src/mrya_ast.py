class Expr:
    pass

class Literal(Expr):
    def __init__(self, value):
        self.value = value

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

class Stmt:
    pass

class LetStatement(Stmt):
    def __init__(self, name, initializer, type_annotation=None):
        self.name = name
        self.initializer = initializer
        self.type_annotation = type_annotation

class OutputStatement(Stmt):
    def __init__(self, expression):
        self.expression = expression

class FunctionDeclaration(Stmt):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

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

class Assignment(Stmt):
    def __init__(self, name, value):
        self.name = name
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