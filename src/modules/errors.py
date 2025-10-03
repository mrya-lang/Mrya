class MryaRasiedError(Exception):
    def __init__(self, *args):
        super().__init__(*args)

def mrya_raise(error_message):
    raise MryaRasiedError(f"{error_message}")

def mrya_assert(condition, expected, message="Assertion failed"):
    if condition != expected:
        raise MryaRasiedError(f"Assertion failed: {message}")