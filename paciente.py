import streamlit as st
import sqlite3
import os

DB_NAME = "centro_medico.db"
STORAGE_DIR = "estudios_firmados"

def iniciar_db_paciente():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estudios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dni_paciente TEXT NOT NULL,
            tipo_estudio TEXT NOT NULL,
            nombre_archivo TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

iniciar_db_paciente()

st.title("🏥 Portal del Paciente - Descarga de Estudios")
st.write("Ingresá tu documento para ver y descargar tus resultados.")

dni_busqueda = st.text_input("Número de DNI").strip()

if st.button("Buscar mis Estudios"):
    if dni_busqueda:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT tipo_estudio, nombre_archivo, fecha FROM estudios WHERE dni_paciente = ?", (dni_busqueda,))
        resultados = cursor.fetchall()
        conn.close()
        
        if resultados:
            st.success(f"Se encontraron {len(resultados)} estudios disponibles:")
            for tipo, archivo, fecha in resultados:
                ruta_archivo = os.path.join(STORAGE_DIR, archivo)
                
                if os.path.exists(ruta_archivo):
                    with open(ruta_archivo, "rb") as f:
                        bytes_archivo = f.read()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"📄 **{tipo}** (Subido el: {fecha[:10]})")
                    with col2:
                        st.download_button(
                            label="📥 Descargar PDF",
                            data=bytes_archivo,
                            file_name=archivo,
                            mime="application/pdf",
                            key=archivo
                        )
                else:
                    st.warning(f"El archivo {tipo} figura en sistema pero no se encuentra en el servidor.")
        else:
            st.info("🔍 No se encontraron estudios para el DNI ingresado. Verificá el número o consultá en recepción.")
    else:
        st.error("⚠️ Por favor, ingresá un número de DNI válido.")
