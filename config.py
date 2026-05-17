# config.py
# Carga todas las variables de configuración
# desde el archivo .env para que el token
# nunca aparezca directamente en el código.

import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN              = os.getenv("BOT_TOKEN", "")
GROUP_CHAT_ID          = int(os.getenv("GROUP_CHAT_ID", "0"))
SHEETS_DOCUMENT_ID     = os.getenv("SHEETS_DOCUMENT_ID", "")
SHEETS_CREDENTIALS_PATH= os.getenv("SHEETS_CREDENTIALS_PATH", "credentials.json")

# Nombres exactos de las hojas en Google Sheets
HOJA_TAREAS   = "TAREAS"
HOJA_EXAMENES = "EXAMENES"

# Asignaturas reales de 2º SMR con abreviatura, nombre completo y emoji
ASIGNATURAS = [
    {"abrev": "AW",   "nombre": "Aplicaciones Web",                          "emoji": "💻"},
    {"abrev": "ING",  "nombre": "Inglés Profesional",                        "emoji": "🇬🇧"},
    {"abrev": "SEG",  "nombre": "Seguridad Informática",                     "emoji": "🔐"},
    {"abrev": "SER",  "nombre": "Servicios en Red",                          "emoji": "🌐"},
    {"abrev": "SOR",  "nombre": "Sistemas Operativos en Red",                "emoji": "🖥"},
    {"abrev": "IPE",  "nombre": "Itinerario Personal para la Empleabilidad", "emoji": "📋"},
    {"abrev": "DIG",  "nombre": "Digitalización Aplicada",                   "emoji": "📱"},
    {"abrev": "SOS",  "nombre": "Sostenibilidad Aplicada",                   "emoji": "♻️"},
    {"abrev": "PI",   "nombre": "Proyecto Intermodular",                     "emoji": "🗂"},
    {"abrev": "FCT",  "nombre": "Formación en Empresas",                     "emoji": "🏢"},
]

# Diccionarios de acceso rápido para el bot
ASIGNATURAS_EMOJI  = {a["abrev"]: a["emoji"]  for a in ASIGNATURAS}
ASIGNATURAS_NOMBRE = {a["abrev"]: a["nombre"] for a in ASIGNATURAS}