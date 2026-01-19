import whisper
import re

model = whisper.load_model("base")

def whisper_transcribe(audio_path: str):
    result = model.transcribe(audio_path)

    raw_text = result.get("text", "").strip()
    confidence = estimate_confidence(result)

    normalized_text = normalize_math_phrases(raw_text)

    return normalized_text, confidence


def normalize_math_phrases(text: str) -> str:
    replacements = {
        r"square root of": "√",
        r"raised to the power of": "^",
        r"raised to": "^",
        r"divided by": "/",
        r"times": "*",
        r"minus": "-",
        r"plus": "+",
        r"equal to": "=",
        r"integral of": "∫",
        r"limit x tends to": "lim x→"
    }

    normalized = text.lower()
    for k, v in replacements.items():
        normalized = re.sub(k, v, normalized)

    return re.sub(r"\s+", " ", normalized).strip()


def estimate_confidence(result: dict) -> float:
    segments = result.get("segments", [])
    if not segments:
        return 0.5

    logprobs = [seg.get("avg_logprob", -1.0) for seg in segments]
    avg = sum(logprobs) / len(logprobs)

    return min(max((avg + 1) / 1, 0.0), 1.0)
