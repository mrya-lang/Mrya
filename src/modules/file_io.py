import os 

def fetch(filepath):
    """Reads the content of a file. If the file does not exist, it will be created with empty content."""
    if not os.path.exists(filepath):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                pass # Create an empty file
            return "" # Return empty string for the new file
        except Exception as e:
            raise RuntimeError(f"Failed to create file '{filepath}': {e}")
    try:
        with open (filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise RuntimeError(f"Failed to read file '{filepath}': {e}")

def fetch_raw(filepath):
    """Reads the raw bytes of a file and returns them."""
    if not os.path.exists(filepath):
        raise RuntimeError(f"File not found at '{filepath}'")
    try:
        with open(filepath, 'rb') as f:
            return f.read()
    except Exception as e:
        raise RuntimeError(f"Failed to read raw file '{filepath}': {e}")

def store(interpreter, filepath, content):
    full_path = os.path.join(interpreter.current_directory, filepath)
    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(str(content))
        return None
    except Exception as e:
        raise RuntimeError(f"Failed to write to file '{full_path}': {e}")

def append_to(interpreter, filepath, content):
    full_path = os.path.join(interpreter.current_directory, filepath)
    try:
        with open(full_path, 'a', encoding='utf-8') as f:
            f.write(str(content))
        return None
    except Exception as e:
        raise RuntimeError(f"Failed to append to file '{full_path}': {e}")
