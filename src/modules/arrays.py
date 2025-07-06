def create(*elements):
    return list(elements)

def get(lst, index):
    try:
        return lst[int(index)]
    except (IndexError, ValueError):
        raise RuntimeError(f"Index {index} out of range or invalid.")

def set(lst, index, value):
    try:
        lst[int(index)] = value
        return None
    except (IndexError, ValueError):
        raise RuntimeError(f"Index {index} out of range or invalid.")

def size(lst):
    return len(lst)

def push(lst, item):
    lst.append(item)
    return None

def pop(lst):
    if not lst:
        raise RuntimeError("Cannot pop from empty list.")
    return lst.pop()

def insert(lst, index, item):
    try:
        lst.insert(int(index), item)
        return None
    except ValueError:
        raise RuntimeError(f"Invalid index: {index}")

def remove(lst, index):
    try:
        return lst.pop(int(index))
    except (IndexError, ValueError):
        raise RuntimeError(f"Index {index} out of range or invalid.")
    
def slice(lst, start, end=None):
    try:
        start_idx = int(start)
        if end is not None:
            end_idx = int(end)
            return lst[start_idx:end_idx]
        else:
            return lst[start_idx:]
    except (ValueError, IndexError) as e:
        raise RuntimeError(f"Invalid slice indices: {start}, {end}") from e

