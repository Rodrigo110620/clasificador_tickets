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
    ("batch_inferencia", "🚀 Batch Inferencia"),
    ("batch_entrenamiento", "🧪 Batch Entrenamiento"),
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

# Posibles soluciones por categoría
SOLUCIONES = {
    "Credenciales": (
        "• Revisar si la cuenta está bloqueada en Active Directory\n"
        "• Restablecer contraseña en AD\n"
        "• Verificar permisos de acceso a la aplicación\n"
        "• Limpiar caché de credenciales del navegador/aplicación\n"
        "• Confirmar que el usuario está en los grupos correctos"
    ),
    "Base de Datos": (
        "• Verificar estado de conexión a la BD (ping, telnet)\n"
        "• Revisar logs de errores (ORA-xxxx, deadlock, timeout)\n"
        "• Comprobar espacio disponible en disco\n"
        "• Validar credenciales de acceso a BD\n"
        "• Reiniciar servicio de BD si es necesario"
    ),
    "Infraestructura": (
        "• Revisar estado de servidores (CPU, memoria, disco)\n"
        "• Verificar conectividad de red\n"
        "• Comprobar puertos abiertos y firewalls\n"
        "• Revisar registros de eventos del sistema\n"
        "• Reiniciar servicios críticos"
    ),
    "Bug de Software": (
        "• Verificar versión actual de la aplicación\n"
        "• Revisar logs de la aplicación\n"
        "• Buscar actualizaciones/parches disponibles\n"
        "• Limpiar caché y datos temporales\n"
        "• Reportar a desarrolladores con detalles del error"
    ),
    "Telefonía": (
        "• Verificar que el equipo de telefonía está encendido\n"
        "• Comprobar conexión de red del dispositivo\n"
        "• Reiniciar centralita o adaptador telefónico\n"
        "• Revisar configuración de extensión\n"
        "• Contactar con proveedor de telefonía si persiste"
    ),
    "Excel": (
        "• Verificar que el archivo no está corrompido\n"
        "• Guardar como .xlsx (formato actual)\n"
        "• Comprobar límites de celdas/filas (máx. 1M)\n"
        "• Limpiar formato excesivo o referencias circulares\n"
        "• Actualizaciones de Microsoft Office"
    ),
    "Hardware": (
        "• Verificar conexiones físicas (cables, puertos)\n"
        "• Revisar estado en Administrador de dispositivos\n"
        "• Ejecutar diagnósticos de hardware\n"
        "• Actualizar drivers del dispositivo\n"
        "• Reemplazar hardware si no funciona"
    ),
    "Correo": (
        "• Verificar credenciales de acceso al buzón\n"
        "• Revisar almacenamiento disponible\n"
        "• Comprobar configuración de sincronización\n"
        "• Limpiar caché de correo\n"
        "• Contactar a equipo de correo para análisis de logs"
    ),
    "VPN": (
        "• Verificar conexión a internet\n"
        "• Revisar estado del cliente VPN\n"
        "• Comprobar certificados de VPN (no expirados)\n"
        "• Reiniciar cliente VPN\n"
        "• Validar permisos de acceso VPN en servidor"
    ),
    "Impresoras": (
        "• Verificar que la impresora está encendida y conectada\n"
        "• Revisar cola de impresión\n"
        "• Limpiar papel atascado\n"
        "• Instalar/actualizar drivers de impresora\n"
        "• Reiniciar servicio de spooler"
    ),
    "Sistema Operativo": (
        "• Verificar actualizaciones del SO pendientes\n"
        "• Revisar espacio en disco disponible\n"
        "• Ejecutar escaneo de malware/antivirus\n"
        "• Comprobar logs del Visor de eventos\n"
        "• Realizar reinicio del sistema"
    ),
    "Redes IP": (
        "• Verificar configuración de IP (ipconfig/ifconfig)\n"
        "• Comprobar conectividad con ping/tracert\n"
        "• Revisar puerta de enlace y DNS\n"
        "• Renovar DHCP o asignar IP estática\n"
        "• Contactar equipo de redes"
    ),
    "Otros": (
        "• Revisar detalles específicos del problema\n"
        "• Consultar documentación disponible\n"
        "• Contactar a equipo especializado\n"
        "• Proporcionar logs o capturas de pantalla\n"
        "• Escalación a nivel superior si es necesario"
    ),
}