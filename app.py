import streamlit as st
import pandas as pd
import json
import re
from processor import process_file
from ai_diagnostics import simplify_clinical_report

# Configure Page
st.set_page_config(
    page_title="BioMind AI — Clinical Report Simplifier",
    page_icon="📄",
    layout="wide"
)

# Header Section
st.title("📄 BioMind AI — Clinical Report Simplifier & Patient Assistant")
st.caption("Powered by Gemini Multimodal Vision • Biomedical Engineering Track • Adamas University")

# Sidebar Controls
st.sidebar.header("⚙️ Configuration")

# Model Selection Dropdown (Gemini 3.x to 1.5)
AVAILABLE_MODELS = [
    # Gemini 3.x Series
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-pro-preview",
    # Gemini 2.5 Series
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    # Gemini 2.0 & 1.5 Baselines
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-1.5-flash-8b",
]

selected_model = st.sidebar.selectbox("Choose Gemini Model", AVAILABLE_MODELS, index=0)

api_key_input = st.sidebar.text_input(
    "Gemini API Key (optional if set in env)",
    type="password"
)

lang = st.sidebar.selectbox(
    "Explanation Language",
    ["English", "Hindi", "Bengali", "Spanish", "French"]
)

# Pre-configured demo samples
SAMPLE_REPORTS = {
    "None": None,
    "Cardiac Triage Panel": {
        "text": "Troponin I: 0.08 ng/mL (Normal: 0.0 - 0.04 ng/mL) [ELEVATED]\nFasting Blood Sugar: 95 mg/dL (Normal: 70 - 100 mg/dL) [NORMAL]\nECG: Sinus Tachycardia, ST elevation noted in leads V1-V3.",
        "table": [
            {"Biomarker": "Fasting Blood Sugar", "Value": "95 mg/dL", "Normal Range": "70 - 100 mg/dL", "Status": "Normal"},
            {"Biomarker": "Troponin", "Value": "0.08 ng/mL", "Normal Range": "0.0 - 0.04 ng/mL", "Status": "Elevated"},
        ]
    },
    "Complete Blood Count (CBC)": {
        "text": "Haemoglobin: 11.0 gm/dl (Reference: 11.0 - 13.0 gm/dl) [NORMAL]\nTotal WBC Count: 7500 /cumm (Reference: 4000 - 11000 /cumm) [NORMAL]\nPlatelet Count: 2.2 Lakhs /cumm (Reference: 1.5 - 4.5 Lakhs) [NORMAL]",
        "table": [
            {"Biomarker": "Haemoglobin", "Value": "11.0 gm/dl", "Normal Range": "11.0 - 13.0 gm/dl", "Status": "Normal"},
            {"Biomarker": "Total WBC Count", "Value": "7500 /cumm", "Normal Range": "4000 - 11000 /cumm", "Status": "Normal"},
            {"Biomarker": "Platelet Count", "Value": "2.2 Lakhs", "Normal Range": "1.5 - 4.5 Lakhs", "Status": "Normal"}
        ]
    }
}

selected_sample = st.sidebar.selectbox("Load Demo Sample", list(SAMPLE_REPORTS.keys()), index=0)

# Main File Upload
uploaded_file = st.file_uploader(
    "Upload Diagnostic Report (PDF, PNG, JPG)",
    type=["pdf", "png", "jpg", "jpeg"]
)

# State initialization
report_data = None
triage_table = []

if uploaded_file is not None:
    # Converts PDF/Image via processor.py
    report_data = process_file(uploaded_file)
    st.info(f"File uploaded: `{uploaded_file.name}` ready for extraction.")
elif selected_sample != "None":
    sample_info = SAMPLE_REPORTS[selected_sample]
    report_data = {"type": "text", "content": sample_info["text"]}
    triage_table = sample_info["table"]
    st.info(f"Loaded pre-configured sample: {selected_sample}")

# Execution Trigger
if report_data is not None:
    if st.button("Analyze & Simplify Report", type="primary"):
        col1, col2 = st.columns([1, 1])

        with col2:
            st.subheader(f"2. Simplified Explanation ({lang})")
            with st.spinner("Translating medical terminology with safety guardrails..."):
                summary = simplify_clinical_report(
                    report_data=report_data,
                    language=lang,
                    api_key=api_key_input if api_key_input else None,
                    model_override=selected_model
                )
                st.markdown(summary)

        with col1:
            st.subheader("1. Biomarker Triage & Anomaly Flags")
            
            # If no hardcoded triage table was provided, parse biomarker lines from summary
            if not triage_table:
                # Basic regex extraction fallback to populate the table from AI response
                extracted_rows = []
                lines = summary.split("\n")
                for line in lines:
                    if any(term in line.lower() for term in ["gm/dl", "mg/dl", "ng/ml", "/cumm", "mmol/l", "%"]):
                        status = "Elevated" if ("elevat" in line.lower() or "high" in line.lower()) else ("Low" if "low" in line.lower() else "Normal")
                        clean_line = re.sub(r"[*_#]", "", line).strip("- ")
                        parts = clean_line.split(":")
                        biomarker = parts[0].strip() if len(parts) > 1 else "Biomarker"
                        val = parts[1].strip() if len(parts) > 1 else clean_line
                        extracted_rows.append({
                            "Biomarker": biomarker,
                            "Value": val,
                            "Normal Range": "See report",
                            "Status": status
                        })
                triage_table = extracted_rows if extracted_rows else [
                    {"Biomarker": "Report Parameters", "Value": "Evaluated", "Normal Range": "Reference Range", "Status": "Normal"}
                ]

            df = pd.DataFrame(triage_table)
            st.dataframe(df, use_container_width=True)

            # Automated Anomaly Alert
            has_elevated = any(row.get("Status") in ["Elevated", "Low", "Abnormal"] for row in triage_table)
            if has_elevated:
                st.error("⚠️ Automated Anomaly Alert: Out-of-range parameters identified. Prioritize physician review.")
            else:
                st.success("✅ All evaluated markers are within standard reference ranges.")

        st.divider()
        st.caption("🛡️ BioMind AI Safety Guardrail: Informational translation only. Does not replace certified medical diagnosis.")
else:
    st.write("Upload a diagnostic report above or select a demo sample from the sidebar to begin.")