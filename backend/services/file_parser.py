# Path: intelligent_summarizer/backend/services/file_parser.py

from PyPDF2 import PdfReader
from docx import Document
from pdf2image import convert_from_path
import pytesseract
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

# Optional Tesseract path from environment
tesseract_path = os.getenv("TESSERACT_PATH")

if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path


def extract_text_from_pdf(file):
    text = ""

    try:
        reader = PdfReader(file)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    except Exception:
        pass

    if len(text.strip()) < 50:
        text = extract_text_from_scanned_pdf(file)

    return text.strip()


def extract_text_from_scanned_pdf(file):
    text = ""

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file.read())
        tmp_path = tmp.name

    try:
        images = convert_from_path(tmp_path)
        for img in images:
            text += pytesseract.image_to_string(img) + "\n"
    finally:
        os.remove(tmp_path)

    return text


def extract_text_from_docx(file):
    document = Document(file)
    return "\n".join([p.text for p in document.paragraphs]).strip()
