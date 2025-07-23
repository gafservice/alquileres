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

from streamlit_js_eval import streamlit_js_eval



st.set_page_config(page_title="INFORMACIÓN GENERAL", layout="centered")



#####################################################
try:
    st.write("🛠️ Conectando a Google Sheets...")
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials_dict = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"]["json_keyfile"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    client = gspread.authorize(creds)

     fila = [hora_visita, user_agent, resolucion, idioma, st.session_state["visita_id"]]
    st.write("📤 Datos a guardar:", fila)

    if all(fila):
        hoja.append_row(fila)
        st.success("✅ Visita registrada correctamente.")
    else:
        st.warning("⚠️ No se registró: algunos campos están vacíos.")

    st.write("✅ Conectado a hoja:", hoja.title)

    hoja.append_row(["Prueba", "Test", "123x456", "es-CR", "demo"])
    st.success("✅ Fila de prueba guardada con éxito.")
except Exception as e:
    st.error("❌ Error al escribir en la hoja")
    st.exception(e)





############################################################


st.title("Para uso: Habitacional / Comercial / Mixto")

st.image("fachada1.jpg", caption="Frente al Palí, Higuito Centro, con acceso a todos los servicios basicos", use_container_width=True)
st.image("Carac.jpg", caption="Frente al Palí, Higuito Centro, un lugar centrico", use_container_width=True)

st.markdown("### 📍 Ubicación del inmueble")
st.components.v1.iframe(
    src="https://www.google.com/maps/embed?pb=!1m14!1m12!1m3!1d245.67975692153937!2d-84.05487347043625!3d9.86076000110528!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!5e0!3m2!1ses-419!2scr!4v1752880163707!5m2!1ses-419!2scr",
    height=450,
    width=600
)

st.video("https://youtu.be/9U7l9rvnVJc")

st.success("Gracias por su interés en esta propiedad. Nos gustaria saber mas de usted y sus necesidades como inquilino. Para lo cual hemos preparado este pequeño formulario. Al llenar el formulario por completo y enviarlo usted quedara en la lista de posibles elegibles.")

st.markdown("### ⚠️ Nota de Confidencialidad y Verificación de Información")
st.info("La información proporcionada en este formulario será tratada con estricta confidencialidad conforme a la Ley 8968 de Protección de la Persona frente al Tratamiento de sus Datos Personales. Los datos se utilizarán únicamente para la evaluación de su solicitud de alquiler. No se compartirán con terceros ni se almacenarán más allá del propósito indicado, salvo que usted lo autorice expresamente. En caso de no concretarse el contrato, los datos serán eliminados de forma segura.\n\n")
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
form_data["Correo electronico"] = st.text_input("Correo electrónico ")
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
if st.button("Enviar solicitud"):
    if not form_data["Consentimiento"] or not form_data["Consentimiento datos"]:
        st.error("Debe aceptar ambas declaraciones para continuar.")
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
    "Vehículos", "Correo electronico", "Historial alquiler", "Propietario anterior",
    "Fiador", "Firma ante Abogado", "Depósito inicial", "Pago servicios", "Monto alquiler estimado",
    "Observaciones", "Consentimiento", "Consentimiento datos", "Fecha de envío"
]


        form_data_ordenado = {col: form_data.get(col, "") for col in columnas_ordenadas}
        df = pd.DataFrame([form_data_ordenado])
        nombre_csv = "Respuestas_Alquiler.csv"
        archivo_existe = False
        try:
            with open(nombre_csv, "r") as f:
                archivo_existe = True
        except FileNotFoundError:
            pass

        df.to_csv(nombre_csv, mode='a', index=False, header=not archivo_existe)

        # ✅ Guardar en Google Sheets
        try:
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            credentials_dict = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"]["json_keyfile"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
            client = gspread.authorize(creds)
            sheet = client.open("Respuestas_Alquiler").sheet1
            # Verifica si la hoja está vacía (sin encabezados)
            sheet.append_row([form_data_ordenado[col] for col in columnas_ordenadas])


        except Exception as e:
            st.error(f"❌ Error al guardar en Google Sheets: {e}")

        # ✅ Enviar correo
        try:
            cuerpo_admin = "\n".join([f"{k}: {str(v)}" for k, v in form_data.items()])
            msg = EmailMessage()
            msg["Subject"] = "Nueva solicitud de alquiler"
            msg["From"] = "admin@vigias.net"
            msg["To"] = "admin@vigias.net"
            msg.set_content(cuerpo_admin)

            correo_usuario = form_data.get("Correo electronico", "").strip()
            enviar_confirmacion = correo_usuario and "@" in correo_usuario

            if enviar_confirmacion:
                cuerpo_usuario = f"""Estimado/a {form_data.get("Nombre completo", "interesado/a")},




Hemos recibido correctamente su solicitud de alquiler enviada a través del formulario.
Resumen de su envío:
----------------------------------
{cuerpo_admin}
----------------------------------
Gracias por confiar en nosotros.

Atentamente,
Administración de Propiedades
"""
                confirmacion = EmailMessage()
                confirmacion["Subject"] = "Confirmación de solicitud de alquiler"
                confirmacion["From"] = "admin@vigias.net"
                confirmacion["To"] = correo_usuario
                confirmacion.set_content(cuerpo_usuario)

            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login("admin@vigias.net", st.secrets["SMTP_PASSWORD"])
                #server.login("admin@vigias.net", "ymsezpxetvlgdhvq")
                server.send_message(msg)
                if enviar_confirmacion:
                    server.send_message(confirmacion)
        except Exception as e:
            st.error(f"❌ Error al enviar correo: {e}")

        # ✅ Guardar archivo adjunto
        if archivo:
            try:
                nombre_archivo = f"archivo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{archivo.name}"
                with open(nombre_archivo, "wb") as f:
                    f.write(archivo.read())
                st.success(f"📎 Archivo guardado exitosamente: {nombre_archivo}")
            except Exception as e:
                st.error(f"❌ Error al guardar archivo adjunto: {e}")

        # ✅ Confirmación final
        st.success("✅ ¡Solicitud enviada con éxito!")
       

        
        st.info("Si desea generar un sistema similar para el alquiler de sus bienes inmuebles, puede contactarnos a: info@vigias.net") 
