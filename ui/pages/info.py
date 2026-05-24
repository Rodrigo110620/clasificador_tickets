import streamlit as st

from ui.components import page_header, render_footer, section_title


def pagina_info(metricas):
    """Solo documentación del proyecto."""
    page_header()
    section_title(1, "Información del Proyecto")
    st.markdown(
        """
        <div class="card">
            <h3 style="margin-top:0;">Sistema Inteligente de Clasificación de Tickets</h3>
            <p>Proyecto académico de clasificación automática de tickets de soporte técnico
            mediante técnicas de <strong>Machine Learning</strong> y <strong>NLP</strong>.</p>
            <h4>Pipeline de procesamiento</h4>
            <ol>
                <li>Limpieza y normalización del texto</li>
                <li>Tokenización y eliminación de stopwords (NLTK)</li>
                <li>Lematización con spaCy (es_core_news_sm)</li>
                <li>Vectorización TF-IDF (unigramas y bigramas)</li>
                <li>Clasificación con Naive Bayes o Regresión Logística</li>
            </ol>
            <h4>Categorías</h4>
            <ul>
                <li>🔐 Credenciales — acceso, contraseñas, autenticación</li>
                <li>🗄️ Base de Datos — consultas, backups, errores SQL</li>
                <li>📡 Infraestructura — red, servidores, VPN, hardware</li>
                <li>🐛 Bug de Software — errores en aplicaciones y UI</li>
            </ul>
            <p><em>Universidad Mayor de San Simón — Facultad de Ciencias y Tecnología — Grupo 1 IA 2026</em></p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_footer(metricas)
