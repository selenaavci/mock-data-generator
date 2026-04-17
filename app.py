"""Mock Data Generator - Streamlit Application.

Supports two modes:
    - upload: infer schema from a sample file and scale it
    - scratch: design a dataset from zero
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

st.set_page_config(
    page_title="Mock Data Generator",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _step_indicator(steps: list[str], current: int):
    cols = st.columns(len(steps))
    for i, (col, step_name) in enumerate(zip(cols, steps), 1):
        if i == current:
            col.markdown(f"**:blue[Adım {i}: {step_name}]**")
        elif i < current:
            col.markdown(f"~~Adım {i}: {step_name}~~")
        else:
            col.markdown(f"Adım {i}: {step_name}")


def main():
    st.title("Mock Data Generator Agent")
    st.caption("Mevcut veriden veya sıfırdan gerçekçi sentetik veri setleri üretin.")

    mode = st.session_state.get("mode")

    if not mode:
        from ui.home_page import render as home_render
        home_render()
        return

    step = st.session_state.get("step", 1)

    if mode == "upload":
        _step_indicator(["Yükleme", "Yapılandırma", "Üretim"], step)
        st.divider()
        if step == 1:
            from ui.upload_page import render
        elif step == 2:
            from ui.analysis_page import render
        else:
            from ui.generation_page import render
        render()
    elif mode == "scratch":
        _step_indicator(["Veri Seti", "Sütunlar", "Üretim"], step)
        st.divider()
        if step == 1:
            from ui.scratch_dataset_page import render
        elif step == 2:
            from ui.scratch_columns_page import render
        else:
            from ui.generation_page import render
        render()


main()
