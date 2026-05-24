from datetime import datetime

import streamlit as st


def deduplicar_historial():
    """Elimina entradas repetidas por texto de ticket."""
    vistos = set()
    unicos = []
    for item in st.session_state.historial:
        clave = item.get("ticket", "").strip()
        if not clave or clave in vistos:
            continue
        vistos.add(clave)
        unicos.append(item)
    st.session_state.historial = unicos[:25]


def agregar_al_historial(ticket: str, resultado: dict):
    ticket = ticket.strip()
    entrada = {
        "ticket": ticket,
        "ticket_corto": ticket[:90] + ("..." if len(ticket) > 90 else ""),
        "categoria": resultado["categoria"],
        "confianza": resultado["confianza"],
        "fecha": datetime.now().strftime("%H:%M %d/%m/%Y"),
    }
    for i, item in enumerate(st.session_state.historial):
        if item.get("ticket", "").strip() == ticket:
            st.session_state.historial[i] = entrada
            deduplicar_historial()
            return
    st.session_state.historial.insert(0, entrada)
    deduplicar_historial()
