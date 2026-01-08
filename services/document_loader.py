from PyPDF2 import PdfReader
from docx import Document

def load_document(file):
    if file.filename.endswith(".pdf"):
        reader = PdfReader(file.file)
        return " ".join([p.extract_text() for p in reader.pages])

    elif file.filename.endswith(".docx"):
        doc = Document(file.file)
        return " ".join([p.text for p in doc.paragraphs])

    elif file.filename.endswith(".txt"):
        return file.file.read().decode("utf-8")

    else:
        raise ValueError("Unsupported file type")
