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

# Vocabulario stemizado típico de tickets de soporte técnico
_STEMS_SOPORTE_IT = {
    "error", "fall", "sistem", "aplic", "program", "softwar", "servidor", "servici",
    "red", "wifi", "vpn", "correo", "outlook", "mail", "base", "dat", "sql",
    "consult", "usuari", "contraseñ", "contrasen", "acces", "sesion", "login",
    "impresor", "excel", "archiv", "window", "linux", "actualiz", "instal",
    "conex", "internet", "naveg", "pantall", "equip", "comput", "laptop",
    "monitor", "teclad", "raton", "backup", "respal", "licenci", "domini",
    "firewall", "dhcp", "dns", "router", "switch", "telefoni", "llam",
    "extension", "ora", "mongodb", "postgresql", "mysql", "tabl", "registr",
    "report", "modul", "factur", "nomina", "crm", "erp", "intranet", "portal",
    "autent", "token", "bloque", "caid", "lent", "lentitud", "memor", "disco",
    "antivirus", "ticket", "soport", "tecnic", "configur", "permis", "rol",
    "servidor", "host", "puert", "protocol", "ssl", "certific", "copi",
    "escan", "toner", "papel", "driver", "control", "version", "patch",
    # Periféricos y hardware frecuentes en tickets
    "mous", "comput", "tecl", "monitor", "pantall", "disc", "memori",
    "proces", "notebook", "laptop", "tablet", "celul", "telefon",
    "cabl", "puert", "usb", "hdmi", "bateri", "cargador", "ventil",
    "fuent", "rack", "ups", "bios", "raid", "ssd", "gpu", "cpu",
    "impresor", "escaner", "camer", "microfon", "auricular", "headset",
    "docking", "adaptador", "conector", "encend", "reinici", "apag",
    "detect", "reconoc", "congel",
    # Acciones IT comunes
    "instal", "desinstal", "actualiz", "configur", "restaur",
    "recuper", "migr", "sincroniz", "integr", "despleg", "ejecut",
    "export", "import", "descarg",
    # Verbos y sustantivos de acceso/sesión frecuentes en tickets cortos
    "ingres", "cuent", "conect", "inici", "acced", "entrar", "abrir",
    "clav", "pass", "login", "sesion", "equip", "disposit", "dat",
    "prend", "encend", "apag", "reinici", "colgars", "cuelg",
    "lent", "tarda", "demor", "bloque", "bloqu",
}

# Temas claramente ajenos a mesa de ayuda IT
_STEMS_FUERA_TEMA = {
    "histor", "bolivia", "peru", "argentin", "chile", "mexic", "geograf",
    "politic", "president", "guerr", "futbol", "deport", "recet", "cocin",
    "pelicul", "cine", "musical", "amor", "matrimon", "boda", "turism",
    "vacacion", "hotel", "literatur", "poem", "novel", "filosof", "religion",
    "univers", "matemat", "fisic", "quimic", "biolog", "animal", "plant",
}


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


def _stem_en_lexico(stem: str, lexico: set) -> bool:
    if stem in lexico:
        return True
    return any(
        stem.startswith(raiz) or raiz.startswith(stem)
        for raiz in lexico
        if len(stem) >= 4 and len(raiz) >= 4
    )


# Umbral mínimo de stems IT sobre el total de stems útiles
_UMBRAL_IT = 0.40


def es_contexto_soporte_tecnico(stems: list) -> tuple[bool, str]:
    """
    Rechaza textos que no describen un problema de soporte técnico.
    Regla: al menos el 40 % de los stems deben pertenecer al léxico IT.
    """
    if not stems:
        return False, "El texto no contiene términos de soporte técnico."

    total = len(stems)
    soporte = sum(1 for s in stems if _stem_en_lexico(s, _STEMS_SOPORTE_IT))
    fuera   = sum(1 for s in stems if _stem_en_lexico(s, _STEMS_FUERA_TEMA))
    pct_it  = soporte / total

    # Tema claramente ajeno (historia, política, cocina…) sin ningún término IT
    if fuera >= 1 and soporte == 0:
        return (
            False,
            "El texto no corresponde a un ticket de soporte técnico "
            "(parece un tema general, no relacionado con sistemas o TI).",
        )

    # Menos del 40 % de términos IT → texto demasiado genérico o fuera de contexto
    if pct_it < _UMBRAL_IT:
        pct_str = f"{pct_it:.0%}"
        return (
            False,
            f"Solo el {pct_str} de los términos son de soporte técnico (mínimo 40 %). "
            "Describe el problema técnico con más detalle: software, red, acceso, "
            "correo, base de datos, equipos, etc.",
        )

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

    ok_soporte, motivo_soporte = es_contexto_soporte_tecnico(detalle["stems"])
    if not ok_soporte:
        return False, motivo_soporte

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