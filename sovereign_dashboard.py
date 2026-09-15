import streamlit as st
import requests

st.set_page_config(page_title="Symmetric UCS Rig", layout="wide")
st.title("🛡️ Universal Construction System: Symmetrical Control Center")

st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Symmetric Mesh", "ONLINE", "3 Nodes Synchronized")
with col2:
    st.metric("Protocols", "REST & WS", "Active Dual-Stack")
with col3:
    st.metric("Memory Grid", "Ray / Redis", "Balanced Substrate")

st.subheader("Live Cluster Mesh Telemetry")
try:
    response = requests.get("http://127.0.0.1:8000/").json()
    st.json(response)
except:
    st.warning("Connecting to Symmetrical Gateway local socket...")
