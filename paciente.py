@st.cache_resource
def inicializar_conexiones():
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        
        # Limpieza automática de la llave privada para evitar el error de Padding
        pkey = creds_dict["private_key"].strip()
        
        # Quitamos encabezados si ya se repitieron y limpiamos espacios o barras raras
        pkey = pkey.replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "")
        pkey = pkey.replace("\\n", "\n").replace(" ", "").strip()
        
        # Volvemos a armar la llave con el formato oficial exacto que exige Google
        private_key_limpia = f"-----BEGIN PRIVATE KEY-----\n{pkey}\n-----END PRIVATE KEY-----\n"
        creds_dict["private_key"] = private_key_limpia
        
        scopes = [
            "https://googleapis.com",
            "https://googleapis.com"
        ]
        
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=scopes)
        gdrive = build('drive', 'v3', credentials=creds)
        gsheets = gspread.authorize(creds)
        return gdrive, gsheets
    except Exception as e:
        st.error(f"Error crítico de conexión: {e}")
        return None, None
