import streamlit as st
import pandas as pd
import smtplib
import json
from email.message import EmailMessage
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuración inicial
st.set_page_config(page_title="Formulario de Solicitud de Alquiler", layout="centered")
st.title("📋 Formulario de Solicitud de Alquiler:  Habitacional / Comercial / Mixto")
st.image("fachada.jpeg", caption="Frente al Palí, Higuito Centro", use_container_width=True)

st.markdown("### ⚠️ Nota de Confidencialidad y Verificación de Información")
st.info(
    "La información que usted proporcione será tratada con estricta confidencialidad y utilizada únicamente para fines de evaluación de su solicitud de alquiler. "
    "Todos los datos personales, referencias y documentos adjuntos podrán ser verificados. "
    "No será compartida sin su autorización y será almacenada de forma segura, conforme a la Ley 8968. "
    "Si no se formaliza el contrato, los datos serán eliminados dentro de un plazo razonable.\n\n"
    "Al continuar, usted acepta estos términos."
)

# Selección inicial
uso = st.radio("¿Para qué desea alquilar la propiedad?", ["Uso habitacional", "Uso comercial", "Uso mixto"])
form_data = {}

# --- Sección Habitacional ---
if uso in ["Uso habitacional", "Uso mixto"]:
    st.header("🏠 Sección: Uso Habitacional")
    form_data["Nombre completo"] = st.text_input("Nombre completo")
    form_data["Cédula o pasaporte"] = st.text_input("Número de cédula o pasaporte")
    form_data["Profesión u ocupación"] = st.text_input("Profesión u ocupación")
    form_data["Teléfono"] = st.text_input("Número de teléfono")
    form_data["Correo alternativo"] = st.text_input("Correo electrónico alternativo")
    form_data["Cantidad de personas"] = st.number_input("¿Cuántas personas vivirán en la casa?", min_value=1, step=1)
    form_data["Relación entre personas"] = st.text_area("¿Relación entre las personas que vivirán ahí?")
    form_data["Niños y edades"] = st.text_area("¿Hay niños? ¿Qué edades?")
    form_data["Mascotas"] = st.text_area("¿Tiene mascotas? (tipo, cantidad, tamaño)")

# --- Sección Comercial ---
if uso in ["Uso comercial", "Uso mixto"]:
    st.header("🏢 Sección: Uso Comercial")
    form_data["Nombre del negocio"] = st.text_input("Nombre del negocio o emprendimiento")
    form_data["Tipo de actividad"] = st.text_input("Tipo de actividad comercial")
    form_data["Horario"] = st.text_input("Horario de funcionamiento")
    form_data["Clientes en el lugar"] = st.radio("¿Recibirá clientes en el lugar?", ["Sí", "No"])
    form_data["Empleados"] = st.number_input("¿Cuántos empleados trabajarán ahí?", min_value=0, step=1)
    form_data["Redes o web"] = st.text_input("Sitio web o redes sociales del negocio")
    form_data["Permisos municipales"] = st.radio("¿Cuenta con permisos municipales?", ["Sí", "No"])

# --- Sección Final Común ---
st.header("🔒 Sección Final y Declaración")
form_data["Monto alquiler estimado"] = st.text_input("¿Cuánto estaría dispuesto a pagar por el alquiler mensual?")
form_data["Vehículos"] = st.text_input("¿Tiene vehículo? ¿Cuántos?")
form_data["Historial alquiler"] = st.text_area("¿Ha alquilado antes? ¿Dónde? ¿Por qué dejó ese lugar?")
form_data["Propietario anterior"] = st.text_input("Nombre y contacto del propietario anterior")
form_data["Fiador"] = st.radio("¿Cuenta con fiador con propiedad en Costa Rica?", ["Sí", "No"])
form_data["Firma ante notario"] = st.radio("¿Acepta firmar contrato ante notario público?", ["Sí", "No"])
form_data["Depósito inicial"] = st.radio("¿Acepta entregar depósito de garantía y primer mes adelantado?", ["Sí", "No"])
form_data["Pago servicios"] = st.radio("¿Quién se encargará del pago de los servicios públicos?",
                                       ["El inquilino", "El propietario", "A convenir entre ambas partes"])
form_data["Observaciones"] = st.text_area("Observaciones adicionales")

form_data["Consentimiento"] = st.checkbox("Declaro que la información proporcionada es verdadera y autorizo su verificación.", value=False)
form_data["Consentimiento datos"] = st.checkbox("Autorizo el uso y eventual verificación de mis datos personales, y acepto su eliminación si no se formaliza un contrato.", value=False)

archivo = st.file_uploader("Opcional: Adjunte foto, referencia o documento", type=["png", "jpg", "jpeg", "pdf"])

# --- Guardar al enviar
if st.button("Enviar solicitud"):
    if not form_data["Consentimiento"] or not form_data["Consentimiento datos"]:
        st.error("Debe aceptar ambas declaraciones para continuar.")
    else:
        form_data["Tipo de uso"] = uso
        form_data["Fecha de envío"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df = pd.DataFrame([form_data])
        df.to_csv("respuestas_alquiler.csv", mode='a', index=False, header=False)

        # ✅ Guardar en Google Sheets
        try:
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            credentials_dict = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"]["json_keyfile"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
            client = gspread.authorize(creds)
            sheet = client.open("Respuestas_Alquiler").sheet1
            sheet.append_row(list(form_data.values()))
        except Exception as e:
            st.error(f"❌ Error al guardar en Google Sheets: {e}")

        # ✅ Enviar correo
        try:
            msg = EmailMessage()
            msg["Subject"] = "Nueva solicitud de alquiler"
            msg["From"] = "geenarfa@gmail.com"
            msg["To"] = "geenarfa@gmail.com"
            msg.set_content("\n".join([f"{k}: {v}" for k, v in form_data.items()]))

            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login("geenarfa@gmail.com", "bvws himz lgdz acit")
                server.send_message(msg)
        except Exception as e:
            st.error(f"❌ Error al enviar correo: {e}")

        # ✅ Guardar archivo adjunto
        if archivo:
            with open(f"archivo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{archivo.name}", "wb") as f:
                f.write(archivo.read())

        st.success("✅ ¡Solicitud enviada con éxito!")
