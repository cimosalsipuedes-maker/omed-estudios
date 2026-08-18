import streamlit as st
import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

# Configuración de la página unificada
st.set_page_config(page_title="Portal Médico OMED", page_icon="🏥", layout="centered")

# =====================================================================
# 1. CONEXIÓN NATIVA ESTÁNDAR A GOOGLE
# =====================================================================
@st.cache_resource
def inicializar_conexiones():
    try:
        # Levantamos las credenciales desde la sección oficial connections.gsheets
        creds_dict = dict(st.secrets["connections"]["gsheets"])
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        
        scopes = [
            "https://googleapis.com",
            "https://googleapis.com"
        ]
        
        # Conexión directa y nativa
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=scopes)
        gdrive = build('drive', 'v3', credentials=creds)
        gc = gspread.authorize(creds)
        return gdrive, gc
    except Exception as e:
        st.error(f"Error crítico en la firma de credenciales: {e}")
        return None, None

# Inicializamos los servicios
drive_service, gc = inicializar_conexiones()

DRIVE_FOLDER_ID = "18vAA3HcfuEldb9vsvyKPYALr2WquCVUD"
SHEET_NAME = "informes omed"

# =====================================================================
# 2. INTERFAZ PÚBLICA: PORTAL DEL PACIENTE
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
    
    if password_input == st.secrets["medicos"]["password"]:
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
