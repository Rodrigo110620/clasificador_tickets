import html

import streamlit as st

from config.constants import UMBRAL_VISUAL_PROB, icono_categoria


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
    """
    Muestra las categorías del modelo filtrando las que están
    por debajo de UMBRAL_VISUAL_PROB (5%) para no confundir al usuario.
    La categoría top siempre se muestra aunque esté por debajo del umbral.
    """
    ordenado = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)
    if not ordenado:
        return

    # FIX: filtrar probabilidades residuales — solo mostrar >= 5% o la top-1
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
    fila_totales = [sum(fila) for fila in matriz]
    total = sum(fila_totales)
    correctos = sum(matriz[i][i] for i in range(len(etiquetas)))
    accuracy_global = correctos / total if total else 0.0

    encabezado = "".join(
        f"<th>{html.escape(lbl)}</th>" for lbl in etiquetas
    )
    cuerpo = []
    recall_rows = []
    for i, real in enumerate(etiquetas):
        fila_total = fila_totales[i]
        celdas = ""
        for j, pred in enumerate(etiquetas):
            valor = matriz[i][j]
            pct = valor / fila_total if fila_total else 0.0
            pct_txt = _formatear_pct(pct)
            title = (
                f"Real: {real} → Pred: {pred} — {valor} ({pct_txt} de esta clase)"
            )
            celdas += (
                f"<td style='{_estilo_celda_matriz(valor, fila_total)}' title='{html.escape(title)}'>"
                f"{valor}<br><span class='cell-pct'>{html.escape(pct_txt)}</span></td>"
            )
        cuerpo.append(
            f"<tr><th class='cm-real'>{html.escape(real)}</th>{celdas}</tr>"
        )
        recall = matriz[i][i] / fila_total if fila_total else 0.0
        recall_rows.append(
            f"<tr><td>{html.escape(real)}</td>"
            f"<td>{_formatear_pct(recall)}</td>"
            f"<td>{fila_total}</td></tr>"
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
                            <tr><th>Categoría</th><th>Recall</th><th>Total real</th></tr>
                        </thead>
                        <tbody>
                            {"".join(recall_rows)}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )