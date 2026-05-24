"""Reentrenamiento invocable desde Streamlit."""

import streamlit as st

from train_model import entrenar_desde_csv


def ejecutar_reentrenamiento() -> dict:
    """Entrena con todos los tickets del CSV y limpia cachés de Streamlit."""
    resultado = entrenar_desde_csv(verbose=False)
    if resultado.get("ok"):
        st.cache_resource.clear()
        st.cache_data.clear()
    return resultado
