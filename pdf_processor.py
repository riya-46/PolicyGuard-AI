import io
import re
import fitz  # PyMuPDF
from google.cloud import vision

def extract_text_from_pdf(uploaded_file):
    """
    Extract text from both:
    - Normal text PDFs
    - Scanned image PDFs using Google Vision OCR
    """

    text = ""

    # ---------------------------
    # Try normal text extraction
    # ---------------------------
    try:
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        for page in doc:
            text += page.get_text()

        # If sufficient text found, return directly
        if len(text.strip()) > 200:
            return text

    except Exception as e:
        print("Normal PDF extraction failed:", e)

    # ---------------------------
    # Fallback to OCR
    # ---------------------------
    try:
        client = vision.ImageAnnotatorClient()

        pdf_bytes = uploaded_file.getvalue()

        image = vision.Image(content=pdf_bytes)
        response = client.document_text_detection(image=image)

        if response.error.message:
            raise Exception(response.error.message)

        text = response.full_text_annotation.text
        return text

    except Exception as e:
        print("OCR extraction failed:", e)
        return ""



def clean_ocr_text(text):
    """
    Clean OCR noise
    """
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    return text.strip()