"""Streamlit uygulaması için yeniden kullanılabilir UI bileşenleri."""

import streamlit as st
import pandas as pd
import numpy as np

from analyzer.schema_analyzer import ColumnProfile
from utils.constants import (
    TYPE_OPTIONS,
    FAKER_PROVIDERS,
    DATE_FORMAT_OPTIONS,
    BOOLEAN_FORMAT_OPTIONS,
)


def column_config_card(profile: ColumnProfile, index: int) -> dict:
    """Sütun yapılandırma kartını render et ve kullanıcı düzenlemelerini döndür."""
    overrides = {}

    with st.expander(f"**{profile.name}** — `{profile.detected_type}`", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
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

        effective_type = overrides.get("detected_type", profile.detected_type)
        cfg = profile.generation_config.copy()

        if effective_type in ("numeric_int", "numeric_float"):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                cfg["min"] = st.number_input("Min", value=float(cfg.get("min", 0)), key=f"min_{index}")
            with c2:
                cfg["max"] = st.number_input("Maks", value=float(cfg.get("max", 100)), key=f"max_{index}")
            with c3:
                cfg["mean"] = st.number_input("Ortalama", value=float(cfg.get("mean", 50)), key=f"mean_{index}")
            with c4:
                cfg["std"] = st.number_input("Std Sapma", value=float(cfg.get("std", 10)), min_value=0.0, key=f"std_{index}")

            dist = st.selectbox(
                "Dağılım", ["normal", "uniform"],
                index=0 if cfg.get("distribution", "normal") == "normal" else 1,
                key=f"dist_{index}",
            )
            cfg["distribution"] = dist
            cfg["is_int"] = effective_type == "numeric_int"
            cfg["allow_negative"] = st.checkbox("Negatif değerlere izin ver", value=cfg.get("allow_negative", True), key=f"neg_{index}")
            cfg["sequential"] = st.checkbox("Sıralı üret", value=cfg.get("sequential", False), key=f"seqnum_{index}")
            if cfg["sequential"]:
                cfg["step"] = st.number_input("Adım", value=float(cfg.get("step", 1)), key=f"step_{index}")
            overrides["generation_config"] = cfg

        elif effective_type == "categorical":
            values = cfg.get("values", [])
            st.write(f"**{len(values)} benzersiz değer tespit edildi**")
            if values:
                st.caption(f"En sık değerler: {', '.join(str(v) for v in values[:10])}")

        elif effective_type == "datetime":
            c1, c2 = st.columns(2)
            with c1:
                start = st.date_input("Başlangıç Tarihi", value=pd.Timestamp(cfg.get("start_date", "2020-01-01")), key=f"start_{index}")
                cfg["start_date"] = str(start)
            with c2:
                end = st.date_input("Bitiş Tarihi", value=pd.Timestamp(cfg.get("end_date", "2024-12-31")), key=f"end_{index}")
                cfg["end_date"] = str(end)

            fmt_keys = list(DATE_FORMAT_OPTIONS.keys())
            fmt_label = st.selectbox("Çıktı formatı", fmt_keys, index=0, key=f"dfmt_{index}")
            cfg["output_format"] = DATE_FORMAT_OPTIONS[fmt_label]
            cfg["include_time"] = st.checkbox("Saat bilgisi dahil", value=cfg.get("include_time", False), key=f"dtime_{index}")
            cfg["business_days_only"] = st.checkbox("Sadece iş günleri", value=cfg.get("business_days_only", False), key=f"dbiz_{index}")
            cfg["sequential"] = st.checkbox("Sıralı (tarih sırasına göre)", value=cfg.get("sequential", False), key=f"seq_{index}")
            overrides["generation_config"] = cfg

        elif effective_type == "boolean":
            cfg["true_ratio"] = st.slider(
                "True Olasılığı", 0.0, 1.0,
                value=float(cfg.get("true_ratio", 0.5)),
                key=f"bool_{index}",
            )
            fmt_keys = list(BOOLEAN_FORMAT_OPTIONS.keys())
            default_fmt_label = next(
                (k for k, v in BOOLEAN_FORMAT_OPTIONS.items() if v == cfg.get("value_format", "true_false")),
                "True / False",
            )
            fmt_label = st.selectbox("Değer formatı", fmt_keys, index=fmt_keys.index(default_fmt_label), key=f"bfmt_{index}")
            cfg["value_format"] = BOOLEAN_FORMAT_OPTIONS[fmt_label]
            overrides["generation_config"] = cfg

        elif effective_type == "id":
            c1, c2, c3 = st.columns(3)
            with c1:
                cfg["prefix"] = st.text_input("Önek", value=cfg.get("prefix", "ID-"), key=f"idpre_{index}")
            with c2:
                cfg["start"] = int(st.number_input("Başlangıç", value=int(cfg.get("start", 1)), key=f"idstart_{index}"))
            with c3:
                cfg["length"] = int(st.number_input("Uzunluk", min_value=1, max_value=20, value=int(cfg.get("length", 6)), key=f"idlen_{index}"))
            cfg["sequential"] = st.checkbox("Sıralı", value=cfg.get("sequential", True), key=f"idseq_{index}")
            cfg["unique"] = True
            overrides["generation_config"] = cfg

        elif effective_type == "pattern":
            st.caption("Sembol: `#` rakam, `@` büyük harf, `&` küçük harf, `?` harf, `*` alfasayısal.")
            cfg["pattern"] = st.text_input("Desen", value=cfg.get("pattern", "####-@@@@"), key=f"pat_{index}")
            overrides["generation_config"] = cfg

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
