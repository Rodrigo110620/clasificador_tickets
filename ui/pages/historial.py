import os

import streamlit as st

from config.constants import RUTA_MEMORIA, icono_categoria
from services.historial import deduplicar_historial
from ui.components import page_header, render_footer, section_title


def pagina_historial(metricas, datos_modelo):
    """Solo listado de tickets clasificados."""
    page_header()

    section_title(1, "Historial de clasificaciones")
    st.markdown(
        '<p class="modelo-subtitle">Tickets únicos clasificados en esta sesión</p>',
        unsafe_allow_html=True,
    )

    deduplicar_historial()
    historial = st.session_state.historial

    if not historial:
        st.info("Ve a **Clasificar Ticket** o **Inicio** para registrar clasificaciones.")
    else:
        st.markdown(
            f'<div class="stats-mini">'
            f'<span class="stat-pill">Total: <strong>{len(historial)}</strong></span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        etiquetas = []
        for h in historial:
            extra = " ⚠️" if h.get("desconocido") else ""
            etiquetas.append(
                f"{icono_categoria(h['categoria'])} {h['categoria']}{extra} — "
                f"{h['confianza']:.0f}% — {h.get('ticket_corto', '')}"
            )
        indice = st.selectbox(
            "Selecciona un ticket del historial",
            range(len(historial)),
            format_func=lambda i: etiquetas[i],
            label_visibility="collapsed",
        )
        item = historial[indice]
        icono = icono_categoria(item["categoria"])
        st.markdown(
            f"""
            <div class="hist-item">
                <strong>{icono} {item['categoria']}</strong>
                — {item['confianza']:.1f}% — <em>{item['fecha']}</em><br>
                <span style="color:#4a5568;">{item['ticket']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("✈️ Usar este ticket en Clasificar", type="primary"):
            st.session_state.ticket_input = item["ticket"]
            st.session_state.pagina = "clasificar"
            st.rerun()

        # ─── Botones para limpiar historial ─────────────────────────
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🧹 Limpiar historial de esta sesión", use_container_width=True):
                st.session_state.historial = []
                st.session_state.ultimo_resultado = None
                st.rerun()
        with col2:
            if st.button("⚠️ Resetear memoria completa (borrar tickets procesados)", use_container_width=True):
                st.warning("Esto eliminará permanentemente todos los tickets guardados en memoria. ¿Estás seguro?")
                if st.button("✅ Sí, resetear memoria", key="confirm_reset"):
                    if os.path.exists(RUTA_MEMORIA):
                        os.remove(RUTA_MEMORIA)
                    # También limpiar historial de sesión
                    st.session_state.historial = []
                    st.session_state.ultimo_resultado = None
                    st.success("Memoria reseteada correctamente. Los tickets nuevos se aprenderán nuevamente.")
                    st.rerun()

    render_footer(metricas)
