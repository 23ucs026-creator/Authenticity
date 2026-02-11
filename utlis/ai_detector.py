import re
import numpy as np

def sentence_lengths(text):
    sentences = re.split(r'[.!?]', text)
    lengths = [len(s.split()) for s in sentences if len(s.split()) > 0]
    return lengths

def lexical_diversity(text):
    words = text.split()
    if not words:
        return 0
    return len(set(words)) / len(words)

def ai_probability_score(text):
    """
    Simple heuristic AI detection:
    - Very uniform sentence length → more AI-like
    - Low lexical diversity → more AI-like
    Returns probability between 0–1
    """

    lengths = sentence_lengths(text)

    if len(lengths) < 2:
        return 0.0

    variance = np.var(lengths)
    diversity = lexical_diversity(text)

    # Heuristic thresholds (adjustable)
    variance_score = 1 / (1 + variance)   # low variance → higher score
    diversity_score = 1 - diversity       # low diversity → higher score

    score = (variance_score + diversity_score) / 2

    # clamp between 0 and 1
    return float(max(0.0, min(score, 1.0)))
