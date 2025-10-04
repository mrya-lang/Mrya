import os
import shutil

def exists(interpreter, path):
    """Returns true if the path exists."""
    full_path = os.path.join(interpreter.current_directory, path)
    return os.path.exists(full_path)

def is_file(interpreter, path):
    """Returns true if the path is a file."""
    full_path = os.path.join(interpreter.current_directory, path)
    return os.path.isfile(full_path)

def is_dir(interpreter, path):
    """Returns true if the path is a directory."""
    full_path = os.path.join(interpreter.current_directory, path)
    return os.path.isdir(full_path)

def list_dir(interpreter, path="."):
    """Returns a list of items in a directory. Defaults to the current directory."""
    full_path = os.path.join(interpreter.current_directory, path)
    return os.listdir(full_path)

def get_size(interpreter, path):
    """Returns the size of a file in bytes."""
    full_path = os.path.join(interpreter.current_directory, path)
    return os.path.getsize(full_path)

def make_dir(interpreter, path):
    """Creates a directory. No error if it already exists."""
    full_path = os.path.join(interpreter.current_directory, path)
    os.makedirs(full_path, exist_ok=True)

def remove_file(interpreter, path):
    """Removes a file."""
    full_path = os.path.join(interpreter.current_directory, path)
    os.remove(full_path)

def remove_dir(interpreter, path):
    """Removes a directory and all its contents."""
    full_path = os.path.join(interpreter.current_directory, path)
    shutil.rmtree(full_path)
