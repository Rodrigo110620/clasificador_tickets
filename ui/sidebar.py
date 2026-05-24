import streamlit as st

from config.constants import MIN_EJEMPLOS_POR_CATEGORIA, MENU_OPCIONES
from services.training import ejecutar_reentrenamiento


def _labels_nav():
    return [label for _, label in MENU_OPCIONES]


def _keys_nav():
    return [key for key, _ in MENU_OPCIONES]


def _boton_reentrenar():
    """Siempre visible en la barra lateral."""
    st.markdown("---")
    if st.button(
        "🔄 Reentrenar modelo",
        type="primary",
        use_container_width=True,
        help="Entrena de nuevo con todos los tickets de dataset/tickets.csv",
    ):
        with st.spinner("Entrenando…"):
            resultado = ejecutar_reentrenamiento()
        if resultado.get("ok"):
            st.success(resultado["mensaje"])
            omitidas = resultado.get("categorias_omitidas") or []
            if omitidas:
                st.warning(
                    f"Omitidas (< {MIN_EJEMPLOS_POR_CATEGORIA} ej.): {', '.join(omitidas)}"
                )
            st.rerun()
        else:
            st.error(resultado.get("mensaje", "No se pudo entrenar"))


def _panel_admin():
    st.checkbox(
        "Modo administrador",
        key="es_admin",
        help="Permite corregir categorías manualmente tras clasificar",
    )


def render_sidebar():
    labels = _labels_nav()
    keys = _keys_nav()
    idx = keys.index(st.session_state.pagina) if st.session_state.pagina in keys else 0

    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-logo">
                <div style="font-size:2.2rem;">🎧</div>
                <h2>Soporte IA</h2>
                <p>Clasificador de Tickets</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        seleccion = st.radio(
            "Navegación",
            labels,
            index=idx,
            label_visibility="collapsed",
        )
        st.session_state.pagina = keys[labels.index(seleccion)]

        _boton_reentrenar()
        _panel_admin()

        try:
            from services.model_loader import obtener_modelo
            datos = obtener_modelo()
            if datos and datos.get("nombre"):
                nombre = datos["nombre"]
                st.markdown(
                    f'<div class="sidebar-modelo-activo">'
                    f'🤖 <strong>Modelo en uso</strong>'
                    f'<span class="modelo-nombre">{nombre}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        except Exception:
            pass

        st.markdown(
            """
            <div class="sidebar-block">
                <strong>Acerca del Proyecto</strong><br><br>
                Clasificación automática de tickets de soporte técnico
                mediante Machine Learning y NLP.
            </div>
            <div class="sidebar-block">
                <strong>Tecnologías</strong>
                <ul class="sidebar-tech">
                    <li>Python · Scikit-learn</li>
                    <li>TF-IDF · NLTK</li>
                    <li>Streamlit</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
