import re
import numpy as np


def split_sentences(text):
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip()]


def sentence_lengths(text):
    sentences = split_sentences(text)
    return [len(s.split()) for s in sentences]


def lexical_diversity(text):
    words = text.lower().split()

    if len(words) == 0:
        return 0

    return len(set(words)) / len(words)


def repetition_score(text):

    words = text.lower().split()

    if len(words) == 0:
        return 0

    unique_words = set(words)

    repetition = 1 - (len(unique_words) / len(words))

    return repetition


def sentence_uniformity(lengths):

    if len(lengths) == 0:
        return 0

    std = np.std(lengths)
    mean = np.mean(lengths)

    return 1 / (1 + (std / (mean + 1e-5)))


def ai_probability_score(text):

    words = text.split()

    if len(words) < 40:
        return 0.0

    lengths = sentence_lengths(text)

    if len(lengths) < 2:
        return 0.0

    diversity = lexical_diversity(text)
    repetition = repetition_score(text)
    uniformity = sentence_uniformity(lengths)

    avg_sentence_length = np.mean(lengths)

    # scoring signals
    diversity_signal = 1 - diversity
    repetition_signal = repetition
    uniformity_signal = uniformity

    length_signal = min(avg_sentence_length / 25, 1)

    score = (
        0.30 * diversity_signal +
        0.25 * repetition_signal +
        0.25 * uniformity_signal +
        0.20 * length_signal
    )

    probability = score * 100

    return round(float(max(0.0, min(probability, 100))), 2)