import html
from datetime import datetime

import streamlit as st

from config.constants import ICONOS, PRIORIDAD
from services.classifier import procesar_clasificacion
from services.metrics import evaluar_en_dataset
from ui.charts import grafico_probabilidades_html, render_matriz_confusion_html


def page_header():
    st.markdown(
        """
        <div class="page-header">
            <h1>🤖 Sistema Inteligente de Clasificación de Tickets</h1>
            <p>Clasificación automática de tickets de soporte técnico usando Inteligencia Artificial</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(num: int, texto: str):
    st.markdown(
        f'<div class="section-title"><span class="section-num">{num}</span> {texto}</div>',
        unsafe_allow_html=True,
    )


def render_resultado(resultado: dict, nombre_modelo: str):
    cat = resultado["categoria"]
    conf = resultado["confianza"]
    icono = ICONOS.get(cat, "📂")
    prioridad, badge_cls = PRIORIDAD.get(cat, ("Media", "badge-media"))
    bar_width = min(int(conf), 100)

    st.markdown(
        f"""
        <div class="result-card">
            <div class="result-header">
                <div>
                    <div style="font-size:0.85rem;color:#4a5568;">✓ Resultado de la clasificación</div>
                    <div class="result-cat">{icono} Categoría detectada: {cat}</div>
                </div>
                <div>
                    <div class="result-conf-label">Confianza del modelo</div>
                    <div class="result-conf-value">{conf:.0f}%</div>
                    <div class="conf-bar-wrap">
                        <div class="conf-bar-fill" style="width:{bar_width}%;"></div>
                    </div>
                </div>
            </div>
            <div class="result-body">
                <div class="badges-row">
                    <span class="badge {badge_cls}">Prioridad sugerida: {prioridad}</span>
                    <span class="badge badge-modelo">Modelo utilizado: {nombre_modelo}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    grafico_probabilidades_html(resultado["probabilidades"], cat)


def render_metricas_cards(metricas: dict):
    m = metricas.get("mejor_metricas", metricas)
    cols = st.columns(4)
    items = [
        ("Accuracy", m.get("accuracy", 0) * 100, "metric-blue"),
        ("Precision (Weighted)", m.get("precision", 0) * 100, "metric-green"),
        ("Recall (Weighted)", m.get("recall", 0) * 100, "metric-orange"),
        ("F1-score (Weighted)", m.get("f1_score", 0) * 100, "metric-purple"),
    ]
    for col, (label, val, cls) in zip(cols, items):
        col.markdown(
            f"""
            <div class="metric-card {cls}">
                <div class="label">{label}</div>
                <div class="value">{val:.1f}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_comparacion_tabla(metricas: dict, mejor_nombre: str):
    filas = metricas.get("comparacion", [])
    if not filas:
        st.info("Entrena el modelo con `python train_model.py` para ver la comparación.")
        return

    mejor = metricas.get("mejor", mejor_nombre)
    filas_html = []
    for fila in filas:
        es_mejor = fila["modelo"] == mejor
        tr_class = "fila-mejor" if es_mejor else ""
        filas_html.append(
            f"<tr class='{tr_class}'>"
            f"<td>{html.escape(fila['modelo'])}</td>"
            f"<td>{fila['accuracy'] * 100:.1f}%</td>"
            f"<td>{fila['precision'] * 100:.1f}%</td>"
            f"<td>{fila['recall'] * 100:.1f}%</td>"
            f"<td>{fila['f1_score'] * 100:.1f}%</td>"
            f"</tr>"
        )

    st.markdown(
        f"""
        <div class="tabla-comparacion-wrap">
            <table class="tabla-comparacion">
                <thead>
                    <tr>
                        <th>Modelo</th>
                        <th>Accuracy</th>
                        <th>Precision</th>
                        <th>Recall</th>
                        <th>F1-score</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(filas_html)}
                </tbody>
            </table>
        </div>
        <p class="tabla-comparacion-msg">
            ✔ Mejor modelo seleccionado: <strong>{html.escape(mejor)}</strong>
            (fila resaltada en verde)
        </p>
        """,
        unsafe_allow_html=True,
    )


def render_matriz_confusion(metricas: dict, nombre_modelo: str, datos_modelo=None):
    matriz = (metricas or {}).get("confusion_matrix")
    etiquetas = (metricas or {}).get("confusion_labels") or (metricas or {}).get("clases")

    if (not matriz or not etiquetas) and datos_modelo:
        m = evaluar_en_dataset()
        if m:
            matriz = m.get("confusion_matrix")
            etiquetas = m.get("confusion_labels")

    if matriz and etiquetas:
        render_matriz_confusion_html(matriz, etiquetas, nombre_modelo)
    else:
        st.warning("Ejecuta `python train_model.py` para generar la matriz de confusión.")


def render_footer(metricas: dict | None):
    fecha = (metricas or {}).get("fecha", datetime.now().strftime("%d/%m/%Y %H:%M"))
    st.markdown(
        f"""
        <div class="footer-bar">
            <span>ℹ️ Este sistema utiliza Procesamiento de Lenguaje Natural (NLP) y Machine Learning
            para clasificar tickets de soporte técnico de forma automática.</span>
            <span class="footer-ts">📅 Última actualización del modelo: {fecha}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def seccion_input(
    mostrar_titulo: bool = True,
    mostrar_boton: bool = True,
    num_seccion: int = 1,
) -> tuple[str, bool]:
    if mostrar_titulo:
        section_title(num_seccion, "Ingrese el ticket")

    st.markdown(
        '<p class="input-label">Escribe aquí el problema o solicitud del usuario:</p>',
        unsafe_allow_html=True,
    )
    ticket = st.text_area(
        "Descripción del problema",
        height=130,
        label_visibility="collapsed",
        key="ticket_input",
    )
    st.markdown(
        f'<p class="char-counter">Caracteres: {len(ticket)}</p>',
        unsafe_allow_html=True,
    )

    clasificar = False
    if mostrar_boton:
        clasificar = st.button("✈️ Clasificar Ticket", type="primary")
    return ticket, clasificar


def seccion_resultado(
    datos_modelo: dict,
    mostrar_titulo: bool = True,
    num_seccion: int = 2,
):
    if mostrar_titulo:
        section_title(num_seccion, "Resultado de la clasificación")
    resultado = st.session_state.ultimo_resultado
    nombre = datos_modelo.get("nombre", "Modelo") if datos_modelo else "—"

    if resultado and datos_modelo:
        render_resultado(resultado, nombre)
        with st.expander("🔬 Ver texto preprocesado (NLP)"):
            texto_nlp = resultado.get("texto_procesado") or "(sin términos significativos)"
            st.markdown(
                f"""
                <div class="nlp-texto-box">
                    <span class="nlp-label">Texto después del pipeline (limpieza, stopwords, lematización):</span>
                    <pre>{html.escape(texto_nlp)}</pre>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div class="placeholder-result"><p>Pulse «Clasificar Ticket» para ver el resultado</p></div>',
            unsafe_allow_html=True,
        )


def _nombre_modelo_eval(metricas: dict, datos_modelo: dict) -> str:
    return metricas.get("mejor", datos_modelo.get("nombre", "")) if metricas else ""


def vista_metricas_kpi(metricas: dict, datos_modelo: dict, num_seccion: int = 1):
    if not metricas:
        st.warning("Entrena el modelo: `python train_model.py`")
        return
    nombre = _nombre_modelo_eval(metricas, datos_modelo)
    section_title(num_seccion, "Métricas del mejor modelo")
    st.markdown(
        f'<p class="modelo-subtitle">Modelo evaluado: <strong>{nombre}</strong></p>',
        unsafe_allow_html=True,
    )
    render_metricas_cards(metricas)


def vista_matriz_confusion(metricas: dict, datos_modelo: dict, num_seccion: int = 1):
    if not metricas:
        return
    nombre = _nombre_modelo_eval(metricas, datos_modelo)
    section_title(num_seccion, "Matriz de confusión")
    render_matriz_confusion(metricas, nombre, datos_modelo)


def vista_comparacion_modelos(metricas: dict, datos_modelo: dict, num_seccion: int = 1):
    if not metricas:
        st.warning("Entrena el modelo: `python train_model.py`")
        return
    section_title(num_seccion, "Comparación de modelos")
    render_comparacion_tabla(metricas, datos_modelo.get("nombre", ""))


def vista_clasificador(datos_modelo: dict, num_input: int = 1, num_resultado: int = 2):
    """Solo entrada + resultado (sin métricas)."""
    col_izq, col_der = st.columns([1, 1], gap="large")
    with col_izq:
        ticket, clasificar = seccion_input(
            mostrar_titulo=True,
            num_seccion=num_input,
        )
        if clasificar:
            procesar_clasificacion(ticket, datos_modelo)
    with col_der:
        seccion_resultado(datos_modelo, mostrar_titulo=True, num_seccion=num_resultado)
    return ticket
