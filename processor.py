import io
import fitz  # PyMuPDF
from PIL import Image

def process_file(uploaded_file):
    if uploaded_file is None:
        return None

    filename = uploaded_file.name.lower()

    if filename.endswith(".pdf"):
        # Convert first page of scanned PDF to high-res image
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        if len(doc) == 0:
            return None
        page = doc.load_page(0)
        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        return {"type": "image", "content": img}

    elif filename.endswith((".png", ".jpg", ".jpeg", ".webp")):
        img = Image.open(uploaded_file)
        return {"type": "image", "content": img}

    else:
        return {
            "type": "text",
            "content": uploaded_file.read().decode("utf-8", errors="ignore")
        }