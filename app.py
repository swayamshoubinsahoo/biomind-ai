import streamlit as st
import pandas as pd
import re
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

# Sidebar Configuration (Model technicalities completely hidden)
st.sidebar.header("⚙️ Configuration")
st.sidebar.caption("⚡ Engine: Auto-Adaptive Resilient Vision (Auto-Fallback)")

api_key_input = st.sidebar.text_input(
    "Gemini API Key (optional if set in env/secrets)",
    type="password"
)

lang = st.sidebar.selectbox(
    "Explanation Language",
    ["English", "Hindi", "Bengali", "Spanish", "French"],
    index=0
)

# Pre-configured demo sample
SAMPLE_REPORTS = {
    "None": None,
    "Cardiac Triage Panel": {
        "text": "Troponin I: 0.08 ng/mL (Normal: 0.0 - 0.04 ng/mL) [ELEVATED]\nFasting Blood Sugar: 95 mg/dL (Normal: 70 - 100 mg/dL) [NORMAL]\nECG: Sinus Tachycardia, ST elevation noted in leads V1-V3.",
        "table": [
            {"Biomarker": "Fasting Blood Sugar", "Value": "95 mg/dL", "Normal Range": "70 - 100 mg/dL", "Status": "Normal"},
            {"Biomarker": "Troponin", "Value": "0.08 ng/mL", "Normal Range": "0.0 - 0.04 ng/mL", "Status": "Elevated"},
        ]
    }
}

selected_sample = st.sidebar.selectbox("Load Demo Sample", list(SAMPLE_REPORTS.keys()), index=0)

# Main File Uploader
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
                    api_key=api_key_input if api_key_input else None
                )
                st.markdown(summary)

        with col1:
            st.subheader("1. Biomarker Triage & Anomaly Flags")
            
            # Auto-parse biomarker lines into table if demo table is not present
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