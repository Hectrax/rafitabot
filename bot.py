# bot.py
# =============================================
# BOT DE TELEGRAM — SOLO LECTURA
#
# Este bot NO permite añadir tareas desde Telegram.
# Solo permite CONSULTAR las tareas y exámenes
# que están en Google Sheets.
#
# Las tareas se añaden desde la web (Lovable).
# n8n gestiona los recordatorios automáticos.
#
# Comandos disponibles:
# /start    → Menú principal con botones
# /tareas   → Ver tareas pendientes
# /examenes → Ver exámenes próximos
# /semana   → Vista semanal por días
# /ayuda    → Lista de comandos
# =============================================


# bot.py — primeras líneas
import os
from telegram.ext import ChatMemberHandler
from dotenv import load_dotenv

# Cargamos el .env con ruta absoluta para evitar problemas
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Verificación — debe imprimir el ID del Sheet, no None
print("DEBUG SHEETS_ID:", os.getenv("SHEETS_DOCUMENT_ID"))
print("DEBUG TOKEN:", os.getenv("BOT_TOKEN", "")[:20] + "...")

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    CallbackQueryHandler, ContextTypes,
)
from telegram.constants import ParseMode
from datetime import date, timedelta
import sheets
import formato as fmt
from config import BOT_TOKEN

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ── Texto del menú principal ──────────────────
TEXTO_MENU = (
    "📚 *RafitaBOT* — Agenda del grupo SMR\n\n"
    "Consulta las tareas y exámenes de la clase.\n"
    "_Las tareas se añaden desde el panel web._\n\n"
    "¿Qué quieres ver?"
)


# ══════════════════════════════════════════════
# TECLADOS
# ══════════════════════════════════════════════

def teclado_menu():
    """Menú principal con los 3 botones principales."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📋 Tareas",      callback_data="ver|tareas"),
            InlineKeyboardButton("📝 Exámenes",    callback_data="ver|examenes"),
        ],
        [
            InlineKeyboardButton("📅 Esta semana", callback_data="ver|semana"),
        ],
    ])


def teclado_volver():
    """Botón para volver al menú principal."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("↩️ Volver al menú", callback_data="ver|menu")]
    ])


# ══════════════════════════════════════════════
# COMANDOS
# ══════════════════════════════════════════════

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # DEBUG — borrar después
    print(f"DEBUG CHAT_ID: {update.effective_chat.id} | TIPO: {update.effective_chat.type}")
    
    # resto del código igual...
    """/start → Muestra el menú principal con botones."""
    await update.message.reply_text(
        TEXTO_MENU,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=teclado_menu()
    )


async def cmd_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/menu → Igual que /start."""
    await cmd_start(update, context)


async def cmd_tareas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tareas = sheets.leer_tareas()
    
    # DEBUG — borrar después
    print(f"DEBUG tareas recibidas: {tareas}")
    print(f"DEBUG cantidad: {len(tareas)}")
    
    texto = fmt.formatear_lista_tareas(tareas)
    await update.message.reply_text(
        texto,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=teclado_volver()
    )


async def cmd_examenes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/examenes → Muestra todos los exámenes próximos."""
    examenes = sheets.leer_examenes()
    texto    = fmt.formatear_lista_examenes(examenes)
    await update.message.reply_text(
        texto,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=teclado_volver()
    )


async def cmd_semana(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/semana → Vista semanal por días."""
    hoy     = date.today()
    inicio  = hoy - timedelta(days=hoy.weekday())
    fin     = inicio + timedelta(days=6)
    inicio_s = inicio.strftime("%Y-%m-%d")
    fin_s    = fin.strftime("%Y-%m-%d")

    tareas   = [t for t in sheets.leer_tareas()   if inicio_s <= t["fecha"] <= fin_s]
    examenes = [e for e in sheets.leer_examenes()  if inicio_s <= e["fecha"] <= fin_s]
    texto    = fmt.formatear_semana(tareas, examenes, inicio_s, fin_s)

    await update.message.reply_text(
        texto,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=teclado_volver()
    )


async def cmd_ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/ayuda → Lista de comandos disponibles."""
    texto = (
        "📚 *RafitaBOT — Ayuda*\n\n"
        "*Comandos disponibles:*\n"
        "• /tareas → Tareas pendientes\n"
        "• /examenes → Exámenes próximos\n"
        "• /semana → Vista de esta semana\n"
        "• /menu → Abrir menú principal\n\n"
        "*¿Cómo añadir tareas?*\n"
        "_Las tareas se añaden desde el panel web._\n"
        "_Pregunta al delegado si no tienes el enlace._"
    )
    await update.message.reply_text(texto, parse_mode=ParseMode.MARKDOWN)


# ══════════════════════════════════════════════
# CALLBACKS DE BOTONES
# ══════════════════════════════════════════════

async def callback_ver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Gestiona todos los botones inline del bot.
    Edita el mensaje existente para no acumular mensajes.
    """
    query  = update.callback_query
    await query.answer()
    accion = query.data.split("|")[1]

    if accion == "menu":
        await query.message.edit_text(
            TEXTO_MENU,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=teclado_menu()
        )

    elif accion == "tareas":
        tareas = sheets.leer_tareas()
        texto  = fmt.formatear_lista_tareas(tareas)
        await query.message.edit_text(
            texto,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=teclado_volver()
        )

    elif accion == "examenes":
        examenes = sheets.leer_examenes()
        texto    = fmt.formatear_lista_examenes(examenes)
        await query.message.edit_text(
            texto,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=teclado_volver()
        )

    elif accion == "semana":
        hoy     = date.today()
        inicio  = hoy - timedelta(days=hoy.weekday())
        fin     = inicio + timedelta(days=6)
        inicio_s = inicio.strftime("%Y-%m-%d")
        fin_s    = fin.strftime("%Y-%m-%d")

        tareas   = [t for t in sheets.leer_tareas()  if inicio_s <= t["fecha"] <= fin_s]
        examenes = [e for e in sheets.leer_examenes() if inicio_s <= e["fecha"] <= fin_s]
        texto    = fmt.formatear_semana(tareas, examenes, inicio_s, fin_s)

        await query.message.edit_text(
            texto,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=teclado_volver()
        )


# ══════════════════════════════════════════════
# MANEJO DE ERRORES
# ══════════════════════════════════════════════

async def manejar_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Captura errores inesperados para que el bot no se caiga."""
    logger.error(f"Error: {context.error}", exc_info=context.error)
    if update and update.message:
        await update.message.reply_text(
            "⚠️ Algo salió mal. Inténtalo de nuevo o usa /menu."
        )


# ══════════════════════════════════════════════
# ARRANQUE DEL BOT
# ══════════════════════════════════════════════
async def bienvenida_nuevo_miembro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Se activa cuando alguien nuevo entra al grupo.
    Le envía un mensaje privado explicando qué es RafitaBOT.
    Si no puede enviar en privado (usuario no ha hablado antes con el bot),
    lo saluda en el grupo brevemente.
    """
    resultado = update.chat_member
    miembro_nuevo = resultado.new_chat_member
    miembro_viejo = resultado.old_chat_member

    # Solo actuamos si alguien se UNIÓ (no si salió)
    if miembro_viejo.status == "left" and miembro_nuevo.status == "member":
        usuario    = miembro_nuevo.user
        nombre     = usuario.first_name

        mensaje_privado = (
            f"👋 ¡Hola, *{nombre}*! Bienvenido/a al grupo de clase.\n\n"
            f"Soy *RafitaBOT*, el asistente de la clase de 2º SMR 📚\n\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "*¿Qué puedo hacer?*\n\n"
            "📋 /tareas — Ver las tareas pendientes\n"
            "📝 /examenes — Ver los exámenes próximos\n"
            "📅 /semana — Vista semanal completa\n\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "*¿Cómo se añaden tareas?*\n\n"
            "Las tareas y exámenes se añaden desde el formulario web.\n"
            "Pídele el enlace al delegado/a.\n\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "_Los recordatorios llegan automáticamente al grupo.\n"
            "No necesitas hacer nada más_ ✅"
        )

        mensaje_grupo = (
            f"👋 ¡Bienvenido/a, *{nombre}*!\n"
            "_Te he enviado un mensaje privado con info sobre RafitaBOT._"
        )

        # Intentamos enviar en privado primero
        try:
            await context.bot.send_message(
                chat_id    = usuario.id,
                text       = mensaje_privado,
                parse_mode = ParseMode.MARKDOWN
            )
            # Si el privado funciona, avisamos en el grupo brevemente
            await context.bot.send_message(
                chat_id    = update.effective_chat.id,
                text       = mensaje_grupo,
                parse_mode = ParseMode.MARKDOWN
            )
        except Exception:
            # Si no puede enviar privado (usuario nunca habló con el bot)
            # mandamos el mensaje completo en el grupo
            await context.bot.send_message(
                chat_id    = update.effective_chat.id,
                text       = (
                    f"👋 ¡Bienvenido/a, *{nombre}*!\n\n"
                    "Soy *RafitaBOT*, el asistente de la clase 📚\n\n"
                    "📋 /tareas · 📝 /examenes · 📅 /semana"
                ),
                parse_mode = ParseMode.MARKDOWN
            )
            
def main():
    logger.info("🚀 Iniciando RafitaBOT...")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start",    cmd_start))
    app.add_handler(CommandHandler("menu",     cmd_menu))
    app.add_handler(CommandHandler("tareas",   cmd_tareas))
    app.add_handler(CommandHandler("examenes", cmd_examenes))
    app.add_handler(CommandHandler("semana",   cmd_semana))
    app.add_handler(CommandHandler("ayuda",    cmd_ayuda))
    # Handler de bienvenida — detecta cuando alguien entra al grupo
    app.add_handler(ChatMemberHandler(
    bienvenida_nuevo_miembro,
    ChatMemberHandler.CHAT_MEMBER
    ))
    # Botones inline
    app.add_handler(CallbackQueryHandler(callback_ver, pattern="^ver\\|"))

    app.add_error_handler(manejar_error)

    logger.info("✅ RafitaBOT listo. Escuchando mensajes...")
    app.run_polling(
    drop_pending_updates=True,
    allowed_updates=Update.ALL_TYPES
)


if __name__ == "__main__":
    main()