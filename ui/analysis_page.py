"""Yükleme modu — Adım 2: Analiz ve yapılandırma sayfası."""

import streamlit as st

from analyzer.schema_analyzer import ColumnProfile
from ui.components import column_config_card
from utils.constants import LOCALE_OPTIONS, MAX_ROWS, WARN_ROWS
from utils.streamlit_compat import safe_rerun


def render():
    profiles: list[ColumnProfile] = st.session_state.get("profiles", [])
    original_df = st.session_state.get("original_df")

    if not profiles or original_df is None:
        st.warning("Henüz analiz edilmiş veri yok. Lütfen geri dönüp dosya yükleyin.")
        if st.button("Yükleme Sayfasına Dön"):
            st.session_state["step"] = 1
            safe_rerun()
        return

    st.header("Adım 2: Şema Analizi ve Yapılandırma")

    if st.button("< Yükleme Sayfasına Dön"):
        st.session_state["step"] = 1
        safe_rerun()

    st.write("Tespit edilen sütun tiplerini inceleyin ve üretim parametrelerini ihtiyacınıza göre ayarlayın.")

    with st.sidebar:
        st.header("Genel Ayarlar")

        num_rows = st.number_input(
            "Üretilecek satır sayısı",
            min_value=1,
            max_value=MAX_ROWS,
            value=min(len(original_df), MAX_ROWS),
            step=100,
            key="num_rows",
        )
        if num_rows > WARN_ROWS:
            st.warning(f"{num_rows:,} satır üretmek yavaş olabilir ve yüksek bellek kullanabilir.")

        locale_name = st.selectbox("Dil (Faker için)", list(LOCALE_OPTIONS.keys()), index=0)
        locale = LOCALE_OPTIONS[locale_name]

        st.divider()

        st.subheader("Veri Kalitesi")
        quality_mode = st.radio("Mod", ["Temiz", "Gerçek Dünya (Gürültülü)"], index=0)
        noise_config: dict = {}
        if quality_mode == "Gerçek Dünya (Gürültülü)":
            noise_config["null_ratio"] = st.slider("Boş değer oranı", 0.0, 0.3, 0.05, 0.01)
            noise_config["outlier_ratio"] = st.slider("Aykırı değer oranı", 0.0, 0.1, 0.01, 0.005)
            noise_config["outlier_scale"] = st.slider("Aykırı değer ölçeği (x std)", 1.0, 5.0, 3.0, 0.5)
            noise_config["duplicate_ratio"] = st.slider("Mükerrer satır oranı", 0.0, 0.2, 0.02, 0.01)
            noise_config["typo_ratio"] = st.slider("Yazım hatası oranı", 0.0, 0.2, 0.02, 0.01)
            noise_config["whitespace_ratio"] = st.slider("Boşluk tutarsızlığı oranı", 0.0, 0.2, 0.02, 0.01)
            noise_config["format_inconsistency_ratio"] = st.slider("Format tutarsızlığı oranı", 0.0, 0.2, 0.02, 0.01)

        st.divider()

        st.subheader("Korelasyon Kuralları")
        num_corr_rules = st.number_input("Kural sayısı", 0, 10, 0, key="num_corr")
        correlation_rules = []
        numeric_cols = [p.name for p in profiles if p.detected_type in ("numeric_int", "numeric_float")]

        for i in range(int(num_corr_rules)):
            st.write(f"**Kural {i + 1}**")
            if len(numeric_cols) >= 2:
                c1, c2 = st.columns(2)
                with c1:
                    source = st.selectbox("Kaynak", numeric_cols, key=f"corr_src_{i}")
                with c2:
                    target = st.selectbox("Hedef", numeric_cols, key=f"corr_tgt_{i}")
                direction = st.selectbox("Yön", ["pozitif", "negatif"], key=f"corr_dir_{i}")
                strength = st.slider("Güç", 0.0, 1.0, 0.5, key=f"corr_str_{i}")
                correlation_rules.append({
                    "source": source,
                    "target": target,
                    "direction": "positive" if direction == "pozitif" else "negative",
                    "strength": strength,
                })
            else:
                st.caption("Korelasyon için en az 2 sayısal sütun gereklidir.")

    st.subheader("Sütun Yapılandırması")

    overrides = {}
    for i, profile in enumerate(profiles):
        override = column_config_card(profile, i)
        if override:
            overrides[profile.name] = override

    st.session_state["user_overrides"] = overrides
    st.session_state["global_config"] = {
        "num_rows": num_rows,
        "locale": locale,
        "noise_config": noise_config if noise_config else None,
        "correlation_rules": correlation_rules if correlation_rules else None,
        "business_rules": business_rules if business_rules else None,
    }

    st.divider()
    if st.button("Sentetik Veri Üret", type="primary", use_container_width=True):
        st.session_state["needs_regeneration"] = True
        st.session_state["step"] = 3
        safe_rerun()
