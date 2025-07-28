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

# 1️⃣ INFORMACIÓN
st.title("🏡 Información del Inmueble")
st.image("fachada1.jpg", caption="Frente al Palí, Higuito Centro, con acceso a todos los servicios básicos", use_container_width=True)
st.image("Carac.jpg", caption="Zona céntrica con acceso inmediato", use_container_width=True)
st.markdown("### 📍 Ubicación del Inmueble")
st.components.v1.iframe(
    src="https://www.google.com/maps/embed?pb=!1m14!1m12!1m3!1d245.67975692153937!2d-84.05487347043625!3d9.86076000110528!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!5e0!3m2!1ses-419!2scr!4v1752880163707!5m2!1ses-419!2scr",
    height=450,
    width=600
)
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
    nombre = st.text_input("Nombre completo")
    celular = st.text_input("Número de teléfono")
    correo = st.text_input("Correo electrónico")
    uso = st.selectbox("Uso previsto", ["Habitacional", "Comercial", "Mixto"])
    presupuesto = st.text_input("Presupuesto aproximado (₡)")
    enviado_rapido = st.form_submit_button("Enviar solicitud rápida")
if enviado_rapido:
    st.session_state["permite_chat"] = True
    st.session_state["datos_rapidos"] = {
        "Nombre": nombre,
        "Celular": celular,
        "Correo": correo,
        "Uso": uso,
        "Presupuesto": presupuesto
    }
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials_dict = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"]["json_keyfile"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open("Respuestas_Alquiler").worksheet("Contactos_Interesados")

        sheet.append_row([nombre, celular, correo, uso, presupuesto, datetime.now(timezone("America/Costa_Rica")).strftime("%Y-%m-%d %H:%M:%S")])
    except Exception as e:
        st.error("❌ Error al guardar en hoja de Contactos_Interesados")
        st.exception(e)



    
    st.success("✅ Puede consultar con Gemini o continuar al formulario completo")


# 3️⃣ INTERACCIÓN CON GEMINI
# 3️⃣ INTERACCIÓN CON GEMINI
if st.session_state.get("permite_chat", False):
    st.markdown("---")
    st.header("🤖 Consultas sobre la Propiedad (Asistente Gemini)")

    try:
        api_key = st.secrets["generativeai"]["api_key"]
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")
    except Exception as e:
        st.error("❌ No se pudo inicializar Gemini.")
        st.stop()

    presupuesto = st.session_state["datos_rapidos"].get("Presupuesto", "No especificado")

    contexto = f"""
Eres un asistente experto en alquiler de propiedades en Costa Rica.

Esta es la propiedad disponible para alquiler:

📍 Ubicación: Frente al Palí, Higuito Centro, zona céntrica con acceso inmediato a servicios básicos y transporte.  
🏠 Uso permitido: Habitacional, Comercial o Mixto.  

🛋️ Características del inmueble:  
- 1 sala / comedor  
- 1 cocina (solo el área, sin electrodomésticos)  
- 3 dormitorios  
- 1 baño con agua caliente  
- 1 cuarto de pilas (espacio de lavado, sin lavadora)  
- Parqueo para 1 vehículo (si requiere más, puede negociarse)  
- Se permiten mascotas bajo tenencia responsable  

📡 Servicios disponibles:  
- Electricidad  
- Agua potable  
- Agua caliente  
- Internet  
- TV Kolbi  

💰 El usuario ha indicado un presupuesto estimado de **{presupuesto} colones mensuales**.  
**Este valor corresponde únicamente a una propuesta por parte del interesado, y no representa el monto oficial del alquiler.**  
El monto real del alquiler será definido por la administración una vez evaluadas las solicitudes.

📅 Para **agendar una visita a la propiedad**, es indispensable **completar el formulario formal**.

📞 Para más información directa, el contacto autorizado es **Alexander Araya**:  
- Teléfono: 8715-5477  
- Correo electrónico: info@vigias.net

Tu tarea es responder exclusivamente preguntas relacionadas con esta propiedad, de manera clara, amable y profesional.
"""

    pregunta = st.text_input("📩 ¿Qué desea saber sobre la propiedad?")
    if pregunta:
        try:
            respuesta = model.generate_content(contexto + "\n\n" + "Pregunta: " + pregunta)
            st.success(respuesta.text)
            st.session_state["permite_formulario"] = True
        except Exception as e:
            st.error("❌ Error al obtener respuesta de Gemini.")


# 3️⃣  fin INTERACCIÓN CON GEMINI



# 4️⃣ FORMULARIO FORMAL
if st.session_state.get("permite_formulario", False):
    st.markdown("---")
    st.header("📝 Formulario Formal de Solicitud")
    with st.form("formulario_formal"):
        uso = st.radio("¿Para qué desea alquilar la propiedad?", ["Uso habitacional", "Uso comercial", "Uso mixto"])
        form_data = {}
        if uso in ["Uso habitacional", "Uso mixto"]:
            st.header("🏠 Sección: Uso Habitacional")
            form_data["Nombre completo"] = st.text_input("Nombre completo")
            form_data["Número de cédula o pasaporte"] = st.text_input("Número de cédula o pasaporte")
            form_data["Profesión u ocupación"] = st.text_input("Profesión u ocupación")
            form_data["Número de teléfono"] = st.text_input("Número de teléfono")
            form_data["Cantidad de personas"] = st.number_input("¿Cuántas personas vivirán en la casa?", min_value=1)
            form_data["Relación entre personas"] = st.text_area("Relación entre las personas")
            form_data["Niños y edades"] = st.text_area("¿Hay niños? ¿Qué edades?")
            form_data["Mascotas"] = st.text_area("¿Tiene mascotas?")
        if uso in ["Uso comercial", "Uso mixto"]:
            st.header("🏢 Sección: Uso Comercial")
            form_data["Nombre Administrador"] = st.text_input("Nombre Administrador")
            form_data["Cédula Administrador"] = st.text_input("Cédula Administrador")
            form_data["Nombre del negocio"] = st.text_input("Nombre del negocio")
            form_data["Tipo de actividad"] = st.text_input("Tipo de actividad comercial")
            form_data["Horario"] = st.text_input("Horario de funcionamiento")
            form_data["Clientes en el lugar"] = st.radio("¿Recibirá clientes?", ["Sí", "No"])
            form_data["Empleados"] = st.number_input("¿Cuántos empleados?", min_value=0)
            form_data["Redes o web"] = st.text_input("Sitio web o redes sociales")
            form_data["Permisos municipales"] = st.radio("Permisos municipales", ["Sí", "No"])
            form_data["Pemisos Ministerio de Salud"] = st.radio("Permisos de Salud", ["Sí", "No"])
        st.header("🔒 Final")
        form_data["Vehículos"] = st.text_input("¿Tiene vehículo?")
        form_data["Correo electrónico"] = st.text_input("Correo electrónico")
        form_data["Historial alquiler"] = st.text_area("¿Ha alquilado antes?")
        form_data["Propietario anterior"] = st.text_input("Propietario anterior")
        form_data["Fiador"] = st.radio("¿Cuenta con fiador?", ["Sí", "No"])
        form_data["Firma ante Abogado"] = st.radio("¿Acepta firmar ante abogado?", ["Sí", "No"])
        form_data["Depósito inicial"] = st.radio("¿Acepta depósito?", ["Sí", "No"])
        form_data["Pago servicios"] = st.radio("¿Quién paga servicios?", ["El inquilino", "El propietario", "A convenir"])
        form_data["Monto alquiler estimado"] = st.text_input("Monto alquiler")
        form_data["Observaciones"] = st.text_area("Observaciones")
        archivo = st.file_uploader("Adjunte documento", type=["pdf", "jpg"])
        form_data["Consentimiento"] = st.checkbox("Información es verdadera", value=False)
        form_data["Consentimiento datos"] = st.checkbox("Autorizo verificación", value=False)
        enviar_formal = st.form_submit_button("Enviar solicitud formal")
        if enviar_formal:
            if not form_data["Consentimiento"] or not form_data["Consentimiento datos"]:
            st.warning("Debe aceptar ambas declaraciones.")
            else:
                form_data["Tipo de uso"] = uso
                cr_tz = timezone("America/Costa_Rica")
                hora_local = datetime.now(cr_tz)
                form_data["Fecha de envío"] = hora_local.strftime("%Y-%m-%d %H:%M:%S")
        
                columnas_ordenadas = [
                    "Tipo de uso", "Nombre completo", "Número de cédula o pasaporte", "Profesión u ocupación", "Número de teléfono",
                    "Cantidad de personas", "Relación entre personas", "Niños y edades", "Mascotas",
                    "Nombre Administrador", "Cédula Administrador", "Nombre del negocio", "Tipo de actividad", "Horario",
                    "Clientes en el lugar", "Empleados", "Redes o web", "Permisos municipales", "Pemisos Ministerio de Salud",
                    "Vehículos", "Correo electrónico", "Historial alquiler", "Propietario anterior",
                    "Fiador", "Firma ante Abogado", "Depósito inicial", "Pago servicios", "Monto alquiler estimado",
                    "Observaciones", "Consentimiento", "Consentimiento datos", "Fecha de envío"
                ]
        
                form_data_ordenado = {col: form_data.get(col, "") for col in columnas_ordenadas}
                df = pd.DataFrame([form_data_ordenado])
        
                # Guardar en CSV
                nombre_csv = "Respuestas_Alquiler.csv"
                archivo_existe = os.path.exists(nombre_csv)
                df.to_csv(nombre_csv, mode='a', index=False, header=not archivo_existe)
        
                # Guardar en Google Sheets
                try:
                    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                    credentials_dict = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"]["json_keyfile"])
                    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
                    client = gspread.authorize(creds)
                    sheet = client.open("Respuestas_Alquiler").worksheet("Formulario_Completo")
                    sheet.append_row([form_data_ordenado[col] for col in columnas_ordenadas])
                except Exception as e:
                    st.error("❌ Error al guardar en Google Sheets")
                    st.exception(e)
        
                # Guardar archivo adjunto
                if archivo:
                    try:
                        nombre_archivo = f"archivo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{archivo.name}"
                        with open(nombre_archivo, "wb") as f:
                            f.write(archivo.read())
                        st.success(f"📎 Archivo guardado exitosamente: {nombre_archivo}")
                    except Exception as e:
                        st.error(f"❌ Error al guardar archivo adjunto: {e}")
        
                st.success("✅ ¡Formulario formal enviado!")
