class Expr:
    pass
class Literal(Expr):
    def __init__(self, value):
        self.value = value

class Variable(Expr):
    def __init__(self, name):
        self.name = name
    
class Assign(Expr):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class Call(Expr):
    def __init__(self, callee, arguments):
        self.callee = callee
        self.arguments = arguments