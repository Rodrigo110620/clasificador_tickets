import gzip
import os
import pickle

import streamlit as st


@st.cache_resource
def cargar_modelo():
    ruta_gz = "models/mejor_modelo.pkl.gz"
    ruta_pkl = "models/mejor_modelo.pkl"
    if os.path.exists(ruta_gz):
        with gzip.open(ruta_gz, "rb") as f:
            return pickle.load(f)
    if os.path.exists(ruta_pkl):
        with open(ruta_pkl, "rb") as f:
            return pickle.load(f)
    return None
