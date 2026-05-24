# memoria.py
# Memoria persistente de tickets procesados usando JSON.
# Evita reprocesar/reentrenar con tickets ya vistos.
# El archivo memoria.json es portable, legible y pesa KBs (no GBs).

import json
import os
from datetime import datetime
from preprocess import md5_texto

RUTA_MEMORIA = "models/memoria.json"


# ── Carga / Guardado base ──────────────────────────────────────

def cargar_memoria() -> dict:
    """
    Lee memoria.json y retorna el diccionario completo.
    Estructura:
    {
      "tickets": {
        "<hash_md5>": {
          "categoria": "Credenciales",
          "fecha":     "22/05/2026 14:30",
          "preview":   "pued inici sesion..."
        }
      },
      "categorias_vistas": ["Credenciales", "Base de Datos", ...]
    }
    """
    if not os.path.exists(RUTA_MEMORIA):
        return {"tickets": {}, "categorias_vistas": []}
    with open(RUTA_MEMORIA, "r", encoding="utf-8") as f:
        return json.load(f)


def _guardar_json(mem: dict):
    os.makedirs(os.path.dirname(RUTA_MEMORIA), exist_ok=True)
    with open(RUTA_MEMORIA, "w", encoding="utf-8") as f:
        json.dump(mem, f, ensure_ascii=False, indent=2)


# ── API pública ────────────────────────────────────────────────

def ticket_ya_procesado(texto_procesado: str) -> bool:
    """True si el hash MD5 del texto procesado ya existe en memoria."""
    mem = cargar_memoria()
    return md5_texto(texto_procesado) in mem["tickets"]


def guardar_en_memoria(texto_procesado: str, categoria: str):
    """
    Guarda un ticket procesado en memoria.json.
    - Si el hash ya existe, actualiza la fecha (no duplica).
    - Si la categoría es nueva, la agrega a categorias_vistas.
    """
    mem   = cargar_memoria()
    h     = md5_texto(texto_procesado)
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M")

    mem["tickets"][h] = {
        "categoria": categoria,
        "fecha":     ahora,
        "preview":   texto_procesado[:60],
    }

    if categoria not in mem["categorias_vistas"]:
        mem["categorias_vistas"].append(categoria)

    _guardar_json(mem)


def guardar_lote(pares: list):
    """
    Guarda múltiples tickets de una vez (más eficiente que llamar
    guardar_en_memoria() en un loop — una sola escritura a disco).
    pares: [{"texto_procesado": "...", "categoria": "..."}, ...]
    """
    mem   = cargar_memoria()
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M")

    for par in pares:
        texto_proc = par["texto_procesado"]
        categoria  = par["categoria"]
        h          = md5_texto(texto_proc)

        mem["tickets"][h] = {
            "categoria": categoria,
            "fecha":     ahora,
            "preview":   texto_proc[:60],
        }
        if categoria not in mem["categorias_vistas"]:
            mem["categorias_vistas"].append(categoria)

    _guardar_json(mem)


def filtrar_nuevos(df_tickets) -> tuple:
    """
    Recibe un DataFrame con columnas ['ticket_procesado', 'categoria'].
    Retorna (df_nuevos, n_omitidos):
      - df_nuevos  : filas cuyo hash NO está en memoria
      - n_omitidos : cuántas filas ya existían
    """
    mem = cargar_memoria()
    conocidos = set(mem["tickets"].keys())

    from preprocess import md5_texto as _md5
    mask      = df_tickets["ticket_procesado"].apply(lambda t: _md5(t) not in conocidos)
    df_nuevos = df_tickets[mask]
    n_omit    = len(df_tickets) - len(df_nuevos)
    return df_nuevos, n_omit


def stats_memoria() -> dict:
    """Estadísticas rápidas para mostrar en la UI o consola."""
    mem = cargar_memoria()
    tickets = mem["tickets"]
    cats    = mem["categorias_vistas"]

    conteo = {}
    for entry in tickets.values():
        c = entry["categoria"]
        conteo[c] = conteo.get(c, 0) + 1

    return {
        "total_tickets":      len(tickets),
        "total_categorias":   len(cats),
        "categorias":         cats,
        "conteo_por_cat":     conteo,
        "ruta":               RUTA_MEMORIA,
        "peso_kb":            round(os.path.getsize(RUTA_MEMORIA) / 1024, 2)
                              if os.path.exists(RUTA_MEMORIA) else 0,
    }


# ── Test rápido ───────────────────────────────────────────────
if __name__ == "__main__":
    import os
    import memoria as _self
    _self.RUTA_MEMORIA = "models/memoria_test.json"
    os.makedirs("models", exist_ok=True)

    print("=== Test memoria.py ===\n")

    guardar_lote([
        {"texto_procesado": "pued inici sesion sistem", "categoria": "Credenciales"},
        {"texto_procesado": "error ora consult sql",    "categoria": "Base de Datos"},
        {"texto_procesado": "vpn conect serv",          "categoria": "Infraestructura"},
    ])
    print("Guardados 3 tickets.")

    ya = ticket_ya_procesado("pued inici sesion sistem")
    no = ticket_ya_procesado("boton guard funcion")
    print(f"'pued inici sesion...' ya procesado: {ya}  (esperado: True)")
    print(f"'boton guard...' ya procesado: {no}  (esperado: False)")

    guardar_en_memoria("boton guard funcion aplic", "Bug de Software")
    print("Guardado ticket con categoría nueva: Bug de Software")

    s = stats_memoria()
    print(f"\nEstadísticas:")
    print(f"  Total tickets  : {s['total_tickets']}")
    print(f"  Categorías     : {s['categorias']}")
    print(f"  Conteo por cat : {s['conteo_por_cat']}")
    print(f"  Peso del JSON  : {s['peso_kb']} KB")

    os.remove(_self.RUTA_MEMORIA)
    print("\nTest completado OK")
