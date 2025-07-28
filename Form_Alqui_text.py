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

# Configuración de página
st.set_page_config(page_title="Alquiler de Propiedad - Higuito Centro", layout="centered")

# -----------------------------------------------------------------------------
# 1️⃣ INFORMACIÓN GENERAL
# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# 2️⃣ FORMULARIO RÁPIDO DE INTERÉS
# -----------------------------------------------------------------------------
st.markdown("---")
st.header("📨 Solicitud Rápida de Interés")

with st.form(key="formulario_rapido"):
    nombre_rapido = st.text_input("Nombre completo")
    celular_rapido = st.text_input("Número de teléfono")
    correo_rapido = st.text_input("Correo electrónico")
    uso_rapido = st.selectbox("Uso previsto", ["Habitacional", "Comercial", "Mixto"])
    presupuesto_rapido = st.text_input("Presupuesto aproximado (₡)")

    enviado_rapido = st.form_submit_button("Enviar solicitud rápida")

if enviado_rapido:
    st.success("✅ Gracias por su interés. Puede continuar al chat o llenar el formulario completo.")
    st.session_state["permite_chat"] = True

# -----------------------------------------------------------------------------
# 3️⃣ INTERACCIÓN CON GEMINI
# -----------------------------------------------------------------------------
if st.session_state.get("permite_chat", False):
    st.markdown("---")
    st.header("🤖 Chat con Gemini")

    # Inicialización de Gemini
    try:
        api_key = st.secrets["generativeai"]["api_key"]
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")
    except Exception as e:
        st.error(f"❌ No se pudo inicializar el modelo Gemini: {e}")
        st.stop()

    contexto_inicial = """
Eres un asistente experto en alquiler de propiedades en Costa Rica. Esta es la propiedad disponible:

📍 Frente al Palí, Higuito Centro, zona céntrica con acceso a servicios.  
🏠 Uso permitido: Habitacional, Comercial o Mixto  
🛋️ Características: 1 sala/comedor, cocina, 3 cuartos, baño con agua caliente, cuarto de pilas, parqueo  
📡 Servicios: Electricidad, Agua, Internet, TV Kolbi  
🎥 Video: https://youtu.be/9U7l9rvnVJc  
🖼️ Imágenes: fachada1.jpg y Carac.jpg  
Responde de manera clara y amable como si atendieras a un inquilino.
"""

    pregunta = st.text_input("💬 Haga una consulta sobre el inmueble")
    if pregunta:
        try:
            prompt = contexto_inicial + "\n\nPregunta del usuario: " + pregunta
            respuesta = model.generate_content(prompt)
            st.success(respuesta.text)
            st.session_state["permite_formulario"] = True
        except Exception as e:
            st.error(f"❌ Error en la respuesta de Gemini: {e}")

# -----------------------------------------------------------------------------
# 4️⃣ FORMULARIO FORMAL COMPLETO
# -----------------------------------------------------------------------------
if st.session_state.get("permite_formulario", False):
    st.markdown("---")
    st.header("📝 Formulario Formal de Solicitud")

    # Aquí puedes insertar TODO el formulario completo que ya desarrollaste (sección 4)
    # Como ya está funcionando, no lo repito completo aquí.
    # Usa un bloque `with st.form("formulario_formal"):` si querés que sea un formulario controlado.
    st.info("Formulario completo para evaluación de alquiler. Por favor llene todos los campos requeridos.")

    with st.form("formulario_formal"):
        uso = st.radio("¿Para qué desea alquilar la propiedad?", ["Uso habitacional", "Uso comercial", "Uso mixto"])
    form_data = {}

    if uso in ["Uso habitacional", "Uso mixto"]:
        st.header("🏠 Sección: Uso Habitacional")
        form_data["Nombre completo"] = st.text_input("Nombre completo")
        form_data["Número de cédula o pasaporte"] = st.text_input("Número de cédula o pasaporte")
        form_data["Profesión u ocupación"] = st.text_input("Profesión u ocupación")
        form_data["Número de teléfono"] = st.text_input("Número de teléfono")
        form_data["Cantidad de personas"] = st.number_input("¿Cuántas personas vivirán en la casa?", min_value=1, step=1)
        form_data["Relación entre personas"] = st.text_area("¿Relación entre las personas que vivirán ahí?")
        form_data["Niños y edades"] = st.text_area("¿Hay niños? ¿Qué edades?")
        form_data["Mascotas"] = st.text_area("¿Tiene mascotas? (tipo, cantidad, tamaño)")

    if uso in ["Uso comercial", "Uso mixto"]:
        st.header("🏢 Sección: Uso Comercial")
        form_data["Nombre Administrador"] = st.text_input("Nombre Administrador")
        form_data["Cédula Administrador"] = st.text_input("Cédula Administrador")
        form_data["Nombre del negocio"] = st.text_input("Nombre del negocio o emprendimiento")
        form_data["Tipo de actividad"] = st.text_input("Tipo de actividad comercial")
        form_data["Horario"] = st.text_input("Horario de funcionamiento")
        form_data["Clientes en el lugar"] = st.radio("¿Recibirá clientes en el lugar?", ["Sí", "No"])
        form_data["Empleados"] = st.number_input("¿Cuántos empleados trabajarán ahí?", min_value=0, step=1)
        form_data["Redes o web"] = st.text_input("Sitio web o redes sociales del negocio")
        form_data["Permisos municipales"] = st.radio("¿Cuenta con permisos municipales?", ["Sí", "No"])
        form_data["Pemisos Ministerio de Salud"] = st.radio("¿Cuenta con permisos del Ministerio de Salud?", ["Sí", "No"])

    st.header("🔒 Sección Final")
    form_data["Vehículos"] = st.text_input("¿Tiene vehículo? ¿Cuántos?")
    form_data["Correo electronico"] = st.text_input("Correo electrónico")
    form_data["Historial alquiler"] = st.text_area("¿Ha alquilado antes? ¿Dónde? ¿Por qué dejó ese lugar?")
    form_data["Propietario anterior"] = st.text_input("Nombre y contacto del propietario anterior")
    form_data["Fiador"] = st.radio("¿Cuenta con fiador con propiedad en Costa Rica?", ["Sí", "No"])
    form_data["Firma ante Abogado"] = st.radio("¿Acepta firmar contrato ante Abogado?", ["Sí", "No"])
    form_data["Depósito inicial"] = st.radio("¿Acepta entregar depósito de garantía y primer mes adelantado?", ["Sí", "No"])
    form_data["Pago servicios"] = st.radio("¿Quién se encargará del pago de los servicios públicos?",
                                           ["El inquilino", "El propietario", "A convenir entre ambas partes"])
    form_data["Monto alquiler estimado"] = st.text_input("¿Cuánto estaría dispuesto a pagar por el alquiler mensual?")
    form_data["Observaciones"] = st.text_area("Observaciones adicionales")
    archivo = st.file_uploader("Opcional: Adjunte foto, referencia o documento", type=["png", "jpg", "jpeg", "pdf"])
    form_data["Consentimiento"] = st.checkbox("Declaro que la información proporcionada es verdadera", value=False)
    form_data["Consentimiento datos"] = st.checkbox("Autorizo su verificación.", value=False)

    enviar_formal = st.form_submit_button("Enviar solicitud formal")


if enviar_formal:
    if not form_data["Consentimiento"] or not form_data["Consentimiento datos"]:
        st.error("❌ Debe aceptar ambas declaraciones para continuar.")
    else:
        form_data["Tipo de uso"] = uso
        hora_local = datetime.now(timezone("America/Costa_Rica"))
        form_data["Fecha de envío"] = hora_local.strftime("%Y-%m-%d %H:%M:%S")

        columnas = [
            "Tipo de uso", "Nombre completo", "Número de cédula o pasaporte", "Profesión u ocupación", "Número de teléfono",
            "Cantidad de personas", "Relación entre personas", "Niños y edades", "Mascotas",
            "Nombre Administrador", "Cédula Administrador", "Nombre del negocio", "Tipo de actividad", "Horario",
            "Clientes en el lugar", "Empleados", "Redes o web", "Permisos municipales", "Pemisos Ministerio de Salud",
            "Vehículos", "Correo electronico", "Historial alquiler", "Propietario anterior",
            "Fiador", "Firma ante Abogado", "Depósito inicial", "Pago servicios", "Monto alquiler estimado",
            "Observaciones", "Consentimiento", "Consentimiento datos", "Fecha de envío"
        ]

        datos_ordenados = {col: form_data.get(col, "") for col in columnas}
        df = pd.DataFrame([datos_ordenados])
        nombre_csv = "Respuestas_Alquiler.csv"
        df.to_csv(nombre_csv, mode='a', index=False, header=not os.path.exists(nombre_csv))

        try:
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            credentials_dict = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"]["json_keyfile"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
            client = gspread.authorize(creds)
            sheet = client.open("Respuestas_Alquiler").worksheet("Formulario_Completo")
            sheet.append_row([datos_ordenados[col] for col in columnas])
        except Exception as e:
            st.error(f"❌ Error al guardar en Google Sheets: {e}")

        try:
            cuerpo_admin = "\n".join([f"{k}: {v}" for k, v in datos_ordenados.items()])
            msg = EmailMessage()
            msg["Subject"] = "Nueva solicitud de alquiler"
            msg["From"] = "admin@vigias.net"
            msg["To"] = "admin@vigias.net"
            msg.set_content(cuerpo_admin)

            correo_usuario = form_data.get("Correo electronico", "").strip()
            if correo_usuario and "@" in correo_usuario:
                msg_usr = EmailMessage()
                msg_usr["Subject"] = "Confirmación de solicitud de alquiler"
                msg_usr["From"] = "admin@vigias.net"
                msg_usr["To"] = correo_usuario
                msg_usr.set_content(f"""Estimado/a {form_data.get("Nombre completo", "interesado/a")},

Hemos recibido su solicitud de alquiler con la siguiente información:
----------------------------------
{cuerpo_admin}
----------------------------------
Nos pondremos en contacto pronto.

Atentamente,
Administración de Propiedades
""")

                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login("admin@vigias.net", "ymsezpxetvlgdhvq")
                    server.send_message(msg)
                    server.send_message(msg_usr)
            else:
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login("admin@vigias.net", "ymsezpxetvlgdhvq")
                    server.send_message(msg)
        except Exception as e:
            st.error(f"❌ Error al enviar correo: {e}")

        if archivo:
            try:
                nombre_archivo = f"archivo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{archivo.name}"
                with open(nombre_archivo, "wb") as f:
                    f.write(archivo.read())
                st.success(f"📎 Archivo guardado exitosamente: {nombre_archivo}")
            except Exception as e:
                st.error(f"❌ Error al guardar archivo adjunto: {e}")

        st.success("✅ ¡Formulario enviado con éxito!")
        st.info("Si desea generar un sistema similar, contáctenos a: info@vigias.net")

    st.markdown("⚠️ [Sección del formulario formal aquí...]")

# -----------------------------------------------------------------------------
# OPCIONAL: botón de reinicio
# -----------------------------------------------------------------------------
st.markdown("---")
if st.button("🔄 Reiniciar formulario"):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.experimental_rerun()
