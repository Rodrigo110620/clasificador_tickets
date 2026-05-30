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
    # Errores, fallos, anomalías
    "error", "fall", "fallo", "falla", "bug", "excepcion", "crash", "tild", "colg", "cuelg",
    "lent", "lentitud", "tarda", "demor", "bloque", "bloqu", "caid", "caida", "caido",
    "incorrect", "incorrecto", "invalid", "invalido", "fail", "failure", "problema", "problemas",
    "issue", "issues", "glitch", "panic", "kernel", "bsod", "pantalla azul", "stop", "exception",
    "timeout", "deadlock", "corrupt", "corrupto", "roto", "rota", "roto", "dañado", "dañada",
    "mal funcion", "mal funcionamiento", "no funciona", "no and", "no march", "no responde",
    "congel", "congelado", "colgado", "tildado", "lento", "lentitud", "demora", "tarda mucho",
    "reinici", "reinicio", "apag", "apagar", "apagado", "encend", "encender", "prend", "prender",
    "arranc", "inici", "inicio", "boot", "arranque", "bucle", "loop", "infinito", "reinicia solo",

    # Sistemas, aplicaciones, software
    "sistem", "aplic", "aplicacion", "program", "softwar", "software", "app", "apps", "herramient",
    "util", "utilidad", "modul", "modulo", "component", "componente", "servici", "servicio",
    "proceso", "proces", "ejecut", "ejecucion", "lanz", "lanzar", "inicializ", "inicializar",
    "actualiz", "actualizacion", "parche", "patch", "update", "upgrade", "mejora", "optimiz",
    "configur", "configuracion", "parametro", "instal", "instalacion", "desinstal", "desinstalacion",
    "migr", "migracion", "integracion", "despliegue", "versión", "compatible", "compatibilidad",
    "driver", "controlador", "firmware", "bios", "uefi", "plugin", "complemento", "extension",
    "macro", "vba", "script", "batch", "autom", "automatizacion", "api", "webservice", "endpoint",
    "backend", "frontend", "cliente", "servidor", "host", "cloud", "nube", "virtual", "docker",
    "vm", "virtualizacion", "contenedor", "kubernetes", "orquest", "cluster",

    # Hardware y periféricos (MUY ampliado)
    "equip", "equipo", "comput", "computador", "pc", "laptop", "notebook", "netbook", "tablet",
    "ipad", "celul", "celular", "smartphone", "telefon", "telefono", "monitor", "pantall", "pantalla",
    "display", "touch", "tactil", "táctil", "teclad", "teclado", "raton", "mouse", "mous", "trackpad",
    "impresor", "impresora", "escaner", "scanner", "cam", "camara", "webcam", "microfon", "microfono",
    "auricular", "headset", "parlante", "altavoz", "disco", "ssd", "hdd", "nvme", "memori", "memoria",
    "ram", "procesador", "cpu", "gpu", "tarjet", "tarjeta", "placa", "motherboard", "raid", "ups",
    "fuente", "bateri", "bateria", "cargador", "ventil", "ventilador", "docking", "adaptador",
    "conector", "cabl", "cable", "puert", "puerto", "usb", "hdmi", "vga", "displayport", "thunderbolt",
    "ethernet", "conect", "enchuf", "detect", "detectar", "reconoc", "reconocer", "congel", "congelar",
    "tild", "colgado", "calient", "caliente", "temperatura", "sobrecalient", "ruido", "ventilador",
    "led", "luz", "parpade", "parpadea", "enciende", "apaga", "reinicia", "bios", "cmos", "pila",
    "disipador", "pasta termica", "carcasa", "chasis", "rack", "gabinete", "torre", "mini pc",
    "workstation", "estacion trabajo", "servidor", "nas", "san", "almacenamiento", "disco duro",
    "disco externo", "pendrive", "usb", "memoria usb", "lector", "huella", "biometrico", "dactilar",

    # Redes y conectividad (ampliado)
    "red", "wifi", "wireless", "lan", "wan", "vlan", "vpn", "ip", "tcp", "udp", "icmp", "dns", "dhcp",
    "gateway", "router", "switch", "firewall", "proxy", "balanceador", "ap", "access point", "accesspoint",
    "conex", "conexion", "conectividad", "enlace", "ping", "latencia", "paquete", "paquetes", "perdid",
    "perdida", "caida", "caido", "flapping", "bucle", "broadcast", "subred", "mascara", "máscara", "cidr",
    "nat", "pat", "tunel", "túnel", "ipsec", "ssl", "tls", "certific", "certificado", "ssl/tls",
    "radius", "ldap", "active directory", "dominio", "controlador dominio", "dc", "dns", "forward",
    "reverse", "ptr", "registro", "resolucion", "falla dns", "no resuelve", "dhcp", "asignacion ip",
    "ip fija", "ip dinamica", "pool", "rango", "mascara", "gateway", "route", "tabla enrutamiento",
    "vlan", "trunk", "access", "puerto switch", "uplink", "sfp", "fibra optica", "enlace", "mpls",
    "bw", "ancho banda", "congestion", "qos", "calidad servicio", "jitter", "perdida paquete",

    # Correo y mensajería
    "correo", "email", "mail", "outlook", "gmail", "exchange", "buzon", "bandeja", "mensaj", "mensaje",
    "adjunt", "adjunto", "spam", "filtro", "regla", "firma", "calendario", "contacto", "sincroniz",
    "sincronizar", "pop", "imap", "smtp", "send", "receive", "enviar", "recibir", "rebot", "bounce",
    "entrega", "entregado", "no entregado", "cuota", "tamaño", "adjunto grande", "archivo adjunto",
    "phishing", "virus", "malware", "antivirus", "cuarentena", "correo no deseado", "bandeja spam",

    # Bases de datos
    "base", "dat", "dato", "bd", "database", "sql", "mysql", "postgresql", "mongodb", "oracle", "sqlite",
    "tabl", "tabla", "registr", "registro", "consulta", "query", "select", "insert", "update", "delete",
    "procedimiento", "store", "stored procedure", "indice", "deadlock", "timeout", "pool", "transaccion",
    "backup", "respaldo", "restaur", "restore", "recuper", "migracion", "replica", "log", "logfile",
    "dump", "export", "import", "cargar", "descargar", "ejecutar", "optimizar", "analizar", "vacuum",
    "cluster", "shard", "replicaset", "failover", "ha", "alta disponibilidad", "concurrencia", "lock",

    # Credenciales y acceso (ampliado)
    "usuari", "usuario", "cuent", "cuenta", "login", "log in", "iniciar sesion", "acced", "acceso",
    "entrar", "ingres", "clav", "clave", "contraseñ", "contrasena", "password", "pass", "pin", "token",
    "autent", "autenticacion", "autoriz", "permis", "permiso", "rol", "privilegi", "bloqueo", "desbloqu",
    "desbloquear", "reset", "restablecer", "cambiar", "recuperar", "olvid", "olvide", "doble factor",
    "2fa", "mfa", "multi factor", "sms", "codigo", "verificacion", "validar", "expir", "vencido",
    "caduc", "inactivo", "desactivado", "suspendido", "baja", "alta", "crear", "eliminar", "modificar",

    # Telefonía
    "telefoni", "telefonia", "llam", "llamada", "extension", "centralita", "pbx", "voip", "sip", "troncal",
    "conferencia", "buzon", "voz", "fax", "virtual", "ip phone", "softphone", "codec", "audio", "eco",
    "ruido", "corte", "se corta", "no se oye", "no hay tono", "marcar", "discar", "recib", "entrante",
    "saliente", "transferir", "desviar", "captura", "grupo", "anexo", "interno", "externo", "larga distancia",

    # Excel y ofimática (muy ampliado)
    "excel", "hoja", "celda", "libro", "macro", "vba", "grafico", "formula", "funcion", "buscarv",
    "filtro", "ordenar", "export", "importar", "csv", "pdf", "word", "powerpoint", "office", "sharepoint",
    "onedrive", "drive", "documento", "archivo", "formato", "compatible", "abrir", "guardar", "cerrar",
    "calculo", "total", "suma", "promedio", "contar", "max", "min", "tabla dinamica", "segmentacion",
    "conexion", "origen datos", "actualizar", "refrescar", "vincular", "vínculo", "rotura", "error",

    # Sistemas operativos (ampliado)
    "window", "windows", "linux", "ubuntu", "centos", "debian", "redhat", "fedora", "mac", "macos",
    "ios", "android", "actualiz", "parche", "update", "service pack", "driver", "controlador", "firmware",
    "uefi", "boot", "arranque", "kernel", "evento", "explorador", "archivo", "carpeta", "dominio",
    "grupo", "politica", "gpo", "registro", "regedit", "cmd", "powershell", "terminal", "consola",
    "shell", "bash", "script", "batch", "ejecutar", "permiso", "admin", "administrador", "usuario",
    "cuenta", "sesion", "cierre", "logoff", "shutdown", "reinicio", "apagado", "hibernate", "suspender",

    # Impresoras
    "impresor", "imprimir", "impresion", "cola", "spooler", "toner", "cartucho", "tinta", "papel",
    "atasc", "atascado", "escane", "escanear", "multifuncional", "compartida", "driver", "red", "usb",
    "wifi", "ethernet", "ip", "puerto", "trabajo", "documento", "calidad", "borroso", "mancha",
    "raya", "blanco", "negro", "color", "no imprime", "no escanea", "no enciende", "error", "alarma",

    # Términos generales de TI y verbos (adicionales)
    "soporte", "tecnico", "tecnologia", "informatico", "it", "tic", "infraestructura", "monitoreo",
    "alerta", "performance", "rendimiento", "capacidad", "recurso", "consumo", "cpu", "memoria", "disco",
    "red", "ancho banda", "latencia", "tiempo respuesta", "log", "registro", "evento", "trace", "debug",
    "diagnostico", "solucion", "troubleshooting", "analisis", "revision", "verificacion", "prueba",
    "test", "validacion", "aceptacion", "implementacion", "puesta marcha", "produccion", "desarrollo",
    "qa", "calidad", "seguridad", "vulnerabilidad", "parche", "actualizacion", "backup", "restore",
    "recuperacion", "desastre", "drp", "bcm", "continuidad", "copi", "seguridad", "cifrado", "encriptar",
    "ssl", "tls", "https", "certificado", "firewall", "ids", "ips", "antivirus", "malware", "ransomware",
    "phishing", "spam", "virus", "troyano", "rootkit", "exploit", "zero day", "parche", "actualizacion",

    # Verbos y acciones clave
    "instalar", "configurar", "actualizar", "reiniciar", "apagar", "encender", "conectar", "desconectar",
    "abrir", "cerrar", "guardar", "descargar", "subir", "copiar", "pegar", "eliminar", "mover", "renombrar",
    "buscar", "encontrar", "solucionar", "arreglar", "corregir", "reparar", "diagnosticar", "verificar",
    "validar", "probar", "testear", "analizar", "revisar", "chequear", "controlar", "monitorear", "alertar",
    "notificar", "reportar", "registrar", "loggear", "trazar", "depurar", "debuggear", "ejecutar", "lanzar",
    "detener", "parar", "pausar", "reanudar", "cancelar", "deshacer", "rehacer", "revertir", "retroceder",

    # Interfaz de usuario y frontend
    "interfaz", "vent", "ventas", "ventana", "dialogo", "formulario", "campo", "input", "boton", "click",
    "clic", "seleccion", "checkbox", "radio", "dropdown", "lista", "tabla", "grilla", "reporte", "dashboard",
    "filtro", "ordenamiento", "busqueda", "resultado", "mostrar", "ocultar", "refrescar", "recargar",
    "cargar", "procesar", "validacion", "regla", "rango", "fecha", "numero", "texto", "archivo", "imagen",
    "json", "xml", "api", "webservice", "endpoint", "backend", "frontend", "cliente", "servidor", "base",
    "datos", "consulta", "sql", "navegador", "browser", "chrome", "firefox", "edge", "safari", "caché",
    "cache", "cookie", "sesion", "localstorage", "sessionstorage", "dom", "html", "css", "javascript",
    "react", "angular", "vue", "node", "python", "java", "c#", ".net", "php", "ruby", "go", "rust",
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