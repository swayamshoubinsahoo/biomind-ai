import streamlit as st
import pandas as pd
from processor import parse_report_data, evaluate_biomarkers_demo
from ai_diagnostics import simplify_clinical_report

st.set_page_config(page_title="BioMind AI", page_icon="🏥", layout="wide")

st.title("🏥 BioMind AI — Clinical Report Simplifier & Patient Assistant")
st.caption("Powered by Gemini Multimodal Vision • Biomedical Engineering Track • Adamas University")

# Sidebar Configuration
st.sidebar.header("Configuration")
api_key_input = st.sidebar.text_input(
    "Gemini API Key (Optional)", 
    type="password", 
    help="Enter your Google AI Studio API key to enable live cloud multimodal vision parsing."
)
lang = st.sidebar.selectbox("Patient Vernacular Language", ["English", "Bengali (বাংলা)", "Hindi (हिन्दी)"])

st.sidebar.divider()
st.sidebar.subheader("Demo Sample Presets")
sample_choice = st.sidebar.selectbox("Or Load Pre-saved Lab Report", ["None", "Sample Diabetic Panel", "Sample Cardiac ECG & Troponin"])

uploaded_file = st.file_uploader("Upload Diagnostic Report (PDF, PNG, JPG)", type=["pdf", "png", "jpg", "jpeg"])

report_data = None

if uploaded_file:
    report_data = parse_report_data(uploaded_file)
    st.success(f"Loaded: {uploaded_file.name}")
elif sample_choice == "Sample Diabetic Panel":
    sample_text = "Patient: 48M. HbA1c: 6.8%. Fasting Blood Sugar: 135 mg/dL. Total Cholesterol: 210 mg/dL. Hemoglobin: 14.2 g/dL."
    report_data = {"type": "text", "content": sample_text}
    st.info("Loaded pre-configured sample: Diabetic & Lipid Panel")
elif sample_choice == "Sample Cardiac ECG & Troponin":
    sample_text = "Patient: 54F. Presenting with chest discomfort. Troponin: 0.08 ng/mL (High). Sinus tachycardia present. Fasting Blood Sugar: 95 mg/dL."
    report_data = {"type": "text", "content": sample_text}
    st.info("Loaded pre-configured sample: Cardiac Triage Panel")

if report_data and st.button("Analyze & Simplify Report", type="primary"):
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Biomarker Triage & Anomaly Flags")
        demo_metrics = {"HbA1c": 6.8, "Fasting Blood Sugar": 135, "Total Cholesterol": 210, "Hemoglobin": 14.2}
        if "Cardiac" in sample_choice:
            demo_metrics = {"Troponin": 0.08, "Fasting Blood Sugar": 95}
            
        triage_table = evaluate_biomarkers_demo(demo_metrics)
        df = pd.DataFrame(triage_table)
        st.dataframe(df, use_container_width=True)
        
        has_elevated = any(row["Status"] != "Normal" for row in triage_table)
        if has_elevated:
            st.error("⚠️ Automated Anomaly Alert: Out-of-range parameters identified. Prioritize physician review.")
        else:
            st.success("✅ All evaluated markers are within standard reference ranges.")

    with col2:
        st.subheader(f"2. Simplified Explanation ({lang})")
        with st.spinner("Translating medical terminology with safety guardrails..."):
            summary = simplify_clinical_report(report_data, language=lang, api_key=api_key_input)
            st.markdown(summary)
            
    st.divider()
    st.caption("🛡️ BioMind AI Safety Guardrail: Informational translation only. Does not replace certified medical diagnosis.")
else:
    st.write("Upload a diagnostic report above or select a demo sample from the sidebar to begin.")