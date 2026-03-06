import difflib
import re

def split_sentences(text):
    return re.split(r'[.!?]', text)


def similarity(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()


def check_plagiarism(new_text, documents):

    new_sentences = split_sentences(new_text)

    report = []
    highest_score = 0

    for doc in documents:

        if not doc.original_text:
            continue

        existing_sentences = split_sentences(doc.original_text)

        for s1 in new_sentences:
            for s2 in existing_sentences:

                score = similarity(s1.strip(), s2.strip())

                if score > 0.75:   # similarity threshold

                    percent = round(score * 100, 2)

                    report.append({
                        "matched_sentence": s1.strip(),
                        "source_document": doc.filename,
                        "similarity": percent
                    })

                    if percent > highest_score:
                        highest_score = percent

    return highest_score, report