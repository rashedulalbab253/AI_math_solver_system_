import sympy as sp


class VerifierAgent:
    """
    Verifies correctness of solver output.
    Conservative: only fails if solution is clearly invalid.
    """

    def verify(self, structured_problem: dict, solution: dict) -> dict:
        final_answer = solution.get("final_answer", "")

        # Empty answer → invalid
        if not final_answer:
            return {
                "is_valid": False,
                "reason": "Empty solution."
            }

        # Rejects Invalid answer
        if "invalid answer format" in solution["final_answer"].lower():
            return {
                "is_valid": False,
                "reason": "Solver produced an answer inconsistent with problem intent."
            }
    
        # If solver explicitly says it cannot solve
        if "could not" in final_answer.lower():
            return {
                "is_valid": False,
                "reason": "Solver failed to compute solution."
            }

        # Otherwise accept
        return {
            "is_valid": True
        }
