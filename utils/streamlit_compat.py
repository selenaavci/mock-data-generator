"""Streamlit sürüm uyumluluğu için yardımcılar.

Eski Streamlit sürümlerinde ``st.rerun`` bulunmaz; yerine
``st.experimental_rerun`` kullanılır. Bu modül, hangi sürüm kurulu olursa olsun
çalışan tek bir ``safe_rerun`` fonksiyonu sunar.
"""

import streamlit as st


def safe_rerun() -> None:
    """Kurulu Streamlit sürümüne göre uygun rerun fonksiyonunu çağır."""
    rerun_fn = getattr(st, "rerun", None) or getattr(st, "experimental_rerun", None)
    if rerun_fn is None:
        raise RuntimeError(
            "Streamlit kurulumunda ne 'rerun' ne de 'experimental_rerun' "
            "bulundu. Lütfen Streamlit'i güncelleyin: pip install -U streamlit"
        )
    rerun_fn()
