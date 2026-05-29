import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* ── HIDE STREAMLIT CHROME ─────────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
footer { display: none !important; }

/* ── LAYOUT ─────────────────────────────────────────────── */
[data-testid="stAppViewContainer"] .main {
    background: #f5f6fa;
}
[data-testid="stAppViewContainer"] .main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1100px;
}

/* ── SIDEBAR ─────────────────────────────────────────────── */
section[data-testid="stSidebar"] > div {
    background: #0f1623 !important;
}
[data-testid="stSidebar"] {
    background: #0f1623;
    border-right: 1px solid #1e2a3a;
}
[data-testid="stSidebar"] * {
    color: #c8d3e0 !important;
}
[data-testid="stSidebar"] .stRadio label {
    background: transparent;
    padding: 0.55rem 0.75rem;
    border-radius: 8px;
    width: 100%;
    font-weight: 500;
    transition: background 0.15s;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"] {
    margin-bottom: 0.1rem;
    border-radius: 8px;
    transition: background 0.15s;
}
[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
    background: rgba(99, 179, 237, 0.14) !important;
    border-left: 3px solid #3b82f6;
}
[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) p {
    color: #93c5fd !important;
    font-weight: 600 !important;
}

/* ── SIDEBAR BLOCKS ──────────────────────────────────────── */
.sidebar-logo {
    text-align: center;
    padding: 1rem 0 1.25rem;
    border-bottom: 1px solid #1e2a3a;
    margin-bottom: 1rem;
}
.sidebar-logo h2 {
    font-size: 1.25rem;
    font-weight: 700;
    color: #60a5fa !important;
    margin: 0.25rem 0 0;
}
.sidebar-logo p {
    font-size: 0.76rem;
    color: #64748b !important;
    margin: 0;
}
.sidebar-block {
    background: rgba(255,255,255,0.04);
    border: 1px solid #1e2a3a;
    border-radius: 10px;
    padding: 0.9rem 1rem;
    margin: 1rem 0;
    font-size: 0.82rem;
    line-height: 1.5;
    color: #94a3b8 !important;
}
.sidebar-modelo-activo {
    background: rgba(59,130,246,0.12);
    border: 1px solid rgba(59,130,246,0.3);
    border-left: 3px solid #22c55e;
    border-radius: 10px;
    padding: 0.75rem 0.85rem;
    margin: 0.75rem 0;
    font-size: 0.83rem;
    line-height: 1.5;
    color: #e2e8f0 !important;
}
.sidebar-modelo-activo strong {
    color: #93c5fd !important;
    font-weight: 600;
}
.sidebar-modelo-activo .modelo-nombre {
    display: block;
    margin-top: 0.3rem;
    color: #ffffff !important;
    font-weight: 700;
    font-size: 0.88rem;
}
.sidebar-tech li {
    margin-bottom: 0.2rem;
    color: #64748b !important;
}

/* ── GLOBAL TEXT FIX ─────────────────────────────────────── */
[data-testid="stAppViewContainer"] .main p,
[data-testid="stAppViewContainer"] .main span,
[data-testid="stAppViewContainer"] .main td,
[data-testid="stAppViewContainer"] .main th,
[data-testid="stAppViewContainer"] .main li {
    color: #1e293b;
}

/* ── TYPOGRAPHY ──────────────────────────────────────────── */
.page-header {
    margin-bottom: 1.75rem;
}
.page-header h1 {
    font-size: 1.7rem;
    font-weight: 700;
    color: #0f172a;
    margin: 0 0 0.2rem;
    letter-spacing: -0.02em;
}
.page-header p {
    color: #64748b;
    font-size: 0.93rem;
    margin: 0;
}
.section-title {
    font-size: 1rem;
    font-weight: 600;
    color: #1e293b;
    margin: 1.5rem 0 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-num {
    background: #3b82f6;
    color: white;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.78rem;
    font-weight: 700;
    flex-shrink: 0;
}

/* ── CARDS ───────────────────────────────────────────────── */
.card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    margin-bottom: 1rem;
}

/* ── TEXTAREA ────────────────────────────────────────────── */
div[data-testid="stTextArea"] {
    background: #fff;
    border: 1.5px solid #e2e8f0;
    border-radius: 12px;
    padding: 0.3rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    margin-bottom: 0.25rem;
}
div[data-testid="stTextArea"] textarea {
    background: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-size: 0.95rem !important;
    color: #1e293b !important;
    font-family: 'DM Sans', sans-serif !important;
}
div[data-testid="stTextArea"]:focus-within {
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.12);
}

/* ── CATEGORY EXAMPLE BUTTONS ────────────────────────────── */
/* Fix: texto visible y estilo claro para los botones de ejemplo */
[data-testid="stAppViewContainer"] .main .stButton > button {
    background: #ffffff !important;
    color: #1e293b !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 0.5rem 0.75rem !important;
    transition: all 0.15s ease !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
[data-testid="stAppViewContainer"] .main .stButton > button:hover {
    background: #f0f7ff !important;
    border-color: #93c5fd !important;
    color: #1d4ed8 !important;
    box-shadow: 0 2px 8px rgba(59,130,246,0.15) !important;
    transform: translateY(-1px);
}
[data-testid="stAppViewContainer"] .main .stButton > button:active {
    transform: translateY(0);
}

/* Botón primario clasificar */
.stButton > button[kind="primary"] {
    background: #2563eb !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.65rem 1.75rem !important;
    box-shadow: 0 2px 8px rgba(37,99,235,0.25) !important;
    transition: all 0.15s ease !important;
}
.stButton > button[kind="primary"]:hover {
    background: #1d4ed8 !important;
    box-shadow: 0 4px 16px rgba(37,99,235,0.35) !important;
    transform: translateY(-1px);
}

/* ── MISC LABELS ─────────────────────────────────────────── */
.ejemplos-label {
    font-size: 0.84rem;
    color: #64748b;
    margin: 0.75rem 0 0.4rem;
    font-weight: 500;
}
.char-counter {
    font-size: 0.8rem;
    color: #94a3b8;
    margin-top: -0.4rem;
    margin-bottom: 0.5rem;
}
.input-label {
    font-size: 0.88rem;
    color: #475569;
    margin-bottom: 0.5rem;
    font-weight: 500;
}
.clasif-divider {
    border: none;
    border-top: 1px solid #e9ecf3;
    margin: 1.5rem 0 1rem;
}

/* ── RESULT HERO ─────────────────────────────────────────── */
.result-hero {
    background: #ffffff;
    border: 1.5px solid #bbf7d0;
    border-left: 4px solid #22c55e;
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 12px rgba(34,197,94,0.1);
}
.result-hero-warn {
    border-color: #fde68a;
    border-left-color: #f59e0b;
    box-shadow: 0 2px 12px rgba(245,158,11,0.1);
}
.result-hero-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.3rem;
}
.result-hero-label {
    font-size: 0.73rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748b;
    font-weight: 600;
}
.result-hero-conf {
    font-size: 0.9rem;
    font-weight: 700;
    color: #16a34a;
    background: #dcfce7;
    padding: 0.2rem 0.65rem;
    border-radius: 20px;
}
.result-hero-warn .result-hero-conf {
    color: #b45309;
    background: #fef3c7;
}
.result-hero-cat {
    font-size: 1.65rem;
    font-weight: 700;
    color: #0f172a;
    margin: 0.3rem 0 0.7rem;
    line-height: 1.2;
    letter-spacing: -0.02em;
}
.conf-bar-wrap {
    background: #f1f5f9;
    border-radius: 6px;
    height: 8px;
    margin-bottom: 0.85rem;
    overflow: hidden;
}
.conf-bar-fill {
    background: linear-gradient(90deg, #4ade80, #22c55e);
    height: 100%;
    border-radius: 6px;
    transition: width 0.5s ease;
}
.result-hero-warn .conf-bar-fill {
    background: linear-gradient(90deg, #fcd34d, #f59e0b);
}
.conf-bar-hero { margin-bottom: 0.85rem; }

/* ── BADGES ──────────────────────────────────────────────── */
.badges-row {
    display: flex;
    gap: 0.6rem;
    flex-wrap: wrap;
}
.badge {
    padding: 0.28rem 0.8rem;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    border: 1.5px solid;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
}
.badge-alta {
    color: #b91c1c;
    border-color: #fca5a5;
    background: #fff1f2;
}
.badge-media {
    color: #b45309;
    border-color: #fcd34d;
    background: #fffbeb;
}
.badge-modelo {
    color: #6d28d9;
    border-color: #c4b5fd;
    background: #f5f3ff;
}
.badge-en-uso {
    display: inline-flex;
    align-items: center;
    background: #16a34a;
    color: #fff;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 0.1rem 0.4rem;
    border-radius: 5px;
    margin-left: 0.35rem;
    vertical-align: middle;
}

/* ── ALERT DESCONOCIDO ───────────────────────────────────── */
.alert-desconocido {
    background: #fffbeb;
    border: 1px solid #fcd34d;
    border-radius: 10px;
    padding: 0.85rem 1rem;
    margin-bottom: 1rem;
    color: #92400e;
    font-size: 0.92rem;
    line-height: 1.5;
}

/* ── PROBABILITY CHART ───────────────────────────────────── */
.prob-panel {
    background: #ffffff;
    border: 1px solid #e9ecf3;
    border-radius: 12px;
    padding: 1rem 1.1rem;
    margin-bottom: 1rem;
}
.prob-panel-title {
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 0.75rem;
    font-size: 0.92rem;
}
.prob-sum-hint {
    font-weight: 400;
    font-size: 0.75rem;
    color: #94a3b8;
    margin-left: 0.4rem;
}
.prob-list { padding-right: 4px; }
.prob-row {
    display: grid;
    grid-template-columns: minmax(130px, 1.5fr) 3fr 46px;
    gap: 0.5rem;
    align-items: center;
    margin-bottom: 0.5rem;
    font-size: 0.86rem;
}
.prob-row-top {
    background: #f0fdf4;
    border-radius: 8px;
    padding: 0.35rem 0.45rem;
    margin-left: -0.45rem;
    margin-right: -0.45rem;
    padding-left: 0.45rem;
    padding-right: 0.45rem;
}
.prob-label {
    color: #475569;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    font-weight: 500;
}
.prob-row-top .prob-label { font-weight: 700; color: #15803d; }
.prob-track {
    background: #f1f5f9;
    border-radius: 5px;
    height: 8px;
    overflow: hidden;
}
.prob-fill {
    background: linear-gradient(90deg, #60a5fa, #3b82f6);
    height: 100%;
    border-radius: 5px;
}
.prob-row-top .prob-fill {
    background: linear-gradient(90deg, #4ade80, #16a34a);
}
.prob-pct {
    font-weight: 700;
    text-align: right;
    color: #374151;
    font-size: 0.83rem;
}

/* ── PLACEHOLDER ─────────────────────────────────────────── */
.placeholder-result {
    background: #f8fafc;
    border: 2px dashed #cbd5e1;
    border-radius: 14px;
    padding: 2.5rem;
    text-align: center;
    color: #94a3b8;
    font-size: 0.93rem;
}

/* ── CHART HTML (barras de distribución) ─────────────────── */
.chart-html {
    background: #ffffff;
    border: 1px solid #e9ecf3;
    border-radius: 12px;
    padding: 1rem 1.1rem;
    margin-top: 0.5rem;
}
.chart-html-title {
    color: #1e293b !important;
    font-size: 0.88rem;
    font-weight: 600;
    margin: 0 0 0.75rem;
}
.bar-row {
    display: grid;
    grid-template-columns: 140px 1fr 48px;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 0.55rem;
}
.bar-label { color: #475569 !important; font-size: 0.82rem; font-weight: 500; text-align: right; }
.bar-track { background: #f1f5f9; border-radius: 6px; height: 20px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 6px; min-width: 2px; }
.bar-pct { color: #374151 !important; font-size: 0.82rem; font-weight: 700; text-align: right; }

/* ── METRICS CARDS ───────────────────────────────────────── */
.metric-card {
    background: #fff;
    border: 1px solid #e9ecf3;
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
}
.metric-card .label {
    font-size: 0.74rem;
    color: #64748b;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.metric-card .value {
    font-size: 1.55rem;
    font-weight: 700;
    margin-top: 0.2rem;
}
.metric-blue .value  { color: #2563eb; }
.metric-green .value { color: #16a34a; }
.metric-orange .value{ color: #d97706; }
.metric-purple .value{ color: #7c3aed; }

/* ── COMPARACION TABLE ───────────────────────────────────── */
.tabla-comparacion-wrap {
    background: #fff;
    border: 1px solid #e9ecf3;
    border-radius: 12px;
    overflow: hidden;
    margin: 0.25rem 0 0.5rem;
}
.tabla-comparacion { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.tabla-comparacion thead th {
    background: #1e3a5f !important;
    color: #ffffff !important;
    padding: 0.75rem 1rem;
    font-weight: 600;
    text-align: center;
}
.tabla-comparacion thead th:first-child { text-align: left; }
.tabla-comparacion tbody td {
    padding: 0.7rem 1rem;
    text-align: center;
    color: #1e293b !important;
    background: #fff !important;
    border-bottom: 1px solid #f1f5f9;
}
.tabla-comparacion tbody td:first-child { text-align: left; font-weight: 500; }
.tabla-comparacion tbody tr:nth-child(even) td { background: #f8fafc !important; }
.tabla-comparacion tbody tr.fila-mejor td {
    background: #f0fdf4 !important;
    color: #166534 !important;
    font-weight: 700 !important;
    border-bottom: 1px solid #bbf7d0;
}
.tabla-comparacion-hint { font-size: 0.8rem; color: #94a3b8; }
.tabla-comparacion-msg { color: #166534 !important; font-size: 0.88rem; margin-top: 0.6rem; font-weight: 500; }

/* ── CONFUSION MATRIX ────────────────────────────────────── */
.matriz-wrap {
    background: #fff;
    border: 1px solid #e9ecf3;
    border-radius: 12px;
    padding: 1rem;
    overflow-x: auto;
}
.matriz-title { color: #1e293b !important; font-size: 0.9rem; font-weight: 700; margin: 0 0 0.75rem; }
.matriz-subtitle { color: #64748b !important; font-size: 0.8rem; margin: 0 0 0.5rem; }
.tabla-matriz { width: 100%; border-collapse: collapse; font-size: 0.83rem; min-width: 320px; }
.tabla-matriz thead th {
    background: #1e3a5f !important;
    color: #fff !important;
    padding: 0.5rem 0.4rem;
    font-weight: 600;
    text-align: center;
}
.tabla-matriz tbody th.cm-real {
    background: #f8fafc !important;
    color: #1e293b !important;
    font-weight: 600;
    text-align: left;
    padding: 0.45rem 0.6rem;
    border: 1px solid #e9ecf3;
}
.tabla-matriz tbody td {
    text-align: center;
    font-weight: 700;
    padding: 0.45rem 0.4rem;
    border: 1px solid #e9ecf3;
    min-width: 2.2rem;
}
.matriz-leyenda {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 0.65rem;
    font-size: 0.75rem;
    color: #475569 !important;
}
.matriz-leyenda-bar {
    flex: 1;
    max-width: 160px;
    height: 10px;
    border-radius: 5px;
    background: linear-gradient(90deg, #dbeafe, #1d4ed8);
}
.matriz-summary {
    display: grid;
    gap: 0.75rem;
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #e9ecf3;
}
.matriz-summary-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 0.95rem 1rem;
}
.matriz-summary-card .matriz-summary-label {
    display: block;
    font-size: 0.82rem;
    color: #475569 !important;
    margin-bottom: 0.35rem;
    font-weight: 600;
}
.matriz-summary-value {
    font-size: 1.4rem;
    font-weight: 700;
    color: #0f172a !important;
    margin-bottom: 0.35rem;
}
.matriz-summary-hint {
    font-size: 0.82rem;
    color: #64748b !important;
}
.matriz-recall-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.82rem;
}
.matriz-recall-table th,
.matriz-recall-table td {
    padding: 0.45rem 0.55rem;
    text-align: left;
    border: 1px solid #e9ecf3;
}
.matriz-recall-table th {
    background: #eef2ff;
    color: #1e293b !important;
    font-weight: 700;
}
.matriz-recall-table tbody tr:nth-child(even) td {
    background: #f8fafc !important;
}
.cell-pct {
    display: block;
    margin-top: 0.2rem;
    font-size: 0.72rem;
    font-weight: 500;
    color: rgba(30, 41, 59, 0.8) !important;
}

/* ── NLP TEXT BOX ────────────────────────────────────────── */
[data-testid="stAppViewContainer"] .main .nlp-texto-box,
[data-testid="stAppViewContainer"] .main .nlp-texto-box pre {
    background: #f8fafc !important;
    color: #1e293b !important;
    border: 1px solid #e2e8f0 !important;
}
[data-testid="stAppViewContainer"] .main .nlp-texto-box pre {
    margin: 0.5rem 0 0;
    padding: 0.85rem 1rem;
    border-radius: 8px;
    font-size: 0.88rem;
    font-family: 'DM Mono', monospace;
    line-height: 1.5;
    white-space: pre-wrap;
}
[data-testid="stAppViewContainer"] .main .nlp-texto-box .nlp-label {
    color: #64748b !important;
    font-size: 0.8rem;
    font-weight: 600;
}
[data-testid="stAppViewContainer"] .main [data-testid="stCodeBlock"] pre,
[data-testid="stAppViewContainer"] .main [data-testid="stCodeBlock"] code {
    background: #f8fafc !important;
    color: #1e293b !important;
    border: 1px solid #e2e8f0 !important;
    font-family: 'DM Mono', monospace !important;
}

/* ── HISTORIAL ───────────────────────────────────────────── */
.hist-item {
    background: #fff;
    border: 1px solid #e9ecf3;
    border-left: 3px solid #3b82f6;
    padding: 0.75rem 1rem;
    border-radius: 0 10px 10px 0;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
    color: #1e293b;
}

/* ── FOOTER ──────────────────────────────────────────────── */
.footer-bar {
    background: #fff;
    border: 1px solid #e9ecf3;
    border-radius: 10px;
    padding: 0.85rem 1.25rem;
    margin-top: 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.5rem;
    font-size: 0.85rem;
    color: #64748b;
}
.footer-ts { color: #94a3b8; font-size: 0.82rem; }

/* ── MISC ────────────────────────────────────────────────── */
.modelo-subtitle { color: #64748b; font-size: 0.88rem; margin: -0.2rem 0 0.75rem; }
.modelo-subtitle strong { color: #2563eb; }
.stats-mini { display: flex; gap: 1rem; flex-wrap: wrap; margin-top: 1rem; }
.stat-pill {
    background: #fff;
    border: 1px solid #e9ecf3;
    border-radius: 8px;
    padding: 0.45rem 0.9rem;
    font-size: 0.84rem;
    color: #475569;
}
.stat-pill strong { color: #1e293b; }

div[data-testid="stDataFrame"] table tbody tr:last-child,
.highlight-row { background-color: #f0fdf4 !important; }
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)