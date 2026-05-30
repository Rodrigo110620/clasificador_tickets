"""ui/pages/batch_infer.py — Inferencia por lotes (clasificar sin categoría)."""

import io
import time

import pandas as pd
import streamlit as st

from preprocess import es_texto_valido, preprocesar_con_detalle
from services.classifier import clasificar_ticket
from ui.components import section_title


def pagina_batch_inferencia(datos_modelo: dict, metricas=None):
    st.markdown(
        """
        <div class="page-header">
            <h1>🔮 Inferencia por lotes</h1>
            <p>Sube un CSV con tickets sin categoría y el modelo los clasificará automáticamente.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not datos_modelo or not datos_modelo.get("modelo"):
        st.error("No hay modelo cargado. Entrená el modelo primero desde la barra lateral.")
        return

    nombre_modelo = datos_modelo.get("nombre", "Modelo")

    # ── Instrucciones ──────────────────────────────────────────
    with st.expander("📋 Formato requerido del CSV", expanded=False):
        st.markdown(
            """
            El archivo debe tener **una columna llamada `ticket`**:

            | ticket |
            |--------|
            | No puedo iniciar sesión en el sistema |
            | Error al conectar con la base de datos |

            - Codificación: **UTF-8**
            - Separador: **coma** (`,`)
            - Hasta **9 000 filas** por lote
            - El resultado incluye: `ticket`, `categoria_predicha`, `confianza`, `valido`, `motivo_rechazo`
            """
        )

    # ── Upload ─────────────────────────────────────────────────
    section_title(1, "Selecciona el archivo CSV")
    archivo = st.file_uploader(
        "Archivo CSV de tickets sin categoría",
        type=["csv"],
        label_visibility="collapsed",
        key="batch_infer_upload",
    )

    if archivo is None:
        st.markdown(
            '<div class="placeholder-result">Sube un CSV para comenzar la inferencia por lotes.</div>',
            unsafe_allow_html=True,
        )
        return

    # ── Leer CSV ───────────────────────────────────────────────
    try:
        df = pd.read_csv(archivo)
    except Exception as e:
        st.error(f"No se pudo leer el CSV: {e}")
        return

    if "ticket" not in df.columns:
        st.error("El CSV debe tener al menos una columna llamada **ticket**.")
        return

    df = df[["ticket"]].dropna()
    total = len(df)

    if total == 0:
        st.warning("El archivo está vacío o no tiene filas válidas.")
        return
    if total > 9000:
        st.warning(f"El archivo tiene {total} filas. Se procesarán solo las primeras 9 000.")
        df = df.head(9000)
        total = 9000

    st.markdown(
        f"""
        <div class="card">
            <strong>{total}</strong> tickets encontrados &nbsp;|&nbsp;
            Modelo: <strong>{nombre_modelo}</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Botón procesar ──────────────────────────────────────────
    section_title(2, "Clasificar lote")
    if not st.button("🚀 Iniciar inferencia", type="primary", key="btn_batch_infer"):
        return

    inicio = time.perf_counter()
    modelo = datos_modelo["modelo"]

    logs_container = st.empty()
    progress_bar = st.progress(0)

    resultados: list[dict] = []
    confianzas_validos: list[float] = []
    logs: list[str] = []
    n_validos = 0

    with st.status("Clasificando tickets…", expanded=True) as status:
        for i, row in enumerate(df.itertuples(index=False)):
            texto = str(row.ticket).strip()

            detalle = preprocesar_con_detalle(texto)
            ok, motivo = es_texto_valido(texto, detalle)

            if ok:
                resultado = clasificar_ticket(modelo, texto, detalle)
                categoria = resultado["categoria"]
                confianza = round(resultado["confianza"], 2)
                confianzas_validos.append(confianza)
                n_validos += 1
                logs.append(
                    f"✓ [{i+1}/{total}] {categoria:<20} {confianza:.1f}% — "
                    f"{texto[:50]}{'…' if len(texto) > 50 else ''}"
                )
                resultados.append({
                    "ticket": texto,
                    "categoria_predicha": categoria,
                    "confianza": confianza,
                    "valido": True,
                    "motivo_rechazo": "",
                })
            else:
                logs.append(f"✗ [{i+1}/{total}] Inválido — {motivo[:60]}")
                resultados.append({
                    "ticket": texto,
                    "categoria_predicha": "",
                    "confianza": 0.0,
                    "valido": False,
                    "motivo_rechazo": motivo,
                })

            logs_container.code("\n".join(logs[-8:]), language=None)
            progress_bar.progress((i + 1) / total)

        latencia_ms = int((time.perf_counter() - inicio) * 1000)
        score_conf = sum(confianzas_validos) / len(confianzas_validos) if confianzas_validos else 0
        score_valid = n_validos / total * 100 if total > 0 else 0

        status.update(label="✅ Inferencia completada", state="complete")

    progress_bar.empty()
    logs_container.empty()

    # ── Métricas resultado ──────────────────────────────────────
    section_title(3, "Resultado")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total procesados", total)
    c2.metric("Clasificados", n_validos, delta=f"{score_valid:.1f}% válidos")
    c3.metric("Confianza promedio", f"{score_conf:.1f}%")
    c4.metric("Latencia total", f"{latencia_ms:,} ms")

    st.markdown(
        f"""
        <div class="card" style="margin-top:0.75rem;">
            <strong>Score:</strong> {score_conf:.1f}% confianza promedio en tickets clasificados &nbsp;|&nbsp;
            <strong>Tickets inválidos:</strong> {total - n_validos}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Preview tabla ───────────────────────────────────────────
    section_title(4, "Vista previa de resultados")
    df_result = pd.DataFrame(resultados)

    # Resaltar columna de categoría
    st.dataframe(
        df_result,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ticket":            st.column_config.TextColumn("Ticket", width="large"),
            "categoria_predicha":st.column_config.TextColumn("Categoría predicha", width="medium"),
            "confianza":         st.column_config.NumberColumn("Confianza (%)", format="%.1f"),
            "valido":            st.column_config.CheckboxColumn("Válido"),
            "motivo_rechazo":    st.column_config.TextColumn("Motivo rechazo", width="large"),
        },
    )

    # ── Distribución por categoría ──────────────────────────────
    if n_validos > 0:
        with st.expander("📊 Distribución por categoría predicha"):
            dist = (
                df_result[df_result["valido"]]
                .groupby("categoria_predicha")
                .size()
                .reset_index(name="cantidad")
                .sort_values("cantidad", ascending=False)
            )
            st.dataframe(dist, use_container_width=True, hide_index=True)

    # ── Descarga ────────────────────────────────────────────────
    section_title(5, "Descargar resultados")
    csv_bytes = df_result.to_csv(index=False, encoding="utf-8").encode("utf-8")
    st.download_button(
        label="⬇️ Descargar CSV de resultados",
        data=csv_bytes,
        file_name="inferencia_resultado.csv",
        mime="text/csv",
        type="primary",
        key="btn_download_infer",
    )