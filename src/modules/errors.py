from mrya_errors import MryaRaisedError

def mrya_raise(error_message):
    raise MryaRaisedError(None, f"{error_message}")

def mrya_assert(condition, expected, message=None):
    if condition != expected:
        error_msg = f"Assertion failed: expected '{expected}', but got '{condition}'."
        if message:
            error_msg = f"Assertion failed: {message}. Expected '{expected}', but got '{condition}'."
        raise MryaRaisedError(None, error_msg)