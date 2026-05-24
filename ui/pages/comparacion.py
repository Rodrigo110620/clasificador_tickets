import streamlit as st

from services.metrics import cargar_metricas
from ui.components import page_header, render_footer, vista_comparacion_modelos


def pagina_comparacion(metricas, datos_modelo):
    """Solo tabla comparativa de modelos."""
    page_header()
    if datos_modelo is None:
        st.error("Modelo no encontrado. Ejecuta `python train_model.py`")
        return
    if not metricas:
        metricas = cargar_metricas(datos_modelo)

    vista_comparacion_modelos(metricas, datos_modelo, num_seccion=1)
    render_footer(metricas)
