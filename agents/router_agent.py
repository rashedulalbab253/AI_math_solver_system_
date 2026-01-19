class RouterAgent:
    """
    Routes based on mathematical structure, not wording.
    """

    def route(self, structured_problem: dict) -> str:
        text = structured_problem["problem_text"]

        # Normalize
        t = text.lower()

        # Optimization (must come first)
        if "minimum" in t or "maximum" in t:
            return "quadratic_optimization"

        # Any equation with '=' → solve
        if "=" in text:
            return "quadratic_equation"

        # Pure algebraic expression → factor
        if "x" in text:
            return "expression_analysis"

        return "unknown"
