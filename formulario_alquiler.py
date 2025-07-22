import streamlit as st
import pandas as pd
import smtplib
import json
from email.message import EmailMessage
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pytz import timezone

st.set_page_config(page_title="Formulario de Solicitud de Alquiler", layout="centered")
st.title("📋 Formulario de Solicitud de Alquiler: Habitacional / Comercial / Mixto")
st.success("Gracias por su interés en alquilar una de nuestras propiedades. Este formulario le tomará menos de 5 minutos y nos permitirá conocer su perfil como inquilino.")
st.success("Si desea generar un sistema similar para el alquiler de sus bienes inmuebles, puede contactarnos a: info@vigias.net")

st.image("fachada1.jpg", caption="Frente al Palí, Higuito Centro", use_container_width=True)
st.image("Carac.jpg", caption="Frente al Palí, Higuito Centro", use_container_width=True)

st.markdown("### 📍 Ubicación del inmueble")
st.components.v1.iframe(
    src="https://www.google.com/maps/embed?pb=!1m14!1m12!1m3!1d245.67975692153937!2d-84.05487347043625!3d9.86076000110528!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!5e0!3m2!1ses-419!2scr!4v1752880163707!5m2!1ses-419!2scr",
    height=450,
    width=600
)

st.video("https://youtu.be/9U7l9rvnVJc")
st.markdown("### ⚠️ Nota de Confidencialidad y Verificación de Información")
st.info(
    "La información que usted proporcione será tratada con estricta confidencialidad y utilizada únicamente para fines de evaluación de su solicitud de alquiler. "
    "Todos los datos personales, referencias y documentos adjuntos podrán ser verificados. "
    "Ningun dato será compartirido ni almacenado sin su autorización explicita, si no se formaliza el contrato, los datos serán eliminados en su todalidad.\n\n"
    "Al continuar, usted acepta estos términos."
)

uso = st.radio("¿Para qué desea alquilar la propiedad?", ["Uso habitacional", "Uso comercial", "Uso mixto"])
form_data = {}

if uso in ["Uso habitacional", "Uso mixto"]:
    st.header("🏠 Sección: Uso Habitacional")
    form_data["Nombre completo"] = st.text_input("Nombre completo")
    form_data["Cédula o pasaporte"] = st.text_input("Número de cédula o pasaporte")
    form_data["Profesión u ocupación"] = st.text_input("Profesión u ocupación")
    form_data["Teléfono"] = st.text_input("Número de teléfono")
    form_data["Cantidad de personas"]_
