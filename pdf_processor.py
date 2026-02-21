from google.cloud import vision
from google.oauth2 import service_account
import io
import re

# Load Vision credentials
credentials = service_account.Credentials.from_service_account_file(
    "vision_key.json"
)

client = vision.ImageAnnotatorClient(credentials=credentials)


def extract_text_from_pdf(file_input):
    """
    Accepts either:
    - Streamlit UploadedFile
    - File path string
    """

    # Case 1: Streamlit UploadedFile
    if hasattr(file_input, "read"):
        file_input.seek(0)
        content = file_input.read()

    # Case 2: Normal file path
    else:
        with io.open(file_input, "rb") as pdf_file:
            content = pdf_file.read()

    input_config = vision.InputConfig(
        content=content,
        mime_type="application/pdf"
    )

    feature = vision.Feature(
        type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION
    )

    request = vision.AnnotateFileRequest(
        input_config=input_config,
        features=[feature]
    )

    response = client.batch_annotate_files(requests=[request])

    text = ""

    for res in response.responses[0].responses:
        if res.full_text_annotation:
            text += res.full_text_annotation.text

    return text


def clean_ocr_text(text):
    text = re.sub(r'-\s+', '', text)
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    text = re.sub(r'\s([?.!,])', r'\1', text)
    return text.strip()


def split_into_paragraphs(text):
    paragraphs = re.split(r'(?<=\.)\s+(?=[A-Z])', text)
    return paragraphs