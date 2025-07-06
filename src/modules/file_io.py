import os 

def fetch(filepath):
    if not os.path.exists(filepath):
        if filepath.endswith(".mrya"):
            default_content = 'output("Hello from Mrya!")\n'
        else:
            default_content = "Hello from Mrya!\n"

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(default_content)
        except Exception as e:
            raise RuntimeError(f"Failed to create file '{filepath}': {e}")
        
    try:
        with open (filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise RuntimeError(f"Failed to read file '{filepath}': {e}")

def store(filepath, content):
    try:
        content = str(content).replace('\\n', '\n')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return None
    except Exception as e:
        raise RuntimeError(f"Failed to write to file '{filepath}': {e}")

def append_to(filepath, content):
    try:
        content = str(content).replace('\\n', '\n')
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(content)
        return None
    except Exception as e:
        raise RuntimeError(f"Failed to append to file '{filepath}: {e}")