import streamlit as st


def init_session():
    if st.session_state.get("_ui_version") != 4:
        st.session_state.ultimo_resultado = None
        st.session_state._ui_version = 4

    if "pagina" not in st.session_state:
        st.session_state.pagina = "inicio"
    if "historial" not in st.session_state:
        st.session_state.historial = []
    if "ultimo_resultado" not in st.session_state:
        st.session_state.ultimo_resultado = None
    # ticket_input persiste entre páginas gracias a que Streamlit lo restaura
    # automáticamente desde session_state cuando el widget se recrea al volver a la página.
    if "ticket_input" not in st.session_state:
        st.session_state.ticket_input = ""
    if "es_admin" not in st.session_state:
        st.session_state.es_admin = False