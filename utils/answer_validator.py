import re


class AnswerValidator:
    """
    Validates solver output against expected answer type.
    """

    @staticmethod
    def validate(route: str, final_answer: str) -> bool:
        if not final_answer or not isinstance(final_answer, str):
            return False

        answer = final_answer.lower()

        # -------- Quadratic equation --------
        if route == "quadratic_equation":
            # Must solve for x
            return bool(
                re.search(r"x\s*=", answer) or
                re.search(r"x\s*∈", answer)
            )

        # -------- Quadratic optimization --------
        if route == "quadratic_optimization":
            # Must mention k or minimum/maximum
            return (
                "k =" in answer or
                "minimum" in answer or
                "maximum" in answer
            )

        # -------- Expression analysis --------
        if route == "expression_analysis":
            # Must return expression, not x or k
            return not (
                "x =" in answer or
                "k =" in answer
            )

        return False
