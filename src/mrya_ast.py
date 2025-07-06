class Expr:
    pass

class Literal(Expr):
    def __init__(self, value):
        self.value = value

class Variable(Expr):
    def __init__(self, name_token):  # Accept token, not string
        self.name = name_token       # Store token itself here

class Assign(Expr):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class Call(Expr):
    def __init__(self, callee, arguments):
        self.callee = callee
        self.arguments = arguments

class BinaryExpression(Expr):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class Stmt:
    pass

class LetStatement(Stmt):
    def __init__(self, name, initializer):
        self.name = name  # Token for variable name
        self.initializer = initializer  # Expr

class OutputStatement(Stmt):
    def __init__(self, expression):
        self.expression = expression  # Expr

class FunctionDeclaration(Stmt):
    def __init__(self, name, params, body):
        self.name = name  # Token for function name
        self.params = params  # List of parameter tokens
        self.body = body  # List of statements

class FunctionCall(Expr):
    def __init__(self, name, arguments):
        self.name = name  # Token for function name
        self.arguments = arguments  # List of Expr

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