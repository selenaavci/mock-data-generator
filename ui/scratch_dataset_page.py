"""Sıfırdan mod — Adım 1: Genel veri seti yapılandırması."""

import streamlit as st

from utils.constants import LOCALE_OPTIONS, MAX_ROWS, WARN_ROWS
from utils.streamlit_compat import safe_rerun


def render():
    st.header("Adım 1: Veri Seti Yapılandırması")
    st.write("Üretilecek veri setinin temel özelliklerini belirleyin.")

    if st.button("< Mod Seçimine Dön"):
        st.session_state.pop("mode", None)
        st.session_state["step"] = 1
        safe_rerun()

    existing = st.session_state.get("scratch_dataset", {})

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Veri Seti Adı (opsiyonel)", value=existing.get("name", ""))
        num_rows = st.number_input(
            "Satır Sayısı",
            min_value=1,
            max_value=MAX_ROWS,
            value=int(existing.get("num_rows", 1000)),
            step=100,
        )
        if num_rows > WARN_ROWS:
            st.warning(f"{num_rows:,} satır üretmek yavaş olabilir.")

    with col2:
        num_columns = st.number_input(
            "Sütun Sayısı (başlangıç)",
            min_value=1, max_value=100,
            value=int(existing.get("num_columns", 5)),
        )
        locale_name = st.selectbox(
            "Dil (Faker)",
            list(LOCALE_OPTIONS.keys()),
            index=list(LOCALE_OPTIONS.keys()).index(existing.get("locale_name", "İngilizce"))
            if existing.get("locale_name", "İngilizce") in LOCALE_OPTIONS else 0,
        )

    description = st.text_area(
        "Açıklama / Amaç (opsiyonel)",
        value=existing.get("description", ""),
        height=80,
    )

    st.divider()
    c1, c2 = st.columns([1, 1])
    with c2:
        if st.button("Sütunları Tanımla →", type="primary", use_container_width=True):
            st.session_state["scratch_dataset"] = {
                "name": name,
                "num_rows": int(num_rows),
                "num_columns": int(num_columns),
                "locale_name": locale_name,
                "locale": LOCALE_OPTIONS[locale_name],
                "description": description,
            }
            # Initialize column list if not yet
            cols_state = st.session_state.get("scratch_columns", [])
            if len(cols_state) < num_columns:
                for i in range(len(cols_state), int(num_columns)):
                    cols_state.append({
                        "name": f"column_{i + 1}",
                        "user_type": "Tam Sayı (Integer)",
                        "nullable": False,
                        "unique": False,
                        "config": {},
                    })
            elif len(cols_state) > num_columns:
                cols_state = cols_state[: int(num_columns)]
            st.session_state["scratch_columns"] = cols_state
            st.session_state["step"] = 2
            safe_rerun()
