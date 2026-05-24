import html
from datetime import datetime

import streamlit as st

from config.constants import PRIORIDAD, icono_categoria
from services.classifier import guardar_para_entrenamiento, procesar_clasificacion
from services.dataset import contar_por_categoria, ejemplos_por_categoria
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


def nombre_modelo_activo(metricas: dict | None, datos_modelo: dict | None) -> str:
    if datos_modelo and datos_modelo.get("nombre"):
        return datos_modelo["nombre"]
    if metricas:
        return metricas.get("modelo_activo") or metricas.get("mejor", "—")
    return "—"


def _contenido_analisis(resultado: dict):
    claves = resultado.get("palabras_clave") or []
    if claves:
        st.markdown(f"**Palabras clave:** {', '.join(claves)}")
    else:
        st.markdown("**Palabras clave:** No se encontraron términos útiles.")
    st.markdown(f"**Texto limpio (stemming):** `{resultado.get('texto_procesado', '')}`")
    tokens = resultado.get("tokens_utiles") or []
    st.markdown(f"**Tokens útiles:** {', '.join(tokens) if tokens else '—'}")
    stems = resultado.get("stems") or []
    st.markdown(f"**Stems aplicados:** {', '.join(stems) if stems else '—'}")
    elim = resultado.get("palabras_eliminadas") or []
    if elim:
        muestra = ", ".join(elim[:12])
        if len(elim) > 12:
            muestra += f" … (+{len(elim) - 12})"
        st.caption(f"Stopwords / ruido eliminado: {muestra}")


def render_resultado(resultado: dict, nombre_modelo: str):
    cat = resultado.get("categoria_modelo", resultado["categoria"])
    conf = resultado["confianza"]
    icono = icono_categoria(cat)
    prioridad, badge_cls = PRIORIDAD.get(cat, PRIORIDAD.get("Otros", ("Media", "badge-media")))
    bar_width = min(max(int(conf), 8), 100)
    desconocido = resultado.get("desconocido", False)
    umbral = resultado.get("umbral_pct", 20)

    estado_cls = "result-hero" if not desconocido else "result-hero result-hero-warn"
    st.markdown(
        f"""
        <div class="{estado_cls}">
            <div class="result-hero-top">
                <span class="result-hero-label">Categoría detectada</span>
                <span class="result-hero-conf">{conf:.0f}% confianza</span>
            </div>
            <div class="result-hero-cat">{icono} {html.escape(cat)}</div>
            <div class="conf-bar-wrap conf-bar-hero">
                <div class="conf-bar-fill" style="width:{bar_width}%;"></div>
            </div>
            <div class="badges-row">
                <span class="badge {badge_cls}">Prioridad: {prioridad[0]}</span>
                <span class="badge badge-modelo">🤖 {html.escape(nombre_modelo)}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if desconocido:
        st.markdown(
            f"""
            <div class="alert-desconocido">
                ⚠️ {html.escape(resultado.get('mensaje_desconocido', ''))}
                (umbral dinámico ~{umbral:.0f}%, margen sobre 2.ª opción: {resultado.get('margen_segunda_pct', 0):.0f}%)
            </div>
            """,
            unsafe_allow_html=True,
        )

    grafico_probabilidades_html(resultado["probabilidades"], cat)

    with st.expander("🔎 Análisis del ticket", expanded=False):
        _contenido_analisis(resultado)

    render_admin_etiquetado(resultado)


def render_admin_etiquetado(resultado: dict):
    if not st.session_state.get("es_admin"):
        return

    st.markdown("---")
    st.markdown("**🛠 Revisión manual (administrador)**")

    cats_dataset = sorted(contar_por_categoria().keys())
    sugeridas = sorted(resultado.get("probabilidades", {}).keys(), reverse=False)
    opciones = sorted(set(cats_dataset) | set(sugeridas))
    if resultado.get("categoria_modelo") and resultado["categoria_modelo"] not in opciones:
        opciones.append(resultado["categoria_modelo"])

    default_idx = 0
    if resultado.get("categoria_modelo") in opciones:
        default_idx = opciones.index(resultado["categoria_modelo"])

    categoria_correcta = st.selectbox(
        "Asignar categoría correcta",
        opciones,
        index=default_idx,
        key=f"admin_cat_{resultado.get('hash_md5', 'x')}",
    )
    nueva_categoria = st.text_input(
        "O crear categoría nueva",
        placeholder="Ej: Telefonía, VPN, Excel…",
        key=f"admin_new_{resultado.get('hash_md5', 'x')}",
    )
    cat_final = nueva_categoria.strip() if nueva_categoria.strip() else categoria_correcta

    if st.button("💾 Etiquetar y agregar al entrenamiento", type="primary"):
        guardar_para_entrenamiento(resultado["ticket"], cat_final)
        st.success(f"Ticket guardado como **{cat_final}**. Usa «Reentrenar modelo» para incorporarlo.")
        st.info(
            f"La categoría necesita al menos 20 ejemplos en el CSV para incluirse en el próximo entrenamiento. "
            f"Actualmente: {contar_por_categoria().get(cat_final, 0)}"
        )


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


def render_comparacion_tabla(metricas: dict, datos_modelo: dict | None = None):
    filas = metricas.get("comparacion", [])
    if not filas:
        st.info("Entrena el modelo con `python train_model.py` o el botón de reentrenar.")
        return

    modelo_activo = nombre_modelo_activo(metricas, datos_modelo)
    filas_html = []
    for fila in filas:
        en_uso = fila.get("en_uso") or fila["modelo"] == modelo_activo
        tr_class = "fila-mejor" if en_uso else ""
        nombre_celda = html.escape(fila["modelo"])
        if en_uso:
            nombre_celda += ' <span class="badge-en-uso">★ En uso</span>'
        filas_html.append(
            f"<tr class='{tr_class}'>"
            f"<td>{nombre_celda}</td>"
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
            ★ <strong>Modelo en uso para clasificar:</strong> {html.escape(modelo_activo)}
            <br><span class="tabla-comparacion-hint">Se elige por mayor F1-score en prueba y se calibra (sigmoid).</span>
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
        st.warning("Ejecuta el entrenamiento para generar la matriz de confusión.")


def render_footer(metricas: dict | None):
    fecha = (metricas or {}).get("fecha", datetime.now().strftime("%d/%m/%Y %H:%M"))
    st.markdown(
        f"""
        <div class="footer-bar">
            <span>ℹ️ NLP + Machine Learning para clasificación automática de tickets.</span>
            <span class="footer-ts">📅 Última actualización del modelo: {fecha}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _aplicar_ejemplo(texto: str):
    st.session_state.ticket_input = texto
    st.session_state.clasificar_ejemplo = texto


def render_ejemplos_por_categoria():
    ejemplos = ejemplos_por_categoria()
    if not ejemplos:
        return

    st.markdown(
        '<p class="ejemplos-label">Ejemplos rápidos por categoría:</p>',
        unsafe_allow_html=True,
    )
    categorias = sorted(ejemplos.keys())
    n_cols = 4
    for i in range(0, len(categorias), n_cols):
        fila = categorias[i : i + n_cols]
        cols = st.columns(len(fila))
        for col, cat in zip(cols, fila):
            etiqueta = f"{icono_categoria(cat)} {cat}"
            with col:
                st.button(
                    etiqueta,
                    key=f"ejemplo_{cat}",
                    use_container_width=True,
                    on_click=_aplicar_ejemplo,
                    args=(ejemplos[cat],),
                )


def _guardar_ticket_input():
    """on_change del textarea: persiste el valor cada vez que el usuario escribe."""
    st.session_state.ticket_input = st.session_state.ticket_input


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

    # La clave es NO tocar session_state["ticket_input"] antes de renderizar el widget.
    # Streamlit lo restaura solo desde session_state cuando el widget se recrea al
    # volver a esta página. on_change lo mantiene actualizado mientras el usuario escribe.
    ticket = st.text_area(
        "Descripción del problema",
        height=130,
        label_visibility="collapsed",
        key="ticket_input",
        placeholder="Describe el problema o solicitud del usuario…",
        on_change=_guardar_ticket_input,
    )

    st.markdown(
        f'<p class="char-counter">Caracteres: {len(ticket)}</p>',
        unsafe_allow_html=True,
    )

    render_ejemplos_por_categoria()

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
    nombre = nombre_modelo_activo(None, datos_modelo)

    if resultado and datos_modelo:
        render_resultado(resultado, nombre)
    else:
        st.markdown(
            '<div class="placeholder-result"><p>Pulse «Clasificar Ticket» para ver el resultado</p></div>',
            unsafe_allow_html=True,
        )


def vista_metricas_kpi(metricas: dict, datos_modelo: dict, num_seccion: int = 1):
    if not metricas:
        st.warning("Entrena el modelo: `python train_model.py` o reentrena desde el panel lateral.")
        return
    nombre = nombre_modelo_activo(metricas, datos_modelo)
    section_title(num_seccion, "Métricas del modelo en uso")
    st.markdown(
        f'<p class="modelo-subtitle">Clasificación con: <strong>{html.escape(nombre)}</strong></p>',
        unsafe_allow_html=True,
    )
    render_metricas_cards(metricas)


def vista_matriz_confusion(metricas: dict, datos_modelo: dict, num_seccion: int = 1):
    if not metricas:
        return
    nombre = nombre_modelo_activo(metricas, datos_modelo)
    section_title(num_seccion, "Matriz de confusión")
    render_matriz_confusion(metricas, nombre, datos_modelo)


def vista_comparacion_modelos(metricas: dict, datos_modelo: dict, num_seccion: int = 1):
    if not metricas:
        st.warning("Entrena el modelo para ver la comparación.")
        return
    section_title(num_seccion, "Comparación de modelos")
    render_comparacion_tabla(metricas, datos_modelo)


def vista_clasificador(datos_modelo: dict, num_input: int = 1, num_resultado: int = 2):
    ticket, clasificar = seccion_input(mostrar_titulo=True, num_seccion=num_input)

    ejemplo = st.session_state.pop("clasificar_ejemplo", None)
    if ejemplo:
        procesar_clasificacion(ejemplo, datos_modelo)
    elif clasificar:
        procesar_clasificacion(ticket, datos_modelo)

    st.markdown('<div class="clasif-divider"></div>', unsafe_allow_html=True)
    section_title(num_resultado, "Resultado de la clasificación")

    if st.session_state.get("ultimo_resultado") and datos_modelo:
        render_resultado(
            st.session_state.ultimo_resultado,
            nombre_modelo_activo(None, datos_modelo),
        )
    else:
        st.markdown(
            '<div class="placeholder-result"><p>Pulse «Clasificar Ticket» para ver el resultado</p></div>',
            unsafe_allow_html=True,
        )
    return ticket