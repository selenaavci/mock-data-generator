"""Mock Data Generator - Streamlit Application.

A tool that analyzes uploaded datasets and generates realistic mock data
with the same structure, distributions, and relationships.
"""

import sys
from pathlib import Path

# Ensure project root is in Python path (needed for Streamlit Cloud)
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

st.set_page_config(
    page_title="Mock Data Generator",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    # Title
    st.title("Mock Data Generator")
    st.caption("Verinizi yükleyin, yapısını analiz edin ve aynı yapıda gerçekçi sentetik veri üretin.")

    # Initialize session state
    if "step" not in st.session_state:
        st.session_state["step"] = 1

    # Step indicator
    steps = ["Yükleme", "Yapılandırma", "Üretim"]
    current_step = st.session_state["step"]

    cols = st.columns(3)
    for i, (col, step_name) in enumerate(zip(cols, steps), 1):
        if i == current_step:
            col.markdown(f"**:blue[Adım {i}: {step_name}]**")
        elif i < current_step:
            col.markdown(f"~~Adım {i}: {step_name}~~")
        else:
            col.markdown(f"Adım {i}: {step_name}")

    st.divider()

    # Render current step
    if current_step == 1:
        from ui.upload_page import render
        render()
    elif current_step == 2:
        from ui.analysis_page import render
        render()
    elif current_step == 3:
        from ui.generation_page import render
        render()


main()
