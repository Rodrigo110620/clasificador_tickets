from datetime import datetime

import streamlit as st

from memoria import guardar_en_memoria, ticket_ya_procesado
from preprocess import es_texto_valido, extraer_palabras_clave, preprocesar_con_detalle
from services.historial import agregar_al_historial


def clasificar_ticket(modelo, texto: str, detalle: dict | None = None) -> dict:
    if detalle is None:
        detalle = preprocesar_con_detalle(texto)
    texto_proc = detalle["texto_procesado"]
    categoria = modelo.predict([texto_proc])[0]
    probs = modelo.predict_proba([texto_proc])[0]
    confianza = float(max(probs)) * 100
    prob_dict = dict(zip(modelo.classes_, probs))
    return {
        "categoria": categoria,
        "confianza": confianza,
        "probabilidades": prob_dict,
        "texto_procesado": texto_proc,
        "tokens_utiles": detalle["tokens_utiles"],
        "stems": detalle["stems"],
        "palabras_eliminadas": detalle["palabras_eliminadas"],
        "es_valido": detalle["es_valido"],
        "motivo_rechazo": detalle["motivo_rechazo"],
        "hash_md5": detalle["hash_md5"],
        "n_palabras_originales": detalle["n_palabras_originales"],
        "n_palabras_utiles": detalle["n_palabras_utiles"],
    }


def procesar_clasificacion(ticket: str, datos_modelo: dict):
    if not ticket.strip():
        st.warning("Por favor ingresa la descripción del ticket antes de clasificar.")
        return

    detalle = preprocesar_con_detalle(ticket)
    valido, motivo = es_texto_valido(ticket, detalle)
    if not valido:
        st.warning("Ticket inválido: " + motivo)
        return

    if ticket_ya_procesado(detalle["texto_procesado"]):
        st.info("Este ticket ya fue procesado anteriormente y está registrado en memoria.")
        return

    palabras_clave = extraer_palabras_clave(ticket)
    with st.expander("🔎 Análisis del ticket"):
        if palabras_clave:
            st.markdown(
                f"**Palabras clave extraídas:** {', '.join(palabras_clave)}"
            )
        else:
            st.markdown("**Palabras clave extraídas:** No se encontraron términos útiles.")
        st.markdown(f"**Texto limpio:** {detalle['texto_procesado']}")
        st.markdown(f"**Tokens útiles:** {', '.join(detalle['tokens_utiles'])}")

    modelo = datos_modelo["modelo"]
    nombre = datos_modelo.get("nombre", "Modelo")

    with st.spinner("Analizando el ticket..."):
        resultado = clasificar_ticket(modelo, ticket, detalle)
        resultado["ticket"] = ticket
        resultado["fecha"] = datetime.now().strftime("%H:%M:%S %d/%m/%Y")

    st.session_state.ultimo_resultado = resultado
    agregar_al_historial(ticket, resultado)
    guardar_en_memoria(resultado["texto_procesado"], resultado["categoria"])
