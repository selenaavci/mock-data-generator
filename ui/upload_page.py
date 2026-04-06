"""Step 1: File upload page."""

import streamlit as st

from utils.io_helpers import read_upload
from analyzer.schema_analyzer import analyze


def render():
    """Render the upload page."""
    st.header("Step 1: Upload Your Data")
    st.write("Upload a CSV or Excel file to analyze its structure and generate mock data with the same schema.")

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["csv", "xlsx", "xls"],
        key="file_uploader",
    )

    if uploaded_file is not None:
        try:
            df = read_upload(uploaded_file)
            st.session_state["original_df"] = df

            st.success(f"File loaded: **{uploaded_file.name}** — {df.shape[0]} rows, {df.shape[1]} columns")

            # Preview
            st.subheader("Data Preview")
            st.dataframe(df.head(10), use_container_width=True)

            # Column info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rows", df.shape[0])
            with col2:
                st.metric("Columns", df.shape[1])
            with col3:
                null_pct = df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100
                st.metric("Missing Values", f"{null_pct:.1f}%")

            # Analyze button
            if st.button("Analyze & Configure", type="primary", use_container_width=True):
                with st.spinner("Analyzing data structure..."):
                    profiles = analyze(df)
                    st.session_state["profiles"] = profiles
                    st.session_state["step"] = 2
                    st.rerun()

        except Exception as e:
            st.error(f"Error reading file: {e}")
