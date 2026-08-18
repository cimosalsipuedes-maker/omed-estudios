import streamlit as st
import pandas as pd
import os

# Configuración de la página unificada y profesional
st.set_page_config(page_title="Portal Médico OMED", page_icon="🏥", layout="centered")

# Nombre del archivo base de datos local
DB_FILE = "base_datos_informes.csv"
CARPETA_PDFS = "estudios_medicos_respaldo"

# Creamos la base de datos y la carpeta de almacenamiento de forma automática si no existen
if not os.path.exists(DB_FILE):
    df_init = pd.DataFrame(columns=["DNI", "Nombre", "Enlace_PDF"])
    df_init.to_csv(DB_FILE, index=False)

if not os.path.exists(CARPETA_PDFS):
    os.makedirs(CARPETA_PDFS)

# =====================================================================
# 1. INTERFAZ PÚBLICA: PORTAL DEL PACIENTE
# =====================================================================
st.title("🏥 Portal de Estudios Médicos - OMED")
st.write("Bienvenido. Ingrese su número de documento para descargar sus resultados.")

# Buscador para el paciente
dni_busqueda = st.text_input("Ingrese su número de DNI (sin puntos):", max_chars=10)

if st.button("Buscar mis Estudios"):
    if dni_busqueda:
        with st.spinner("Buscando en el sistema..."):
            try:
                # Leemos la base de datos local
                df = pd.read_csv(DB_FILE)
                
                # Convertimos la columna a texto limpio para que coincida siempre
                df["DNI"] = df["DNI"].astype(str).str.strip()
                dni_limpio = str(dni_busqueda).strip()
                
                # Buscamos el registro correspondiente al DNI
                registro = df[df["DNI"] == dni_limpio]
                
                if not registro.empty:
                    # Extracción segura de celdas por valores nativos
                    nombre_paciente = registro["Nombre"].values[0]
                    ruta_archivo_pdf = registro["Enlace_PDF"].values[0]
                    
                    st.success(f"✅ Estudio encontrado para: {nombre_paciente}")
                    
                    # Verificamos que el archivo físico realmente exista en el servidor
                    if os.path.exists(ruta_archivo_pdf):
                        with open(ruta_archivo_pdf, "rb") as f:
                            bytes_pdf = f.read()
                        
                        # BOTÓN CORREGIDO: Cambiado 'mimetype' por 'mime' para evitar el error
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
    else:
        st.info("Por favor, escriba un número de DNI para iniciar la búsqueda.")

# =====================================================================
# 2. ACCESO EXCLUSIVO PARA MÉDICOS (Panel oculto seguro de producción)
# =====================================================================
st.markdown("---")
with st.expander("🛠️ Acceso Exclusivo para Personal Médico"):
    st.write("Área restringida para la carga de nuevos estudios al sistema.")
    
    password_input = st.text_input("Introduzca la clave médica:", type="password", key="med_pass")
    
    if password_input == "omed123":
        st.success("🔓 Panel de carga desbloqueado.")
        
        # Formulario interno de carga de datos
        dni_paciente = st.text_input("DNI del Paciente (Sin puntos ni espacios):")
        nombre_paciente = st.text_input("Nombre Completo del Paciente:")
        archivo_pdf = st.file_uploader("Seleccione el archivo PDF del estudio:", type=["pdf"])
        
        if st.button("Subir e Informar"):
            if dni_paciente and nombre_paciente and archivo_pdf:
                with st.spinner("Guardando PDF de forma permanente y registrando..."):
                    try:
                        # 1. Definimos el nombre y la ruta final donde se alojará el archivo
                        nombre_seguro = f"{dni_paciente}_{archivo_pdf.name.replace(' ', '_')}"
                        ruta_destino_final = os.path.join(CARPETA_PDFS, nombre_seguro)
                        
                        # 2. Guardamos físicamente el archivo PDF de manera permanente dentro del servidor
                        with open(ruta_destino_final, "wb") as f:
                            f.write(archivo_pdf.getbuffer())
                        
                        # 3. Registramos la información de manera permanente en el archivo CSV local
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
