import streamlit as st
import pandas as pd
import os

# Configuración de la página unificada y profesional
st.set_page_config(page_title="Portal Médico OMED", page_icon="🏥", layout="centered")

# =====================================================================
# CONFIGURACIÓN VISUAL: LOGO DE FONDO (DISEÑO TRANSPARENTE CERTIFICADO)
# =====================================================================
# Transformamos tu link en descarga directa para que el servidor lo dibuje sin bloqueos
URL_LOGO_FONDO = "https://google.com"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("{URL_LOGO_FONDO}");
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
        background-size: 50%; /* Tamaño justo para que quede estético de fondo */
        background-color: #f7f9fc; /* Color sutil médico para los bordes */
    }}
    /* Capa translúcida elegante para que el texto sea 100% legible */
    .block-container {{
        background-color: rgba(255, 255, 255, 0.94);
        padding: 3rem 2rem;
        border-radius: 12px;
        box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.06);
        margin-top: 2rem;
    }}
    /* Estilo para los botones principales */
    .stButton>button {{
        width: 100%;
        border-radius: 6px;
    }}
    </style>
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
# 1. INTERFAZ PÚBLICA: PORTAL DEL PACIENTE (CON DOBLE FILTRO)
# =====================================================================
st.title("🏥 Portal de Estudios Médicos - OMED")
st.write("Bienvenido. Ingrese sus datos de acceso provistos por el centro médico.")

# Cajas de acceso obligatorio para el paciente
dni_busqueda = st.text_input("Ingrese su número de DNI (sin puntos):", max_chars=10)
pass_paciente = st.text_input("Ingrese la contraseña general del portal:", type="password")

# CONTRASEÑA GENERAL PARA PACIENTES (Modificable de acá si lo deseas)
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
                    nombre_paciente = registro["Nombre"].values[0]
                    ruta_archivo_pdf = registro["Enlace_PDF"].values[0]
                    
                    st.success(f"✅ Estudio encontrado para: {nombre_paciente}")
                    
                    if os.path.exists(ruta_archivo_pdf):
                        with open(ruta_archivo_pdf, "rb") as f:
                            bytes_pdf = f.read()
                        
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
# 2. ACCESO EXCLUSIVO PARA MÉDICOS
# =====================================================================
st.markdown("---")
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
                        
                        st.success(f"🎉 ¡Éxito! El estudio de {nombre_paciente} ya está disponible de forma permanente en el portal.")
                    except Exception as e:
                        st.error(f"Error en el proceso de almacenamiento interno: {e}")
            else:
                st.error("Faltan datos obligatorios para procesar la subida.")
                
    elif password_input != "":
        st.error("❌ Contraseña incorrecta. Acceso denegado.")
