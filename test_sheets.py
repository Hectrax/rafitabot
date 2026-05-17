# test_sheets.py
# Script de diagnóstico — borrar después de probar

import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

ID_SHEET = "1OFMaCMIYSwP4SK5TzU74-ywoixGI74J-Wx4mZlKGtgg"

print("1. Cargando credenciales...")
try:
    creds   = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    cliente = gspread.authorize(creds)
    print("   ✅ Credenciales OK")
except Exception as e:
    print(f"   ❌ Error credenciales: {e}")
    exit()

print("2. Abriendo Google Sheet...")
try:
    doc = cliente.open_by_key(ID_SHEET)
    print("   ✅ Sheet encontrado")
except Exception as e:
    print(f"   ❌ Error abriendo Sheet: {e}")
    print("   → Comparte el Sheet con el client_email del credentials.json")
    exit()

print("3. Hojas disponibles:")
for hoja in doc.worksheets():
    print(f"   - {hoja.title}")

print("4. Leyendo filas de TAREAS...")
try:
    hoja   = doc.worksheet("TAREAS")
    filas  = hoja.get_all_records()
    print(f"   ✅ {len(filas)} fila(s) encontrada(s)")
    if filas:
        print(f"   Primera fila: {filas[0]}")
except Exception as e:
    print(f"   ❌ Error: {e}")