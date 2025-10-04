from mrya_errors import MryaRaisedError

def mrya_raise(error_message):
    raise MryaRaisedError(None, f"{error_message}")

def mrya_assert(condition, expected, message="Assertion failed"):
    if condition != expected:
        raise MryaRaisedError(None, f"Assertion failed: {message}")