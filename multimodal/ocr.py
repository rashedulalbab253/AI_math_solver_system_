import easyocr
import numpy as np
import re

reader = None

def _get_reader():
    global reader
    if reader is None:
        reader = easyocr.Reader(['en'], gpu=False)
    return reader

def run_ocr(image:np.ndarray):
    """
    image: numpy.ndarray (RGB)

    """
    reader_instance = _get_reader()
    results = reader_instance.readtext(image)

    if not results:
        return "", 0.0

    texts = []
    confidences = []

    for (_, text, conf) in results:
        texts.append(text)
        confidences.append(conf)

    combined_text = " ".join(texts)
    combined_text = normalize_math_ocr(combined_text)
    avg_confidence = float(np.mean(confidences))

    return combined_text, avg_confidence

def normalize_math_ocr(text: str) -> str:
    """
    Fix common OCR mistakes in math expressions.
    """
    text = re.sub(r'([a-zA-Z])\s*2\b', r'\1^2', text)
    text = re.sub(r'([a-zA-Z])\s*22\b', r'\1^2', text)
    text = re.sub(r'\b22\b', '^2', text)

    return text
