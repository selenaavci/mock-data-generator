"""Streamlit uygulaması için yeniden kullanılabilir UI bileşenleri."""

import streamlit as st
import pandas as pd
import numpy as np

from analyzer.schema_analyzer import ColumnProfile
from utils.constants import TYPE_OPTIONS, FAKER_PROVIDERS


def column_config_card(profile: ColumnProfile, index: int) -> dict:
    """Sütun yapılandırma kartını render et ve kullanıcı düzenlemelerini döndür."""
    overrides = {}

    with st.expander(f"**{profile.name}** — `{profile.detected_type}`", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            # Tip değiştirme
            current_idx = TYPE_OPTIONS.index(profile.detected_type) if profile.detected_type in TYPE_OPTIONS else 0
            new_type = st.selectbox(
                "Sütun Tipi",
                TYPE_OPTIONS,
                index=current_idx,
                key=f"type_{index}",
            )
            if new_type != profile.detected_type:
                overrides["detected_type"] = new_type

        with col2:
            # Faker sağlayıcı
            faker_options = [str(p) if p else "Yok" for p in FAKER_PROVIDERS]
            current_faker = profile.faker_hint or "Yok"
            faker_idx = faker_options.index(current_faker) if current_faker in faker_options else 0
            new_faker = st.selectbox(
                "Faker Sağlayıcı",
                faker_options,
                index=faker_idx,
                key=f"faker_{index}",
            )
            if new_faker != "Yok":
                overrides["faker_hint"] = new_faker
                if new_type == "faker" or (new_type == profile.detected_type and profile.detected_type != "faker"):
                    overrides["detected_type"] = "faker"
                    overrides.setdefault("generation_config", {})["faker_provider"] = new_faker

        # Tipe özgü yapılandırma
        effective_type = overrides.get("detected_type", profile.detected_type)

        if effective_type in ("numeric_int", "numeric_float"):
            c1, c2, c3, c4 = st.columns(4)
            config = profile.generation_config.copy()
            with c1:
                config["min"] = st.number_input("Min", value=float(config.get("min", 0)), key=f"min_{index}")
            with c2:
                config["max"] = st.number_input("Maks", value=float(config.get("max", 100)), key=f"max_{index}")
            with c3:
                config["mean"] = st.number_input("Ortalama", value=float(config.get("mean", 50)), key=f"mean_{index}")
            with c4:
                config["std"] = st.number_input("Std Sapma", value=float(config.get("std", 10)), min_value=0.0, key=f"std_{index}")

            dist = st.selectbox(
                "Dağılım", ["normal", "uniform"],
                index=0 if config.get("distribution", "normal") == "normal" else 1,
                key=f"dist_{index}",
            )
            config["distribution"] = dist
            config["is_int"] = effective_type == "numeric_int"
            overrides["generation_config"] = config

        elif effective_type == "categorical":
            config = profile.generation_config.copy()
            values = config.get("values", [])
            st.write(f"**{len(values)} benzersiz değer tespit edildi**")
            if values:
                st.caption(f"En sık değerler: {', '.join(str(v) for v in values[:10])}")

        elif effective_type == "datetime":
            config = profile.generation_config.copy()
            c1, c2 = st.columns(2)
            with c1:
                start = st.date_input("Başlangıç Tarihi", value=pd.Timestamp(config.get("start_date", "2020-01-01")), key=f"start_{index}")
                config["start_date"] = str(start)
            with c2:
                end = st.date_input("Bitiş Tarihi", value=pd.Timestamp(config.get("end_date", "2024-12-31")), key=f"end_{index}")
                config["end_date"] = str(end)
            config["sequential"] = st.checkbox("Sıralı (tarih sırasına göre)", value=config.get("sequential", False), key=f"seq_{index}")
            overrides["generation_config"] = config

        elif effective_type == "boolean":
            config = profile.generation_config.copy()
            config["true_ratio"] = st.slider(
                "True Olasılığı", 0.0, 1.0,
                value=float(config.get("true_ratio", 0.5)),
                key=f"bool_{index}",
            )
            overrides["generation_config"] = config

        # Boş değer oranı bilgisi
        if profile.nullable:
            st.caption(f"Orijinal boş değer oranı: %{profile.null_ratio:.1%}")

    return overrides


def stats_comparison(original_df: pd.DataFrame, generated_df: pd.DataFrame):
    """Orijinal ve üretilen veri istatistiklerini yan yana göster."""
    st.subheader("Orijinal ve Üretilen Veri Karşılaştırması")

    for col in original_df.columns:
        if col not in generated_df.columns:
            continue

        with st.expander(f"**{col}**", expanded=False):
            c1, c2 = st.columns(2)

            with c1:
                st.write("**Orijinal**")
                if pd.api.types.is_bool_dtype(original_df[col]):
                    vc = original_df[col].value_counts()
                    st.write(f"True: {vc.get(True, 0)}, False: {vc.get(False, 0)}")
                    st.bar_chart(vc)
                elif pd.api.types.is_numeric_dtype(original_df[col]):
                    st.write(original_df[col].describe().round(2))
                else:
                    vc = original_df[col].value_counts().head(10)
                    st.write(f"Benzersiz: {original_df[col].nunique()}")
                    st.bar_chart(vc)

            with c2:
                st.write("**Üretilen**")
                if pd.api.types.is_bool_dtype(generated_df[col]):
                    vc = generated_df[col].value_counts()
                    st.write(f"True: {vc.get(True, 0)}, False: {vc.get(False, 0)}")
                    st.bar_chart(vc)
                elif pd.api.types.is_numeric_dtype(generated_df[col]):
                    st.write(generated_df[col].describe().round(2))
                else:
                    vc = generated_df[col].value_counts().head(10)
                    st.write(f"Benzersiz: {generated_df[col].nunique()}")
                    st.bar_chart(vc)
