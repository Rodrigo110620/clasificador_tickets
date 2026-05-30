"""ui/pages/batch_train.py — Carga por lotes para entrenamiento."""

import time

import pandas as pd
import streamlit as st

from memoria import guardar_en_memoria
from preprocess import es_texto_valido, preprocesar_con_detalle, preprocesar_texto
from services.dataset import agregar_lote
from services.training import ejecutar_reentrenamiento
from ui.components import section_title


def _color_estado(estado: str) -> str:
    if estado == "✓ Agregado":
        return "#16a34a"
    if estado == "⚠ Duplicado":
        return "#d97706"
    if estado == "✗ Inválido":
        return "#dc2626"
    return "#64748b"


def pagina_batch_entrenamiento(datos_modelo=None, metricas=None):
    st.markdown(
        """
        <div class="page-header">
            <h1>📦 Carga por lotes — Entrenamiento</h1>
            <p>Sube un CSV con tickets etiquetados para agregar al dataset y reentrenar el modelo.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Instrucciones ──────────────────────────────────────────
    with st.expander("📋 Formato requerido del CSV", expanded=False):
        st.markdown(
            """
            El archivo debe tener **exactamente dos columnas**:

            | ticket | categoria |
            |--------|-----------|
            | No puedo iniciar sesión en el sistema | Credenciales |
            | Error al conectar con la base de datos | Base de Datos |

            - Codificación: **UTF-8**
            - Separador: **coma** (`,`)
            - Hasta **9 000 filas** por lote
            - Las categorías deben coincidir con las del modelo actual
            """
        )

    # ── Upload ─────────────────────────────────────────────────
    section_title(1, "Selecciona el archivo CSV")
    archivo = st.file_uploader(
        "Archivo CSV de tickets etiquetados",
        type=["csv"],
        label_visibility="collapsed",
        key="batch_train_upload",
    )

    if archivo is None:
        st.markdown(
            '<div class="placeholder-result">Sube un CSV para comenzar la carga por lotes.</div>',
            unsafe_allow_html=True,
        )
        return

    # ── Leer CSV ───────────────────────────────────────────────
    try:
        df = pd.read_csv(archivo)
    except Exception as e:
        st.error(f"No se pudo leer el CSV: {e}")
        return

    if "ticket" not in df.columns or "categoria" not in df.columns:
        st.error("El CSV debe tener las columnas **ticket** y **categoria**.")
        return

    df = df[["ticket", "categoria"]].dropna()
    total = len(df)

    if total == 0:
        st.warning("El archivo está vacío o no tiene filas válidas.")
        return
    if total > 9000:
        st.warning(f"El archivo tiene {total} filas. Se procesarán solo las primeras 9 000.")
        df = df.head(9000)
        total = 9000

    st.markdown(
        f'<div class="card"><strong>{total}</strong> tickets encontrados en el archivo.</div>',
        unsafe_allow_html=True,
    )

    # ── Botón procesar ──────────────────────────────────────────
    section_title(2, "Procesar lote")
    if not st.button("🚀 Iniciar carga por lotes", type="primary", key="btn_batch_train"):
        return

    inicio = time.perf_counter()

    # ── Logs en tiempo real ────────────────────────────────────
    logs_container = st.empty()
    progress_bar = st.progress(0)

    validos, invalidos, duplicados_mem = [], [], 0
    logs: list[str] = []

    with st.status("Procesando tickets…", expanded=True) as status:
        for i, row in enumerate(df.itertuples(index=False)):
            texto = str(row.ticket).strip()
            categoria = str(row.categoria).strip()

            detalle = preprocesar_con_detalle(texto)
            ok, motivo = es_texto_valido(texto, detalle)

            if ok:
                validos.append({"ticket": texto, "categoria": categoria})
                logs.append(f"✓ [{i+1}/{total}] Válido → {categoria[:30]}")
            else:
                invalidos.append({"ticket": texto, "motivo": motivo})
                logs.append(f"✗ [{i+1}/{total}] Inválido — {motivo[:60]}")

            # Mostrar últimas 8 líneas de log
            logs_container.code("\n".join(logs[-8:]), language=None)
            progress_bar.progress((i + 1) / total)

        # Agregar al CSV
        st.write("💾 Guardando en dataset/tickets.csv…")
        resultado_csv = agregar_lote(validos)

        # Guardar en memoria solo los genuinamente nuevos
        st.write("🧠 Actualizando memoria.json…")
        for fila in validos:
            texto_proc = preprocesar_texto(fila["ticket"])
            guardar_en_memoria(texto_proc, fila["categoria"])

        latencia_ms = int((time.perf_counter() - inicio) * 1000)
        score = len(validos) / total * 100 if total > 0 else 0

        status.update(label="✅ Carga completada", state="complete")

    progress_bar.empty()
    logs_container.empty()

    # ── Métricas resultado ──────────────────────────────────────
    section_title(3, "Resultado")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total procesados", total)
    c2.metric("Válidos", len(validos), delta=f"{score:.1f}% del total")
    c3.metric("Inválidos", len(invalidos))
    c4.metric("Duplicados (omitidos)", resultado_csv["duplicados"])

    st.markdown(
        f"""
        <div class="card" style="margin-top:0.75rem;">
            <strong>Score de calidad:</strong> {score:.1f}% de tickets válidos&nbsp;&nbsp;|&nbsp;&nbsp;
            <strong>Agregados al CSV:</strong> {resultado_csv['agregados']}&nbsp;&nbsp;|&nbsp;&nbsp;
            <strong>Latencia total:</strong> {latencia_ms:,} ms
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Detalle de inválidos
    if invalidos:
        with st.expander(f"Ver {len(invalidos)} tickets rechazados"):
            df_inv = pd.DataFrame(invalidos)
            st.dataframe(df_inv, use_container_width=True, hide_index=True)

    # ── Reentrenar ─────────────────────────────────────────────
    if resultado_csv["agregados"] > 0:
        section_title(4, "Reentrenar modelo")
        st.info(
            f"Se agregaron **{resultado_csv['agregados']}** tickets nuevos. "
            "Podés reentrenar el modelo ahora para incorporarlos."
        )
        if st.button("🔄 Reentrenar ahora", type="primary", key="btn_reentrenar_batch"):
            with st.spinner("Reentrenando el modelo…"):
                res = ejecutar_reentrenamiento()
            if res.get("ok"):
                st.success(
                    f"✅ Modelo reentrenado — F1: {res.get('f1', 0):.2%} | "
                    f"Latencia: {res.get('latencia_ms', 0):,} ms"
                )
            else:
                st.error(res.get("mensaje", "Error al reentrenar."))
    else:
        st.info("No se agregaron tickets nuevos (todos eran duplicados o inválidos).")