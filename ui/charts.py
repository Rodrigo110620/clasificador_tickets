import html

import streamlit as st

from config.constants import UMBRAL_VISUAL_PROB, icono_categoria


def _estilo_celda_matriz(valor: int, vmax: int) -> str:
    if vmax <= 0:
        ratio = 0.0
    else:
        ratio = min(valor / vmax, 1.0)
    fondo_r = int(235 - ratio * (235 - 29))
    fondo_g = int(248 - ratio * (248 - 78))
    fondo_b = int(255 - ratio * (255 - 216))
    texto = "#ffffff" if ratio > 0.55 else "#1e293b"
    return (
        f"background:#{fondo_r:02x}{fondo_g:02x}{fondo_b:02x} !important;"
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
    vmax = max((max(fila) for fila in matriz), default=1)
    encabezado = "".join(
        f"<th>{html.escape(lbl)}</th>" for lbl in etiquetas
    )
    cuerpo = []
    for i, real in enumerate(etiquetas):
        celdas = "".join(
            f"<td style='{_estilo_celda_matriz(matriz[i][j], vmax)}'>"
            f"{matriz[i][j]}</td>"
            for j in range(len(etiquetas))
        )
        cuerpo.append(
            f"<tr><th class='cm-real'>{html.escape(real)}</th>{celdas}</tr>"
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
                <span>Alto ({vmax})</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )