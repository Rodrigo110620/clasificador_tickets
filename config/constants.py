TEXTO_EJEMPLO = (
    "No puedo conectarme al WiFi de la oficina, me aparece que la contraseña es incorrecta."
)
RUTA_DATASET = "dataset/tickets.csv"
RUTA_MODELO = "models/mejor_modelo.pkl.gz"
RUTA_MEMORIA = "models/memoria.json"

# Clasificación (umbral adaptativo según cantidad de categorías)
UMBRAL_CONFIANZA_MIN = 0.25   # subido de 0.18 → pide mínimo 25% de confianza
UMBRAL_MARGEN_SEGUNDA = 0.15  # subido de 0.05 → exige 15% de margen real entre top-1 y top-2
CATEGORIA_DESCONOCIDA = "Otros"
MENSAJE_CATEGORIA_DESCONOCIDA = (
    "Confianza baja o resultado ambiguo — requiere revisión manual"
)

# Umbral visual: no mostrar categorías con menos de este % en el gráfico
UMBRAL_VISUAL_PROB = 0.05


def umbral_confiancia_dinamico(n_categorias: int) -> float:
    """Mínimo razonable para N clases (con 12 clases ≈ 25%)."""
    if n_categorias <= 1:
        return 0.5
    return max(UMBRAL_CONFIANZA_MIN, 2.5 / n_categorias)


def es_clasificacion_ambigua(probabilidades_ordenadas: list) -> tuple[bool, float, float]:
    """
    Desconocido si la probabilidad máxima es muy baja o casi empata con la segunda.
    Retorna (es_ambiguo, p_top, margen_sobre_segunda).
    """
    if not probabilidades_ordenadas:
        return True, 0.0, 0.0
    n = len(probabilidades_ordenadas)
    p_top = float(probabilidades_ordenadas[0][1])
    p_second = float(probabilidades_ordenadas[1][1]) if n > 1 else 0.0
    margen = p_top - p_second
    umbral = umbral_confiancia_dinamico(n)
    ambiguo = p_top < umbral or (n > 1 and margen < UMBRAL_MARGEN_SEGUNDA)
    return ambiguo, p_top, margen

# Entrenamiento
MIN_EJEMPLOS_POR_CATEGORIA = 20

MENU_OPCIONES = [
    ("inicio", "🏠 Inicio"),
    ("clasificar", "🎫 Clasificar Ticket"),
    ("historial", "📋 Historial"),
    ("metricas", "📊 Métricas"),
    ("comparacion", "⚖️ Comparación de Modelos"),
    ("info", "ℹ️ Información del Proyecto"),
]

ICONOS = {
    "Credenciales": "🔐",
    "Base de Datos": "🗄️",
    "Infraestructura": "📡",
    "Bug de Software": "🐛",
    "Telefonía": "📞",
    "Excel": "📊",
    "Hardware": "🖥️",
    "Correo": "📧",
    "VPN": "🔒",
    "Impresoras": "🖨️",
    "Sistema Operativo": "💻",
    "Redes IP": "🌐",
    "Otros": "❓",
}


def icono_categoria(categoria: str) -> str:
    return ICONOS.get(categoria, "📂")

PRIORIDAD = {
    "Credenciales": ("Alta", "badge-alta"),
    "Infraestructura": ("Alta", "badge-alta"),
    "Base de Datos": ("Media", "badge-media"),
    "Bug de Software": ("Media", "badge-media"),
    "Otros": ("Media", "badge-media"),
}