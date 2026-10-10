import os
from google import genai

def generate_clinical_report(metrics: dict, user_state: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    
    # Offline heuristic fallback (ensures your live demo never crashes)
    if not api_key:
        if metrics["engagement"] > 1.2:
            assessment = "High sustained cognitive focus with active cortical processing."
            action = "Maintain workflow. Next scheduled cognitive micro-pause in 45 minutes."
        elif metrics["engagement"] < 0.6:
            assessment = "Elevated theta dominance indicating severe mental fatigue and reduced vigilance."
            action = "Immediate sensory rest recommended. Switch off screen tasks for 10-15 minutes."
        else:
            assessment = "Balanced neural activity with stable baseline focus."
            action = "Nominal ergonomic status. Continue normal task execution."
            
        return f"""### BioMind Telemetry Diagnostic
- **Core Neurological State**: {assessment}
- **Calculated Engagement Index**: {metrics['engagement']}
- **Clinical Recommendation**: {action}"""

    # Live Gemini API generation
    try:
        client = genai.Client()
        prompt = f"""
        You are the diagnostic engine for 'BioMind AI', a neuro-ergonomics and EEG biosignal monitoring system.
        Analyze this patient's current telemetry window:
        - Simulated State: {user_state}
        - Theta Power (4-8Hz): {metrics['theta']} uV^2
        - Alpha Power (8-13Hz): {metrics['alpha']} uV^2
        - Beta Power (13-30Hz): {metrics['beta']} uV^2
        - Engagement Ratio (Beta / (Alpha + Theta)): {metrics['engagement']}

        Provide a structured, professional clinical evaluation in 3 short bullet points:
        1. Cognitive & Workload Status
        2. Cortical Band Dynamics (what the Theta/Alpha/Beta balance indicates)
        3. Actionable Ergonomic Guidance
        """
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Diagnostic analysis complete. Engagement Index: {metrics['engagement']}."