import os
import shutil

def exists(path):
    """Returns true if the path exists."""
    return os.path.exists(path)

def is_file(path):
    """Returns true if the path is a file."""
    return os.path.isfile(path)

def is_dir(path):
    """Returns true if the path is a directory."""
    return os.path.isdir(path)

def list_dir(path="."):
    """Returns a list of items in a directory. Defaults to the current directory."""
    return os.listdir(path)

def get_size(path):
    """Returns the size of a file in bytes."""
    return os.path.getsize(path)

def make_dir(path):
    """Creates a directory. No error if it already exists."""
    os.makedirs(path, exist_ok=True)

def remove_file(path):
    """Removes a file."""
    os.remove(path)

def remove_dir(path):
    """Removes a directory and all its contents."""
    shutil.rmtree(path)