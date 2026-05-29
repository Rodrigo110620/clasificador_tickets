import time

import streamlit as st

from preprocess import es_texto_valido, preprocesar_con_detalle
from services.dataset import cargar_dataset
from ui.components import page_header, render_footer


def pagina_batch_entrenamiento(datos_modelo, metricas):
    page_header()
    if datos_modelo is None:
        st.error("⚠️ Modelo no encontrado. Ejecuta `python train_model.py`")
        return

    st.markdown(
        "Este proceso recorre el dataset completo y valida cada ticket como si fuera parte del flujo de entrenamiento. Se mide la latencia total y la latencia promedio por ticket."
    )

    df = cargar_dataset()
    if df.empty:
        st.warning("No hay tickets en dataset/tickets.csv para procesar en batch.")
        return

    if st.button("▶️ Ejecutar lote de validación de entrenamiento"):
        tickets = df["ticket"].astype(str).tolist()
        total = len(tickets)
        status = st.empty()
        progress = st.progress(0)
        validos = 0
        inicio = time.perf_counter()
        update_step = max(1, total // 15)

        for idx, texto in enumerate(tickets, start=1):
            pre = preprocesar_con_detalle(texto)
            valido, _ = es_texto_valido(texto, pre)
            if valido:
                validos += 1

            if idx % update_step == 0 or idx == total:
                porcentaje = validos * 100 / idx if idx else 0.0
                status.info(
                    f"Validando tickets: {idx}/{total} — válidos {validos} ({porcentaje:.1f}%)"
                )
                progress.progress(idx / total)

        total_ms = int((time.perf_counter() - inicio) * 1000)
        promedio_ms = total_ms / total if total else 0
        porcentaje_validos = validos * 100 / total if total else 0.0

        st.markdown("---")
        st.success("Batch de entrenamiento finalizado")
        cols = st.columns(3)
        cols[0].metric("Tickets válidos", f"{validos}/{total}")
        cols[1].metric("% de tickets válidos", f"{porcentaje_validos:.1f}%")
        cols[2].metric("Latencia total", f"{total_ms} ms")
        st.metric("Latencia media por ticket", f"{promedio_ms:.0f} ms")

    render_footer(metricas)
