# --- Enviar al presionar botón ---
if st.button("Enviar solicitud"):

    if not form_data["Consentimiento"] or not form_data["Consentimiento datos"]:
        st.error("Debe aceptar ambas declaraciones para continuar.")

    else:
        # ✅ 1. Agregar metadatos
        form_data["Tipo de uso"] = uso
        form_data["Fecha de envío"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ✅ 2. Guardar localmente
        df = pd.DataFrame([form_data])
        df.to_csv("respuestas_alquiler.csv", mode='a', index=False, header=False)

        # ✅ 3. Guardar en Google Sheets
        try:
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            credentials_dict = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"]["json_keyfile"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
            client = gspread.authorize(creds)
            sheet = client.open("Respuestas_Alquiler").sheet1
            sheet.append_row(list(form_data.values()))
        except Exception as e:
            st.error(f"❌ Error al guardar en Google Sheets: {e}")

        # ✅ 4. Enviar correos
        try:
            # --- correo a admin ---
            msg = EmailMessage()
            msg["Subject"] = "Nueva solicitud de alquiler"
            msg["From"] = "admin@vigias.net"
            msg["To"] = "admin@vigias.net"
            msg.set_content("\n".join([f"{k}: {v}" for k, v in form_data.items()]))

            # --- correo al usuario ---
            correo_usuario = form_data.get("Correo alternativo", "").strip()
            enviar_confirmacion = correo_usuario and "@" in correo_usuario

            if enviar_confirmacion:
                confirmacion = EmailMessage()
                confirmacion["Subject"] = "Hemos recibido su solicitud de alquiler"
                confirmacion["From"] = "admin@vigias.net"
                confirmacion["To"] = correo_usuario
                cuerpo = f"""
Estimado/a {form_data.get("Nombre completo", "interesado/a")},

Gracias por completar el formulario de solicitud de alquiler. Hemos recibido su información correctamente.

Nuestro equipo validará la información recibida. Si desea más información o modificar su solicitud, puede escribirnos a info@vigias.net.

Esta es una copia de su envío:
---------------------------------------
{chr(10).join([f"{k}: {str(v)}" for k, v in form_data.items()])}
---------------------------------------

Gracias por su interés.

Atentamente,
Administración de Propiedades
"""
                confirmacion.set_content(cuerpo)

            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login("admin@vigias.net", "ymse zpxe tvlg dhvq")
                server.send_message(msg)
                if enviar_confirmacion:
                    server.send_message(confirmacion)
        except Exception as e:
            st.error(f"❌ Error al enviar correo: {e}")

        # ✅ 5. Guardar archivo
        if archivo:
            with open(f"archivo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{archivo.name}", "wb") as f:
                f.write(archivo.read())

        # ✅ 6. Mensaje final
        st.success("✅ ¡Solicitud enviada con éxito!")
        st.success("Si desea generar un sistemas similar para el alquiler de sus bienes inmuebles, puede contactarnos a: info@vigias.net")
