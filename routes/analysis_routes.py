from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.document import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.download('punkt', quiet=True)

analysis_bp = Blueprint("analysis", __name__)

def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text.lower())
    return ' '.join([w for w in tokens if w.isalnum() and w not in stop_words])

@analysis_bp.route("/documents/<int:doc_id>/plagiarism", methods=["POST"])
@jwt_required()
def check_plagiarism(doc_id):
    user_id = get_jwt_identity()
    doc = Document.query.filter_by(id=doc_id, user_id=user_id).first()
    if not doc or not doc.original_text:
        return jsonify({"msg": "Document not found or no text"}), 404
    
    data = request.get_json()
    reference_texts = data.get("references", [])  # List of reference document texts
    
    if not reference_texts:
        return jsonify({"msg": "No reference texts provided"}), 400
    
    # Preprocess all texts
    target_text = preprocess_text(doc.original_text)
    ref_texts = [preprocess_text(ref) for ref in reference_texts]
    all_texts = [target_text] + ref_texts
    
    # TF-IDF vectorization
    vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    
    # Cosine similarities
    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
    
    results = [{"similarity": float(sim), "percentage": f"{float(sim)*100:.1f}%"} for sim in similarities]
    max_similarity = max(results, key=lambda x: x["similarity"])
    
    return jsonify({
        "document_id": doc_id,
        "plagiarism_risk": max_similarity["percentage"],
        "all_scores": results,
        "status": "High" if float(max_similarity["similarity"]) > 0.3 else "Low"
    }), 200
