"""Adım 1: Dosya yükleme sayfası."""

import streamlit as st

from utils.io_helpers import read_upload
from analyzer.schema_analyzer import analyze


def render():
    """Yükleme sayfasını render et."""
    st.header("Adım 1: Verinizi Yükleyin")
    st.write("Yapısını analiz etmek ve aynı şemada sentetik veri üretmek için bir CSV veya Excel dosyası yükleyin.")

    uploaded_file = st.file_uploader(
        "Dosya seçin",
        type=["csv", "xlsx", "xls"],
        key="file_uploader",
    )

    if uploaded_file is not None:
        try:
            df = read_upload(uploaded_file)
            st.session_state["original_df"] = df

            st.success(f"Dosya yüklendi: **{uploaded_file.name}** — {df.shape[0]} satır, {df.shape[1]} sütun")

            # Önizleme
            st.subheader("Veri Önizleme")
            st.dataframe(df.head(10), use_container_width=True)

            # Sütun bilgisi
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Satır Sayısı", df.shape[0])
            with col2:
                st.metric("Sütun Sayısı", df.shape[1])
            with col3:
                null_pct = df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100
                st.metric("Eksik Değerler", f"%{null_pct:.1f}")

            # Analiz butonu
            if st.button("Analiz Et ve Yapılandır", type="primary", use_container_width=True):
                with st.spinner("Veri yapısı analiz ediliyor..."):
                    profiles = analyze(df)
                    st.session_state["profiles"] = profiles
                    st.session_state["step"] = 2
                    st.rerun()

        except Exception as e:
            st.error(f"Dosya okunurken hata oluştu: {e}")
