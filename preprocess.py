# preprocess.py — SnowballStemmer + normalización de acentos + stopwords extendidas

import re
import hashlib
import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer

nltk.download('stopwords', quiet=True)

STEMMER = SnowballStemmer("spanish")

# Stopwords base de NLTK
_SW_BASE = set(stopwords.words('spanish'))

# Stopwords extra: saludos, muletillas y palabras no-IT que NLTK no cubre
_SW_EXTRA = {
    "hola", "buenas", "buenos", "buen", "dias", "tardes", "noches",
    "gracias", "saludos", "cordialmente", "atte", "favor", "porfavor",
    "porfa", "please", "ok", "okay", "okey", "oki",
    "jaja", "jeje", "xd", "lol", "hmm", "mmm", "eee",
    "ahi", "aca", "alla", "aqui", "donde", "cuando", "como",
    "alguien", "nadie", "nada", "algo", "todo", "todos",
    "necesito", "quiero", "quisiera", "podrian", "pueden",
    "ayuda", "ayudar", "ayudame", "apoyar", "apoyo",
    "urgente", "urgente", "rapido", "pronto",
    "ver", "saber", "decir", "hacer", "poder",
    "dia", "semana", "mes", "ano", "hoy", "ayer", "manana",
}

STOPWORDS_ES = _SW_BASE | _SW_EXTRA
MIN_PALABRAS_UTILES = 3
MAX_LONGITUD_PALABRA = 15
MIN_LONGITUD_TEXTO = 20


# ── Helpers ───────────────────────────────────────────────────

def _normalizar_acentos(texto: str) -> str:
    """á→a, é→e … para que stopwords coincidan sin importar tilde."""
    tabla = str.maketrans("áéíóúü", "aeiouu")
    return texto.translate(tabla)


def limpiar_texto(texto: str) -> str:
    texto = texto.lower()
    texto = re.sub(r'[^a-záéíóúüñ\s]', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto


def md5_texto(texto_procesado: str) -> str:
    return hashlib.md5(texto_procesado.encode()).hexdigest()


# ── Pipeline ───────────────────────────────────────────────────

def preprocesar_texto(texto: str) -> str:
    """Pipeline rápido → string listo para vectorizar."""
    tokens_orig = limpiar_texto(texto).split()
    utiles, _ = _filtrar(tokens_orig)
    stems = [STEMMER.stem(t) for t in utiles]
    return " ".join(stems)


def preprocesar_con_detalle(texto: str) -> dict:
    """Pipeline completo con metadata para la UI."""
    texto_limpio = limpiar_texto(texto)
    tokens_orig = texto_limpio.split()

    utiles, eliminadas = _filtrar(tokens_orig)
    stems = [STEMMER.stem(t) for t in utiles]
    texto_proc = " ".join(stems)
    valido, mot = _validar(stems)

    return {
        "texto_procesado":       texto_proc,
        "tokens_utiles":         utiles,
        "stems":                 stems,
        "palabras_eliminadas":   eliminadas,
        "es_valido":             valido,
        "motivo_rechazo":        mot,
        "hash_md5":              md5_texto(texto_proc),
        "n_palabras_originales": len(tokens_orig),
        "n_palabras_utiles":     len(utiles),
    }


def _filtrar(tokens_orig: list) -> tuple:
    """
    Retorna (utiles, eliminadas).
    Compara contra stopwords usando versión sin acentos.
    """
    utiles, eliminadas = [], []
    for t in tokens_orig:
        t_norm = _normalizar_acentos(t)
        if t_norm in STOPWORDS_ES or len(t_norm) <= 2:
            eliminadas.append(t)
        else:
            utiles.append(t)
    return utiles, eliminadas


def _validar(stems: list) -> tuple:
    if len(stems) < MIN_PALABRAS_UTILES:
        return False, f"Solo {len(stems)} palabra(s) útil(es) tras filtrar"
    return True, ""


def es_texto_valido(texto: str, detalle: dict | None = None) -> tuple[bool, str]:
    """Valida el ticket y devuelve (es_valido, motivo)."""
    if detalle is None:
        detalle = preprocesar_con_detalle(texto)

    texto_limpio = limpiar_texto(texto)
    if len(texto_limpio) < MIN_LONGITUD_TEXTO:
        return False, f"El texto limpio debe tener al menos {MIN_LONGITUD_TEXTO} caracteres."

    if detalle["n_palabras_utiles"] < MIN_PALABRAS_UTILES:
        return False, f"Se requieren al menos {MIN_PALABRAS_UTILES} palabras útiles; actualmente hay {detalle['n_palabras_utiles']}."

    palabras_largas = [t for t in texto_limpio.split() if len(t) > MAX_LONGITUD_PALABRA]
    if palabras_largas:
        muestra = ", ".join(palabras_largas[:3])
        return False, f"Palabra(s) anormalmente larga(s) detectada(s): {muestra}."

    return True, ""


def extraer_palabras_clave(texto: str, max_palabras: int = 5) -> list[str]:
    """Extrae palabras clave útiles para mostrar en la interfaz."""
    detalle = preprocesar_con_detalle(texto)
    claves = []
    for token in detalle["tokens_utiles"]:
        if token not in claves:
            claves.append(token)
        if len(claves) >= max_palabras:
            break
    return claves


# ── Test ───────────────────────────────────────────────────────
if __name__ == "__main__":
    casos = [
        "Hola no funciona excel dónde está la base de datos",
        "No puedo iniciar sesión en el sistema, mi contraseña no funciona!!",
        "Error ORA-00942 al ejecutar la consulta SQL",
        "hola buenos dias jaja",
        "!!! ???",
    ]
    for c in casos:
        r = preprocesar_con_detalle(c)
        valido, motivo = es_texto_valido(c, r)
        estado = "OK" if valido else f"RECHAZADO — {motivo}"
        print(f"\n[{estado}]")
        print(f"  Original       : {c}")
        print(f"  Texto limpio   : {limpiar_texto(c)}")
        print(f"  Palabras útiles: {r['tokens_utiles']}")
        print(f"  Claves         : {extraer_palabras_clave(c)}")
        print(f"  Eliminadas     : {r['palabras_eliminadas']}")
