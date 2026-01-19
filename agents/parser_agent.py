import re
class HumanInTheLoopRequired(Exception):
    pass


def build_parser_input(
    input_type: str,
    original_input,
    extracted_text: str,
    confidence: float,
    user_confirmed: bool
):
    """
    Builds the canonical input object for the Parser Agent.
    """

    if input_type not in ["image", "audio", "text"]:
        raise ValueError("Invalid input_type")

    if not user_confirmed:
        raise HumanInTheLoopRequired(
            "User did not confirm extracted text"
        )

    if confidence < 0.75 and not user_confirmed:
        raise HumanInTheLoopRequired(
        "Low OCR/ASR confidence. Please review and confirm the text."
    )

    return {
        "input_type": input_type,          # "image" | "audio" | "text"
        "original_input": original_input,
        "extracted_text": extracted_text,
        "confidence": confidence,
        "user_confirmed": user_confirmed
    }



class ParserAgent:

    def parse(self, parser_input: dict) -> dict:
        text = self._clean_text(parser_input["extracted_text"])

        topic = self._detect_topic(text)
        variables = self._extract_variables(text)
        constraints = self._extract_constraints(text)
        needs_clarification, reason = self._detect_ambiguity(text)

        if needs_clarification:
            raise HumanInTheLoopRequired(reason)

        return {
            "problem_text": text,
            "topic": topic,
            "variables": variables,
            "constraints": constraints,
            "needs_clarification": False,
            "clarification_reason": None
        }
    
    def _clean_text(self, text: str) -> str:
        text = text.replace("÷", "/").replace("×", "*")
        text = re.sub(r"\s+", " ", text)
        return text.strip()
    
    def _detect_topic(self, text: str) -> str:
        t = text.lower()
        if any(w in t for w in ["integral", "derivative", "limit"]):
            return "calculus"
        if any(w in t for w in ["matrix", "determinant", "eigen"]):
            return "linear_algebra"
        if any(w in t for w in ["probability", "dice", "coin", "random"]):
            return "probability"
        return "algebra"
    
    def _extract_variables(self, text: str) -> list:
        return sorted(set(re.findall(r"\b[a-zA-Z]\b", text)))
    
    def _extract_constraints(self, text: str) -> list:
        constraints = []
        if "x > 0" in text:
            constraints.append("x > 0")
        if "x >= 0" in text or "x ≥ 0" in text:
            constraints.append("x >= 0")
        return constraints

    def _detect_ambiguity(self, text: str) -> tuple:
        ambiguous_terms = ["something", "approx", "around", "etc"]

        for term in ambiguous_terms:
            if term in text.lower():
                return True, f"Ambiguous phrase detected: '{term}'"

        if len(text.strip()) < 10:
            return True, "Problem statement too short"

        return False, None