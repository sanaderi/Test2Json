from fastapi import FastAPI, File, UploadFile, HTTPException
import fitz  # PyMuPDF
from pdf2image import convert_from_bytes
import pytesseract

app = FastAPI()

def is_text_pdf(file_bytes: bytes) -> bool:
    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for page in doc:
                if page.get_text().strip():
                    return True
    except Exception:
        return False
    return False

def extract_text_from_text_pdf(file_bytes: bytes) -> str:
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text.strip()

def extract_text_from_image_pdf(file_bytes: bytes) -> str:
    text = ""
    images = convert_from_bytes(file_bytes)
    for image in images:
        text += pytesseract.image_to_string(image)
    return text.strip()

@app.post("/extract-text/")
async def extract_text(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    contents = await file.read()
    if is_text_pdf(contents):
        extracted = extract_text_from_text_pdf(contents)
        mode = "text-based PDF"
    else:
        extracted = extract_text_from_image_pdf(contents)
        mode = "image-based PDF (OCR)"
    return {"mode": mode, "extracted_text": extracted}
