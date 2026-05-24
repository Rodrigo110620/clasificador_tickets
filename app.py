# app.py
# Sistema Inteligente de Clasificación de Tickets — Interfaz Streamlit
# Ejecutar con: streamlit run app.py

import streamlit as st

from services.metrics import cargar_metricas
from services.model_loader import cargar_modelo
from services.session import asegurar_contenido_inicial, init_session
from ui.pages.clasificar import pagina_clasificar
from ui.pages.comparacion import pagina_comparacion
from ui.pages.historial import pagina_historial
from ui.pages.info import pagina_info
from ui.pages.inicio import pagina_inicio
from ui.pages.metricas import pagina_metricas
from ui.sidebar import render_sidebar
from ui.styles import inject_css

st.set_page_config(
    page_title="Sistema Inteligente de Clasificación de Tickets",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    inject_css()
    init_session()
    render_sidebar()

    datos_modelo = cargar_modelo()
    if datos_modelo:
        asegurar_contenido_inicial(datos_modelo)

    pagina = st.session_state.pagina
    necesita_metricas = pagina in ("inicio", "metricas", "comparacion")
    metricas = cargar_metricas(datos_modelo) if datos_modelo and necesita_metricas else None
    if datos_modelo and not metricas and pagina == "inicio":
        metricas = datos_modelo.get("metricas")

    if pagina == "inicio":
        pagina_inicio(datos_modelo, metricas)
    elif pagina == "clasificar":
        pagina_clasificar(datos_modelo, metricas)
    elif pagina == "historial":
        pagina_historial(metricas, datos_modelo)
    elif pagina == "metricas":
        pagina_metricas(datos_modelo, metricas)
    elif pagina == "comparacion":
        pagina_comparacion(metricas, datos_modelo)
    elif pagina == "info":
        pagina_info(metricas)
    else:
        pagina_inicio(datos_modelo, metricas)


if __name__ == "__main__":
    main()
