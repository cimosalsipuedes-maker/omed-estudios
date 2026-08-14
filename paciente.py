import streamlit as st
import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# 1. CONFIGURACIÓN DE LAS CREDENCIALES DE GOOGLE (Desde Streamlit Secrets)
DRIVE_FOLDER_ID = "18vAA3HcfuEldb9vsvyKPYALr2WquCVUD"
SHEETS_NAME = "informes omed" 

SCOPES = [
    "https://googleapis.com",
    "https://googleapis.com"
]

def conectar_google():
    # Trae los datos en formato diccionario para poder manipular la llave
    creds_dict = dict(st.secrets["gcp_service_account"])
    
    # REPARACIÓN DE LA LLAVE: Convierte los saltos de línea de texto a formato PEM real
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    
    creds = service_account.Credentials.from_service_account_info(creds_dict)
    creds_with_scope = creds.with_scopes(SCOPES)
    
    client_sheets = gspread.authorize(creds_with_scope)
    servicio_drive = build("drive", "v3", credentials=creds_with_scope)
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
                    
                    celda = hoja.find(dni_ingresado, in_column=1)
                    
                    if celda:
                        fila_datos = hoja.row_values(celda.row)
                        # Índices corregidos para listas de Python (0=DNI, 1=Nombre, 2=Link)
                        nombre_paciente = fila_datos[1]
                        link_pdf = fila_datos[2]
                        
                        st.success(f"¡Hola {nombre_paciente}! Tu estudio está disponible.")
                        st.markdown(f"📥 **[Hacer clic aquí para descargar tu estudio en PDF]({link_pdf})**")
                    else:
                        st.error("No se encontraron estudios para el DNI ingresado.")
                except Exception as e:
                    st.error(f"Error al conectar con la base de datos: {e}")
        else:
            st.warning("Por favor, ingrese un número de DNI.")

# ----------------- ACCESO MÉDICOS (Con bloqueo de contraseña) -----------------
elif opcion == "Acceso Médicos":
    st.header("👨‍⚕️ Panel de Carga para Profesionales")
    
    # Sistema de seguridad con la contraseña de los Secrets
    password_ingresada = st.text_input("Ingrese la clave médica de acceso:", type="password")
    
    if password_ingresada == st.secrets["medicos"]["password"]:
        st.success("Acceso concedido al panel de carga.")
        st.divider()
        
        dni_paciente = st.text_input("DNI del Paciente:")
        nombre_paciente = st.text_input("Nombre y Apellido completo:")
        archivo_subido = st.file_uploader("Subir estudio médico (Formato PDF)", type=["pdf"])
        
        if st.button("Subir y Registrar Estudio"):
            if dni_paciente and nombre_paciente and archivo_subido:
                with st.spinner("Subiendo estudio al respaldo permanente de Drive..."):
                    try:
                        client_sheets, servicio_drive = conectar_google()
                        
                        # A. Subir archivo a Google Drive
                        nombre_archivo = f"Estudio_{dni_paciente}.pdf"
                        metadatos = {
                            "name": nombre_archivo,
                            "parents": [DRIVE_FOLDER_ID]
                        }
                        media = MediaIoBaseUpload(io.BytesIO(archivo_subido.read()), mimetype="application/pdf")
                        archivo_drive = servicio_drive.files().create(body=metadatos, media_body=media, fields="id").execute()
                        id_archivo = archivo_drive.get("id")
                        
                        # Permisos públicos de lectura para el archivo en Drive
                        permiso = {"type": "anyone", "role": "reader"}
                        servicio_drive.permissions().create(fileId=id_archivo, body=permiso).execute()
                        
                        # Enlace directo de descarga corregido
                        link_compartir = f"https://google.com{id_archivo}&export=download"
                        
                        # B. Registrar datos en Google Sheets
                        hoja = client_sheets.open(SHEETS_NAME).sheet1
                        hoja.append_row([dni_paciente, nombre_paciente, link_compartir])
                        
                        st.success(f"¡Estudio de {nombre_paciente} subido con éxito y guardado para siempre!")
                    except Exception as e:
                        st.error(f"Error técnico durante la carga: {e}")
            else:
                st.warning("Por favor, complete todos los campos y seleccione un archivo PDF.")
    elif password_ingresada != "":
        st.error("Contraseña incorrecta. Intente nuevamente.")
