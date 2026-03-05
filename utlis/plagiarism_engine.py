from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def check_plagiarism(new_text, documents):

    if not documents:
        return 0, []

    texts = [doc.original_text for doc in documents]  # ✅ FIXED
    texts.append(new_text)

    vectorizer = TfidfVectorizer(stop_words="english")

    tfidf_matrix = vectorizer.fit_transform(texts)

    similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])[0]

    similarity_report = []

    for i, score in enumerate(similarities):

        similarity_report.append({
            "document_id": documents[i].id,
            "filename": documents[i].filename,
            "similarity": round(score * 100, 2)
        })

    plagiarism_score = max(similarities) * 100

    return round(plagiarism_score, 2), similarity_report