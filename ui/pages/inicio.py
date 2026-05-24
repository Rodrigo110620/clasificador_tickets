import streamlit as st

from ui.components import (
    page_header,
    render_footer,
    vista_clasificador,
    vista_comparacion_modelos,
    vista_matriz_confusion,
    vista_metricas_kpi,
)


def pagina_inicio(datos_modelo, metricas):
    """Dashboard completo: clasificación + métricas + matriz + comparación."""
    page_header()
    if datos_modelo is None:
        st.error("⚠️ Modelo no encontrado. Ejecuta primero `python train_model.py`")
        st.code("python train_model.py", language="bash")
        if st.button("🔄 Reintentar carga del modelo"):
            st.cache_resource.clear()
            st.cache_data.clear()
        return

    vista_clasificador(datos_modelo, num_input=1, num_resultado=2)

    if metricas:
        vista_metricas_kpi(metricas, datos_modelo, num_seccion=3)
        col_cm, col_tab = st.columns(2, gap="large")
        with col_cm:
            vista_matriz_confusion(metricas, datos_modelo, num_seccion=4)
        with col_tab:
            vista_comparacion_modelos(metricas, datos_modelo, num_seccion=5)

    render_footer(metricas)
