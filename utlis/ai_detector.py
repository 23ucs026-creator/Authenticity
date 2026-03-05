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
    words = text.split()
    if len(words) < 50:
        return 0.0

    lengths = sentence_lengths(text)
    if len(lengths) < 2:
        return 0.0

    variance = np.var(lengths)
    diversity = lexical_diversity(text)

    burst = np.std(lengths) / (np.mean(lengths) + 1e-5)

    variance_score = 1 / (1 + variance)
    diversity_score = 1 - diversity
    burst_score = 1 / (1 + burst)

    score = (variance_score + diversity_score + burst_score) / 3

    return float(max(0.0, min(score, 1.0)))