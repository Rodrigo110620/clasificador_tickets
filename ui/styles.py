import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* Texto legible en el área principal (evita herencia de colores claros) */
[data-testid="stAppViewContainer"] .main,
[data-testid="stAppViewContainer"] .main p,
[data-testid="stAppViewContainer"] .main span,
[data-testid="stAppViewContainer"] .main td,
[data-testid="stAppViewContainer"] .main th,
[data-testid="stAppViewContainer"] .main li,
[data-testid="stAppViewContainer"] .main .tabla-modelos,
[data-testid="stAppViewContainer"] .main .tabla-modelos * {
    color: #1a202c !important;
}
[data-testid="stAppViewContainer"] .main .tabla-modelos th {
    background: #edf2f7 !important;
    font-weight: 600 !important;
}
[data-testid="stAppViewContainer"] .main .fila-mejor td {
    background: #f0fff4 !important;
    font-weight: 700 !important;
}

/* Bloque de texto preprocesado NLP (fondo claro, texto oscuro) */
[data-testid="stAppViewContainer"] .main .nlp-texto-box,
[data-testid="stAppViewContainer"] .main .nlp-texto-box pre {
    background: #f8fafc !important;
    color: #1e293b !important;
    border: 1px solid #cbd5e0 !important;
}
[data-testid="stAppViewContainer"] .main .nlp-texto-box pre {
    margin: 0.5rem 0 0;
    padding: 0.85rem 1rem;
    border-radius: 8px;
    font-size: 0.9rem;
    line-height: 1.5;
    white-space: pre-wrap;
    word-wrap: break-word;
}
[data-testid="stAppViewContainer"] .main .nlp-texto-box .nlp-label {
    color: #4a5568 !important;
    font-size: 0.82rem;
    font-weight: 600;
}
[data-testid="stAppViewContainer"] .main [data-testid="stCodeBlock"] pre,
[data-testid="stAppViewContainer"] .main [data-testid="stCodeBlock"] code {
    background: #f8fafc !important;
    color: #1e293b !important;
    border: 1px solid #cbd5e0 !important;
}

.tabla-comparacion-wrap {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    margin: 0.25rem 0 0.5rem;
}
.tabla-comparacion {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.92rem;
}
.tabla-comparacion thead th {
    background: #2c5282 !important;
    color: #ffffff !important;
    padding: 0.8rem 1rem;
    font-weight: 600;
    text-align: center;
}
.tabla-comparacion thead th:first-child {
    text-align: left;
}
.tabla-comparacion tbody td {
    padding: 0.75rem 1rem;
    text-align: center;
    color: #1a202c !important;
    background: #ffffff !important;
    border-bottom: 1px solid #edf2f7;
}
.tabla-comparacion tbody td:first-child {
    text-align: left;
    font-weight: 500;
}
.tabla-comparacion tbody tr:nth-child(even) td {
    background: #f7fafc !important;
    color: #1a202c !important;
}
.tabla-comparacion tbody tr.fila-mejor td {
    background: #c6f6d5 !important;
    color: #22543d !important;
    font-weight: 700 !important;
    border-bottom: 1px solid #9ae6b4;
}
.badge-en-uso {
    display: inline-block;
    background: #276749;
    color: #fff;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 0.12rem 0.45rem;
    border-radius: 6px;
    margin-left: 0.35rem;
    vertical-align: middle;
}
.tabla-comparacion-hint {
    font-size: 0.82rem;
    color: #718096;
    font-weight: 400;
}
.tabla-comparacion-msg {
    color: #276749 !important;
    font-size: 0.9rem;
    margin-top: 0.6rem;
    font-weight: 500;
}

#MainMenu, footer, header {visibility: hidden;}
footer {display: none !important;}

[data-testid="stAppViewContainer"] .main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}
[data-testid="stAppViewContainer"] .main {
    background-color: #eef1f6;
}
section[data-testid="stSidebar"] > div {
    background: linear-gradient(180deg, #0e1117 0%, #161b28 100%) !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0e1117 0%, #1a1f2e 100%);
    border-right: 1px solid #2d3748;
}
[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
[data-testid="stSidebar"] .stRadio label {
    background: transparent;
    padding: 0.55rem 0.75rem;
    border-radius: 8px;
    width: 100%;
    font-weight: 500;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(99, 179, 237, 0.12);
}
[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 0.1rem;
}
[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"] {
    margin-bottom: 0.1rem;
    border-radius: 8px;
    transition: background 0.15s;
}
[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
    background: rgba(66, 153, 225, 0.22) !important;
    border-left: 3px solid #63b3ed;
}
[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) p {
    color: #90cdf4 !important;
    font-weight: 600 !important;
}

div[data-testid="stTextArea"] textarea {
    background: #fff !important;
    border: 1px solid #d1d9e6 !important;
    border-radius: 10px !important;
    font-size: 0.95rem !important;
    color: #2d3748 !important;
    box-shadow: inset 0 1px 2px rgba(0,0,0,0.04);
}
div[data-testid="stTextArea"] {
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 0.35rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    margin-bottom: 0.25rem;
}
/* Gráfico HTML — probabilidades por categoría */
.chart-html {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1rem 1.1rem;
    margin-top: 0.5rem;
}
.chart-html-title {
    color: #2d3748 !important;
    font-size: 0.88rem;
    font-weight: 700;
    margin: 0 0 0.75rem;
}
.bar-row {
    display: grid;
    grid-template-columns: 140px 1fr 48px;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 0.55rem;
}
.bar-label {
    color: #2d3748 !important;
    font-size: 0.82rem;
    font-weight: 500;
    text-align: right;
}
.bar-track {
    background: #e2e8f0;
    border-radius: 6px;
    height: 22px;
    overflow: hidden;
}
.bar-fill {
    height: 100%;
    border-radius: 6px;
    min-width: 2px;
    transition: width 0.3s ease;
}
.bar-pct {
    color: #2d3748 !important;
    font-size: 0.82rem;
    font-weight: 700;
    text-align: right;
}

/* Matriz de confusión HTML */
.matriz-wrap {
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    overflow-x: auto;
}
.matriz-title {
    color: #2d3748 !important;
    font-size: 0.9rem;
    font-weight: 700;
    margin: 0 0 0.75rem;
}
.matriz-subtitle {
    color: #718096 !important;
    font-size: 0.8rem;
    margin: 0 0 0.5rem;
}
.tabla-matriz {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
    min-width: 320px;
}
.tabla-matriz thead th {
    background: #2c5282 !important;
    color: #fff !important;
    padding: 0.55rem 0.45rem;
    font-weight: 600;
    text-align: center;
}
.tabla-matriz tbody th.cm-real {
    background: #edf2f7 !important;
    color: #2d3748 !important;
    font-weight: 600;
    text-align: left;
    padding: 0.5rem 0.65rem;
    border: 1px solid #e2e8f0;
}
.tabla-matriz tbody td {
    text-align: center;
    font-weight: 700;
    padding: 0.5rem 0.45rem;
    border: 1px solid #e2e8f0;
    min-width: 2.5rem;
}
.matriz-leyenda {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 0.65rem;
    font-size: 0.75rem;
    color: #4a5568 !important;
}
.matriz-leyenda-bar {
    flex: 1;
    max-width: 160px;
    height: 10px;
    border-radius: 5px;
    background: linear-gradient(90deg, #ebf8ff, #2b6cb0);
}

.sidebar-logo {
    text-align: center;
    padding: 1rem 0 1.25rem;
    border-bottom: 1px solid #2d3748;
    margin-bottom: 1rem;
}
.sidebar-logo h2 {
    font-size: 1.35rem;
    font-weight: 700;
    color: #63b3ed !important;
    margin: 0.25rem 0 0;
}
.sidebar-logo p {
    font-size: 0.78rem;
    color: #a0aec0 !important;
    margin: 0;
}
.sidebar-block {
    background: rgba(255,255,255,0.04);
    border-radius: 10px;
    padding: 0.9rem 1rem;
    margin: 1rem 0;
    font-size: 0.82rem;
    line-height: 1.5;
    color: #cbd5e0 !important;
}
.sidebar-tech li {
    margin-bottom: 0.2rem;
    color: #a0aec0 !important;
}

.page-header {
    margin-bottom: 1.5rem;
}
.page-header h1 {
    font-size: 1.75rem;
    font-weight: 700;
    color: #1a202c;
    margin: 0 0 0.25rem;
}
.page-header p {
    color: #718096;
    font-size: 0.95rem;
    margin: 0;
}

.section-title {
    font-size: 1.05rem;
    font-weight: 600;
    color: #2d3748;
    margin: 1.5rem 0 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-num {
    background: #4361ee;
    color: white;
    width: 26px;
    height: 26px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    font-weight: 700;
}

.card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    margin-bottom: 1rem;
}

.sidebar-modelo-activo {
    background: linear-gradient(135deg, rgba(49, 130, 206, 0.35) 0%, rgba(44, 82, 130, 0.55) 100%);
    border: 1px solid #63b3ed;
    border-left: 4px solid #48bb78;
    border-radius: 10px;
    padding: 0.75rem 0.85rem;
    margin: 0.75rem 0;
    font-size: 0.84rem;
    line-height: 1.5;
    color: #f7fafc !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
}
.sidebar-modelo-activo strong {
    color: #bee3f8 !important;
    font-weight: 600;
}
.sidebar-modelo-activo .modelo-nombre {
    display: block;
    margin-top: 0.35rem;
    color: #ffffff !important;
    font-weight: 700;
    font-size: 0.9rem;
    word-break: break-word;
}

.ejemplos-label {
    font-size: 0.85rem;
    color: #718096;
    margin: 0.5rem 0 0.35rem;
}

.clasif-divider {
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 1.25rem 0 1rem;
}

.result-hero {
    background: linear-gradient(135deg, #f0fff4 0%, #e6fffa 100%);
    border: 2px solid #48bb78;
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 14px rgba(72, 187, 120, 0.15);
}
.result-hero-warn {
    background: linear-gradient(135deg, #fffaf0 0%, #fefcbf 100%);
    border-color: #ed8936;
    box-shadow: 0 4px 14px rgba(237, 137, 54, 0.12);
}
.result-hero-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.35rem;
}
.result-hero-label {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #4a5568;
    font-weight: 600;
}
.result-hero-conf {
    font-size: 1rem;
    font-weight: 700;
    color: #276749;
}
.result-hero-warn .result-hero-conf {
    color: #c05621;
}
.result-hero-cat {
    font-size: 1.75rem;
    font-weight: 800;
    color: #22543d;
    margin: 0.25rem 0 0.75rem;
    line-height: 1.2;
}
.result-hero-warn .result-hero-cat {
    color: #744210;
}
.conf-bar-hero {
    height: 10px;
    margin-bottom: 0.85rem;
}

.prob-panel {
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1rem 1.1rem;
    margin-bottom: 1rem;
}
.prob-panel-title {
    font-weight: 700;
    color: #2d3748;
    margin-bottom: 0.75rem;
    font-size: 0.95rem;
}
.prob-sum-hint {
    font-weight: 400;
    font-size: 0.78rem;
    color: #718096;
    margin-left: 0.35rem;
}
.prob-list {
    max-height: 280px;
    overflow-y: auto;
    padding-right: 4px;
}
.prob-row {
    display: grid;
    grid-template-columns: minmax(120px, 1.4fr) 3fr 42px;
    gap: 0.5rem;
    align-items: center;
    margin-bottom: 0.45rem;
    font-size: 0.88rem;
}
.prob-row-top {
    background: #f0fff4;
    border-radius: 8px;
    padding: 0.35rem 0.45rem;
    margin-left: -0.45rem;
    margin-right: -0.45rem;
    padding-left: 0.45rem;
    padding-right: 0.45rem;
}
.prob-row-top .prob-label {
    font-weight: 700;
    color: #276749;
}
.prob-label {
    color: #4a5568;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.prob-track {
    background: #edf2f7;
    border-radius: 6px;
    height: 8px;
    overflow: hidden;
}
.prob-fill {
    background: linear-gradient(90deg, #4299e1, #3182ce);
    height: 100%;
    border-radius: 6px;
    transition: width 0.3s ease;
}
.prob-row-top .prob-fill {
    background: linear-gradient(90deg, #48bb78, #38a169);
}
.prob-pct {
    font-weight: 700;
    text-align: right;
    color: #2d3748;
    font-size: 0.85rem;
}

.alert-desconocido {
    background: #fffaf0;
    border: 1px solid #f6ad55;
    border-radius: 10px;
    padding: 0.85rem 1rem;
    margin-bottom: 1rem;
    color: #744210;
    font-size: 0.95rem;
    line-height: 1.5;
}

.result-card {
    border: 1px solid #c6f6d5;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(72,187,120,0.12);
    margin-bottom: 1rem;
}
.result-header {
    background: linear-gradient(90deg, #f0fff4, #e6fffa);
    padding: 1rem 1.5rem;
    border-bottom: 1px solid #c6f6d5;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
}
.result-cat {
    font-size: 1.5rem;
    font-weight: 700;
    color: #276749;
}
.result-conf-label {
    font-size: 0.85rem;
    color: #4a5568;
    text-align: right;
}
.result-conf-value {
    font-size: 1.25rem;
    font-weight: 700;
    color: #276749;
}
.conf-bar-wrap {
    background: #e2e8f0;
    border-radius: 6px;
    height: 8px;
    width: 140px;
    margin-top: 4px;
}
.conf-bar-fill {
    background: linear-gradient(90deg, #48bb78, #38a169);
    height: 8px;
    border-radius: 6px;
}
.result-body {
    padding: 1rem 1.5rem 1.25rem;
    background: #fff;
}
.badges-row {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin-bottom: 1rem;
}
.badge {
    padding: 0.35rem 0.9rem;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
    border: 1.5px solid;
}
.badge-alta {
    color: #c53030;
    border-color: #fc8181;
    background: #fff5f5;
}
.badge-media {
    color: #c05621;
    border-color: #f6ad55;
    background: #fffaf0;
}
.badge-modelo {
    color: #6b46c1;
    border-color: #b794f4;
    background: #faf5ff;
}

.metric-card {
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.metric-card .label {
    font-size: 0.78rem;
    color: #718096;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}
.metric-card .value {
    font-size: 1.6rem;
    font-weight: 700;
    margin-top: 0.25rem;
}
.metric-blue .value { color: #3182ce; }
.metric-green .value { color: #38a169; }
.metric-orange .value { color: #dd6b20; }
.metric-purple .value { color: #805ad5; }

.modelo-subtitle {
    color: #718096;
    font-size: 0.9rem;
    margin: -0.25rem 0 0.75rem 0;
}
.modelo-subtitle strong { color: #4361ee; }

.char-counter {
    font-size: 0.82rem;
    color: #718096;
    margin-top: -0.5rem;
    margin-bottom: 0.5rem;
}

.placeholder-result {
    background: #f7fafc;
    border: 2px dashed #cbd5e0;
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    color: #a0aec0;
}

.footer-bar {
    background: linear-gradient(90deg, #ebf8ff, #e6fffa);
    border: 1px solid #bee3f8;
    border-radius: 10px;
    padding: 0.85rem 1.25rem;
    margin-top: 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.5rem;
    font-size: 0.88rem;
    color: #2c5282;
}
.footer-ts {
    color: #4a5568;
    font-size: 0.85rem;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #4361ee, #3a56d4) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.65rem 1.5rem !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(90deg, #3a56d4, #2f4ac0) !important;
}

div[data-testid="stDataFrame"] table tbody tr:last-child,
.highlight-row {
    background-color: #f0fff4 !important;
}

.hist-item {
    background: #f7fafc;
    border-left: 4px solid #4361ee;
    padding: 0.75rem 1rem;
    border-radius: 0 8px 8px 0;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
}
.input-label {
    font-size: 0.88rem;
    color: #4a5568;
    margin-bottom: 0.5rem;
    font-weight: 500;
}
.stats-mini {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-top: 1rem;
}
.stat-pill {
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-size: 0.85rem;
    color: #4a5568;
}
.stat-pill strong { color: #2d3748; }
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)
