"""Gestión del repositorio de entrenamiento (tickets.csv)."""

import os

import pandas as pd

from config.constants import RUTA_DATASET
from preprocess import limpiar_texto, md5_texto, preprocesar_texto


def _normalizar_ticket(texto: str) -> str:
    return " ".join(limpiar_texto(texto).split())


def hash_ticket(texto: str) -> str:
    return md5_texto(preprocesar_texto(texto))


def cargar_dataset() -> pd.DataFrame:
    if not os.path.exists(RUTA_DATASET):
        os.makedirs(os.path.dirname(RUTA_DATASET), exist_ok=True)
        return pd.DataFrame(columns=["ticket", "categoria"])
    return pd.read_csv(RUTA_DATASET)


def ticket_existe(texto: str) -> bool:
    df = cargar_dataset()
    if df.empty:
        return False
    h = hash_ticket(texto)
    if "_hash" not in df.columns:
        df["_hash"] = df["ticket"].astype(str).apply(hash_ticket)
    return h in df["_hash"].values


def agregar_ticket(texto: str, categoria: str) -> bool:
    """
    Añade un ticket al CSV si no está duplicado.
    Retorna True si se agregó, False si ya existía.
    """
    texto = texto.strip()
    categoria = categoria.strip()
    if not texto or not categoria:
        return False

    if ticket_existe(texto):
        return False

    os.makedirs(os.path.dirname(RUTA_DATASET), exist_ok=True)
    nueva = pd.DataFrame([{"ticket": texto, "categoria": categoria}])
    if os.path.exists(RUTA_DATASET):
        df = pd.read_csv(RUTA_DATASET)
        df = pd.concat([df, nueva], ignore_index=True)
    else:
        df = nueva
    df.to_csv(RUTA_DATASET, index=False, encoding="utf-8")
    return True


def actualizar_categoria(texto: str, categoria: str) -> bool:
    """Actualiza la categoría de un ticket existente (revisión manual admin)."""
    texto = texto.strip()
    if not os.path.exists(RUTA_DATASET):
        return agregar_ticket(texto, categoria)

    df = pd.read_csv(RUTA_DATASET)
    h = hash_ticket(texto)
    df["_hash"] = df["ticket"].astype(str).apply(hash_ticket)
    mask = df["_hash"] == h
    if mask.any():
        df.loc[mask, "categoria"] = categoria
        df.drop(columns=["_hash"], inplace=True)
        df.to_csv(RUTA_DATASET, index=False, encoding="utf-8")
        return True

    df.drop(columns=["_hash"], errors="ignore", inplace=True)
    return agregar_ticket(texto, categoria)


def contar_por_categoria() -> dict[str, int]:
    df = cargar_dataset()
    if df.empty:
        return {}
    return df["categoria"].value_counts().to_dict()


def ejemplos_por_categoria() -> dict[str, str]:
    """Un ticket de ejemplo por cada categoría del dataset (orden alfabético)."""
    df = cargar_dataset()
    if df.empty:
        return {}
    ejemplos: dict[str, str] = {}
    for categoria in sorted(df["categoria"].dropna().unique()):
        fila = df[df["categoria"] == categoria].iloc[0]
        texto = str(fila["ticket"]).strip()
        ejemplos[categoria] = texto
    return ejemplos
