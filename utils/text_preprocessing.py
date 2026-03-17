import re

def preprocess_text(text):
    text = text.lower()

    # keep letters, numbers, and sentence punctuation
    text = re.sub(r"[^a-z0-9\s\.\!\?]", "", text)

    # normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()