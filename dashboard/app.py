import os

import pandas as pd
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
    This companion dashboard is used for quick local runtime checks.

    Current milestone:

    **v1.7.0 — Provider Sync Observability & Runtime Demo**

    For now, the dashboard can load sample World Cup fixture data into PostgreSQL
    and display it through the FastAPI backend.
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

st.divider()

st.subheader("Fixture Sync")

st.write(
    "Load sample World Cup 2026 fixtures into PostgreSQL. "
    "This gives the project a working data flow before connecting a real football API."
)

if st.button("Sync Sample Fixtures"):
    try:
        sync_response = requests.post(
            f"{BACKEND_API_URL}/fixtures/sync/sample",
            timeout=10,
        )
        sync_response.raise_for_status()

        st.success("Sample fixtures synced successfully")
        st.json(sync_response.json())

    except Exception as error:
        st.error("Could not sync sample fixtures")
        st.exception(error)

st.divider()

st.subheader("Fixtures")

try:
    fixtures_response = requests.get(
        f"{BACKEND_API_URL}/fixtures",
        timeout=10,
    )
    fixtures_response.raise_for_status()

    fixtures_data = fixtures_response.json()
    fixtures = fixtures_data.get("fixtures", [])

    if fixtures:
        df = pd.DataFrame(fixtures)

        display_columns = [
            "group_name",
            "home_team",
            "away_team",
            "home_score",
            "away_score",
            "status",
            "kickoff_time",
            "venue",
        ]

        st.dataframe(
            df[display_columns],
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info("No fixtures found yet. Click 'Sync Sample Fixtures' to load sample data.")

except Exception as error:
    st.error("Could not load fixtures")
    st.exception(error)