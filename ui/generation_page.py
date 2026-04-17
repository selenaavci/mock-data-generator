"""Son adım: Veri üretimi ve dışa aktarım sayfası (upload + scratch modları)."""

import streamlit as st
import pandas as pd
from copy import deepcopy

from analyzer.schema_analyzer import ColumnProfile
from generator.engine import generate
from ui.components import stats_comparison
from utils.io_helpers import df_to_csv_bytes, df_to_excel_bytes, df_to_json_bytes
from utils.streamlit_compat import safe_rerun


def _apply_overrides(profiles: list[ColumnProfile], overrides: dict) -> list[ColumnProfile]:
    updated = []
    for p in profiles:
        profile = deepcopy(p)
        if profile.name in overrides:
            ov = overrides[profile.name]
            if "detected_type" in ov:
                profile.detected_type = ov["detected_type"]
            if "faker_hint" in ov:
                profile.faker_hint = ov["faker_hint"]
            if "generation_config" in ov:
                profile.generation_config.update(ov["generation_config"])
        updated.append(profile)
    return updated


def render():
    profiles = st.session_state.get("profiles", [])
    original_df = st.session_state.get("original_df")
    overrides = st.session_state.get("user_overrides", {})
    global_config = st.session_state.get("global_config", {})
    mode = st.session_state.get("mode", "upload")

    if not profiles:
        st.warning("Yapılandırılmış veri bulunamadı. Lütfen geri dönün.")
        if st.button("Başa Dön"):
            st.session_state["step"] = 1
            safe_rerun()
        return

    st.header("Üretilen Sentetik Veri")

    if st.button("< Önceki Adıma Dön"):
        st.session_state["step"] = 2
        safe_rerun()

    final_profiles = _apply_overrides(profiles, overrides)

    num_rows = global_config.get("num_rows", len(original_df) if original_df is not None else 1000)
    locale = global_config.get("locale", "en_US")
    noise_config = global_config.get("noise_config")
    correlation_rules = global_config.get("correlation_rules")
    business_rules = global_config.get("business_rules")

    if "generated_df" not in st.session_state or st.session_state.get("needs_regeneration", True):
        with st.spinner(f"{num_rows:,} satır sentetik veri üretiliyor..."):
            generated_df = generate(
                profiles=final_profiles,
                num_rows=num_rows,
                locale=locale,
                noise_config=noise_config,
                correlation_rules=correlation_rules,
                business_rules=business_rules,
            )
            st.session_state["generated_df"] = generated_df
            st.session_state["needs_regeneration"] = False

    generated_df = st.session_state["generated_df"]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Üretilen Satır", f"{len(generated_df):,}")
    with col2:
        st.metric("Sütun Sayısı", len(generated_df.columns))
    with col3:
        null_pct = generated_df.isnull().sum().sum() / (generated_df.shape[0] * generated_df.shape[1]) * 100 if generated_df.size > 0 else 0
        st.metric("Eksik Değerler", f"%{null_pct:.1f}")

    st.subheader("Veri Önizleme")
    st.dataframe(generated_df.head(100), use_container_width=True)

    # Null distribution per column
    if generated_df.size > 0:
        with st.expander("Sütun Özeti (tip + boş değer)"):
            summary = pd.DataFrame({
                "Tip": [str(generated_df[c].dtype) for c in generated_df.columns],
                "Boş Değer Sayısı": [int(generated_df[c].isna().sum()) for c in generated_df.columns],
                "Benzersiz": [int(generated_df[c].nunique(dropna=True)) for c in generated_df.columns],
            }, index=generated_df.columns)
            st.dataframe(summary, use_container_width=True)

    st.subheader("Dışa Aktar")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button(
            label="CSV İndir",
            data=df_to_csv_bytes(generated_df),
            file_name="sentetik_veri.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with c2:
        if len(generated_df) > 100_000:
            st.caption("Büyük veri: Excel yavaş olabilir")
        st.download_button(
            label="Excel İndir",
            data=df_to_excel_bytes(generated_df),
            file_name="sentetik_veri.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with c3:
        st.download_button(
            label="JSON İndir",
            data=df_to_json_bytes(generated_df),
            file_name="sentetik_veri.json",
            mime="application/json",
            use_container_width=True,
        )

    st.divider()
    if st.button("Aynı Ayarlarla Yeniden Üret", use_container_width=True):
        st.session_state["needs_regeneration"] = True
        safe_rerun()

    if original_df is not None and mode == "upload":
        st.divider()
        stats_comparison(original_df, generated_df)
