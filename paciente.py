import streamlit as st
import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

# Configuración de la página unificada
st.set_page_config(page_title="Portal Médico OMED", page_icon="🏥", layout="centered")

# =====================================================================
# 1. CONEXIÓN DIRECTA Y SEGURA A GOOGLE CLOUD
# =====================================================================
@st.cache_resource
def inicializar_conexiones():
    try:
        # Extraemos el diccionario nativo cargado desde Secrets
        creds_dict = dict(st.secrets["gcp_service_account"])
        
        scopes = [
            "https://googleapis.com",
            "https://googleapis.com"
        ]
        
        # Autenticación directa utilizando el string multilinea exacto
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=scopes)
        gdrive = build('drive', 'v3', credentials=creds)
        gsheets = gspread.authorize(creds)
        return gdrive, gsheets
    except Exception as e:
        st.error(f"Error crítico en la firma de credenciales: {e}")
        return None, None

# Inicializamos los servicios en la nube
drive_service, gc = inicializar_conexiones()
