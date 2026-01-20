from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import datetime
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config["SECRET_KEY"] = "super-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
    app.config["JWT_SECRET_KEY"] = "jwt-secret-key"
    app.config["UPLOAD_FOLDER"] = "uploads"

    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    db.init_app(app)
    jwt = JWTManager(app)

    # ---------------------- DATABASE MODELS ----------------------
    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(100), unique=True, nullable=False)
        email = db.Column(db.String(200), unique=True, nullable=False)
        password = db.Column(db.String(200), nullable=False)

    class Document(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        filename = db.Column(db.String(200))
        text_length = db.Column(db.Integer)
        max_similarity = db.Column(db.Float)
        ai_generated_prob = db.Column(db.Float)

    app.User = User
    app.Document = Document

    # ---------------------- CREATE TABLES ----------------------
    with app.app_context():
        db.create_all()

    # ---------------------- AUTH ROUTES ----------------------
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            user = User.query.filter_by(username=username).first()
            if not user or not check_password_hash(user.password, password):
                return render_template("login.html", error="Invalid login")

            access_token = create_access_token(
                identity=user.id,
                expires_delta=datetime.timedelta(hours=6)
            )
            return redirect(url_for("dashboard", token=access_token))

        return render_template("login.html")

    @app.route("/create_user", methods=["GET", "POST"])
    def create_user():
        if request.method == "POST":
            username = request.form["username"]
            email = request.form["email"]
            password = generate_password_hash(request.form["password"])

            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for("list_users"))

        return render_template("create_user.html")

    @app.route("/users")
    def list_users():
        users = User.query.all()
        return render_template("users.html", users=users)

    @app.route("/edit_user/<int:id>", methods=["GET", "POST"])
    def edit_user(id):
        user = User.query.get(id)

        if request.method == "POST":
            user.username = request.form["username"]
            user.email = request.form["email"]
            if request.form["password"]:
                user.password = generate_password_hash(request.form["password"])
            db.session.commit()
            return redirect(url_for("list_users"))

        return render_template("edit_user.html", user=user)

    @app.route("/delete_user/<int:id>")
    def delete_user(id):
        user = User.query.get(id)
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for("list_users"))

    # ---------------------- ADMIN DASHBOARD ----------------------
    @app.route("/dashboard")
    def dashboard():
        documents = Document.query.all()
        return render_template("dashboard.html", documents=documents)

    # ---------------------- FILE UPLOAD API ----------------------
    @app.route("/api/upload", methods=["POST"])
    def upload_api():
        file = request.files["file"]
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        # Dummy processing
        text_length = 14
        similarity = 1.0
        ai_prob = 0.0

        new_doc = Document(
            filename=file.filename,
            text_length=text_length,
            max_similarity=similarity,
            ai_generated_prob=ai_prob,
        )

        db.session.add(new_doc)
        db.session.commit()

        return jsonify({
            "msg": "File uploaded",
            "document_id": new_doc.id,
            "text_length": text_length,
            "max_similarity": similarity,
            "ai_generated_prob": ai_prob
        })

    # ---------------------- INDEX PAGE ----------------------
    @app.route("/")
    def index():
        return render_template("index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
