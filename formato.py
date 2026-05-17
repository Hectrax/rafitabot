# formato.py
# =============================================
# FUNCIONES DE FORMATO DE MENSAJES
#
# Convierte los datos de Sheets en mensajes
# bonitos y legibles para Telegram.
# Usa Markdown para negritas, cursivas, etc.
# =============================================

from datetime import datetime, date, timedelta
from collections import defaultdict
from config import ASIGNATURAS_EMOJI

MESES = {
    "01": "enero",    "02": "febrero",  "03": "marzo",
    "04": "abril",    "05": "mayo",     "06": "junio",
    "07": "julio",    "08": "agosto",   "09": "septiembre",
    "10": "octubre",  "11": "noviembre","12": "diciembre",
}

DIAS_SEMANA = [
    "Lunes", "Martes", "Miércoles",
    "Jueves", "Viernes", "Sábado", "Domingo"
]


def formatear_fecha(fecha_str):
    """'2025-06-10' → '10 de junio de 2025'"""
    try:
        p = fecha_str.split("-")
        return f"{p[2].lstrip('0')} de {MESES.get(p[1], p[1])} de {p[0]}"
    except Exception:
        return fecha_str


def dias_restantes(fecha_str):
    """
    Devuelve texto visual de urgencia.
    Ejemplos: 🔥 ¡HOY!, ⚠️ Mañana, ⏰ En 2 días, 📅 En 7 días
    """
    try:
        diff = (datetime.strptime(fecha_str, "%Y-%m-%d").date() - date.today()).days
        if diff < 0:  return f"⛔ Hace {abs(diff)}d"
        if diff == 0: return "🔥 ¡HOY!"
        if diff == 1: return "⚠️ Mañana"
        if diff <= 3: return f"⏰ En {diff} días"
        if diff <= 7: return f"📅 En {diff} días"
        return        f"🗓 En {diff} días"
    except Exception:
        return ""


def emoji_asignatura(asig):
    """Devuelve el emoji de una asignatura por su abreviatura."""
    return ASIGNATURAS_EMOJI.get(asig.upper(), "📌")


def emoji_prioridad(prioridad):
    """Devuelve emoji según la prioridad de la tarea."""
    p = prioridad.lower()
    if p == "alta":   return "🔴"
    if p == "normal": return "🟡"
    return "🔵"


# ══════════════════════════════════════════════
# FORMATO DE ELEMENTOS INDIVIDUALES
# ══════════════════════════════════════════════

def formatear_tarea(tarea):
    """Formatea una tarea en 2 líneas visuales para listas."""
    emoji_p = emoji_prioridad(tarea.get("prioridad", "normal"))
    emoji_a = emoji_asignatura(tarea.get("asignatura", ""))
    tiempo  = dias_restantes(tarea.get("fecha", ""))
    fecha_b = formatear_fecha(tarea.get("fecha", ""))
    asig    = tarea.get("asignatura", "—")

    linea1 = f"{emoji_p} *{tarea['titulo']}*"
    linea2 = f"┗ {emoji_a} {asig}  ·  {fecha_b}  {tiempo}"

    if tarea.get("descripcion", "").strip():
        linea2 += f"\n   ↳ _{tarea['descripcion']}_"

    return f"{linea1}\n{linea2}"


def formatear_examen(examen):
    """Formatea un examen con todos sus detalles."""
    emoji_a = emoji_asignatura(examen.get("asignatura", ""))
    tiempo  = dias_restantes(examen.get("fecha", ""))
    fecha_b = formatear_fecha(examen.get("fecha", ""))
    asig    = examen.get("asignatura", "—")

    linea1 = f"📝 *{examen['titulo']}*"
    linea2 = f"┗ {emoji_a} {asig}  ·  {fecha_b}  {tiempo}"

    if examen.get("temas", "").strip():
        linea2 += f"\n   📖 _{examen['temas']}_"
    if examen.get("aula", "").strip():
        linea2 += f"\n   🚪 Aula: {examen['aula']}"

    return f"{linea1}\n{linea2}"


# ══════════════════════════════════════════════
# FORMATO DE LISTAS COMPLETAS
# ══════════════════════════════════════════════

def formatear_lista_tareas(tareas, titulo="📋 Tareas pendientes"):
    """Lista completa de tareas con cabecera y total."""
    if not tareas:
        return (
            f"*{titulo}*\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "📭 No hay tareas pendientes.\n\n"
            "_¡El grupo está al día!_ 🎉"
        )
    lineas = [f"*{titulo}*", "━━━━━━━━━━━━━━━━━━━", ""]
    for t in tareas:
        lineas.append(formatear_tarea(t))
        lineas.append("")
    lineas += [
        "━━━━━━━━━━━━━━━━━━━",
        f"_{len(tareas)} tarea(s) pendiente(s)_",
        "_Las tareas se añaden desde el panel web_"
    ]
    return "\n".join(lineas)


def formatear_lista_examenes(examenes, titulo="📝 Exámenes próximos"):
    """Lista completa de exámenes."""
    if not examenes:
        return (
            f"*{titulo}*\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "📭 No hay exámenes próximos."
        )
    lineas = [f"*{titulo}*", "━━━━━━━━━━━━━━━━━━━", ""]
    for e in examenes:
        lineas.append(formatear_examen(e))
        lineas.append("")
    lineas += [
        "━━━━━━━━━━━━━━━━━━━",
        f"_{len(examenes)} examen(es) próximo(s)_"
    ]
    return "\n".join(lineas)


def formatear_semana(tareas, examenes, inicio_str, fin_str):
    """
    Vista semanal con tareas y exámenes separados por día.
    Solo muestra días con actividad + hoy y mañana siempre.
    """
    hoy    = date.today()
    inicio = datetime.strptime(inicio_str, "%Y-%m-%d").date()
    fin    = datetime.strptime(fin_str,    "%Y-%m-%d").date()

    por_fecha = defaultdict(list)
    for t in tareas:
        por_fecha[t["fecha"]].append(("tarea", t))
    for e in examenes:
        por_fecha[e["fecha"]].append(("examen", e))

    lineas = ["*📅 Esta semana*", "━━━━━━━━━━━━━━━━━━━", ""]

    fecha_actual = inicio
    hay_algo     = False

    while fecha_actual <= fin:
        fecha_str   = fecha_actual.strftime("%Y-%m-%d")
        dia_nombre  = DIAS_SEMANA[fecha_actual.weekday()]
        fecha_b     = formatear_fecha(fecha_str)
        diff        = (fecha_actual - hoy).days
        actividades = por_fecha.get(fecha_str, [])

        if actividades or diff in [0, 1]:
            hay_algo = True
            if diff == 0:
                lineas.append(f"📌 *{dia_nombre}, {fecha_b}*  🔥 _Hoy_")
            elif diff == 1:
                lineas.append(f"📌 *{dia_nombre}, {fecha_b}*  ⚠️ _Mañana_")
            else:
                lineas.append(f"📌 *{dia_nombre}, {fecha_b}*")

            lineas.append("──────────────")

            if actividades:
                for tipo, item in actividades:
                    if tipo == "tarea":
                        lineas.append(formatear_tarea(item))
                    else:
                        lineas.append(formatear_examen(item))
                    lineas.append("")
            else:
                lineas.append("_Sin actividades_ ✓")
                lineas.append("")

        fecha_actual += timedelta(days=1)

    if not hay_algo:
        lineas.append("_¡Semana tranquila! Sin actividades._ 🎉")

    total = len(tareas) + len(examenes)
    lineas.append("━━━━━━━━━━━━━━━━━━━")
    if total > 0:
        lineas.append(f"_{len(tareas)} tarea(s) · {len(examenes)} examen(es) esta semana_")

    return "\n".join(lineas)


def formatear_recordatorio_examen(examen):
    """
    Formato especial para el recordatorio de examen próximo.
    Más llamativo que el formato de lista normal.
    """
    emoji_a = emoji_asignatura(examen.get("asignatura", ""))
    fecha_b = formatear_fecha(examen.get("fecha", ""))

    lineas = [
        "🚨 *¡RECORDATORIO DE EXAMEN!*",
        "━━━━━━━━━━━━━━━━━━━",
        f"📝 *{examen['titulo']}*",
        f"{emoji_a} Asignatura: *{examen.get('asignatura', '—')}*",
        f"📅 Fecha: *{fecha_b}*  ⚠️ *¡MAÑANA!*",
    ]

    if examen.get("temas", "").strip():
        lineas.append(f"📖 Temas: _{examen['temas']}_")
    if examen.get("aula", "").strip():
        lineas.append(f"🚪 Aula: *{examen['aula']}*")

    lineas += [
        "━━━━━━━━━━━━━━━━━━━",
        "_¡Mucho ánimo! 💪_"
    ]
    return "\n".join(lineas)