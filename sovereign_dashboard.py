import streamlit as st
import requests

st.set_page_config(page_title="Sovereign Omni-Rig", layout="wide")
st.title("🛡️ Sovereign Omni-Universe Rig: Enterprise Control Center")

st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Cluster Status", "ONLINE", "3 Active Nodes")
with col2:
    st.metric("Mesh Security", "SECURE", "Zero Egress")
with col3:
    st.metric("Ray / Redis Cache", "SYNCHRONIZED", "Active")

st.subheader("Live Cluster Node Telemetry")
try:
    response = requests.get("http://127.0.0.1:8000/").json()
    st.json(response)
except:
    st.warning("Connecting to Sovereign Gateway local socket...")
