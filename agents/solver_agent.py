import sympy as sp
import re
from utils.answer_validator import AnswerValidator


class SolverAgent:
    """
    SolverAgent handles mathematical solving using symbolic computation.
    Supports:
    - Quadratic equations
    - Quadratic optimization (min/max)
    - Expression analysis (factoring)
    """

    # -------------------------------------------------
    # PUBLIC ENTRY POINT
    # -------------------------------------------------
    def solve(self, structured_problem: dict, rag_context: list, route: str) -> dict:
        if route == "quadratic_equation":
            result = self._solve_quadratic_equation(structured_problem)

        elif route == "quadratic_optimization":
            result = self._solve_quadratic_optimization(structured_problem)

        elif route == "expression_analysis":
            result = self._analyze_expression(structured_problem)

        else:
            return {
                "final_answer": "Unsupported problem type.",
                "steps": [],
                "used_context": []
            }

        # -------- ANSWER-TYPE VALIDATION (FORMAT ONLY) --------
        if not AnswerValidator.validate(route, result.get("final_answer", "")):
            return {
                "final_answer": (
                    "The computed result does not match the expected answer type "
                    "for this problem."
                ),
                "steps": result.get("steps", []),
                "used_context": [],
                "error": "Answer-type validation failed"
            }

        return result

    # -------------------------------------------------
    # NORMALIZATION (CRITICAL)
    # -------------------------------------------------
    @staticmethod
    def normalize_math_text(text: str) -> str:
        """
        Converts human-readable / OCR math into SymPy-friendly syntax
        """
        replacements = {
            "²": "**2",
            "³": "**3",
            "–": "-",
            "−": "-",
            "^": "**",
            "×": "*",
            "·": "*",
        }

        for k, v in replacements.items():
            text = text.replace(k, v)

        # 2x -> 2*x
        text = re.sub(r"(\d)([a-zA-Z])", r"\1*\2", text)

        # )( -> )*(
        text = re.sub(r"\)\(", r")*(", text)

        return text.replace(" ", "")

    # -------------------------------------------------
    # 1. QUADRATIC EQUATION SOLVER
    # -------------------------------------------------
    def _solve_quadratic_equation(self, structured_problem):
        steps = []
        x = sp.symbols("x")
        text = structured_problem["problem_text"]

        steps.append("Identify the quadratic equation.")

        try:
            lhs, rhs = text.split("=")
            lhs = self.normalize_math_text(lhs)
            rhs = self.normalize_math_text(rhs)
            expr = sp.sympify(lhs) - sp.sympify(rhs)
        except Exception:
            return {
                "final_answer": "Could not parse the equation.",
                "steps": steps,
                "used_context": []
            }

        steps.append("Convert equation to standard form ax² + bx + c = 0.")

        try:
            solutions = sp.solve(expr, x)
        except Exception:
            return {
                "final_answer": "Could not solve the equation.",
                "steps": steps,
                "used_context": []
            }

        if not solutions:
            return {
                "final_answer": "No real solutions.",
                "steps": steps,
                "used_context": []
            }

        sol_str = ", ".join(str(sol) for sol in solutions)
        steps.append("Solve using symbolic computation.")

        return {
            "final_answer": f"x = {sol_str}",
            "steps": steps,
            "used_context": []
        }

    # -------------------------------------------------
    # 2. QUADRATIC OPTIMIZATION SOLVER
    # -------------------------------------------------
    def _solve_quadratic_optimization(self, structured_problem):
        steps = []
        x = sp.symbols("x")
        text = structured_problem["problem_text"]

        steps.append("Identify the quadratic function f(x).")

        try:
            fx_part = text.split(",")[0]
            expr_raw = fx_part.split("=")[1]
            expr = sp.sympify(self.normalize_math_text(expr_raw))
        except Exception:
            return {
                "final_answer": "Could not parse the function f(x).",
                "steps": steps,
                "used_context": []
            }

        steps.append("Differentiate f(x) to find the critical point.")

        derivative = sp.diff(expr, x)
        critical_points = sp.solve(derivative, x)

        if not critical_points:
            return {
                "final_answer": "No critical point found.",
                "steps": steps,
                "used_context": []
            }

        x_vertex = critical_points[0]
        steps.append(f"Critical point at x = {x_vertex}.")

        extremum_value = expr.subs(x, x_vertex)
        steps.append("Evaluate f(x) at the critical point.")

        # Extract minimum or maximum value if given
        match = re.search(r"(minimum|maxim(?:um)?) value\s*=?\s*([0-9\.\-]+)", text.lower())
        if match:
            given_val = sp.sympify(match.group(2))
            k_solution = sp.solve(extremum_value - given_val)

            if k_solution:
                steps.append("Solve for the unknown constant.")
                return {
                    "final_answer": f"k = {str(k_solution[0])}",
                    "steps": steps,
                    "used_context": []
                }

        return {
            "final_answer": f"Extremum value = {str(extremum_value)}",
            "steps": steps,
            "used_context": []
        }

    # -------------------------------------------------
    # 3. EXPRESSION ANALYSIS (FACTORING)
    # -------------------------------------------------
    def _analyze_expression(self, structured_problem):
        steps = []
        text = structured_problem["problem_text"]

        try:
            expr = sp.sympify(self.normalize_math_text(text))
            factored = sp.factor(expr)
        except Exception:
            return {
                "final_answer": "Could not analyze the expression.",
                "steps": steps,
                "used_context": []
            }

        steps.append("Factor the quadratic expression.")

        return {
            "final_answer": f"Factored form: {str(factored)}",
            "steps": steps,
            "used_context": []
        }
