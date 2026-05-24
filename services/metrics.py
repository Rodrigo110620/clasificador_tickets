import gzip
import os
import pickle
from datetime import datetime

import pandas as pd
import streamlit as st
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

from config.constants import RUTA_DATASET, RUTA_MODELO
from preprocess import preprocesar_texto


def _leer_metricas_archivo():
    for ruta in ("models/metricas_entrenamiento.pkl", RUTA_MODELO):
        if not os.path.exists(ruta):
            continue
        try:
            if ruta.endswith(".gz"):
                with gzip.open(ruta, "rb") as f:
                    datos = pickle.load(f)
            else:
                with open(ruta, "rb") as f:
                    datos = pickle.load(f)
        except Exception:
            continue
        if isinstance(datos, dict) and datos.get("metricas"):
            return datos["metricas"]
        if isinstance(datos, dict) and datos.get("comparacion"):
            return datos
    return None


@st.cache_data(show_spinner=False)
def evaluar_en_dataset(_version: str = "v2"):
    """Recalcula métricas y matriz de confusión (datos para gráficos HTML)."""
    if not os.path.exists(RUTA_DATASET):
        return None

    if not os.path.exists(RUTA_MODELO):
        alt_ruta = "models/mejor_modelo.pkl"
        if os.path.exists(alt_ruta):
            with open(alt_ruta, "rb") as f:
                datos = pickle.load(f)
        else:
            return None
    elif RUTA_MODELO.endswith(".gz"):
        with gzip.open(RUTA_MODELO, "rb") as f:
            datos = pickle.load(f)
    else:
        with open(RUTA_MODELO, "rb") as f:
            datos = pickle.load(f)

    modelo = datos["modelo"]
    nombre = datos.get("nombre", "Modelo")

    df = pd.read_csv(RUTA_DATASET)
    df["ticket_procesado"] = df["ticket"].apply(preprocesar_texto)
    X = df["ticket_procesado"]
    y = df["categoria"]

    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    y_pred = modelo.predict(X_test)
    clases = sorted(y.unique().tolist())
    cm = confusion_matrix(y_test, y_pred, labels=clases)

    metricas_archivo = _leer_metricas_archivo()
    comparacion = (metricas_archivo or {}).get("comparacion")
    mejor = (metricas_archivo or {}).get("mejor", nombre)

    if not comparacion:
        comparacion = [{
            "modelo": nombre,
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, average="weighted", zero_division=0),
            "recall": recall_score(y_test, y_pred, average="weighted", zero_division=0),
            "f1_score": f1_score(y_test, y_pred, average="weighted", zero_division=0),
        }]
        mejor = nombre

    return {
        "comparacion": comparacion,
        "mejor": mejor,
        "mejor_metricas": {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, average="weighted", zero_division=0),
            "recall": recall_score(y_test, y_pred, average="weighted", zero_division=0),
            "f1_score": f1_score(y_test, y_pred, average="weighted", zero_division=0),
        },
        "confusion_matrix": cm.tolist(),
        "confusion_labels": clases,
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "clases": clases,
    }


def cargar_metricas(datos_modelo=None):
    metricas = _leer_metricas_archivo()
    if metricas and metricas.get("comparacion") and metricas.get("mejor_metricas"):
        if metricas.get("confusion_matrix") and metricas.get("confusion_labels"):
            return metricas
    if datos_modelo:
        return evaluar_en_dataset()
    return metricas
