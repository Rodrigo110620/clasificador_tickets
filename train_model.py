# train_model.py
# Script principal de entrenamiento para el clasificador de tickets de soporte técnico
# Entrena solo con tickets NUEVOS (no procesados anteriormente) usando memoria persistente.
# Guarda el mejor modelo comprimido con gzip.

import os
import pickle
import gzip
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, classification_report, confusion_matrix
)
from sklearn.pipeline import Pipeline

from preprocess import preprocesar_texto
import memoria  # <-- importar memoria persistente


# ─────────────────────────────────────────────
# 1. CARGA Y PREPROCESAMIENTO DEL DATASET (SOLO NUEVOS)
# ─────────────────────────────────────────────

def cargar_dataset_nuevos(ruta_csv: str) -> pd.DataFrame:
    """Carga el dataset CSV, filtra solo tickets nuevos (no en memoria) y aplica preprocesamiento."""
    print("[1/5] Cargando dataset...")
    df = pd.read_csv(ruta_csv)
    print(f"      Total de tickets en CSV: {len(df)}")

    print("[2/5] Preprocesando texto...")
    df['ticket_procesado'] = df['ticket'].apply(preprocesar_texto)

    # Filtrar solo los tickets que NO están en memoria (nuevos)
    df_nuevos, n_omitidos = memoria.filtrar_nuevos(df[['ticket_procesado', 'categoria']])

    print(f"      Tickets ya procesados (omitidos): {n_omitidos}")
    print(f"      Tickets NUEVOS a entrenar: {len(df_nuevos)}")

    if len(df_nuevos) == 0:
        print("      No hay tickets nuevos. Se omite el entrenamiento.")
        return pd.DataFrame()  # vacío

    print(f"      Categorías presentes: {df_nuevos['categoria'].unique().tolist()}")
    print(f"      Distribución:\n{df_nuevos['categoria'].value_counts().to_string()}\n")

    return df_nuevos


# ─────────────────────────────────────────────
# 2. CONSTRUCCIÓN DE PIPELINES OPTIMIZADOS (más livianos)
# ─────────────────────────────────────────────

def construir_pipelines() -> dict:
    """
    Crea pipelines con TF-IDF optimizado (unigramas, max_features, etc.)
    """
    # Parámetros comunes optimizados para reducir peso
    tfidf_params = {
        "ngram_range": (1, 1),  # solo unigramas (reduce dimensionalidad)
        "max_features": 5000,  # máximo 5000 términos
        "min_df": 2,  # ignorar términos que aparecen solo una vez
        "max_df": 0.9,  # ignorar términos muy frecuentes
        "sublinear_tf": True
    }

    pipelines = {
        "Naive Bayes": Pipeline([
            ("tfidf", TfidfVectorizer(**tfidf_params)),
            ("clf", MultinomialNB(alpha=0.1))
        ]),
        "Regresión Logística": Pipeline([
            ("tfidf", TfidfVectorizer(**tfidf_params)),
            ("clf", LogisticRegression(
                max_iter=1000,
                C=1.0,
                solver='lbfgs',
                multi_class='multinomial',
                random_state=42
            ))
        ])
    }
    return pipelines


# ─────────────────────────────────────────────
# 3. EVALUACIÓN
# ─────────────────────────────────────────────

def evaluar_modelo(nombre: str, pipeline, X_test, y_test) -> dict:
    y_pred = pipeline.predict(X_test)
    metricas = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, average='weighted', zero_division=0),
        "recall": recall_score(y_test, y_pred, average='weighted', zero_division=0),
        "f1_score": f1_score(y_test, y_pred, average='weighted', zero_division=0),
        "y_pred": y_pred
    }
    print(f"\n  ── {nombre} ──")
    print(f"  Accuracy:  {metricas['accuracy']:.4f}")
    print(f"  Precision: {metricas['precision']:.4f}")
    print(f"  Recall:    {metricas['recall']:.4f}")
    print(f"  F1-Score:  {metricas['f1_score']:.4f}")
    print(f"\n  Reporte detallado:\n{classification_report(y_test, y_pred, zero_division=0)}")
    return metricas


def graficar_confusion(nombre: str, y_test, y_pred, clases: list, carpeta: str = "models"):
    """Opcional: guarda matriz de confusión (solo la del mejor modelo)."""
    cm = confusion_matrix(y_test, y_pred, labels=clases)
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=clases, yticklabels=clases, ax=ax)
    ax.set_title(f"Matriz de Confusión - {nombre}", fontsize=13, fontweight='bold')
    ax.set_xlabel("Predicción", fontsize=11)
    ax.set_ylabel("Real", fontsize=11)
    plt.tight_layout()
    nombre_archivo = nombre.lower().replace(" ", "_").replace("ó", "o")
    ruta = os.path.join(carpeta, f"confusion_{nombre_archivo}.png")
    plt.savefig(ruta, dpi=150)
    plt.close()
    print(f"  Matriz de confusión guardada en: {ruta}")


# ─────────────────────────────────────────────
# 4. OPTIMIZACIÓN NAIVE BAYES (con vectorizador optimizado)
# ─────────────────────────────────────────────

def optimizar_naive_bayes(X_train, y_train) -> Pipeline:
    print("\n[4/5] Optimizando Naive Bayes con GridSearchCV (K=5)...")
    pipeline_nb = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 1), max_features=5000, min_df=2, max_df=0.9, sublinear_tf=True)),
        ("clf", MultinomialNB())
    ])
    param_grid = {'clf__alpha': [0.001, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0]}
    grid_search = GridSearchCV(pipeline_nb, param_grid, cv=5, scoring='f1_weighted', n_jobs=-1, verbose=0)
    grid_search.fit(X_train, y_train)
    print(f"  Mejor Alpha: {grid_search.best_params_['clf__alpha']} | F1: {grid_search.best_score_:.4f}")
    return grid_search.best_estimator_


# ─────────────────────────────────────────────
# 5. FLUJO PRINCIPAL (con guardado comprimido y actualización de memoria)
# ─────────────────────────────────────────────

def main():
    os.makedirs("models", exist_ok=True)

    # Cargar SOLO tickets nuevos (no procesados)
    df_nuevos = cargar_dataset_nuevos("dataset/tickets.csv")
    if df_nuevos.empty:
        print("No hay tickets nuevos. Entrenamiento cancelado.")
        return

    X = df_nuevos['ticket_procesado']
    y = df_nuevos['categoria']
    clases = sorted(y.unique().tolist())

    # División entrenamiento/prueba
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"[3/5] División: entrenamiento {len(X_train)} | prueba {len(X_test)}\n")

    # Entrenar pipelines base
    pipelines = construir_pipelines()
    resultados = {}

    print("[3/5] Entrenando modelos base...")
    for nombre, pipeline in pipelines.items():
        pipeline.fit(X_train, y_train)
        metricas = evaluar_modelo(nombre, pipeline, X_test, y_test)
        resultados[nombre] = {"pipeline": pipeline, "metricas": metricas}
        # Solo guardar gráfico del mejor más adelante (opcional)

    # Optimizar Naive Bayes
    nb_optimizado = optimizar_naive_bayes(X_train, y_train)
    metricas_opt = evaluar_modelo("Naive Bayes Optimizado", nb_optimizado, X_test, y_test)
    resultados["Naive Bayes Optimizado"] = {"pipeline": nb_optimizado, "metricas": metricas_opt}

    # Seleccionar mejor modelo por F1
    mejor_nombre = max(resultados, key=lambda k: resultados[k]["metricas"]["f1_score"])
    mejor_modelo = resultados[mejor_nombre]["pipeline"]
    mejor_f1 = resultados[mejor_nombre]["metricas"]["f1_score"]
    print(f"\n  ✔ Mejor modelo: {mejor_nombre} (F1: {mejor_f1:.4f})")

    # Guardar gráfico de confusión solo del mejor modelo
    y_pred_mejor = resultados[mejor_nombre]["metricas"]["y_pred"]
    graficar_confusion(mejor_nombre, y_test, y_pred_mejor, clases)

    # Preparar métricas para dashboard
    nombres_tabla = {
        "Naive Bayes": "Naive Bayes (default)",
        "Naive Bayes Optimizado": "Naive Bayes optimizado",
        "Regresión Logística": "Regresión Logística",
    }
    comparacion = []
    for nombre, datos in resultados.items():
        m = datos["metricas"]
        comparacion.append({
            "modelo": nombres_tabla.get(nombre, nombre),
            "accuracy": m["accuracy"],
            "precision": m["precision"],
            "recall": m["recall"],
            "f1_score": m["f1_score"],
        })
    mejor_nombre_tabla = nombres_tabla.get(mejor_nombre, mejor_nombre)
    cm_mejor = confusion_matrix(y_test, y_pred_mejor, labels=clases)
    ruta_confusion = f"models/confusion_{mejor_nombre.lower().replace(' ', '_').replace('ó', 'o')}.png"

    metricas_dashboard = {
        "comparacion": comparacion,
        "mejor": mejor_nombre_tabla,
        "mejor_metricas": {k: v for k, v in resultados[mejor_nombre]["metricas"].items() if k != "y_pred"},
        "confusion_matrix": cm_mejor.tolist(),
        "confusion_labels": clases,
        "confusion_img": ruta_confusion if os.path.exists(ruta_confusion) else None,
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "clases": clases,
    }

    # Guardar modelo COMPRIMIDO con gzip
    ruta_modelo = "models/mejor_modelo.pkl.gz"
    with gzip.open(ruta_modelo, "wb") as f:
        pickle.dump({
            "modelo": mejor_modelo,
            "clases": clases,
            "nombre": mejor_nombre,
            "metricas": metricas_dashboard,
        }, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"  Modelo comprimido guardado en: {ruta_modelo}")

    # Guardar métricas sin compresión (es pequeño)
    with open("models/metricas_entrenamiento.pkl", "wb") as f:
        pickle.dump(metricas_dashboard, f)
    print("  Métricas del dashboard guardadas en: models/metricas_entrenamiento.pkl")

    # Actualizar memoria con los tickets NUEVOS que se usaron en entrenamiento
    # (para que no se vuelvan a entrenar en el futuro)
    pares_memoria = []
    for idx, row in df_nuevos.iterrows():
        pares_memoria.append({
            "texto_procesado": row['ticket_procesado'],
            "categoria": row['categoria']
        })
    memoria.guardar_lote(pares_memoria)
    print(f"  Memoria actualizada con {len(pares_memoria)} tickets nuevos.")

    # Resumen
    print("\n" + "=" * 55)
    print("  RESUMEN COMPARATIVO DE MODELOS")
    print("=" * 55)
    print(f"  {'Modelo':<30} {'F1-Score':>10}")
    print("-" * 55)
    for nombre, datos in resultados.items():
        marcador = " ← MEJOR" if nombre == mejor_nombre else ""
        print(f"  {nombre:<30} {datos['metricas']['f1_score']:>10.4f}{marcador}")
    print("=" * 55)

    # Mostrar tamaño del modelo comprimido
    tamaño_mb = os.path.getsize(ruta_modelo) / (1024 * 1024)
    print(f"\n  Tamaño del modelo comprimido: {tamaño_mb:.2f} MB")


if __name__ == "__main__":
    main()