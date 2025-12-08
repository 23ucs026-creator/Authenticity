# app.py
from flask import Flask
from extensions import db, jwt


def create_app():
    app = Flask(__name__)

    # ---- Config ----
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///auth_validator.db"
    app.config["SECRET_KEY"] = "change_this_secret"
    app.config["JWT_SECRET_KEY"] = "change_this_jwt_secret"

    # ---- Init extensions ----
    db.init_app(app)
    jwt.init_app(app)

    # ---- Register blueprints ----
    from routes.auth_routes import auth_bp
    from routes.document_routes import document_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(document_bp)

    # ---- Simple home route ----
    @app.route("/")
    def home():
        return "Authenticity Validator is running with DB and auth"

    # ---- Create tables ----
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
