import streamlit as st

from services.metrics import cargar_metricas
from ui.components import (
    page_header,
    render_footer,
    vista_matriz_confusion,
    vista_metricas_kpi,
)


def pagina_metricas(datos_modelo, metricas):
    """Solo KPIs y matriz de confusión."""
    page_header()
    if datos_modelo is None:
        st.error("Modelo no encontrado. Ejecuta `python train_model.py`")
        return
    if not metricas:
        metricas = cargar_metricas(datos_modelo)

    vista_metricas_kpi(metricas, datos_modelo, num_seccion=1)
    vista_matriz_confusion(metricas, datos_modelo, num_seccion=2)
    render_footer(metricas)
