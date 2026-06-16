import os

import requests
import streamlit as st


BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")


st.set_page_config(
    page_title="World Cup 2026 AI Stats",
    page_icon="⚽",
    layout="wide",
)

st.title("⚽ World Cup 2026 AI Stats")
st.caption("AI-assisted match reports, team stats, and player breakdowns.")

st.markdown(
    """
    This dashboard will eventually show:
    
    - Finished World Cup matches
    - Team statistics
    - Player-level breakdowns
    - AI-generated match summaries
    - Telegram notification links
    """
)

st.divider()

st.subheader("Backend Health Check")

try:
    response = requests.get(f"{BACKEND_API_URL}/health", timeout=5)
    response.raise_for_status()
    data = response.json()

    st.success("Backend is healthy")
    st.json(data)

except Exception as error:
    st.error("Backend is not reachable")
    st.exception(error)