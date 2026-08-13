import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# 1. CONFIGURACIÓN DE LAS CREDENCIALES DE GOOGLE
# El archivo .json que descargaste debe estar en la misma carpeta que tu código
JSON_FILE = "portal-medico-505421-eff4836032e5.json" 

# ID de tu carpeta de Drive (Cargado automáticamente desde tu captura)
DRIVE_FOLDER_ID = "18vAA3HcfuEldb9vsvyKPYALr2WquCVUD"

# Nombre exacto de tu planilla de Google Sheets
SHEETS_NAME = "informes omed" 

SCOPES = [
    "https://googleapis.com",
    "https://googleapis.com"
]

def conectar_google():
    creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_FILE, SCOPES)
    client_sheets = gspread.authorize(creds)
    servicio_drive = build("drive", "v3", credentials=creds)
    return client_sheets, servicio_drive

# 2. INTERFAZ DE LA APLICACIÓN
st.set_page_config(page_title="Portal Médico OMED", page_icon="🏥", layout="centered")
st.title("🏥 Portal de Gestión Médica (OMED)")

opcion = st.sidebar.radio("Seleccionar Rol", ["Portal del Paciente", "Acceso Médicos"])

# ----------------- PORTAL DEL PACIENTE -----------------
if opcion == "Portal del Paciente":
    st.header("🔍 Consulta de Estudios Médicos")
    st.write("Ingrese su documento para descargar sus resultados disponibles.")
    
    dni_ingresado = st.text_input("DNI del Paciente:", max_chars=12)
    
    if st.button("Buscar Estudio"):
        if dni_ingresado:
            with st.spinner("Buscando en la base de datos..."):
                try:
                    client_sheets, _ = conectar_google()
                    hoja = client_sheets.open(SHEETS_NAME).sheet1
                    
                    # Busca el DNI en la columna A
                    celda = hoja.find(dni_ingresado, in_column=1)
                    
                    if celda:
                        fila_datos = hoja.row_values(celda.row)
                        nombre_paciente = fila_datos[1]
                        link_pdf = fila_datos[2]
                        
                        st.success(f"¡Hola {nombre_paciente}! Tu estudio está disponible.")
                        st.markdown(f"📥 **[Hacer clic aquí para descargar tu estudio en PDF]({link_pdf})**")
                    else:
                        st.error("No se encontraron estudios para el DNI ingresado.")
                except Exception as e:
                    st.error("Error al conectar con la base de datos permanente.")
        else:
            st.warning("Por favor, ingrese un número de DNI.")

# ----------------- ACCESO MÉDICOS -----------------
elif opcion == "Acceso Médicos":
    st.header("👨‍⚕️ Panel de Carga para Profesionales")
    
    dni_paciente = st.text_input("DNI del Paciente:")
    nombre_paciente = st.text_input("Nombre y Apellido completo:")
    archivo_subido = st.file_uploader("Subir estudio médico (Formato PDF)", type=["pdf"])
    
    if st.button("Subir y Registrar Estudio"):
        if dni_paciente and nombre_paciente and archivo_subido:
            with st.spinner("Subiendo estudio al respaldo permanente de Drive..."):
                try:
                    client_sheets, servicio_drive = conectar_google()
                    
                    # A. Subir archivo a la carpeta específica de Google Drive
                    nombre_archivo = f"Estudio_{dni_paciente}.pdf"
                    metadatos = {
                        "name": nombre_archivo,
                        "parents": [DRIVE_FOLDER_ID]
                    }
                    media = MediaIoBaseUpload(io.BytesIO(archivo_subido.read()), mimetype="application/pdf")
                    archivo_drive = servicio_drive.files().create(body=metadatos, media_body=media, fields="id").execute()
                    id_archivo = archivo_drive.get("id")
                    
                    # Dar permisos públicos de lectura al archivo para que el paciente pueda descargarlo
                    permiso = {"type": "anyone", "role": "reader"}
                    servicio_drive.permissions().create(fileId=id_archivo, body=permiso).execute()
                    
                    # Generar enlace directo de visualización
                    link_compartir = f"https://google.com{id_archivo}/view?usp=sharing"
                    
                    # B. Registrar datos en Google Sheets de forma permanente
                    hoja = client_sheets.open(SHEETS_NAME).sheet1
                    hoja.append_row([dni_paciente, nombre_paciente, link_compartir])
                    
                    st.success(f"¡Estudio de {nombre_paciente} subido con éxito y guardado para siempre!")
                except Exception as e:
                    st.error(f"Error técnico durante la carga: {e}")
        else:
            st.warning("Por favor, complete todos los campos y seleccione un archivo PDF.")
