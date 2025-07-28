import streamlit as st
import pandas as pd
import smtplib
import json
from email.message import EmailMessage
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pytz import timezone
import streamlit.components.v1 as components
from streamlit_javascript import st_javascript
import google.generativeai as genai
import os

st.set_page_config(page_title="Alquiler de Propiedad - Higuito Centro", layout="centered")

# 1️⃣ INFORMACIÓN GENERAL
st.title("🏡 Información del Inmueble")
st.image("fachada1.jpg", caption="Frente al Palí, Higuito Centro, con acceso a todos los servicios básicos", use_container_width=True)
st.image("Carac.jpg", caption="Zona céntrica con acceso inmediato", use_container_width=True)
st.markdown("### 📍 Ubicación del Inmueble")
st.components.v1.iframe(
    src="https://www.google.com/maps/embed?pb=!1m14!1m12!1m3!1d245.67975692153937!2d-84.05487347043625!3d9.86076000110528!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!5e0!3m2!1ses-419!2scr!4v1752880163707!5m2!1ses-419!2scr",
    height=450,
    width=600
)
st.markdown("### 🎥 Video del Inmueble")
st.video("https://youtu.be/9U7l9rvnVJc")

with st.expander("📋 Ver características del inmueble"):
    st.markdown("""
    - 1 Sala / Comedor  
    - 1 Cocina (solo el área, sin electrodomésticos)  
    - 3 Dormitorios  
    - 1 Baño con agua caliente  
    - 1 Cuarto de Pilas (área de lavado, no incluye lavadora)  
    - 1 espacio de parqueo  
    - Servicios disponibles: Electricidad, Agua potable, Internet, TV Kolbi, Agua caliente  
    """)

# 2️⃣ FORMULARIO RÁPIDO
st.markdown("---")
st.header("📨 Solicitud Rápida de Interés")

with st.form("formulario_rapido"):
    nombre_rapido = st.text_input("Nombre completo")
    celular_rapido = st.text_input("Número de teléfono")
    correo_rapido = st.text_input("Correo electrónico")
    uso_rapido = st.selectbox("Uso previsto", ["Habitacional", "Comercial", "Mixto"])
    presupuesto_rapido = st.text_input("Presupuesto aproximado (₡)")
    enviado_rapido = st.form_submit_button("Enviar solicitud rápida")

if enviado_rapido:
    st.session_state["permite_chat"] = True
    st.session_state["datos_rapidos"] = {
        "Nombre": nombre_rapido,
        "Teléfono": celular_rapido,
        "Correo": correo_rapido,
        "Uso": uso_rapido,
        "Presupuesto": presupuesto_rapido
    }
    st.success("✅ Datos guardados. Puede continuar al chat o llenar el formulario completo.")
    try:
        datos = st.session_state["datos_rapidos"]
        with open("respuestas_rapidas.csv", "a") as f:
            f.write(",".join([str(x) for x in datos.values()]) + "\n")
    except Exception as e:
        st.warning(f"Error al guardar CSV local: {e}")

# 3️⃣ CHAT CON GEMINI
if st.session_state.get("permite_chat", False):
    st.markdown("---")
    st.header("🤖 Chat con Gemini")
    try:
        api_key = st.secrets["generativeai"]["api_key"]
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")
    except Exception as e:
        st.error("No se pudo inicializar Gemini")
        st.stop()

    contexto = f"""
Eres un asistente experto en alquiler de propiedades en Costa Rica.
Propiedad frente al Palí, Higuito Centro.
Uso previsto: {st.session_state['datos_rapidos'].get('Uso')}
Presupuesto del usuario: {st.session_state['datos_rapidos'].get('Presupuesto')}
"""
    pregunta = st.text_input("¿Qué desea saber sobre el inmueble?")
    if pregunta:
        try:
            respuesta = model.generate_content(contexto + "\n\nPregunta: " + pregunta)
            st.success(respuesta.text)
            st.session_state["permite_formulario"] = True
        except Exception as e:
            st.error("Error al responder con Gemini.")

# 4️⃣ FORMULARIO COMPLETO
if st.session_state.get("permite_formulario", False):
    st.markdown("---")
    st.header("📝 Formulario Formal de Solicitud")

    with st.form("formulario_formal"):
        datos_previos = st.session_state.get("datos_rapidos", {})
        nombre = st.text_input("Nombre completo", value=datos_previos.get("Nombre", ""))
        correo = st.text_input("Correo electrónico", value=datos_previos.get("Correo", ""))
        telefono = st.text_input("Número de teléfono", value=datos_previos.get("Teléfono", ""))
        uso = st.selectbox("Uso previsto", ["Habitacional", "Comercial", "Mixto"], index=["Habitacional", "Comercial", "Mixto"].index(datos_previos.get("Uso", "Habitacional")))
        presupuesto = st.text_input("Presupuesto mensual", value=datos_previos.get("Presupuesto", ""))
        comentarios = st.text_area("Observaciones adicionales")
        archivo = st.file_uploader("Adjunte documento opcional", type=["pdf", "jpg", "png"])
        aceptar = st.checkbox("Confirmo que la información es correcta", value=False)
        enviar_formal = st.form_submit_button("Enviar solicitud formal")

        if enviar_formal:
            if not aceptar:
                st.warning("Debe aceptar para continuar.")
            else:
                datos = {
                    "Nombre": nombre,
                    "Correo": correo,
                    "Teléfono": telefono,
                    "Uso": uso,
                    "Presupuesto": presupuesto,
                    "Comentarios": comentarios,
                    "Fecha": datetime.now(timezone("America/Costa_Rica")).strftime("%Y-%m-%d %H:%M:%S")
                }
                df = pd.DataFrame([datos])
                df.to_csv("formulario_completo.csv", mode="a", index=False, header=not os.path.exists("formulario_completo.csv"))

                try:
                    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                    credentials_dict = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"]["json_keyfile"])
                    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
                    client = gspread.authorize(creds)
                    sheet = client.open("Respuestas_Alquiler").worksheet("Formulario_Completo")
                    sheet.append_row(list(datos.values()))
                except Exception as e:
                    st.warning(f"Error al guardar en Google Sheets: {e}")

                try:
                    msg = EmailMessage()
                    msg["Subject"] = "Nueva Solicitud de Alquiler"
                    msg["From"] = "admin@vigias.net"
                    msg["To"] = "admin@vigias.net"
                    cuerpo = "\n".join([f"{k}: {v}" for k, v in datos.items()])
                    msg.set_content(cuerpo)
                    with smtplib.SMTP("smtp.gmail.com", 587) as server:
                        server.starttls()
                        server.login("admin@vigias.net", "ymsezpxetvlgdhvq")
                        server.send_message(msg)
                except Exception as e:
                    st.warning("No se pudo enviar el correo.")

                if archivo:
                    try:
                        nombre_archivo = f"adjunto_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{archivo.name}"
                        with open(nombre_archivo, "wb") as f:
                            f.write(archivo.read())
                        st.success(f"Archivo guardado: {nombre_archivo}")
                    except Exception as e:
                        st.warning("No se pudo guardar el archivo.")

                st.success("✅ ¡Formulario formal enviado con éxito!")
