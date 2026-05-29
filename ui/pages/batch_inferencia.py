import time

import streamlit as st

from preprocess import es_texto_valido, preprocesar_con_detalle
from services.classifier import clasificar_ticket
from services.dataset import cargar_dataset
from ui.components import page_header, render_footer


def pagina_batch_inferencia(datos_modelo, metricas):
    page_header()
    if datos_modelo is None:
        st.error("⚠️ Modelo no encontrado. Ejecuta `python train_model.py`")
        return

    st.markdown(
        "Ejecuta inferencia en batch sobre el dataset completo para medir rendimiento y confianza promedio."
    )

    df = cargar_dataset()
    if df.empty:
        st.warning("No hay tickets en dataset/tickets.csv para procesar en batch.")
        return

    if st.button("▶️ Ejecutar lote de inferencia"):
        tickets = df["ticket"].astype(str).tolist()
        total = len(tickets)
        status = st.empty()
        progress = st.progress(0)
        suma_confianza = 0.0
        cont_clasificados = 0
        no_validos = 0
        inicio = time.perf_counter()
        update_step = max(1, total // 15)
        modelo = datos_modelo["modelo"]

        for idx, texto in enumerate(tickets, start=1):
            pre = preprocesar_con_detalle(texto)
            valido, _ = es_texto_valido(texto, pre)
            if not valido:
                no_validos += 1
            else:
                resultado = clasificar_ticket(modelo, texto, pre)
                suma_confianza += resultado.get("confianza", 0.0)
                cont_clasificados += 1

            if idx % update_step == 0 or idx == total:
                status.info(
                    f"Inferencia: {idx}/{total} tickets procesados — inválidos {no_validos}"
                )
                progress.progress(idx / total)

        total_ms = int((time.perf_counter() - inicio) * 1000)
        promedio_ms = total_ms / total if total else 0
        promedio_confianza = suma_confianza / cont_clasificados if cont_clasificados else 0.0
        porcentaje_validos = cont_clasificados * 100 / total if total else 0.0

        st.markdown("---")
        st.success("Batch de inferencia completado")
        cols = st.columns(3)
        cols[0].metric("Tickets inferidos", f"{cont_clasificados}/{total}")
        cols[1].metric("% inferidos válidos", f"{porcentaje_validos:.1f}%")
        cols[2].metric("Latencia total", f"{total_ms} ms")
        st.metric("Confianza promedio", f"{promedio_confianza:.1f}%")
        if no_validos:
            st.warning(f"{no_validos} tickets no eran válidos y se omitieron de la inferencia.")

    render_footer(metricas)
