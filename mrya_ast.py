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

class Stmt:
    pass

class LetStatement(Stmt):
    def __init__(self, name, initializer):
        self.name = name  # should be a string
        self.initializer = initializer  # should be an Expr

class OutputStatement(Stmt):
    def __init__(self, expression):
        self.expression = expression  # should be an Expr

class BinaryExpression(Expr):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
