import html

import streamlit as st


def _estilo_celda_matriz(valor: int, vmax: int) -> str:
    if vmax <= 0:
        ratio = 0.0
    else:
        ratio = min(valor / vmax, 1.0)
    fondo_r = int(235 - ratio * (235 - 43))
    fondo_g = int(248 - ratio * (248 - 108))
    fondo_b = int(255 - ratio * (255 - 176))
    texto = "#ffffff" if ratio > 0.5 else "#1a202c"
    return (
        f"background:#{fondo_r:02x}{fondo_g:02x}{fondo_b:02x} !important;"
        f"color:{texto} !important;"
    )


def grafico_probabilidades_html(prob_dict: dict, categoria_pred: str):
    ordenado = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)
    st.markdown("**Probabilidades por categoría**")
    for cat, prob in ordenado:
        pct = int(round(prob * 100))
        color = "#38a169" if cat == categoria_pred else "#4299e1"
        col_label, col_bar, col_pct = st.columns([2, 5, 1])
        with col_label:
            st.markdown(f"**{html.escape(cat)}**")
        with col_bar:
            st.progress(pct / 100)
        with col_pct:
            st.markdown(f"**{pct}%**")


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
                        <th style="background:#4a5568 !important;">Real \\ Pred</th>
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
