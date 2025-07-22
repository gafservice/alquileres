import streamlit as st
import pandas as pd
import json
from datetime import datetime
from pytz import timezone
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from email.message import EmailMessage
import smtplib

st.title("Formulario de Solicitud de Alquiler")

uso = st.radio("Tipo de uso del inmueble", ["Habitacional", "Mixto"])

# Campos base
form_data = {
    "Nombre completo": st.text_input("Nombre completo"),
    "Cédula o pasaporte": st.text_input("Cédula o pasaporte"),
    "Profesión u ocupación": st.text_input("Profesión u ocupación"),
    "Teléfono": st.text_input("Teléfono"),
    "Cantidad de personas": st.number_input("Cantidad de personas", min_value=1, step=1),
    "Relación entre personas": st.text_input("Relación entre personas"),
    "Niños y edades": st.text_input("Niños y edades"),
    "Mascotas": st.text_input("Mascotas"),
    "Correo electrónico": st.text_input("Correo electrónico"),
    "Historial alquiler": st.text_area("Historial de alquiler"),
    "Propietario anterior": st.text_input("Nombre del propietario anterior"),
    "Fiador": st.text_input("Fiador"),
    "Firma ante notario": st.selectbox("¿Está dispuesto a firmar ante notario?", ["Sí", "No"]),
    "Depósito inicial": st.selectbox("¿Está dispuesto a dejar depósito inicial?", ["Sí", "No"]),
    "Pago servicios": st.selectbox("¿Asumirá pago de servicios?", ["Sí", "No"]),
    "Monto alquiler estimado": st.text_input("Monto estimado para alquiler"),
    "Observaciones": st.text_area("Observaciones"),
    "Consentimiento": st.checkbox("Autorizo el tratamiento de mis datos para fines administrativos."),
    "Consentimiento datos": st.checkbox("Acepto los términos y condiciones del alquiler.")
}

# Si es uso mixto, se agregan campos comerciales
if uso == "Mixto":
    form_data.update({
        "Nombre del negocio": st.text_input("Nombre del negocio"),
        "Tipo de actividad": st.text_input("Tipo de actividad comercial"),
        "Horario": st.text_input("Horario de atención"),
        "Clientes en el lugar": st.text_input("Cantidad estimada de clientes en el lugar"),
        "Empleados": st.text_input("Cantidad de empleados"),
        "Redes o web": st.text_input("Redes sociales o sitio web"),
        "Permisos municipales": st.text_input("Permisos municipales"),
        "Permisos Ministerio de Salud": st.text_input("Permisos del Ministerio de Salud"),
        "Vehículos": st.text_input("Vehículos asociados")
    })
else:
    form_data.update({
        "Nombre del negocio": "",
        "Tipo de actividad": "",
        "Horario": "",
        "Clientes en el lugar": "",
        "Empleados": "",
        "Redes o web": "",
        "Permisos municipales": "",
        "Permisos Ministerio de Salud": "",
        "Vehículos": ""
    })

archivo = st.file_uploader("Subir documento adicional (opcional)", type=["pdf", "jpg", "png", "docx"])

# Al enviar el formulario
if st.button("Enviar solicitud"):
    if not form_data["Consentimiento"] or not form_data["Consentimiento datos"]:
        st.error("Debe aceptar ambas declaraciones.")
    else:
        form_data["Tipo de uso"] = uso
        form_data["Fecha de envío"] = datetime.now(timezone("America/Costa_Rica")).strftime("%Y-%m-%d %H:%M:%S")

        # Crear CSV con encabezados solo si no existe
        columnas = list(form_data.keys())
        df = pd.DataFrame([form_data])
        csv_path = "respuestas_alquiler.csv"
        try:
            open(csv_path, "r")
            df.to_csv(csv_path, mode="a", index=False, header=False)
        except FileNotFoundError:
            df.to_csv(csv_path, index=False, header=True)

        # Subir a Google Sheets
        try:
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            credentials_dict = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"]["json_keyfile"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
            client = gspread.authorize(creds)
            sheet = client.open("Respuestas_Alquiler").sheet1
            sheet.append_row(list(form_data.values()))
        except Exception as e:
            st.error(f"Error al guardar en Google Sheets: {e}")

        # Enviar correo
        try:
            cuerpo = "\n".join(f"{k}: {v}" for k, v in form_data.items())
            msg = EmailMessage()
            msg["Subject"] = "Nueva solicitud de alquiler"
            msg["From"] = "admin@vigias.net"
            msg["To"] = "admin@vigias.net"
            msg.set_content(cuerpo)

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login("admin@vigias.net", "ymse zpxe tvlg dhvq")
            server.send_message(msg)

            correo_usuario = form_data["Correo electrónico"]
            if correo_usuario and "@" in correo_usuario:
                confirm = EmailMessage()
                confirm["Subject"] = "Confirmación de envío"
                confirm["From"] = "admin@vigias.net"
                confirm["To"] = correo_usuario
                confirm.set_content(f"""Hola {form_data['Nombre completo']},

Recibimos su solicitud de alquiler. Pronto será revisada.

Gracias,
Administración de Propiedades
""")
                server.send_message(confirm)

            server.quit()
        except Exception as e:
            st.error(f"Error al enviar correo: {e}")

        # Guardar archivo
        if archivo:
            with open(f"docs/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{archivo.name}", "wb") as f:
                f.write(archivo.read())

        st.success("¡Solicitud enviada con éxito!")
