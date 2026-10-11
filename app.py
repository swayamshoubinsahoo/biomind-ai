import streamlit as st
import pandas as pd
import re
import os
from processor import process_file
from ai_diagnostics import simplify_clinical_report

# Page Setup
st.set_page_config(
    page_title="BioMind AI — Clinical Report Simplifier",
    page_icon="📄",
    layout="wide"
)

# Header Section
st.title("📄 BioMind AI — Clinical Report Simplifier & Patient Assistant")
st.caption("Powered by Gemini Multimodal Vision • Biomedical Engineering Track • Adamas University")

# Sidebar Configuration
st.sidebar.header("⚙️ Configuration")
st.sidebar.caption("⚡ Engine: Auto-Adaptive Resilient Vision (Auto-Fallback)")

# 1. READ PERMANENT SECRET KEY
secret_key = ""
if "GEMINI_API_KEY" in st.secrets:
    secret_key = st.secrets["GEMINI_API_KEY"]
elif os.environ.get("GEMINI_API_KEY"):
    secret_key = os.environ.get("GEMINI_API_KEY")

api_key_input = st.sidebar.text_input(
    "Gemini API Key (optional if set in env/secrets)",
    value=secret_key,
    type="password"
)

lang = st.sidebar.selectbox(
    "Explanation Language",
    ["English", "Bengali", "Hindi", "Spanish", "French"],
    index=0
)

# 2. ALL 3 CLINICAL DEMO SAMPLES
SAMPLE_REPORTS = {
    "None": None,
    "Cardiac Triage Panel": {
        "text": "Troponin I: 0.08 ng/mL (Normal: 0.0 - 0.04 ng/mL) [ELEVATED]\nFasting Blood Sugar: 95 mg/dL (Normal: 70 - 100 mg/dL) [NORMAL]\nECG: Sinus Tachycardia, ST elevation noted in leads V1-V3.",
        "table": [
            {"Biomarker": "Fasting Blood Sugar", "Value": "95 mg/dL", "Normal Range": "70 - 100 mg/dL", "Status": "Normal"},
            {"Biomarker": "Troponin I", "Value": "0.08 ng/mL", "Normal Range": "0.0 - 0.04 ng/mL", "Status": "Elevated"},
        ]
    },
    "Complete Blood Count (CBC)": {
        "text": "Haemoglobin (Hb): 9.2 gm/dL (Reference Range: 13.0 - 17.0 gm/dL) [LOW]\nTotal RBC Count: 3.4 mill/cumm (Reference Range: 4.5 - 5.5 mill/cumm) [LOW]\nTotal Leucocyte Count (TLC): 7,800 /cumm (Reference Range: 4,000 - 11,000 /cumm) [NORMAL]\nPlatelet Count: 210,000 /cumm (Reference Range: 150,000 - 450,000 /cumm) [NORMAL]",
        "table": [
            {"Biomarker": "Haemoglobin (Hb)", "Value": "9.2 gm/dL", "Normal Range": "13.0 - 17.0 gm/dL", "Status": "Low"},
            {"Biomarker": "Total RBC Count", "Value": "3.4 mill/cumm", "Normal Range": "4.5 - 5.5 mill/cumm", "Status": "Low"},
            {"Biomarker": "Total Leucocyte Count", "Value": "7,800 /cumm", "Normal Range": "4,000 - 11,000 /cumm", "Status": "Normal"},
            {"Biomarker": "Platelet Count", "Value": "210,000 /cumm", "Normal Range": "150,000 - 450,000 /cumm", "Status": "Normal"}
        ]
    },
    "Endocrine / Prolactin Panel": {
        "text": "Clinical Parameter: Serum Prolactin\nObserved Value: 42.5 ng/mL\nBiological Reference Interval: Non-pregnant Female: 4.8 - 23.3 ng/mL [ELEVATED]\nTSH: 2.1 uIU/mL (Reference Range: 0.4 - 4.2 uIU/mL) [NORMAL]",
        "table": [
            {"Biomarker": "Serum Prolactin", "Value": "42.5 ng/mL", "Normal Range": "4.8 - 23.3 ng/mL", "Status": "Elevated"},
            {"Biomarker": "TSH", "Value": "2.1 uIU/mL", "Normal Range": "0.4 - 4.2 uIU/mL", "Status": "Normal"}
        ]
    }
}

selected_sample = st.sidebar.selectbox("Load Demo Sample", list(SAMPLE_REPORTS.keys()), index=0)

# Main Area
uploaded_file = st.file_uploader(
    "Upload Diagnostic Report (PDF, PNG, JPG)",
    type=["pdf", "png", "jpg", "jpeg"]
)

report_data = None
triage_table = []

if uploaded_file is not None:
    report_data = process_file(uploaded_file)
    st.info(f"File uploaded: `{uploaded_file.name}` ready for extraction.")
elif selected_sample != "None":
    sample_info = SAMPLE_REPORTS[selected_sample]
    report_data = {"type": "text", "content": sample_info["text"]}
    triage_table = sample_info["table"]

# Run Analysis
if report_data is not None:
    if st.button("Analyze & Simplify Report", type="primary"):
        effective_key = api_key_input if api_key_input else secret_key
        
        col1, col2 = st.columns([1, 1])

        with col2:
            st.subheader(f"2. Simplified Explanation ({lang})")
            with st.spinner("Translating medical terminology with safety guardrails..."):
                summary = simplify_clinical_report(
                    report_data=report_data,
                    language=lang,
                    api_key=effective_key if effective_key else None
                )
                st.markdown(summary)

        with col1:
            st.subheader("1. Biomarker Triage & Anomaly Flags")
            
            if not triage_table:
                extracted_rows = []
                for line in summary.split("\n"):
                    if any(u in line.lower() for u in ["gm/dl", "mg/dl", "ng/ml", "/cumm", "%", "mmol/l"]):
                        status = "Elevated" if any(k in line.lower() for k in ["elevat", "high"]) else ("Low" if "low" in line.lower() else "Normal")
                        clean_line = re.sub(r"[*_#]", "", line).strip("- ")
                        parts = clean_line.split(":")
                        biomarker = parts[0].strip() if len(parts) > 1 else "Biomarker"
                        val = parts[1].strip() if len(parts) > 1 else clean_line
                        extracted_rows.append({
                            "Biomarker": biomarker,
                            "Value": val,
                            "Normal Range": "Standard Reference",
                            "Status": status
                        })
                triage_table = extracted_rows if extracted_rows else [
                    {"Biomarker": "Evaluated Biomarker", "Value": "See Summary", "Normal Range": "Standard Range", "Status": "Normal"}
                ]

            df = pd.DataFrame(triage_table)
            st.dataframe(df, use_container_width=True)

            has_elevated = any(row.get("Status") in ["Elevated", "Low", "Abnormal"] for row in triage_table)
            if has_elevated:
                st.error("⚠️ Automated Anomaly Alert: Out-of-range parameters identified. Prioritize physician review.")
            else:
                st.success("✅ All evaluated markers are within standard reference ranges.")

        st.divider()
        st.caption("🛡️ BioMind AI Safety Guardrail: Informational translation only. Does not replace certified medical diagnosis.")
else:
    st.write("Upload a diagnostic report above or select a demo sample from the sidebar to begin.")