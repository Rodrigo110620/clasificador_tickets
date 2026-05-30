# ui/charts.py (versión corregida)

import html

import streamlit as st

from config.constants import UMBRAL_VISUAL_PROB, icono_categoria
from services.dataset import contar_por_categoria   # <-- NUEVO


def _estilo_celda_matriz(valor: int, fila_total: int) -> str:
    if fila_total <= 0:
        ratio = 0.0
    else:
        ratio = min(valor / fila_total, 1.0)
    hue = int(120 * ratio)
    texto = "#ffffff" if ratio > 0.55 else "#1e293b"
    return (
        f"background:hsl({hue}, 80%, 65%) !important;"
        f"color:{texto} !important;"
    )


def _formatear_pct(prob: float) -> str:
    pct = prob * 100
    if pct >= 10:
        return f"{pct:.0f}%"
    if pct >= 1:
        return f"{pct:.1f}%"
    if pct >= 0.1:
        return f"{pct:.2f}%"
    if pct > 0.0001:
        return f"{pct:.3f}%"
    return "<0.1%"


def _ancho_barra(prob: float) -> float:
    pct = prob * 100
    if pct <= 0:
        return 0.0
    return max(pct, 0.5)


def grafico_probabilidades_html(prob_dict: dict, categoria_destacada: str):
    """(sin cambios)"""
    ordenado = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)
    if not ordenado:
        return
    top_cat = ordenado[0][0]
    visible = [
        (cat, prob) for cat, prob in ordenado
        if prob >= UMBRAL_VISUAL_PROB or cat == top_cat
    ]
    ocultas = len(ordenado) - len(visible)
    filas = []
    for cat, prob in visible:
        pct_txt = _formatear_pct(prob)
        ancho = _ancho_barra(prob)
        es_top = cat == categoria_destacada
        clase = "prob-row prob-row-top" if es_top else "prob-row"
        icono = icono_categoria(cat)
        filas.append(
            f'<div class="{clase}">'
            f'  <div class="prob-label">{icono} {html.escape(cat)}</div>'
            f'  <div class="prob-track"><div class="prob-fill" style="width:{ancho:.2f}%;"></div></div>'
            f'  <div class="prob-pct">{pct_txt}</div>'
            f"</div>"
        )
    hint_ocultas = f" · {ocultas} categorías omitidas (&lt;5%)" if ocultas > 0 else ""
    st.markdown(
        f"""
        <div class="prob-panel">
            <div class="prob-panel-title">
                Probabilidades por categoría
                <span class="prob-sum-hint">(suma 100% · {len(visible)} mostradas{hint_ocultas})</span>
            </div>
            <div class="prob-list">
                {"".join(filas)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_matriz_confusion_html(
    matriz: list,
    etiquetas: list,
    nombre_modelo: str,
):
    # Obtener totales reales de cada categoría en el dataset completo
    conteo_real = contar_por_categoria()  # dict {categoria: total_en_csv}

    fila_totales = [sum(fila) for fila in matriz]   # totales en TEST
    total = sum(fila_totales)
    correctos = sum(matriz[i][i] for i in range(len(etiquetas)))
    accuracy_global = correctos / total if total else 0.0

    encabezado = "".join(f"<th>{html.escape(lbl)}</th>" for lbl in etiquetas)
    cuerpo = []
    recall_rows = []

    for i, real in enumerate(etiquetas):
        fila_total_test = fila_totales[i]
        total_real_csv = conteo_real.get(real, 0)   # <-- total real en CSV

        # Celdas de la matriz
        celdas = ""
        for j, pred in enumerate(etiquetas):
            valor = matriz[i][j]
            pct = valor / fila_total_test if fila_total_test else 0.0
            pct_txt = _formatear_pct(pct)
            title = f"Real: {real} → Pred: {pred} — {valor} ({pct_txt} de esta clase)"
            celdas += (
                f"<td style='{_estilo_celda_matriz(valor, fila_total_test)}' title='{html.escape(title)}'>"
                f"{valor}<br><span class='cell-pct'>{html.escape(pct_txt)}</span></td>"
            )
        cuerpo.append(f"<tr><th class='cm-real'>{html.escape(real)}</th>{celdas}</tr>")

        # Fila de recall (ahora con tres columnas)
        recall = matriz[i][i] / fila_total_test if fila_total_test else 0.0
        recall_rows.append(
            f"<tr>"
            f"<td>{html.escape(real)}</td>"
            f"<td>{_formatear_pct(recall)}</td>"
            f"<td>{fila_total_test}</td>"
            f"<td><strong>{total_real_csv}</strong></td>"   # <-- Nueva columna
            f"</tr>"
        )

    st.markdown(
        f"""
        <div class="matriz-wrap">
            <div class="matriz-title">Matriz de confusión — {html.escape(nombre_modelo)}</div>
            <div class="matriz-subtitle">Eje vertical: categoría real · Eje horizontal: predicción</div>
            <table class="tabla-matriz">
                <thead>
                    <tr>
                        <th style="background:#1e3a5f !important;">Real \\ Pred</th>
                        {encabezado}
                    </tr>
                </thead>
                <tbody>
                    {"".join(cuerpo)}
                </tbody>
            </table>
            <div class="matriz-leyenda">
                <span>Bajo</span>
                <div class="matriz-leyenda-bar"></div>
                <span>Alto (100%)</span>
            </div>
            <div class="matriz-summary">
                <div class="matriz-summary-card">
                    <div class="matriz-summary-label">Accuracy global</div>
                    <div class="matriz-summary-value">{accuracy_global * 100:.1f}%</div>
                    <div class="matriz-summary-hint">Correctas / total: {correctos} / {total}</div>
                </div>
                <div class="matriz-summary-card matriz-summary-recall">
                    <div class="matriz-summary-label">Recall por categoría</div>
                    <table class="matriz-recall-table">
                        <thead>
                            <tr>
                                <th>Categoría</th>
                                <th>Recall</th>
                                <th>Total en test</th>
                                <th>Total en CSV</th>
                            </tr>
                        </thead>
                        <tbody>
                            {"".join(recall_rows)}
                        </tbody>
                    </table>
                </div>
            </div>
            <div class="matriz-nota" style="margin-top: 1rem; font-size: 0.8rem; color: #475569; background: #f8fafc; padding: 0.5rem; border-radius: 8px;">
                ℹ️ Las métricas se calculan sobre el <strong>20% de los tickets</strong> (conjunto de prueba).<br>
                Solo se incluyen categorías con al menos <strong>20 ejemplos</strong> en el dataset completo. 
                La columna <strong>Total en CSV</strong> muestra el número real de tickets por categoría en todo el archivo.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )