import streamlit as st

from ui.components import page_header, render_footer, vista_clasificador


def pagina_clasificar(datos_modelo, metricas):
    """Solo clasificación de tickets (sin métricas ni tablas)."""
    page_header()
    if datos_modelo is None:
        st.error("⚠️ Modelo no encontrado. Ejecuta `python train_model.py`")
        return

    vista_clasificador(datos_modelo, num_input=1, num_resultado=2)
    render_footer(metricas)
