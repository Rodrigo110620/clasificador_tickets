from datetime import datetime

import streamlit as st

from config.constants import (
    CATEGORIA_DESCONOCIDA,
    MENSAJE_CATEGORIA_DESCONOCIDA,
    es_clasificacion_ambigua,
    umbral_confiancia_dinamico,
)
from memoria import guardar_en_memoria
from preprocess import es_texto_valido, extraer_palabras_clave, preprocesar_con_detalle
from services.dataset import agregar_ticket
from services.historial import agregar_al_historial


def clasificar_ticket(modelo, texto: str, detalle: dict | None = None) -> dict:
    if detalle is None:
        detalle = preprocesar_con_detalle(texto)
    texto_proc = detalle["texto_procesado"]
    probs = modelo.predict_proba([texto_proc])[0]
    prob_dict = dict(zip(modelo.classes_, probs))
    ordenadas = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)

    categoria = ordenadas[0][0]
    confianza_max = float(ordenadas[0][1])
    desconocido, _, margen = es_clasificacion_ambigua(ordenadas)
    umbral = umbral_confiancia_dinamico(len(ordenadas))

    return {
        "categoria": CATEGORIA_DESCONOCIDA if desconocido else categoria,
        "categoria_modelo": categoria,
        "confianza": confianza_max * 100,
        "probabilidades": prob_dict,
        "probabilidades_ordenadas": ordenadas,
        "desconocido": desconocido,
        "umbral_pct": umbral * 100,
        "margen_segunda_pct": margen * 100,
        "mensaje_desconocido": MENSAJE_CATEGORIA_DESCONOCIDA if desconocido else "",
        "texto_procesado": texto_proc,
        "tokens_utiles": detalle["tokens_utiles"],
        "stems": detalle["stems"],
        "palabras_clave": extraer_palabras_clave(texto),
        "palabras_eliminadas": detalle["palabras_eliminadas"],
        "es_valido": detalle["es_valido"],
        "motivo_rechazo": detalle["motivo_rechazo"],
        "hash_md5": detalle["hash_md5"],
        "n_palabras_originales": detalle["n_palabras_originales"],
        "n_palabras_utiles": detalle["n_palabras_utiles"],
    }


def guardar_para_entrenamiento(ticket: str, categoria: str) -> bool:
    from preprocess import preprocesar_texto

    texto_proc = preprocesar_texto(ticket)
    agregado = agregar_ticket(ticket, categoria)
    if not agregado:
        from services.dataset import actualizar_categoria
        actualizar_categoria(ticket, categoria)
    guardar_en_memoria(texto_proc, categoria)
    return agregado


def procesar_clasificacion(ticket: str, datos_modelo: dict, *, silencioso: bool = False) -> bool:
    ticket = ticket.strip()
    if not ticket:
        if not silencioso:
            st.warning("Por favor ingresa la descripción del ticket antes de clasificar.")
        return False

    detalle = preprocesar_con_detalle(ticket)
    valido, motivo = es_texto_valido(ticket, detalle)
    if not valido:
        st.session_state.ultimo_resultado = None
        if not silencioso:
            st.error(f"**Ticket rechazado:** {motivo}")
        return False

    modelo = datos_modelo["modelo"]
    nombre = datos_modelo.get("nombre", "Modelo")

    with st.spinner("Analizando el ticket..."):
        resultado = clasificar_ticket(modelo, ticket, detalle)
        resultado["ticket"] = ticket
        resultado["fecha"] = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
        resultado["modelo"] = nombre

    agregar_ticket(ticket, resultado["categoria_modelo"])
    guardar_en_memoria(resultado["texto_procesado"], resultado["categoria_modelo"])

    st.session_state.ultimo_resultado = resultado
    agregar_al_historial(ticket, resultado)
    return True
