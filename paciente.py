import streamlit as st
import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

# Configuración de la página unificada
st.set_page_config(page_title="Portal Médico OMED", page_icon="🏥", layout="centered")

# =====================================================================
# 1. CONEXIÓN DIRECTA CERTIFICADA (Alineación estricta por bloques)
# =====================================================================
@st.cache_resource
def inicializar_conexiones():
    try:
        # Reconstruimos la firma digital original en renglones exactos de 64 bytes
        # Esto elimina de raíz cualquier problema de caracteres extra, padding o truncado web
        bloques_clave = [
            "MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDF4n4KGocv2Koj",
            "nkv7u4EX4iIFycqMGmue6MQSsYikeAE77u90k8p7VFT0ONEK1BjUXbvcfDnBlatl",
            "v+bDaaPdlcNrjQm6JUeh7FKmTOTSLLNAGZyUC1gxoxiTDRg75tlBcLR5tR73FKZg",
            "n6hyCosoyTh0tDywErVLF4Yc/sNjMCR31cIkUzSXG0Z9luWd6VIW7+YyZdBpCwSC",
            "4n3BMkMhIVjHREG1fOaFzjctN0/AnbqyVMFBl39wuhEJF/D51K94D0dLZ65/wDjG",
            "Aanigml6c5nxUUb6igm7RZZr+Cdx7SQYXLkYMnKLz8P1yRAJsoyNzolvPxt8+Rat",
            "PZnnQDPKMKvAgMBAAECggEAVdQ2udgmwZx2sOZBN63j+3iiKdLt4zmyHDGtdJp6",
            "UXnnP0vXOqzVJZSjYRLwKwQFBfnszs2ie6N0BEbYag8ge2wqiR7bKwRM5B/QyXpQ",
            "Xnw9QpC/FeYVVrxZzZ+vpY6+hjkxThkOaOgaOZaOzp7WbPJc+aVo+xMh3vZTMI3",
            "VzlnfVqfsK1WAQFgxW0Acy2g8Dhhq5Vvd2jbztsU1iNJTLtqCSTb7Z+2EQIYy62y",
            "tOSmn50+pNsM7y1biLqisQlX9zQ3haYFvNa7+Ur1RSbiCvB0e61wW+zm1QvKZn/",
            "9sEV7nN7KMqL5gv7G5Jf+4cbMaWq6gd44/+QQnP4/idyWYQKbGQdZ4HZ0F+uMYiLo",
            "BxZLnm5QQ6e6sNE5LeYFiarRcJhq0GuqTQr4HcmU1oQMFKXOW+6dAtiWiWI1RQw0",
            "+biNwn/Al5SErbbYSHEz217M7cBwuEBXmqR+R+ieEswbi9jyEjjjB/iCFQHP4eKQ",
            "BgS4mVn4Ak4YZL1rRJaWFb7Lc2S8AiHjwKBgQDPuL3Rh7XbAlMdf1i+mz0yx/AN",
            "niOjG6WdsncRbQ9V17MuY3LmPuX+6H36XqxoSAzuEw0Ty4D+/TZ5c3RsJhxgrY1v",
            "4wmBWdBnbyvg1W7v+yhED8qpQ46n91v7mkcx6r/ceLpSSAi/FFq4FIr1pY6f+hiP",
            "Af7Mnidakjn2C4QKBgAEnUKGf7M9wq2Xh1sGbvwQfYp6u9tOi+QhSrUE/vxiuFuC",
            "vXtnqdLm+ip7zHT7bIeDx/a91byKqpvd/YDtUEsAkooTLitPASW5JwLXzCKrhamm",
            "lgWn4T/I1NzGMIHwikzWKgumuOdmijcEpTJIHFiXGidvX47bl3nA4+EXyx1AoGAK",
            "ostnjm4MUj1YnrdvXIhYp0k3gn7fXvRGPFNKAtOx7RgKwyi7isS/Mui9mEp6D/kj",
            "nbXEMnzFV0Tb3Nb/cS+lGdvG73sdLP2tWjP5vayCMDnWb0xsK5m2pRemAZcZKcZS",
            "Vkloy1ynsqFebUyNQndt/uQ1J9T2HAoka0XdmdTME8/EECgYEA7RW6T44WZFEuG",
            "I+c0RUen8R0C5Ltpji115dMzcGxp+RqN1it+cV41ryWw+KGgaXCN9wR4XY93i6lI",
            "qJk0SNPIncgy0lCYkksB2RtI7naaYfoSf9b/fmME1Jcuygy7bK58FH56fcGOfH8M",
            "mhIVGGVbEnPs29h6CvQgUc5fWQ1M2gGIA=="
        ]
        
        # Estructuramos la clave PEM limpia de forma nativa en memoria
        cuerpo_pem = "\n".join(bloques_clave)
        private_key_fija = f"-----BEGIN PRIVATE KEY-----\n{cuerpo_pem}\n-----END PRIVATE KEY-----\n"

        # Armamos el diccionario directo para el conector oficial de Google Cloud
        info_servicio = {
            "type": "service_account",
            "project_id": "portal-medico-505421",
            "private_key_id": "eff4836032e5e386152bd1031b01f3c7e203f2d9",
            "private_key": private_key_fija,
            "client_email": "streamlit@://gserviceaccount.com",
            "client_id": "107894406539201206914",
            "auth_uri": "https://google.com",
            "token_uri": "https://google.com",
            "auth_provider_x509_cert_url": "https://googleapis.com",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/streamlit%40://gserviceaccount.com",
            "universe_domain": "googleapis.com"
        }

        scopes = [
            "https://googleapis.com",
            "https://googleapis.com"
        ]
        
        # Inicialización directa pasándole la estructura alineada de forma manual
        creds = service_account.Credentials.from_service_account_info(info_servicio, scopes=scopes)
        gdrive = build('drive', 'v3', credentials=creds)
        gc = gspread.authorize(creds)
        return gdrive, gc
    except Exception as e:
        st.error(f"Error crítico en la firma de credenciales: {e}")
        return None, None

# Inicializamos las conexiones
drive_service, gc = inicializar_conexiones()

DRIVE_FOLDER_ID = "18vAA3HcfuEldb9vsvyKPYALr2WquCVUD"
SHEET_NAME = "informes omed"

# =====================================================================
# 2. INTERFAZ PÚBLICA: PORTAL DEL PACINETE
# =====================================================================
st.title("🏥 Portal de Estudios Médicos - OMED")
st.write("Bienvenido. Ingrese su número de documento para descargar sus resultados.")

dni_busqueda = st.text_input("Ingrese su número de DNI (sin puntos):", max_chars=10)

if st.button("Buscar mis Estudios"):
    if dni_busqueda and gc:
        with st.spinner("Buscando en el sistema..."):
            try:
                sheet = gc.open(SHEET_NAME).sheet1
                registros = sheet.get_all_records()
                
                encontrado = False
                for fila in registros:
                    if str(fila.get("DNI")).strip() == dni_busqueda.strip():
                        st.success(f"✅ Estudio encontrado para: {fila.get('Nombre')}")
                        st.markdown(f"🔗 [Haga clic aquí para descargar su informe en PDF]({fila.get('Enlace_PDF')})")
                        encontrado = True
                        break
                
                if not encontrado:
                    st.warning("⚠️ No se encontraron registros para el DNI ingresado. Verifique el número.")
            except Exception as e:
                st.error(f"Error al conectar con la base de datos: {e}")
    else:
        st.info("Por favor, escriba un número de DNI para iniciar la búsqueda.")

# =====================================================================
# 3. ACCESO EXCLUSIVO PARA MÉDICOS (Panel oculto seguro)
# =====================================================================
st.markdown("---")
with st.expander("🛠️ Acceso Exclusivo para Personal Médico"):
    st.write("Área restringida para la carga de nuevos estudios al sistema.")
    
    password_input = st.text_input("Introduzca la clave médica:", type="password", key="med_pass")
    
    # Intentamos leer la contraseña de los secrets, si no, tomamos la de respaldo nativa
    try:
        pass_sistema = st.secrets["medicos"]["password"]
    except:
        pass_sistema = "omed123"
        
    if password_input == pass_sistema:
        st.success("🔓 Panel de carga desbloqueado.")
        
        dni_paciente = st.text_input("DNI del Paciente (Sin puntos ni espacios):")
        nombre_paciente = st.text_input("Nombre Completo del Paciente:")
        archivo_pdf = st.file_uploader("Seleccione el archivo PDF del estudio:", type=["pdf"])
        
        if st.button("Subir e Informar"):
            if dni_paciente and nombre_paciente and archivo_pdf and drive_service and gc:
                with st.spinner("Subiendo PDF a la nube y registrando..."):
                    try:
                        nombre_archivo = f"{dni_paciente}_{archivo_pdf.name}"
                        with open(nombre_archivo, "wb") as f:
                            f.write(archivo_pdf.getbuffer())
                        
                        metadata = {
                            'name': nombre_archivo,
                            'parents': [DRIVE_FOLDER_ID]
                        }
                        media = MediaFileUpload(nombre_archivo, mimetype='application/pdf')
                        archivo_drive = drive_service.files().create(body=metadata, media_body=media, fields='id, webViewLink').execute()
                        
                        drive_service.permissions().create(
                            fileId=archivo_drive.get('id'),
                            body={'type': 'anyone', 'role': 'reader'}
                        ).execute()
                        
                        link_pdf = archivo_drive.get('webViewLink')
                        
                        if os.path.exists(nombre_archivo):
                            os.remove(nombre_archivo)
                        
                        sheet = gc.open(SHEET_NAME).sheet1
                        sheet.append_row([dni_paciente, nombre_paciente, link_pdf])
                        
                        st.success(f"🎉 ¡Éxito! El estudio de {nombre_paciente} ya está disponible.")
                    except Exception as e:
                        st.error(f"Error en el proceso de carga: {e}")
            else:
                st.error("Faltan datos obligatorios para procesar la subida.")
                
    elif password_input != "":
        st.error("❌ Contraseña incorrecta. Acceso denegado.")
