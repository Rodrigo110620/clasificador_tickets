TEXTO_EJEMPLO = (
    "No puedo conectarme al WiFi de la oficina, me aparece que la contraseña es incorrecta."
)
RUTA_DATASET = "dataset/tickets.csv"
RUTA_MODELO = "models/mejor_modelo.pkl.gz"
RUTA_MEMORIA = "models/memoria.json"

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
}

PRIORIDAD = {
    "Credenciales": ("Alta", "badge-alta"),
    "Infraestructura": ("Alta", "badge-alta"),
    "Base de Datos": ("Media", "badge-media"),
    "Bug de Software": ("Media", "badge-media"),
}
