import time as py_time
from datetime import datetime

def sleep(seconds):
    """Pauses execution for a given number of seconds."""
    try:
        py_time.sleep(float(seconds))
    except (ValueError, TypeError):
        raise RuntimeError(f"sleep() requires a number, but got '{seconds}'.")

def time():
    """Returns the current time in seconds since the Epoch."""
    return py_time.time()

def datetime_now():
    """Returns the current date and time as a formatted string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")