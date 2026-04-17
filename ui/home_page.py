"""Başlangıç sayfası: mod seçimi (yükleme / sıfırdan tasarım)."""

import streamlit as st

from utils.streamlit_compat import safe_rerun


def render():
    st.header("Nasıl Başlamak İstersiniz?")
    st.write(
        "Mevcut bir veri setini yükleyip yapısına benzer sentetik veri üretebilir "
        "ya da sıfırdan kendi veri setinizi tasarlayabilirsiniz."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📂 Mevcut Veriyi Yükle")
        st.write(
            "- CSV veya Excel dosyası yükleyin\n"
            "- Sistem sütun tiplerini otomatik algılar\n"
            "- Yapıyı korurken satır sayısını istediğiniz gibi ölçekleyin"
        )
        if st.button("Dosya Yükle", type="primary", use_container_width=True, key="mode_upload"):
            st.session_state["mode"] = "upload"
            st.session_state["step"] = 1
            safe_rerun()

    with col2:
        st.subheader("✏️ Sıfırdan Tasarla")
        st.write(
            "- Sütunları tek tek tanımlayın\n"
            "- Tip, kısıtlar ve değer aralıklarını siz belirleyin\n"
            "- Gerçekçi / gürültülü veri üretin"
        )
        if st.button("Sıfırdan Başla", type="primary", use_container_width=True, key="mode_scratch"):
            st.session_state["mode"] = "scratch"
            st.session_state["step"] = 1
            safe_rerun()
