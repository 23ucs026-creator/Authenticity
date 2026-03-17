import os
import pdfplumber
import docx


def extract_text_from_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".txt":
        return extract_txt(filepath)

    elif ext == ".pdf":
        return extract_pdf(filepath)

    elif ext == ".docx":
        return extract_docx(filepath)

    else:
        return ""


def extract_txt(filepath):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        print("TXT extraction error:", e)
        return ""


def extract_pdf(filepath):
    text = ""

    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()

                if extracted:
                    text += extracted + " "

    except Exception as e:
        print("PDF extraction error:", e)
        return ""

    return text


def extract_docx(filepath):
    try:
        doc = docx.Document(filepath)
        return " ".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print("DOCX extraction error:", e)
        return ""