from flask import Flask, request, render_template, redirect, url_for, session, jsonify, flash

from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

from extensions import db, jwt
from models.user import User
from models.document import Document

from utils.text_extractor import extract_text_from_file
from utils.plagiarism import calculate_plagiarism,clean_text
from utils.ai_detector import ai_probability_score
from utils.text_preprocessing import preprocess_text

import io
import base64
import matplotlib.pyplot as plt
import numpy as np

from utils.plagiarism_engine import check_plagiarism
from models.document import Document
import json

from utils.analytics import generate_plagiarism_chart



def create_app():
    app = Flask(__name__)
    CORS(app)

    # ---------------- PATHS ----------------
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
    UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

    os.makedirs(INSTANCE_DIR, exist_ok=True)
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # ---------------- CONFIG ----------------
    app.config["SECRET_KEY"] = "super-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(INSTANCE_DIR, 'site.db')}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = UPLOAD_DIR

    # ---------------- INIT ----------------
    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        db.create_all()

    # ---------------- ROUTES ----------------
    @app.route("/")
    def index():
        return redirect(url_for("login"))


    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]

            user = User.query.filter_by(username=username).first()
            if not user or not check_password_hash(user.password, password):
                return render_template("auth.html", error="Invalid credentials")

            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role   # ✅ ADD THIS

            if user.role == "admin":
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("dashboard"))

        return render_template("auth.html")



    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.route("/create_user", methods=["GET", "POST"])
    def create_user():
        if request.method == "POST":
            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]

            existing_user = User.query.filter(
                (User.username == username) | (User.email == email)
            ).first()

        if existing_user:
            return render_template("create_user.html", error="Username or Email already exists")

        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            role="user"
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))


    @app.route("/dashboard")
    def dashboard():
        if "user_id" not in session:
            return redirect(url_for("login"))

        docs = Document.query.all()
        return render_template("dashboard.html", documents=docs)

    
    @app.route("/admin")
    def admin_dashboard():

        if session.get("role") != "admin":
            return redirect(url_for("dashboard"))

        total_users = User.query.count()

        docs = Document.query.all()

        total_docs = len(docs)

        avg_plagiarism = round(
            sum(d.plagiarism_score for d in docs) / total_docs, 2
        )   if total_docs > 0 else 0

        avg_ai = round(
            sum(d.ai_generated_prob for d in docs) / total_docs, 2
        ) if total_docs > 0 else 0

        max_plagiarism = max(
            (d.plagiarism_score for d in docs),
            default=0
        )

        # ✅ ADD THIS HERE
        scores = [d.plagiarism_score for d in docs]
        generate_plagiarism_chart(scores)

        return render_template(
            "admin_dashboard.html",
            total_users=total_users,
            total_docs=total_docs,
            avg_plagiarism=avg_plagiarism,
            avg_ai=avg_ai,
            max_plagiarism=max_plagiarism,
            documents=docs
        )
    
    @app.route("/similarity-graph")
    def similarity_graph():
        docs = Document.query.all()
        texts = [d.original_text for d in docs if d.original_text]

        if len(texts) < 2:
            return "Not enough documents to compare"

        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(texts)
        similarity_matrix = cosine_similarity(tfidf_matrix)

        # Plot heatmap
        fig, ax = plt.subplots()
        cax = ax.matshow(similarity_matrix)
        fig.colorbar(cax)

        plt.title("Document Similarity Matrix")

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)

        image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        plt.close()

        return render_template(
            "similarity_graph.html",
            image=image_base64
        )

    @app.route("/document/<int:doc_id>")
    def document_detail(doc_id):

        doc = Document.query.get_or_404(doc_id)

        report = []

        if doc.similarity_report:
            report = json.loads(doc.similarity_report)

        return render_template(
            "document_detail.html",
            doc=doc,
            report=report
    )


    @app.route("/upload", methods=["GET", "POST"])
    def upload():
        if "user_id" not in session:
            return redirect(url_for("login"))

        if request.method == "POST":
            file = request.files.get("file")
            if not file or file.filename == "":
                return "No file selected", 400

            filename = secure_filename(file.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(path)

            # 1️⃣ Extract text
            text = extract_text_from_file(path)

            if not text or not text.strip():
                return "No readable text found", 400

            # 2️⃣ Clean text
            processed_text = preprocess_text(text)

            # 3️⃣ Get existing documents
            existing_docs = Document.query.all()

            # 4️⃣ Calculate plagiarism
            plagiarism_score, similarity_report = check_plagiarism(processed_text, existing_docs)

            # 5️⃣ Calculate AI probability
            ai_prob = round(ai_probability_score(processed_text), 2)

            print("TEXT LENGTH:", len(processed_text))
            print("AI SCORE:", ai_prob)

            # 6️⃣ Save to DB
            doc = Document(
                user_id=session["user_id"],
                filename=filename,
                file_type=filename.rsplit(".", 1)[-1],
                original_text=processed_text,
                plagiarism_score=plagiarism_score,
                ai_generated_prob=ai_prob,
                similarity_report=json.dumps(similarity_report)
            )

            db.session.add(doc)
            db.session.commit()

            flash("File uploaded and analyzed successfully!")
            return redirect(url_for("dashboard"))

    

        return render_template("upload.html")



    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
