import streamlit as st


def init_session():
    # Migración: limpiar texto precargado de sesiones anteriores
    if st.session_state.get("_ui_version") != 2:
        st.session_state.ticket_input = ""
        st.session_state.ultimo_resultado = None
        st.session_state._ui_version = 2

    if "pagina" not in st.session_state:
        st.session_state.pagina = "inicio"
    if "historial" not in st.session_state:
        st.session_state.historial = []
    if "ultimo_resultado" not in st.session_state:
        st.session_state.ultimo_resultado = None
    if "ticket_input" not in st.session_state:
        st.session_state.ticket_input = ""
    if "es_admin" not in st.session_state:
        st.session_state.es_admin = False
