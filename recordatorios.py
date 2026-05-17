# recordatorios.py
# =============================================
# RECORDATORIOS AUTOMÁTICOS
#
# Este script se puede ejecutar aparte o
# llamarse desde n8n a través del webhook.
#
# Envía mensajes al grupo cuando hay exámenes
# o tareas próximas sin que nadie lo active.
# =============================================

import asyncio
import logging
from datetime import date, timedelta
from telegram import Bot
from telegram.constants import ParseMode
import sheets
import formato as fmt
from config import BOT_TOKEN, GROUP_CHAT_ID

logger = logging.getLogger(__name__)


async def enviar_recordatorio_examenes():
    """
    Busca exámenes para mañana y envía un recordatorio al grupo.
    n8n llama a esta función a las 20:00 del día anterior.
    """
    if not GROUP_CHAT_ID:
        logger.warning("GROUP_CHAT_ID no configurado.")
        return

    manana   = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    examenes = [e for e in sheets.leer_examenes() if e["fecha"] == manana]

    if not examenes:
        logger.info("Sin exámenes mañana. No se envía recordatorio.")
        return

    bot = Bot(token=BOT_TOKEN)

    for examen in examenes:
        texto = fmt.formatear_recordatorio_examen(examen)
        try:
            await bot.send_message(
                chat_id    = GROUP_CHAT_ID,
                text       = texto,
                parse_mode = ParseMode.MARKDOWN
            )
            logger.info(f"✅ Recordatorio enviado: {examen['titulo']}")
        except Exception as e:
            logger.error(f"Error enviando recordatorio: {e}")


async def enviar_resumen_semanal():
    """
    Envía el resumen de la semana al grupo.
    n8n llama a esto los lunes a las 9:00.
    """
    if not GROUP_CHAT_ID:
        return

    hoy      = date.today()
    inicio   = hoy - timedelta(days=hoy.weekday())
    fin      = inicio + timedelta(days=6)
    inicio_s = inicio.strftime("%Y-%m-%d")
    fin_s    = fin.strftime("%Y-%m-%d")

    tareas   = [t for t in sheets.leer_tareas()  if inicio_s <= t["fecha"] <= fin_s]
    examenes = [e for e in sheets.leer_examenes() if inicio_s <= e["fecha"] <= fin_s]
    texto    = fmt.formatear_semana(tareas, examenes, inicio_s, fin_s)

    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.send_message(
            chat_id    = GROUP_CHAT_ID,
            text       = f"📅 *Resumen semanal — RafitaBOT*\n\n{texto}",
            parse_mode = ParseMode.MARKDOWN
        )
        logger.info("✅ Resumen semanal enviado.")
    except Exception as e:
        logger.error(f"Error enviando resumen semanal: {e}")


if __name__ == "__main__":
    asyncio.run(enviar_recordatorio_examenes())