"""Adım 3: Veri üretimi ve dışa aktarım sayfası."""

import streamlit as st
import pandas as pd
from copy import deepcopy

from analyzer.schema_analyzer import ColumnProfile
from generator.engine import generate
from ui.components import stats_comparison
from utils.io_helpers import df_to_csv_bytes, df_to_excel_bytes


def _apply_overrides(profiles: list[ColumnProfile], overrides: dict) -> list[ColumnProfile]:
    """Kullanıcı düzenlemelerini profillere uygula."""
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
    """Üretim ve dışa aktarım sayfasını render et."""
    profiles = st.session_state.get("profiles", [])
    original_df = st.session_state.get("original_df")
    overrides = st.session_state.get("user_overrides", {})
    global_config = st.session_state.get("global_config", {})

    if not profiles or original_df is None:
        st.warning("Yapılandırılmış veri bulunamadı. Lütfen geri dönün.")
        if st.button("Yükleme Sayfasına Dön"):
            st.session_state["step"] = 1
            st.rerun()
        return

    st.header("Adım 3: Üretilen Sentetik Veri")

    # Geri butonu
    if st.button("< Yapılandırmaya Dön"):
        st.session_state["step"] = 2
        st.rerun()

    # Düzenlemeleri uygula
    final_profiles = _apply_overrides(profiles, overrides)

    num_rows = global_config.get("num_rows", len(original_df))
    locale = global_config.get("locale", "en_US")
    noise_config = global_config.get("noise_config")
    correlation_rules = global_config.get("correlation_rules")
    business_rules = global_config.get("business_rules")

    # Üret veya önbellekten al
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

    # Metrikler
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Üretilen Satır", f"{len(generated_df):,}")
    with col2:
        st.metric("Sütun Sayısı", len(generated_df.columns))
    with col3:
        null_pct = generated_df.isnull().sum().sum() / (generated_df.shape[0] * generated_df.shape[1]) * 100 if generated_df.size > 0 else 0
        st.metric("Eksik Değerler", f"%{null_pct:.1f}")

    # Önizleme
    st.subheader("Veri Önizleme")
    st.dataframe(generated_df.head(100), use_container_width=True)

    # İndirme butonları
    st.subheader("Dışa Aktar")
    col1, col2 = st.columns(2)
    with col1:
        csv_bytes = df_to_csv_bytes(generated_df)
        st.download_button(
            label="CSV İndir",
            data=csv_bytes,
            file_name="sentetik_veri.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col2:
        if len(generated_df) > 100_000:
            st.warning("Büyük veri setlerinde Excel dışa aktarımı yavaş olabilir. CSV önerilir.")
        excel_bytes = df_to_excel_bytes(generated_df)
        st.download_button(
            label="Excel İndir",
            data=excel_bytes,
            file_name="sentetik_veri.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    # Yeniden üret butonu
    st.divider()
    if st.button("Aynı Ayarlarla Yeniden Üret", use_container_width=True):
        st.session_state["needs_regeneration"] = True
        st.rerun()

    # İstatistik karşılaştırması
    st.divider()
    stats_comparison(original_df, generated_df)
