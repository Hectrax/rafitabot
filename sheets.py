# sheets.py

import logging
import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

logger = logging.getLogger(__name__)

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

# ID hardcodeado temporalmente hasta que .env funcione
SHEET_ID        = "1OFMaCMIYSwP4SK5TzU74-ywoixGI74J-Wx4mZlKGtgg"
HOJA_TAREAS     = "TAREAS"
HOJA_EXAMENES   = "EXAMENES"
CREDENTIALS_PATH = "credentials.json"


def _obtener_cliente():
    """
    Crea cliente autenticado de Google Sheets.
    En Railway usa variable de entorno GOOGLE_CREDENTIALS_JSON.
    En local usa el archivo credentials.json.
    """
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")

    if creds_json:
        info  = json.loads(creds_json)
        creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    else:
        creds = Credentials.from_service_account_file(
            CREDENTIALS_PATH, scopes=SCOPES
        )
    return gspread.authorize(creds)


def normalizar_fecha(fecha_str):
    """
    Convierte cualquier formato de fecha a YYYY-MM-DD.
    Acepta: DD/MM/YYYY, YYYY-MM-DD, YYYY/MM/DD, DD-MM-YYYY
    """
    if not fecha_str or str(fecha_str).strip() == "":
        return ""

    fecha_str = str(fecha_str).strip()

    if len(fecha_str) == 10 and fecha_str[4] == "-":
        return fecha_str

    formatos = [
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%m/%d/%Y",
    ]

    for fmt in formatos:
        try:
            return datetime.strptime(fecha_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    logger.warning(f"No se pudo normalizar la fecha: {fecha_str}")
    return fecha_str


def leer_tareas(solo_pendientes=True):
    """
    Lee las tareas pendientes de Google Sheets.
    """
    try:
        cliente = _obtener_cliente()
        doc     = cliente.open_by_key(SHEET_ID)
        hoja    = doc.worksheet(HOJA_TAREAS)
        filas   = hoja.get_all_records()

        logger.info(f"Filas brutas leídas de TAREAS: {len(filas)}")

        tareas = []
        for fila in filas:
            titulo = str(fila.get("titulo", "")).strip()
            if not titulo:
                continue

            estado = str(fila.get("estado", "pendiente")).strip().lower()
            if solo_pendientes and estado != "pendiente":
                continue

            tareas.append({
                "id":          str(fila.get("id_tarea", "")).strip(),
                "titulo":      titulo,
                "descripcion": str(fila.get("descripcion", "")).strip(),
                "fecha":       normalizar_fecha(fila.get("fecha_entrega", "")),
                "asignatura":  str(fila.get("asignatura", "")).strip(),
                "prioridad":   str(fila.get("prioridad", "normal")).strip().lower(),
                "tipo":        str(fila.get("tipo", "tarea")).strip() or "tarea",
                "estado":      estado,
            })

        logger.info(f"✅ Leídas {len(tareas)} tarea(s) pendiente(s)")
        return tareas

    except Exception as e:
        logger.error(f"❌ Error leyendo tareas: {e}")
        return []


def leer_examenes(solo_pendientes=True):
    """
    Lee los exámenes pendientes de Google Sheets.
    """
    try:
        cliente = _obtener_cliente()
        doc     = cliente.open_by_key(SHEET_ID)
        hoja    = doc.worksheet(HOJA_EXAMENES)
        filas   = hoja.get_all_records()

        logger.info(f"Filas brutas leídas de EXAMENES: {len(filas)}")

        examenes = []
        for fila in filas:
            titulo = str(fila.get("titulo", "")).strip()
            if not titulo:
                continue

            estado = str(fila.get("estado", "pendiente")).strip().lower()
            if solo_pendientes and estado != "pendiente":
                continue

            examenes.append({
                "id":          str(fila.get("id_examen", "")).strip(),
                "titulo":      titulo,
                "descripcion": str(fila.get("descripcion", "")).strip(),
                "fecha":       normalizar_fecha(fila.get("fecha_examen", "")),
                "asignatura":  str(fila.get("asignatura", "")).strip(),
                "temas":       str(fila.get("temas", "")).strip(),
                "aula":        str(fila.get("aula", "")).strip(),
                "estado":      estado,
            })

        logger.info(f"✅ Leídos {len(examenes)} examen(es) pendiente(s)")
        return examenes

    except Exception as e:
        logger.error(f"❌ Error leyendo exámenes: {e}")
        return []