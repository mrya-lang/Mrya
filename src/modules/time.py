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

def format_time(format_str):
    """Formats the current time using strftime format string."""
    try:
        return datetime.now().strftime(format_str)
    except ValueError as e:
        raise RuntimeError(f"Invalid format string: {e}")

def get_time():
    """Returns the current time as HH:MM:SS."""
    return datetime.now().strftime("%H:%M:%S")

def get_date():
    """Returns the current date as YYYY-MM-DD."""
    return datetime.now().strftime("%Y-%m-%d")

def format_datetime(format_str):
    """Alias for format_time."""
    return format_time(format_str)

def military_time():
    """Returns the current time in 24-hour format (HH:MM:SS)."""
    return get_time()

def twelve_hour_time():
    """Returns the current time in 12-hour format (HH:MM:SS AM/PM)."""
    return datetime.now().strftime("%I:%M:%S %p")
