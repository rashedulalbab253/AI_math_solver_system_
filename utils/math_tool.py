def safe_eval(expression: str):
    allowed_chars = "0123456789+-*/().^ "
    for c in expression:
        if c not in allowed_chars:
            raise ValueError("Unsafe expression")

    expression = expression.replace("^", "**")
    return eval(expression)
