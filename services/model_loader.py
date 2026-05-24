import gzip
import os
import pickle

import streamlit as st

from config.constants import RUTA_MODELO


def _version_modelo() -> str:
    """Cambia cuando se reentrena → invalida caché de Streamlit."""
    partes = []
    for ruta in (RUTA_MODELO, "models/mejor_modelo.pkl", "models/metricas_entrenamiento.pkl"):
        if os.path.exists(ruta):
            partes.append(f"{ruta}:{os.path.getmtime(ruta)}")
    return "|".join(partes) or "sin-modelo"


@st.cache_resource
def cargar_modelo(_version: str = ""):
    ruta_gz = RUTA_MODELO
    ruta_pkl = "models/mejor_modelo.pkl"
    if os.path.exists(ruta_gz):
        with gzip.open(ruta_gz, "rb") as f:
            return pickle.load(f)
    if os.path.exists(ruta_pkl):
        with open(ruta_pkl, "rb") as f:
            return pickle.load(f)
    return None


def obtener_modelo():
    return cargar_modelo(_version_modelo())
