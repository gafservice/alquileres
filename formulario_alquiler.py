import streamlit as st
from datetime import datetime
from pytz import timezone
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import time
from streamlit_js_eval import streamlit_js_eval

# --- Evaluación JS del navegador ---
navegador = streamlit_js_eval(
    js_expressions=[
        "navigator.userAgent",
        "screen.width",
        "screen.height",
        "navigator.language"
    ],
    key="registro_navegador"
)

# Detener si aún no se han recibido datos
if navegador is None:
    st.stop()

# Control: solo registrar si no se ha registrado o han pasado más de 30 minutos (1800 segundos)
if "ultima_visita" not in st.session_state or time.time() - st.session_state["ultima_visita"] > 1800:
    st.session_state["ultima_visita"] = time.time()
    st.session_state["visita_id"] = datetime.now().strftime("%H%M%S")

    # Extraer datos
    user_agent = navegador[0]
    resolucion = f"{navegador[1]}x{navegador[2]}"
    idioma = navegador[3]

    # Fecha y hora local
    cr_tz = timezone("America/Costa_Rica")
    hora_visita = datetime.now(cr_tz).strftime("%Y-%m-%d %H:%M:%S")

    # Mostrar datos (opcional)
    st.write("🕒 Fecha:", hora_visita)
    st.write("🧭 Navegador:", user_agent)
    st.write("📐 Resolución:", resolucion)
    st.write("🌐 Idioma:", idioma)

    try:
        # Conexión con Google Sheets
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials_dict = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"]["json_keyfile"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
        client = gspread.authorize(creds)
        hoja = client.open("registro_visitas").sheet1

        # Guardar fila
        hoja.append_row([hora_visita, user_agent, resolucion, idioma, st.session_state["visita_id"]])
        st.success("✅ Visita registrada correctamente.")
    except Exception as e:
        st.error("❌ Error al registrar la visita")
        st.exception(e)
else:
    st.info("⏱ Ya se registró una visita reciente. Esperá al menos 30 minutos para registrar otra.")
