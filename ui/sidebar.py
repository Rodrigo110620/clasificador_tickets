import streamlit as st

from config.constants import MENU_OPCIONES


def _labels_nav():
    return [label for _, label in MENU_OPCIONES]


def _keys_nav():
    return [key for key, _ in MENU_OPCIONES]


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

        st.markdown(
            """
            <div class="sidebar-block">
                <strong>Acerca del Proyecto</strong><br><br>
                Sistema de clasificación automática de tickets de soporte técnico
                mediante modelos de aprendizaje supervisado y procesamiento de lenguaje natural.
            </div>
            <div class="sidebar-block">
                <strong>Tecnologías Utilizadas</strong>
                <ul class="sidebar-tech">
                    <li>Python</li>
                    <li>Scikit-learn</li>
                    <li>TF-IDF</li>
                    <li>NLP (NLTK, spaCy)</li>
                    <li>Streamlit</li>
                    <li>Pandas, NumPy</li>
                    <li>Matplotlib, Seaborn</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
