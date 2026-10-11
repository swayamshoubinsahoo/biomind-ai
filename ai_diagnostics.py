import os
from google import genai

def simplify_clinical_report(report_data, language="English", api_key=None):
    key = api_key or os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=key)

    prompt = f"""
You are BioMind AI, an expert clinical report assistant.
Analyze this diagnostic lab report thoroughly and return your response in {language}.

Format your output strictly with these sections:
**Patient-Friendly Summary**
Provide a calm, clear summary of what test was conducted and the key takeaway.

**Biomarker Breakdown**
List each biomarker parameter, observed value, standard biological reference range, and status (Normal, Low, or Elevated).

**Doctor Consultation Questions**
Provide 2 practical, relevant questions the patient can ask their physician.
"""

    # Multi-tier resilient fallback: tries fastest vision endpoints first,
    # silently cascades to battle-tested 1.5 baselines if busy or throttled.
    candidate_models = [
        "gemini-2.5-flash",
        "gemini-1.5-flash",
        "gemini-2.0-flash",
        "gemini-3.8-flash",
        "gemini-3.5-flash-lite",
        "gemini-3.1-pro-preview",
        "gemini-2.5-pro",
        "gemini-1.5-pro"
    ]

    last_error = ""

    for model_name in candidate_models:
        try:
            content_input = report_data["content"]
            response = client.models.generate_content(
                model=model_name,
                contents=[content_input, prompt]
            )

            if response and response.text:
                return response.text

        except Exception as e:
            last_error = str(e)
            continue

    return f"Unable to parse report: {last_error}"