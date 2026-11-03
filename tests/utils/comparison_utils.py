def is_match(a, b):
    """convert and Compare two values ,ignore case."""
    try:
        return str(a).casefold() == str(b).casefold()
    except Exception:
        return False

def is_not_match(a, b):
    """call existing is_match function and flip the result using 'not'
    Returns True if the values are different, False if they match."""
    return not is_match(a, b)

# for equal , convert to string for matching action
# def is_EQ(a, b):
#     """convert Compare two values as int."""
#     try:
#         return int(a) == int(b)
#     except Exception:
#         return False

def is_GT(a, b):
    """convert Compare two values as int."""
    try:
        return int(a) > int(b)
    except Exception:
        return False

def is_GTE(a, b):
    """convert Compare two values as int."""
    try:
        return int(a) >= int(b)
    except Exception:
        return False

def is_LT(a, b):
    """convert Compare two values as int."""
    try:
        return int(a) < int(b)
    except Exception:
        return False

def is_LTE(a, b):
    """convert Compare two values as int."""
    try:
        return int(a) <= int(b)
    except Exception:
        return False