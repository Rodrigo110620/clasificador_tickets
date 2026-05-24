import os

import pandas as pd
import streamlit as st

from config.constants import RUTA_DATASET, TEXTO_EJEMPLO
from services.historial import agregar_al_historial, deduplicar_historial


def init_session():
    if "pagina" not in st.session_state:
        st.session_state.pagina = "inicio"
    if "historial" not in st.session_state:
        st.session_state.historial = []
    if "ultimo_resultado" not in st.session_state:
        st.session_state.ultimo_resultado = None
    if "contenido_inicializado" not in st.session_state:
        st.session_state.contenido_inicializado = False
    if "ticket_input" not in st.session_state:
        st.session_state.ticket_input = TEXTO_EJEMPLO


def asegurar_contenido_inicial(datos_modelo: dict):
    """Clasificación demo + historial para que Inicio e Historial no estén vacíos."""
    if st.session_state.contenido_inicializado or not datos_modelo:
        return

    from services.classifier import clasificar_ticket

    modelo = datos_modelo["modelo"]
    try:
        if os.path.exists(RUTA_DATASET):
            df = pd.read_csv(RUTA_DATASET)
            muestras = df.groupby("categoria", sort=False).first().reset_index()
            for _, row in muestras.iterrows():
                texto = str(row["ticket"])
                r = clasificar_ticket(modelo, texto)
                agregar_al_historial(texto, r)
        if st.session_state.ultimo_resultado is None:
            st.session_state.ultimo_resultado = clasificar_ticket(modelo, TEXTO_EJEMPLO)
    except Exception:
        st.session_state.ultimo_resultado = clasificar_ticket(modelo, TEXTO_EJEMPLO)

    deduplicar_historial()
    st.session_state.contenido_inicializado = True
