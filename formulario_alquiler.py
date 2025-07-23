import streamlit as st
from datetime import datetime
from pytz import timezone
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from streamlit_js_eval import streamlit_js_eval

# Leer información del navegador
navegador = streamlit_js_eval(
    js_expressions=[
        "navigator.userAgent",
        "screen.width",
        "screen.height",
        "navigator.language"
    ],
    key="registro_navegador"
)

if navegador is None:
    st.stop()

# Crear un hash único para identificar al navegador (se puede usar solo user_agent también)
user_agent = navegador[0]
resolucion = f"{navegador[1]}x{navegador[2]}"
idioma = navegador[3]

# Usar user_agent como ID de visitante
visitante_id = user_agent

# Obtener hora local
cr_tz = timezone("America/Costa_Rica")
hora_visita = datetime.now(cr_tz).strftime("%Y-%m-%d %H:%M:%S")

# Verificación local: solo registrar si no ha sido registrado en esta sesión
if "visitantes_registrados" not in st.session_state:
    st.session_state["visitantes_registrados"] = set()

if visitante_id not in st.session_state["visitantes_registrados"]:
    try:
        # Conexión con Google Sheets
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials_dict = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"]["json_keyfile"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
        client = gspread.authorize(creds)
        hoja = client.open("registro_visitas").sheet1

        # Guardar fila
        hoja.append_row([hora_visita, user_agent, resolucion, idioma])
        st.session_state["visitantes_registrados"].add(visitante_id)

        st.success("✅ Visita registrada.")
    except Exception as e:
        st.error("❌ Error al registrar la visita.")
        st.exception(e)
else:
    st.info("ℹ️ Esta sesión ya ha sido registrada. No se guardará de nuevo.")
