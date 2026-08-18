import streamlit as st
import pandas as pd
import os

# Configuración de la página unificada y profesional con icono nativo en la pestaña
st.set_page_config(page_title="Portal Médico OMED", page_icon="🏥", layout="centered")

# =====================================================================
# PALETA DE COLORES IDENTITARIA DE TU LOGO "OMED" (DISEÑO LIMPIO)
# =====================================================================
# Azul Omed: #001a57 | Turquesa Omed: #1dd4b6 | Fondo Médico: #f7f9fc
st.markdown(
    """
    <style>
    /* Forzamos el fondo claro médico institucional */
    .stApp {
        background-color: #f7f9fc !important;
    }
    
    /* Contenedor central elegante con sombra suave */
    .block-container {
        background-color: #ffffff;
        padding: 3rem 2rem;
        border-radius: 14px;
        box-shadow: 0px 8px 32px rgba(0, 26, 87, 0.05);
        margin-top: 3rem;
        max-width: 550px !important;
    }
    
    /* Membrete Superior con la marca exacta de tu logo */
    .logo-container {
        text-align: center;
        margin-bottom: 25px;
        padding-bottom: 15px;
        border-bottom: 4px solid #1dd4b6; /* Línea Turquesa Omed */
    }
    .logo-text-principal {
        color: #001a57 !important; /* Azul Omed */
        font-size: 52px !important;
        font-weight: 800 !important;
        margin: 0 !important;
        display: inline-block;
        letter-spacing: -1px;
    }
    .logo-text-secundario {
        color: #001a57 !important; /* Azul Omed */
        font-size: 15px !important;
        font-weight: 700 !important;
        margin-top: 5px !important;
        text-transform: uppercase;
        letter-spacing: 3px;
    }
    
    /* Títulos de las secciones internas */
    .seccion-titulo {
        color: #001a57 !important;
        text-align: center;
        font-size: 24px !important;
        font-weight: 700 !important;
        margin-top: 15px !important;
    }
    
    /* Botones personalizados con el Azul Omed Oficial */
    .stButton>button {
        width: 100%;
        background-color: #001a57 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.7rem !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        transition: all 0.3s ease;
        box-shadow: 0px 4px 12px rgba(0, 26, 87, 0.15);
    }
    .stButton>button:hover {
        background-color: #1dd4b6 !important;
        color: #001a57 !important;
        box-shadow: 0px 4px 16px rgba(29, 212, 182, 0.4);
    }
    
    /* Estilo para las etiquetas de texto de los inputs */
    label {
        color: #001a57 !important;
        font-weight: 600 !important;
    }
    </style>
    
    <!-- Construcción del isotipo tipográfico corporativo limpio -->
    <div class="logo-container">
        <div>
            <h1 class="logo-text-principal">omed</h1>
        </div>
        <div class="logo-text-secundario">Centro Médico</div>
    </div>
    """,
    unsafe_allow_html=True
)

# Nombre del archivo base de datos local
DB_FILE = "base_datos_informes.csv"
CARPETA_PDFS = "estudios_medicos_respaldo"

if not os.path.exists(DB_FILE):
    df_init = pd.DataFrame(columns=["DNI", "Nombre", "Enlace_PDF"])
    df_init.to_csv(DB_FILE, index=False)

if not os.path.exists(CARPETA_PDFS):
    os.makedirs(CARPETA_PDFS)

# =====================================================================
# 1. INTERFAZ PÚBLICA: PORTAL DEL PACIENTE (CON CONTRASEÑA GENERAL)
# =====================================================================
st.markdown("<div class='seccion-titulo'>Portal de Estudios Médicos</div>", unsafe_allow_html=True)
st.write("<p style='color: #555; text-align: center; margin-bottom: 25px;'>Ingrese sus datos de acceso provistos por el centro médico.</p>", unsafe_allow_html=True)

# Cajas de acceso obligatorio para el paciente
dni_busqueda = st.text_input("Número de DNI del Paciente (sin puntos):", max_chars=10)
pass_paciente = st.text_input("Contraseña del Portal:", type="password")

CLAVE_GENERAL_PACIENTES = "omed2026"

if st.button("Buscar mis Estudios"):
    if not dni_busqueda or not pass_paciente:
        st.info("Por favor, complete ambos campos (DNI y Contraseña) para iniciar la búsqueda.")
    elif pass_paciente != CLAVE_GENERAL_PACIENTES:
        st.error("❌ Contraseña del portal incorrecta. Verifique los datos o consulte al personal.")
    else:
        with st.spinner("Buscando en el sistema..."):
            try:
                df = pd.read_csv(DB_FILE)
                df["DNI"] = df["DNI"].astype(str).str.strip()
                dni_limpio = str(dni_busqueda).strip()
                
                registro = df[df["DNI"] == dni_limpio]
                
                if not registro.empty:
                    # Extracción técnica segura forzando string nativo (.item()) para evitar colisiones
                    nombre_paciente = str(registro["Nombre"].values[0])
                    ruta_archivo_pdf = str(registro["Enlace_PDF"].values[0])
                    
                    st.success(f"✅ Estudio encontrado para: {nombre_paciente}")
                    
                    # Verificamos la existencia física real de la ruta limpia
                    if os.path.exists(ruta_archivo_pdf):
                        with open(ruta_archivo_pdf, "rb") as f:
                            bytes_pdf = f.read()
                        
                        # Botón oficial directo de descarga
                        st.download_button(
                            label="⬇️ Descargar mi Informe Médico (PDF)",
                            data=bytes_pdf,
                            file_name=os.path.basename(ruta_archivo_pdf),
                            mime="application/pdf"
                        )
                    else:
                        st.error("El archivo PDF del estudio no se encuentra disponible físicamente. Contacte al centro médico.")
                else:
                    st.warning("⚠️ No se encontraron registros para el DNI ingresado. Verifique el número.")
            except Exception as e:
                st.error(f"Error al leer el sistema de archivos: {e}")

# =====================================================================
# 2. ACCESO EXCLUSIVO PARA MÉDICOS (Panel oculto seguro)
# =====================================================================
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("🛠️ Acceso Exclusivo para Personal Médico"):
    st.write("Área restringida para la carga de nuevos estudios al sistema.")
    
    password_input = st.text_input("Introduzca la clave médica:", type="password", key="med_pass")
    
    if password_input == "omed123":
        st.success("🔓 Panel de carga desbloqueado.")
        
        dni_paciente = st.text_input("DNI del Paciente (Sin puntos ni espacios):")
        nombre_paciente = st.text_input("Nombre Completo del Paciente:")
        archivo_pdf = st.file_uploader("Seleccione el archivo PDF del estudio:", type=["pdf"])
        
        if st.button("Subir e Informar"):
            if dni_paciente and nombre_paciente and archivo_pdf:
                with st.spinner("Guardando PDF de forma permanente y registrando..."):
                    try:
                        nombre_seguro = f"{dni_paciente}_{archivo_pdf.name.replace(' ', '_')}"
                        ruta_destino_final = os.path.join(CARPETA_PDFS, nombre_seguro)
                        
                        with open(ruta_destino_final, "wb") as f:
                            f.write(archivo_pdf.getbuffer())
                        
                        df_actual = pd.read_csv(DB_FILE)
                        nueva_fila = pd.DataFrame([{"DNI": str(dni_paciente).strip(), "Nombre": nombre_paciente, "Enlace_PDF": ruta_destino_final}])
                        df_actual = pd.concat([df_actual, nueva_fila], ignore_index=True)
                        df_actual.to_csv(DB_FILE, index=False)
                        
                        st.success(f"🎉 ¡Éxito! El estudio de {nombre_paciente} ya está disponible de forma permanente.")
                    except Exception as e:
                        st.error(f"Error en el proceso de almacenamiento interno: {e}")
            else:
                st.error("Faltan datos obligatorios para procesar la subida.")
                
    elif password_input != "":
        st.error("❌ Contraseña incorrecta. Acceso denegado.")
