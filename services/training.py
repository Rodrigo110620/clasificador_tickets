"""Reentrenamiento invocable desde Streamlit."""

import time

import streamlit as st

from train_model import entrenar_desde_csv


def ejecutar_reentrenamiento() -> dict:
    """Entrena con todos los tickets del CSV y limpia cachés de Streamlit."""
    inicio = time.perf_counter()
    resultado = entrenar_desde_csv(verbose=False)
    resultado["latencia_ms"] = int((time.perf_counter() - inicio) * 1000)

    if resultado.get("ok"):
        st.cache_resource.clear()
        st.cache_data.clear()
        resultado["cache_invalidado"] = True

    return resultado
