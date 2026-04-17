"""Sıfırdan mod — Adım 2: Sütun tanımlama ve tip bazlı yapılandırma."""

import streamlit as st

from analyzer.schema_analyzer import ColumnProfile
from utils.constants import (
    USER_TYPES,
    DATE_FORMAT_OPTIONS,
    BOOLEAN_FORMAT_OPTIONS,
)
from utils.streamlit_compat import safe_rerun


def _scratch_column_card(col: dict, index: int) -> dict:
    """Render a scratch column card and mutate ``col`` in-place."""
    user_type_keys = list(USER_TYPES.keys())

    with st.expander(f"**{col.get('name', f'column_{index+1}')}** — {col.get('user_type')}", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            col["name"] = st.text_input("Sütun Adı", value=col.get("name", f"column_{index+1}"), key=f"sc_name_{index}")
        with c2:
            idx = user_type_keys.index(col["user_type"]) if col.get("user_type") in user_type_keys else 0
            col["user_type"] = st.selectbox("Veri Tipi", user_type_keys, index=idx, key=f"sc_type_{index}")

        c1, c2 = st.columns(2)
        with c1:
            col["nullable"] = st.checkbox("Boş değerlere izin ver", value=col.get("nullable", False), key=f"sc_null_{index}")
        with c2:
            col["unique"] = st.checkbox("Benzersiz olmalı", value=col.get("unique", False), key=f"sc_uniq_{index}")

        internal_type, faker_provider = USER_TYPES[col["user_type"]]
        cfg = col.setdefault("config", {})

        if internal_type in ("numeric_int", "numeric_float"):
            is_int = internal_type == "numeric_int"
            c1, c2 = st.columns(2)
            with c1:
                cfg["min"] = st.number_input("Min", value=float(cfg.get("min", 0)), key=f"sc_min_{index}")
                cfg["mean"] = st.number_input("Ortalama", value=float(cfg.get("mean", 50)), key=f"sc_mean_{index}")
            with c2:
                cfg["max"] = st.number_input("Maks", value=float(cfg.get("max", 100)), key=f"sc_max_{index}")
                cfg["std"] = st.number_input("Std Sapma", min_value=0.0, value=float(cfg.get("std", 10)), key=f"sc_std_{index}")

            cfg["distribution"] = st.selectbox(
                "Dağılım", ["normal", "uniform"],
                index=0 if cfg.get("distribution", "normal") == "normal" else 1,
                key=f"sc_dist_{index}",
            )
            if not is_int:
                cfg["decimals"] = int(st.number_input("Ondalık hane", 0, 10, int(cfg.get("decimals", 2)), key=f"sc_dec_{index}"))
            cfg["allow_negative"] = st.checkbox("Negatif değerlere izin ver", value=cfg.get("allow_negative", True), key=f"sc_neg_{index}")
            cfg["sequential"] = st.checkbox("Sıralı üret (step)", value=cfg.get("sequential", False), key=f"sc_seq_{index}")
            if cfg["sequential"]:
                cfg["step"] = st.number_input("Adım değeri", value=float(cfg.get("step", 1)), key=f"sc_step_{index}")
            cfg["is_int"] = is_int

        elif internal_type == "categorical":
            raw = st.text_area(
                "Kategoriler (her satıra bir tane, 'değer, ağırlık' formatında opsiyonel)",
                value=cfg.get("_raw", "A, 1\nB, 1\nC, 1"),
                key=f"sc_cat_{index}",
                height=120,
            )
            cfg["_raw"] = raw
            values, weights = [], []
            for line in raw.strip().split("\n"):
                if not line.strip():
                    continue
                parts = [p.strip() for p in line.split(",")]
                values.append(parts[0])
                try:
                    weights.append(float(parts[1]) if len(parts) > 1 else 1.0)
                except ValueError:
                    weights.append(1.0)
            cfg["values"] = values
            cfg["weights"] = weights

        elif internal_type == "datetime":
            c1, c2 = st.columns(2)
            with c1:
                cfg["start_date"] = str(st.date_input("Başlangıç", value=None, key=f"sc_dstart_{index}") or cfg.get("start_date", "2020-01-01"))
            with c2:
                cfg["end_date"] = str(st.date_input("Bitiş", value=None, key=f"sc_dend_{index}") or cfg.get("end_date", "2024-12-31"))
            fmt_keys = list(DATE_FORMAT_OPTIONS.keys())
            fmt_label = st.selectbox("Çıktı formatı", fmt_keys, index=0, key=f"sc_dfmt_{index}")
            cfg["output_format"] = DATE_FORMAT_OPTIONS[fmt_label]
            cfg["include_time"] = st.checkbox("Saat bilgisi dahil", value=cfg.get("include_time", False), key=f"sc_dtime_{index}")
            cfg["business_days_only"] = st.checkbox("Sadece iş günleri", value=cfg.get("business_days_only", False), key=f"sc_dbiz_{index}")
            cfg["sequential"] = st.checkbox("Sıralı", value=cfg.get("sequential", False), key=f"sc_dseq_{index}")

        elif internal_type == "boolean":
            cfg["true_ratio"] = st.slider("True olasılığı", 0.0, 1.0, float(cfg.get("true_ratio", 0.5)), 0.05, key=f"sc_btrue_{index}")
            fmt_keys = list(BOOLEAN_FORMAT_OPTIONS.keys())
            fmt_label = st.selectbox("Değer formatı", fmt_keys, index=0, key=f"sc_bfmt_{index}")
            cfg["value_format"] = BOOLEAN_FORMAT_OPTIONS[fmt_label]

        elif internal_type == "id":
            c1, c2, c3 = st.columns(3)
            with c1:
                cfg["prefix"] = st.text_input("Önek", value=cfg.get("prefix", "ID-"), key=f"sc_idpre_{index}")
            with c2:
                cfg["start"] = int(st.number_input("Başlangıç numarası", value=int(cfg.get("start", 1)), key=f"sc_idstart_{index}"))
            with c3:
                cfg["length"] = int(st.number_input("Sabit uzunluk", min_value=1, max_value=20, value=int(cfg.get("length", 6)), key=f"sc_idlen_{index}"))
            cfg["sequential"] = st.checkbox("Sıralı (aksi takdirde rastgele benzersiz)", value=cfg.get("sequential", True), key=f"sc_idseq_{index}")
            cfg["unique"] = True

        elif internal_type == "pattern":
            st.caption("Sembol: `#` rakam, `@` büyük harf, `&` küçük harf, `?` harf, `*` alfasayısal. Örnek: `ABC-####-@@`")
            cfg["pattern"] = st.text_input("Desen", value=cfg.get("pattern", "####-@@@@"), key=f"sc_pat_{index}")

        elif internal_type == "text":
            cfg["avg_length"] = int(st.number_input(
                "Ortalama karakter uzunluğu",
                min_value=1, max_value=500,
                value=int(cfg.get("avg_length", 20)),
                key=f"sc_tlen_{index}",
            ))

        elif internal_type == "faker":
            cfg["faker_provider"] = faker_provider
            st.caption(f"Faker sağlayıcısı: `{faker_provider}`")

        if col["unique"]:
            cfg["unique"] = True

    return col


def _build_profiles(columns: list) -> list:
    """Convert scratch column definitions to ColumnProfile objects."""
    profiles = []
    for col in columns:
        internal_type, faker_provider = USER_TYPES[col["user_type"]]
        cfg = dict(col.get("config", {}))
        if internal_type == "faker":
            cfg["faker_provider"] = faker_provider
        profile = ColumnProfile(
            name=col["name"],
            detected_type=internal_type,
            nullable=col.get("nullable", False),
            null_ratio=0.1 if col.get("nullable") else 0.0,
            stats={},
            faker_hint=faker_provider,
            generation_config=cfg,
        )
        profiles.append(profile)
    return profiles


def render():
    columns = st.session_state.get("scratch_columns", [])
    dataset = st.session_state.get("scratch_dataset", {})

    if not dataset or not columns:
        st.warning("Veri seti yapılandırması eksik. Başa dönün.")
        if st.button("Başlangıca Dön"):
            st.session_state["step"] = 1
            safe_rerun()
        return

    st.header("Adım 2: Sütun Tanımlama")
    if st.button("< Veri Seti Ayarlarına Dön"):
        st.session_state["step"] = 1
        safe_rerun()

    st.write("Her sütunu modüler kartlar halinde tanımlayın.")

    # --- Sidebar: quality/noise + business rules ---
    with st.sidebar:
        st.header("Veri Kalitesi")
        mode = st.radio("Mod", ["Temiz", "Gerçek Dünya (Gürültülü)"], index=0, key="scratch_mode")

        noise_config = {}
        if mode == "Gerçek Dünya (Gürültülü)":
            noise_config["null_ratio"] = st.slider("Boş değer oranı", 0.0, 0.3, 0.05, 0.01)
            noise_config["outlier_ratio"] = st.slider("Aykırı değer oranı", 0.0, 0.1, 0.02, 0.005)
            noise_config["duplicate_ratio"] = st.slider("Mükerrer satır oranı", 0.0, 0.2, 0.02, 0.01)
            noise_config["typo_ratio"] = st.slider("Yazım hatası oranı", 0.0, 0.2, 0.02, 0.01)
            noise_config["whitespace_ratio"] = st.slider("Boşluk tutarsızlığı oranı", 0.0, 0.2, 0.02, 0.01)
            noise_config["format_inconsistency_ratio"] = st.slider("Format tutarsızlığı oranı", 0.0, 0.2, 0.02, 0.01)

        st.divider()
        st.subheader("İş Kuralları")
        rules_text = st.text_area("Pandas sorguları (her satıra bir tane)", value="", height=80, key="scratch_rules")
        business_rules = [r.strip() for r in rules_text.strip().split("\n") if r.strip()]

    # --- Column cards ---
    for i, col in enumerate(columns):
        _scratch_column_card(col, i)

    # Add/remove row
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("+ Sütun Ekle", use_container_width=True):
            columns.append({
                "name": f"column_{len(columns) + 1}",
                "user_type": "Tam Sayı (Integer)",
                "nullable": False,
                "unique": False,
                "config": {},
            })
            st.session_state["scratch_columns"] = columns
            safe_rerun()
    with c2:
        if len(columns) > 1 and st.button("− Son Sütunu Sil", use_container_width=True):
            columns.pop()
            st.session_state["scratch_columns"] = columns
            safe_rerun()

    st.session_state["scratch_columns"] = columns

    st.divider()
    if st.button("Veri Üret →", type="primary", use_container_width=True):
        profiles = _build_profiles(columns)
        st.session_state["profiles"] = profiles
        st.session_state["global_config"] = {
            "num_rows": dataset["num_rows"],
            "locale": dataset["locale"],
            "noise_config": noise_config if noise_config else None,
            "correlation_rules": None,
            "business_rules": business_rules if business_rules else None,
        }
        st.session_state["user_overrides"] = {}
        st.session_state["needs_regeneration"] = True
        st.session_state["step"] = 3
        safe_rerun()
