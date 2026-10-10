import streamlit as st
import plotly.graph_objects as go
from processor import generate_eeg_stream, extract_band_telemetry
from ai_diagnostics import generate_clinical_report

st.set_page_config(page_title="BioMind AI", layout="wide", page_icon="🧠")

st.title("🧠 BioMind AI — Biosignal & Cognitive Telemetry")
st.markdown("Real-time neuro-ergonomic workload monitoring via automated EEG spectral decomposition.")

# Sidebar telemetry controls
st.sidebar.header("Patient Telemetry Parameters")
selected_state = st.sidebar.selectbox("Simulate Neural State", ["focus", "fatigued", "stressed"])
window_len = st.sidebar.slider("Analysis Window (seconds)", 5, 20, 10)

if st.sidebar.button("Capture & Analyze Biosignal Window", type="primary"):
    with st.spinner("Decomposing frequency bands and running BioMind AI synthesis..."):
        t, eeg = generate_eeg_stream(state=selected_state, duration_sec=window_len)
        metrics = extract_band_telemetry(eeg)
        
        # Telemetry metrics row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Theta Band (Fatigue)", f"{metrics['theta']} μV²")
        m2.metric("Alpha Band (Baseline)", f"{metrics['alpha']} μV²")
        m3.metric("Beta Band (Alertness)", f"{metrics['beta']} μV²")
        m4.metric("Cognitive Index", metrics['engagement'])
        
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.subheader("Raw Biosignal Waveform (EEG Stream)")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=t[:750], y=eeg[:750], mode="lines", name="EEG (μV)", line=dict(color="#00FFAA")))
            fig.update_layout(template="plotly_dark", height=320, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig, use_container_width=True)
            
        with col_right:
            st.subheader("Spectral Band Powers")
            bar = go.Figure(data=[
                go.Bar(
                    x=["Theta (4-8Hz)", "Alpha (8-13Hz)", "Beta (13-30Hz)"],
                    y=[metrics["theta"], metrics["alpha"], metrics["beta"]],
                    marker_color=["#4A90E2", "#50E3C2", "#FF9F1C"]
                )
            ])
            bar.update_layout(template="plotly_dark", height=320, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(bar, use_container_width=True)
            
        st.subheader("AI Clinical & Ergonomic Evaluation")
        report_text = generate_clinical_report(metrics, selected_state)
        st.info(report_text)
else:
    st.info("Select a state profile on the left and click **Capture & Analyze Biosignal Window** to begin.")