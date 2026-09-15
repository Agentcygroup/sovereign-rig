import streamlit as st
import subprocess
import json

st.set_page_config(page_title="Sovereign Control Center", page_icon="🛡️", layout="wide")

st.title("🛡️ Sovereign Rig & Omni-Universe Control Center")
st.markdown("**Local Execution Environment** | Zero Vendor Egress | Apple Silicon MLX Cluster")

# Sidebar Metrics
st.sidebar.header("Cluster Telemetry")
st.sidebar.success("Node Status: 3/3 Active")
st.sidebar.text("• node-01: MLX Worker\n• node-02: Vision Inference\n• node-03: Security Sentinel")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Omni-Universe Orchestration")
    if st.button("🚀 Execute All 10 Domains"):
        with st.spinner("Running sovereign verification across domains..."):
            res = subprocess.run(["python3", "/Users/metadusa/usd-rig/pi_omni_universe_engine.py"], capture_output=True, text=True)
            try:
                data = json.loads(res.stdout)
                st.json(data)
            except Exception:
                st.text(res.stdout)

with col2:
    st.subheader("Spectrum Matrix Status")
    if st.button("📊 Generate Spectrum Matrix"):
        with st.spinner("Compiling A-Z sovereign matrix..."):
            res = subprocess.run(["python3", "/Users/metadusa/usd-rig/omni_spectrum.py"], capture_output=True, text=True)
            try:
                data = json.loads(res.stdout)
                st.json(data)
            except Exception:
                st.text(res.stdout)
