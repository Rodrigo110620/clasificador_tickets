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


def agregar_lote(filas: list[dict]) -> dict:
    """
    Agrega múltiples tickets al CSV en una sola operación (eficiente para lotes grandes).
    Cada elemento de filas: {"ticket": str, "categoria": str}
    Retorna {"agregados": int, "duplicados": int, "errores": int}
    """
    if not filas:
        return {"agregados": 0, "duplicados": 0, "errores": 0}

    os.makedirs(os.path.dirname(RUTA_DATASET), exist_ok=True)
    df_actual = cargar_dataset()

    # Construir set de hashes existentes para lookup O(1)
    if not df_actual.empty:
        hashes_existentes = set(df_actual["ticket"].astype(str).apply(hash_ticket))
    else:
        hashes_existentes = set()

    nuevos, duplicados, errores = [], 0, 0

    for fila in filas:
        try:
            texto = str(fila.get("ticket", "")).strip()
            categoria = str(fila.get("categoria", "")).strip()
            if not texto or not categoria:
                errores += 1
                continue
            h = hash_ticket(texto)
            if h in hashes_existentes:
                duplicados += 1
                continue
            hashes_existentes.add(h)
            nuevos.append({"ticket": texto, "categoria": categoria})
        except Exception:
            errores += 1

    if nuevos:
        df_nuevos = pd.DataFrame(nuevos)
        df_combined = pd.concat([df_actual, df_nuevos], ignore_index=True) if not df_actual.empty else df_nuevos
        df_combined.to_csv(RUTA_DATASET, index=False, encoding="utf-8")

    return {"agregados": len(nuevos), "duplicados": duplicados, "errores": errores}