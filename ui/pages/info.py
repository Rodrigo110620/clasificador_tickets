import streamlit as st

from config.constants import MIN_EJEMPLOS_POR_CATEGORIA, umbral_confiancia_dinamico
from services.dataset import contar_por_categoria
from ui.components import page_header, render_footer, section_title


def pagina_info(metricas):
    """Documentación del proyecto."""
    page_header()
    section_title(1, "Información del Proyecto")

    conteo = contar_por_categoria()
    n_cats = len(conteo) or 12
    umbral_pct = int(umbral_confiancia_dinamico(n_cats) * 100)
    cats_html = "".join(
        f"<li>{c} — {n} tickets</li>" for c, n in sorted(conteo.items(), key=lambda x: -x[1])
    ) or "<li>Sin categorías en el dataset aún</li>"

    st.markdown(
        f"""
        <div class="card">
            <h3 style="margin-top:0;">Sistema Inteligente de Clasificación de Tickets</h3>
            <p>Clasificación automática con <strong>categorías dinámicas</strong> definidas en
            <code>dataset/tickets.csv</code> (sin límite fijo de clases).</p>
            <h4>Funcionalidades</h4>
            <ul>
                <li>Probabilidades por categoría ordenadas de mayor a menor</li>
                <li>Detección de categoría ambigua (umbral dinámico ~{umbral_pct}% con {n_cats} categorías)</li>
                <li>Guardado automático en el dataset y memoria persistente</li>
                <li>Reentrenamiento completo (admin) con mínimo {MIN_EJEMPLOS_POR_CATEGORIA} ejemplos por categoría</li>
                <li>Filtro de texto basura y análisis NLP transparente</li>
                <li>Comparación Naive Bayes (default/optimizado) vs Regresión Logística</li>
            </ul>
            <h4>Pipeline NLP</h4>
            <ol>
                <li>Limpieza y normalización</li>
                <li>Stopwords (NLTK) y stemming (Snowball español)</li>
                <li>Vectorización TF-IDF</li>
                <li>Clasificación supervisada (mejor modelo por F1-score)</li>
            </ol>
            <h4>Categorías en el dataset</h4>
            <ul>{cats_html}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_footer(metricas)
