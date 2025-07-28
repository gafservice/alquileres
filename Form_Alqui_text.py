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

    # (👉 Aquí insertás el formulario extenso que ya tenés: uso, datos personales, historial, etc.)

    st.markdown("⚠️ [Sección del formulario formal aquí...]")

# -----------------------------------------------------------------------------
# OPCIONAL: botón de reinicio
# -----------------------------------------------------------------------------
st.markdown("---")
if st.button("🔄 Reiniciar formulario"):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.experimental_rerun()
