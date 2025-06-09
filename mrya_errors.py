class MryaRuntimeError(Exception):
    def __init__(self, token, message):
        self.token = token
        self.message = message
        super().__init__(message)