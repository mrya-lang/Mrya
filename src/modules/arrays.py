def create(*elements):
    return list(elements)

def get(lst, index):
    return lst[int(index)]

def set(lst, index, value):
    lst[int(index)] = value
    return None


def append(lst, value):
    lst.append(value)
    return None

def length(lst):
    return len(lst)
