class LexerError(Exception):
    """An exception raised for errors during lexing."""
    pass

class MryaRuntimeError(Exception):
    def __init__(self, token, message):
        self.token = token
        self.message = message
        super().__init__(message)

class MryaTypeError(MryaRuntimeError):
    """Raised for type annotation mismatches."""
    pass