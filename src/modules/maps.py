def create_map(*args):
    if len(args) % 2 != 0:
        raise RuntimeError("map() required even number of arguments (key-value pairs).")
    result = {}
    for i in range(0, len(args), 2):
        key = args[i]
        value = args[i + 1]
        result[key] = value
    return result

def get_key(m, key):
    if key not in m:
        raise RuntimeError(f"Key '{key}' not found in map.")
    return m[key]

def set_key(m, key, value):
    m[key] = value
    return None

def has_key(m, key):
    return key in m

def keys(m):
    return list(m.keys())

def values(m):
    return list(m.values())

def delete_key(m, key):
    if key in m:
        del m[key]
        return True
    return False

def map_set(m, key, value):
    if not isinstance(m, dict):
        raise RuntimeError("Mrya Error: map_set expected a map.")
    m[key] = value
    return m