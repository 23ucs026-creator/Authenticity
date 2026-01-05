import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from extensions import db
from models.document import Document

document_bp = Blueprint("documents", __name__)

ALLOWED_EXT = {"pdf", "docx", "txt"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


@document_bp.route("/documents/upload", methods=["POST"])
@jwt_required()
def upload_document():
    # 1. Check file part
    if "file" not in request.files:
        return jsonify({"msg": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"msg": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"msg": "Unsupported file type"}), 400

    # 2. Save file to uploads folder
    filename = secure_filename(file.filename)
    upload_folder = os.path.join(current_app.root_path, "uploads")
    os.makedirs(upload_folder, exist_ok=True)
    path = os.path.join(upload_folder, filename)
    file.save(path)

    # 3. Get user id from JWT (stored as string, convert to int)
    user_id = int(get_jwt_identity())

    ext = filename.rsplit(".", 1)[1].lower()

    # 4. Create Document record (text extraction can be added later)
    doc = Document(
        user_id=user_id,
        filename=filename,
        file_type=ext,
        original_text=None,
    )
    db.session.add(doc)
    db.session.commit()

    return jsonify({"msg": "File uploaded", "document_id": doc.id}), 201
