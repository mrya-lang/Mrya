def evaluate_binary_expression(left, operator, right):
    try:
        if operator == '+':
            return left + right
        elif operator == '-':
            return left - right
        elif operator == '*':
            return left * right
        elif operator == '/':
            if right == 0:
                raise ZeroDivisionError("Division by zero is not allowed.")
            return left / right
        else:
            raise ValueError(f"Unknown operator: {operator}")
    except ZeroDivisionError as e:
        raise RuntimeError(str(e))
    except Exception as e:
        raise RuntimeError(f"Math Error: {str(e)}") 
    
    