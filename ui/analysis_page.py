"""Step 2: Analysis and configuration page."""

import streamlit as st

from analyzer.schema_analyzer import ColumnProfile
from ui.components import column_config_card
from utils.constants import LOCALE_OPTIONS, MAX_ROWS, WARN_ROWS


def render():
    """Render the analysis and configuration page."""
    profiles: list[ColumnProfile] = st.session_state.get("profiles", [])
    original_df = st.session_state.get("original_df")

    if not profiles or original_df is None:
        st.warning("No data analyzed yet. Please go back and upload a file.")
        if st.button("Back to Upload"):
            st.session_state["step"] = 1
            st.rerun()
        return

    st.header("Step 2: Schema Analysis & Configuration")

    # Back button
    if st.button("< Back to Upload"):
        st.session_state["step"] = 1
        st.rerun()

    st.write("Review the detected column types and adjust generation parameters as needed.")

    # --- Sidebar: Global Settings ---
    with st.sidebar:
        st.header("Global Settings")

        # Row count
        num_rows = st.number_input(
            "Number of rows to generate",
            min_value=1,
            max_value=MAX_ROWS,
            value=min(len(original_df), MAX_ROWS),
            step=100,
            key="num_rows",
        )
        if num_rows > WARN_ROWS:
            st.warning(f"Generating {num_rows:,} rows may be slow and use significant memory.")

        # Locale
        locale_name = st.selectbox("Locale (for Faker)", list(LOCALE_OPTIONS.keys()), index=0)
        locale = LOCALE_OPTIONS[locale_name]

        st.divider()

        # Noise settings
        st.subheader("Noise Injection")
        enable_noise = st.checkbox("Enable noise", value=False)
        noise_config = {}
        if enable_noise:
            noise_config["null_ratio"] = st.slider("Null ratio", 0.0, 0.3, 0.05, 0.01)
            noise_config["outlier_ratio"] = st.slider("Outlier ratio", 0.0, 0.1, 0.01, 0.005)
            noise_config["outlier_scale"] = st.slider("Outlier scale (x std)", 1.0, 5.0, 3.0, 0.5)

        st.divider()

        # Business rules
        st.subheader("Business Rules")
        st.caption("Enter pandas query expressions, one per line.\nExample: `age >= 18`")
        rules_text = st.text_area("Rules", value="", height=100, key="business_rules")
        business_rules = [r.strip() for r in rules_text.strip().split("\n") if r.strip()]

        st.divider()

        # Correlation rules
        st.subheader("Correlation Rules")
        num_corr_rules = st.number_input("Number of rules", 0, 10, 0, key="num_corr")
        correlation_rules = []
        numeric_cols = [p.name for p in profiles if p.detected_type in ("numeric_int", "numeric_float")]

        for i in range(int(num_corr_rules)):
            st.write(f"**Rule {i + 1}**")
            if len(numeric_cols) >= 2:
                c1, c2 = st.columns(2)
                with c1:
                    source = st.selectbox("Source", numeric_cols, key=f"corr_src_{i}")
                with c2:
                    target = st.selectbox("Target", numeric_cols, key=f"corr_tgt_{i}")
                direction = st.selectbox("Direction", ["positive", "negative"], key=f"corr_dir_{i}")
                strength = st.slider("Strength", 0.0, 1.0, 0.5, key=f"corr_str_{i}")
                correlation_rules.append({
                    "source": source,
                    "target": target,
                    "direction": direction,
                    "strength": strength,
                })
            else:
                st.caption("Need at least 2 numeric columns for correlations.")

    # --- Main: Column Profiles ---
    st.subheader("Column Configuration")

    overrides = {}
    for i, profile in enumerate(profiles):
        override = column_config_card(profile, i)
        if override:
            overrides[profile.name] = override

    # Store settings in session state
    st.session_state["user_overrides"] = overrides
    st.session_state["global_config"] = {
        "num_rows": num_rows,
        "locale": locale,
        "noise_config": noise_config if enable_noise else None,
        "correlation_rules": correlation_rules if correlation_rules else None,
        "business_rules": business_rules if business_rules else None,
    }

    # Generate button
    st.divider()
    if st.button("Generate Mock Data", type="primary", use_container_width=True):
        st.session_state["step"] = 3
        st.rerun()
