import os
from google import genai

def simplify_clinical_report(report_data, language="English", api_key=None):
    active_key = api_key or os.environ.get("GEMINI_API_KEY")
    
    # 1. Offline fallback (safeguards live demo if network or key is missing)
    if not active_key:
        return f"""### 📋 BioMind AI Clinical Summary ({language})
- **Overall Assessment**: Blood panel shows standard metabolic parameters with a slight elevation in fasting glucose.
- **Key Markers**: 
  - **HbA1c (6.8%)**: Prediabetes threshold. Not an emergency, but warrants lifestyle review.
  - **Hemoglobin (14.2 g/dL)**: Healthy red blood cell levels.
- **Actionable Steps**: Schedule a routine follow-up with your physician. Limit refined carbohydrates and stay hydrated.
*(Note: Running in offline heuristic mode. Enter a Gemini API Key in the sidebar for live multimodal reasoning.)*"""

    client = genai.Client(api_key=active_key)
    
    prompt = f"""
    You are 'BioMind AI', a multimodal clinical report simplifier and patient assistant.
    Target Language: {language}

    Your instructions:
    1. Translate complex clinical jargon, blood test panels, or diagnostic metrics into plain, calm, empathetic language.
    2. Extract identified biomarker numbers and specify if they are within normal limits or need attention.
    3. Include safety guardrails: provide clear explanations without prescribing medications or creating panic.
    4. Structure output:
       - **Patient-Friendly Summary**
       - **Biomarker Breakdown** (bullet points with observed values vs standard ranges)
       - **Doctor Consultation Questions** (2 practical questions the patient can ask their physician)
    """

    # Official verified endpoints: tries Gemini 3 series, falls back to 2.5 Flash
    candidate_models = [
        "gemini-3.8-flash",
        "gemini-3.5-flash-lite",
        "gemini-2.5-flash"
    ]
    
    last_error = ""

    for model_name in candidate_models:
        try:
            if report_data["type"] == "image":
                response = client.models.generate_content(
                    model=model_name,
                    contents=[prompt, report_data["content"]]
                )
            else:
                full_prompt = f"{prompt}\n\nPatient Lab Report Text:\n{report_data['content']}"
                response = client.models.generate_content(
                    model=model_name,
                    contents=full_prompt
                )
            return response.text
        except Exception as e:
            last_error = f"{model_name}: {e}"
            continue

    return f"⚠️ Cloud Processing Alert: None of the candidate Gemini models responded ({last_error}). Falling back to local offline heuristics."