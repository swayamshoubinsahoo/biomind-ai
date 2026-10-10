import os
from google import genai

def simplify_clinical_report(report_data, language="English"):
    api_key = os.environ.get("GEMINI_API_KEY")
    
    # Offline fallback (vital for demo safety if venue Wi-Fi fails)
    if not api_key:
        return f"""### 📋 BioMind AI Clinical Summary ({language})
- **Overall Assessment**: Your blood panel shows typical metabolic parameters, with a slight elevation in fasting glucose.
- **Key Markers**: 
  - **HbA1c (6.2%)**: Prediabetes threshold. Not an emergency, but warrants lifestyle review.
  - **Hemoglobin (13.8 g/dL)**: Healthy red blood cell levels.
- **Actionable Steps**: Schedule a routine follow-up with your physician. Limit refined sugars and maintain daily hydration.
*(Note: Offline mode. Connect GEMINI_API_KEY for live OCR dynamic parsing.)*"""

    client = genai.Client()
    
    prompt = f"""
    You are 'BioMind AI', a multimodal clinical report simplifier and patient assistant.
    Target Language: {language}

    Your instructions:
    1. Translate complex clinical jargon, blood test panels, or ECG metrics into plain, calm, empathetic language.
    2. Extract identified biomarker numbers and specify if they are within normal limits or need attention.
    3. Include safety guardrails: provide clear explanations without prescribing medications or creating panic.
    4. Structure output:
       - **Patient-Friendly Summary**
       - **Biomarker Breakdown** (bullet points)
       - **Doctor Consultation Questions** (2 practical questions the patient can ask their physician)
    """

    try:
        if report_data["type"] == "image":
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt, report_data["content"]]
            )
        else:
            full_prompt = f"{prompt}\n\nPatient Lab Report Text:\n{report_data['content']}"
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt
            )
        return response.text
    except Exception as e:
        return f"BioMind AI Processing notice: {e}"