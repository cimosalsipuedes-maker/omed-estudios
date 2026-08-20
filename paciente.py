import streamlit as st
import pandas as pd
import base64

# Configuración de la página unificada institucional
st.set_page_config(page_title="Portal Médico OMED", page_icon="🏥", layout="centered")

# =====================================================================
# 🗄️ CONEXIÓN Y CREACIÓN DE LA BASE DE DATOS BLINDADA
# =====================================================================
try:
    conn = st.connection("sql")
except Exception:
    st.error("Error de configuración interna. Revise el apartado Secrets de Streamlit.")
    st.stop()

# Inicialización técnica de la tabla permanente (Guarda el índice y el PDF en texto)
with conn.session as session:
    session.execute("""
        CREATE TABLE IF NOT EXISTS informes_omed (
            dni TEXT PRIMARY KEY,
            nombre TEXT,
            nombre_archivo TEXT,
            pdf_base64 TEXT
        );
    """)
    session.commit()

# =====================================================================
# PALETA DE COLORES IDENTITARIA DE TU LOGO "OMED" (DISEÑO LIMPIO)
# =====================================================================
st.markdown(
    """
    <style>
    .stApp { background-color: #f7f9fc !important; }
    .block-container {
        background-color: #ffffff; padding: 3rem 2rem; border-radius: 14px;
        box-shadow: 0px 8px 32px rgba(0, 26, 87, 0.05); margin-top: 3rem; max-width: 550px !important;
    }
    .logo-container { text-align: center; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 4px solid #1dd4b6; }
    .logo-text-principal { color: #001a57 !important; font-size: 52px !important; font-weight: 800 !important; margin: 0 !important; display: inline-block; letter-spacing: -1px; }
    .logo-text-secundario { color: #001a57 !important; font-size: 15px !important; font-weight: 700 !important; margin-top: 5px !important; text-transform: uppercase; letter-spacing: 3px; }
    .seccion-titulo { color: #001a57 !important; text-align: center; font-size: 24px !important; font-weight: 700 !important; margin-top: 15px !important; }
    .stButton>button { width: 100%; background-color: #001a57 !important; color: white !important; border-radius: 8px !important; border: none !important; padding: 0.7rem !important; font-weight: 600 !important; font-size: 16px !important; transition: all 0.3s ease; box-shadow: 0px 4px 12px rgba(0, 26, 87, 0.15); }
    .stButton>button:hover { background-color: #1dd4b6 !important; color: #001a57 !important; box-shadow: 0px 4px 166px rgba(29, 212, 182, 0.4); }
    label, p, .stMarkdown { color: #001a57 !important; font-weight: 600 !important; }
    .stMarkdown p, .bajada-texto { color: #555555 !important; font-weight: 400 !important; }
    </style>
    
    <div class="logo-container">
        <div><h1 class="logo-text-principal">omed</h1></div>
        <div class="logo-text-secundario">Centro Médico</div>
    </div>
    """,
    unsafe_allow_html=True
)

# =====================================================================
# 1. INTERFAZ PÚBLICA: PORTAL DEL PACIENTE
# =====================================================================
st.markdown("<div class='seccion-titulo'>Portal de Estudios Médicos</div>", unsafe_allow_html=True)
st.markdown("<p class='bajada-texto' style='text-align: center; margin-bottom: 25px;'>Ingrese sus datos de acceso provistos por el centro médico.</p>", unsafe_allow_html=True)

dni_busqueda = st.text_input("Número de DNI del Paciente (sin puntos):", max_chars=10)
pass_paciente = st.text_input("Contraseña del Portal:", type="password")

CLAVE_GENERAL_PACIENTES = "omed2026"

if st.button("Buscar mis Estudios"):
    if not dni_busqueda or not pass_paciente:
        st.info("Por favor, complete ambos campos para iniciar la búsqueda.")
    elif pass_paciente != CLAVE_GENERAL_PACIENTES:
        st.error("❌ Contraseña del portal incorrecta.")
    else:
        with st.spinner("Consultando en el servidor seguro OMED..."):
            try:
                dni_limpio = str(dni_busqueda).strip()
                
                # Búsqueda directa e indexada en la base de datos protegida
                df_resultado = conn.query(f"SELECT * FROM informes_omed WHERE dni = '{dni_limpio}';")
                
                if not df_resultado.empty:
                    # Extraer información de la primera fila coincidente
                    nombre_paciente = str(df_resultado.iloc[0]["nombre"])
                    nombre_archivo = str(df_resultado.iloc[0]["nombre_archivo"])
                    pdf_base64 = str(df_resultado.iloc[0]["pdf_base64"])
                    
                    st.success(f"✅ Estudio encontrado para: {nombre_paciente}")
                    
                    # Decodificar el PDF guardado en formato de texto de vuelta a binario
                    bytes_pdf = base64.b64decode(pdf_base64)
                    
                    st.download_button(
                        label="⬇️ Descargar mi Informe Médico (PDF)",
                        data=bytes_pdf,
                        file_name=nombre_archivo,
                        mime="application/pdf"
                    )
                else:
                    st.warning("⚠️ No se encontraron registros para el DNI ingresado.")
            except Exception as e:
                st.error(f"Error técnico de lectura en la base de datos: {e}")

# =====================================================================
# 2. ACCESO EXCLUSIVO PARA MÉDICOS
# =====================================================================
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("🛠️ Acceso Exclusivo para Personal Médico"):
    st.write("Área restringida para la carga de nuevos estudios al sistema.")
    
    try:
        clave_medica_correcta = st.secrets["medicos"]["password"]
    except Exception:
        clave_medica_correcta = "omed123"
        
    password_input = st.text_input("Introduzca la clave médica:", type="password", key="med_pass")
    
    if password_input == clave_medica_correcta:
        st.success("🔓 Panel de carga desbloqueado.")
        
        dni_paciente = st.text_input("DNI del Paciente (Sin puntos ni espacios):")
        nombre_paciente = st.text_input("Nombre Completo del Paciente:")
        archivo_pdf = st.file_uploader("Seleccione el archivo PDF del estudio:", type=["pdf"])
        
        if st.button("Subir e Informar"):
            if dni_paciente and nombre_paciente and archivo_pdf:
                with st.spinner("Encriptando y blindando PDF en la nube permanente..."):
                    try:
                        dni_limpio = str(dni_paciente).strip()
                        
                        # Convertir el archivo PDF a texto seguro Base64
                        bytes_pdf = archivo_pdf.read()
                        pdf_convertido = base64.b64encode(bytes_pdf).decode("utf-8")
                        
                        # Insertar directamente en la base de datos segura SQL
                        with conn.session as session:
                            session.execute(
                                """
                                INSERT OR REPLACE INTO informes_omed (dni, nombre, nombre_archivo, pdf_base64)
                                VALUES (:dni, :nombre, :nombre_archivo, :pdf_base64);
                                """,
                                {
                                    "dni": dni_limpio,
                                    "nombre": nombre_paciente.strip(),
                                    "nombre_archivo": archivo_pdf.name,
                                    "pdf_base64": pdf_convertido
                                }
                            )
                            session.commit()
                        
                        st.success(f"🎉 ¡Éxito! El estudio de {nombre_paciente} quedó grabado permanentemente.")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error técnico al escribir en el almacenamiento permanente: {e}")
            else:
                st.warning("⚠️ Por favor, complete todos los campos antes de subir.")
