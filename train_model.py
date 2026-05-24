# train_model.py
# Entrenamiento del clasificador de tickets.
# Uso CLI: python train_model.py

import gzip
import os
import pickle
from collections import Counter
from datetime import datetime

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

import memoria
from config.constants import MIN_EJEMPLOS_POR_CATEGORIA, RUTA_DATASET
from preprocess import preprocesar_texto


def _tfidf_params() -> dict:
    return {
        "ngram_range": (1, 2),
        "max_features": 8000,
        "min_df": 1,
        "max_df": 1.0,
        "sublinear_tf": True,
    }


def _cv_folds(y) -> int:
    """CV dinámico: máximo min(conteo_clase)-1, entre 2 y 5."""
    min_count = min(Counter(y).values())
    return max(2, min(5, min_count - 1))


def cargar_y_preprocesar(
    ruta_csv: str = RUTA_DATASET,
    min_por_categoria: int = MIN_EJEMPLOS_POR_CATEGORIA,
) -> tuple[pd.DataFrame, list[str]]:
    """Carga TODO el CSV (sin filtrar por memoria) y preprocesa."""
    print("[1/5] Cargando dataset...")
    df = pd.read_csv(ruta_csv)
    antes = len(df)
    df = df.drop_duplicates(subset=["ticket"], keep="first")
    if len(df) < antes:
        print(f"      Duplicados eliminados: {antes - len(df)}")

    print(f"      Total de tickets en CSV: {len(df)}")
    print("[2/5] Preprocesando texto...")
    df["ticket_procesado"] = df["ticket"].apply(preprocesar_texto)

    df, omitidas = filtrar_categorias_minimas(df, min_por_categoria)
    if df.empty:
        return df, omitidas

    print(f"      Categorías en entrenamiento: {df['categoria'].unique().tolist()}")
    print(f"      Distribución:\n{df['categoria'].value_counts().to_string()}\n")
    return df, omitidas


def filtrar_categorias_minimas(df: pd.DataFrame, minimo: int) -> tuple[pd.DataFrame, list[str]]:
    conteo = df["categoria"].value_counts()
    validas = conteo[conteo >= minimo].index.tolist()
    omitidas = conteo[conteo < minimo].index.tolist()
    if omitidas:
        print(
            f"      Categorías omitidas (< {minimo} ejemplos): "
            f"{', '.join(f'{c} ({conteo[c]})' for c in omitidas)}"
        )
    return df[df["categoria"].isin(validas)].copy(), omitidas


def construir_pipelines() -> dict:
    tfidf = _tfidf_params()
    return {
        "Naive Bayes": Pipeline([
            ("tfidf", TfidfVectorizer(**tfidf)),
            ("clf", MultinomialNB(alpha=1.0)),
        ]),
        "Regresión Logística": Pipeline([
            ("tfidf", TfidfVectorizer(**tfidf)),
            ("clf", LogisticRegression(
                max_iter=2000,
                C=0.1,
                solver="lbfgs",
                multi_class="multinomial",
                random_state=42,
            )),
        ]),
    }


def evaluar_modelo(nombre: str, pipeline, X_test, y_test) -> dict:
    y_pred = pipeline.predict(X_test)
    metricas = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, average="weighted", zero_division=0),
        "recall": recall_score(y_test, y_pred, average="weighted", zero_division=0),
        "f1_score": f1_score(y_test, y_pred, average="weighted", zero_division=0),
        "y_pred": y_pred,
    }
    print(f"\n  ── {nombre} ──")
    print(f"  Accuracy:  {metricas['accuracy']:.4f}")
    print(f"  Precision: {metricas['precision']:.4f}")
    print(f"  Recall:    {metricas['recall']:.4f}")
    print(f"  F1-Score:  {metricas['f1_score']:.4f}")
    print(f"\n  Reporte detallado:\n{classification_report(y_test, y_pred, zero_division=0)}")
    return metricas


def graficar_confusion(nombre: str, y_test, y_pred, clases: list, carpeta: str = "models"):
    cm = confusion_matrix(y_test, y_pred, labels=clases)
    fig, ax = plt.subplots(figsize=(max(7, len(clases)), max(5, len(clases) * 0.6)))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=clases, yticklabels=clases, ax=ax)
    ax.set_title(f"Matriz de Confusión - {nombre}", fontsize=13, fontweight="bold")
    ax.set_xlabel("Predicción", fontsize=11)
    ax.set_ylabel("Real", fontsize=11)
    plt.tight_layout()
    nombre_archivo = nombre.lower().replace(" ", "_").replace("ó", "o")
    ruta = os.path.join(carpeta, f"confusion_{nombre_archivo}.png")
    plt.savefig(ruta, dpi=150)
    plt.close()
    print(f"  Matriz de confusión guardada en: {ruta}")
    return ruta


def optimizar_naive_bayes(X_train, y_train) -> Pipeline:
    cv = _cv_folds(y_train)
    print(f"\n[4/5] Optimizando Naive Bayes (CV={cv})...")
    pipeline_nb = Pipeline([
        ("tfidf", TfidfVectorizer(**_tfidf_params())),
        ("clf", MultinomialNB()),
    ])
    param_grid = {"clf__alpha": [0.5, 1.0, 1.5, 2.0, 3.0]}
    grid_search = GridSearchCV(
        pipeline_nb,
        param_grid,
        cv=StratifiedKFold(n_splits=cv, shuffle=True, random_state=42),
        scoring="f1_weighted",
        n_jobs=-1,
        verbose=0,
    )
    grid_search.fit(X_train, y_train)
    print(
        f"  Mejor Alpha: {grid_search.best_params_['clf__alpha']} "
        f"| F1: {grid_search.best_score_:.4f}"
    )
    return grid_search.best_estimator_


def calibrar_probabilidades(pipeline, X_train, y_train):
    """Suaviza probabilidades extremas (evita 100% / 0% rígidos)."""
    cv = _cv_folds(y_train)
    calibrado = CalibratedClassifierCV(
        pipeline,
        method="sigmoid",
        cv=StratifiedKFold(n_splits=cv, shuffle=True, random_state=42),
    )
    calibrado.fit(X_train, y_train)
    return calibrado


def entrenar_desde_csv(
    min_por_categoria: int = MIN_EJEMPLOS_POR_CATEGORIA,
    ruta_csv: str = RUTA_DATASET,
    verbose: bool = True,
) -> dict:
    """Entrena siempre con TODOS los tickets del CSV."""
    os.makedirs("models", exist_ok=True)

    if not os.path.exists(ruta_csv):
        return {"ok": False, "mensaje": f"No existe el dataset: {ruta_csv}"}

    df, omitidas = cargar_y_preprocesar(ruta_csv, min_por_categoria=min_por_categoria)
    if df.empty:
        msg = "No hay tickets para entrenar."
        if omitidas:
            msg += f" Categorías con pocos ejemplos (< {min_por_categoria}): {', '.join(omitidas)}"
        return {"ok": False, "mensaje": msg, "categorias_omitidas": omitidas}

    X = df["ticket_procesado"]
    y = df["categoria"]
    clases = sorted(y.unique().tolist())

    if len(clases) < 2:
        return {
            "ok": False,
            "mensaje": "Se necesitan al menos 2 categorías con suficientes ejemplos.",
        }

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    if verbose:
        print(f"[3/5] División: entrenamiento {len(X_train)} | prueba {len(X_test)}\n")

    pipelines = construir_pipelines()
    resultados = {}

    if verbose:
        print("[3/5] Entrenando modelos base...")
    for nombre, pipeline in pipelines.items():
        pipeline.fit(X_train, y_train)
        metricas = evaluar_modelo(nombre, pipeline, X_test, y_test)
        resultados[nombre] = {"pipeline": pipeline, "metricas": metricas}

    nb_optimizado = optimizar_naive_bayes(X_train, y_train)
    metricas_opt = evaluar_modelo("Naive Bayes Optimizado", nb_optimizado, X_test, y_test)
    resultados["Naive Bayes Optimizado"] = {"pipeline": nb_optimizado, "metricas": metricas_opt}

    nombres_tabla = {
        "Naive Bayes": "Naive Bayes (default)",
        "Naive Bayes Optimizado": "Naive Bayes optimizado",
        "Regresión Logística": "Regresión Logística",
    }

    mejor_key = max(resultados, key=lambda k: resultados[k]["metricas"]["f1_score"])
    mejor_pipeline = resultados[mejor_key]["pipeline"]
    mejor_f1_cv = resultados[mejor_key]["metricas"]["f1_score"]

    if verbose:
        print(f"\n  ✔ Mejor por F1 en prueba: {mejor_key} (F1: {mejor_f1_cv:.4f})")
        print("  Calibrando probabilidades del modelo seleccionado...")

    mejor_modelo = calibrar_probabilidades(mejor_pipeline, X_train, y_train)
    nombre_activo = f"{nombres_tabla.get(mejor_key, mejor_key)} (calibrado)"

    y_pred_mejor = mejor_modelo.predict(X_test)
    if verbose:
        evaluar_modelo(nombre_activo, mejor_modelo, X_test, y_test)

    ruta_confusion = graficar_confusion(mejor_key, y_test, y_pred_mejor, clases)

    metricas_activo = {
        "accuracy": accuracy_score(y_test, y_pred_mejor),
        "precision": precision_score(y_test, y_pred_mejor, average="weighted", zero_division=0),
        "recall": recall_score(y_test, y_pred_mejor, average="weighted", zero_division=0),
        "f1_score": f1_score(y_test, y_pred_mejor, average="weighted", zero_division=0),
    }

    comparacion = []
    for nombre, datos in resultados.items():
        en_uso = nombre == mejor_key
        m = metricas_activo if en_uso else datos["metricas"]
        etiqueta = nombres_tabla.get(nombre, nombre)
        if en_uso:
            etiqueta = f"{etiqueta} (calibrado)"
        comparacion.append({
            "modelo": etiqueta,
            "accuracy": m["accuracy"],
            "precision": m["precision"],
            "recall": m["recall"],
            "f1_score": m["f1_score"],
            "en_uso": en_uso,
        })

    cm_mejor = confusion_matrix(y_test, y_pred_mejor, labels=clases)

    metricas_dashboard = {
        "comparacion": comparacion,
        "mejor": nombre_activo,
        "modelo_activo": nombre_activo,
        "mejor_metricas": metricas_activo,
        "confusion_matrix": cm_mejor.tolist(),
        "confusion_labels": clases,
        "confusion_img": ruta_confusion if os.path.exists(ruta_confusion) else None,
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "clases": clases,
    }

    ruta_modelo = "models/mejor_modelo.pkl.gz"
    with gzip.open(ruta_modelo, "wb") as f:
        pickle.dump({
            "modelo": mejor_modelo,
            "clases": clases,
            "nombre": nombre_activo,
            "metricas": metricas_dashboard,
        }, f, protocol=pickle.HIGHEST_PROTOCOL)

    with open("models/metricas_entrenamiento.pkl", "wb") as f:
        pickle.dump(metricas_dashboard, f)

    pares = [
        {"texto_procesado": row["ticket_procesado"], "categoria": row["categoria"]}
        for _, row in df.iterrows()
    ]
    memoria.guardar_lote(pares)

    if verbose:
        print(f"  Modelo guardado en: {ruta_modelo}")
        print(f"  Memoria sincronizada con {len(pares)} tickets.")

    f1_final = metricas_dashboard["mejor_metricas"]["f1_score"]
    return {
        "ok": True,
        "mensaje": f"Modelo activo: {nombre_activo} (F1 test: {f1_final:.2%}).",
        "mejor_modelo": nombre_activo,
        "f1": f1_final,
        "metricas": metricas_dashboard,
        "categorias": clases,
        "categorias_omitidas": omitidas,
        "n_tickets": len(df),
    }


def main():
    resultado = entrenar_desde_csv()
    if not resultado["ok"]:
        print(resultado["mensaje"])
        return
    print("\n" + "=" * 55)
    print("  ENTRENAMIENTO COMPLETADO")
    print("=" * 55)
    print(f"  {resultado['mensaje']}")


if __name__ == "__main__":
    main()
