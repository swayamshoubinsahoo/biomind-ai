import io
from pypdf import PdfReader
from PIL import Image

def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def parse_report_data(uploaded_file):
    file_type = uploaded_file.name.split(".")[-1].lower()
    
    if file_type == "pdf":
        raw_text = extract_text_from_pdf(uploaded_file)
        return {"type": "text", "content": raw_text}
    elif file_type in ["jpg", "jpeg", "png"]:
        image = Image.open(uploaded_file)
        return {"type": "image", "content": image}
    else:
        return {"type": "unknown", "content": None}

def evaluate_biomarkers_demo(biomarker_dict):
    """
    Standard reference range evaluator to flag critical alerts.
    """
    ranges = {
        "HbA1c": (4.0, 5.6, "%"),
        "Fasting Blood Sugar": (70, 100, "mg/dL"),
        "Total Cholesterol": (125, 200, "mg/dL"),
        "Hemoglobin": (12.0, 17.5, "g/dL"),
        "Troponin": (0.0, 0.04, "ng/mL")
    }
    
    triage = []
    for marker, (low, high, unit) in ranges.items():
        if marker in biomarker_dict:
            val = biomarker_dict[marker]
            status = "Normal"
            if val < low:
                status = "Low"
            elif val > high:
                status = "Elevated"
            triage.append({"Biomarker": marker, "Value": f"{val} {unit}", "Normal Range": f"{low} - {high} {unit}", "Status": status})
            
    return triage