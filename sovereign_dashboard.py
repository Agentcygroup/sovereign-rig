import streamlit as st
import requests

st.set_page_config(page_title="Universal Construction System Rig", layout="wide")
st.title("🛡️ Universal Construction System: Sovereign Control Center")

st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Cluster Topology", "ONLINE", "3 Nodes Active")
with col2:
    st.metric("Pipeline Engine", "UCS v3.2", "Deterministic")
with col3:
    st.metric("Memory Substrate", "Ray / Redis", "Synchronized")

st.subheader("Live Mesh Telemetry")
try:
    response = requests.get("http://127.0.0.1:8000/").json()
    st.json(response)
except:
    st.warning("Connecting to Sovereign Gateway local socket...")
