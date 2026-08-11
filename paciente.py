import streamlit as st
import sqlite3
import os

DB_NAME = "centro_medico.db"
STORAGE_DIR = "estudios_firmados"
os.makedirs(STORAGE_DIR, exist_ok=True)

# Crear base de datos unificada
def iniciar_sistema():
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

iniciar_sistema()

# Panel de navegación arriba de todo
opcion = st.sidebar.selectbox("Seleccione el Portal", ["📥 Portal del Paciente", "🔒 Acceso Médicos"])

# ==================== PORTAL PACIENTE ====================
if opcion == "📥 Portal del Paciente":
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

# ==================== PORTAL MÉDICOS ====================
elif opcion == "🔒 Acceso Médicos":
    def check_password():
        def password_entered():
            if st.session_state["username"] == "admin" and st.session_state["password"] == "omed2026":
                st.session_state["password_correct"] = True
                del st.session_state["password"]  
                del st.session_state["username"]
            else:
                st.session_state["password_correct"] = False

        if "password_correct" not in st.session_state:
            st.title("🔒 Acceso Restringido - Centro Médico")
            st.write("Por favor, identifíquese para cargar estudios.")
            st.text_input("Usuario", key="username")
            st.text_input("Contraseña", type="password", key="password")
            st.button("Iniciar Sesión", on_click=password_entered)
            return False
        elif not st.session_state["password_correct"]:
            st.title("🔒 Acceso Restringido - Centro Médico")
            st.text_input("Usuario", key="username")
            st.text_input("Contraseña", type="password", key="password")
            st.button("Iniciar Sesión", on_click=password_entered)
            st.error("❌ Usuario o contraseña incorrectos")
            return False
        return True

    if check_password():
        st.title("🏥 Panel Médico - Carga de Estudios")
        st.subheader("Cargar nuevo informe para paciente")

        dni = st.text_input("DNI del Paciente (sin puntos)").strip()
        
        tipo = st.selectbox("Tipo de Estudio", [
            "Análisis Clínicos", "Anatomía Patológica", "Audiología", "Cardiología", 
            "Clínica Médica", "Ecografías", "Endocrinología", "Fisiatría (Kinesiología)", 
            "Fonoaudiología", "Ginecología", "Neumología", "Odontología", 
            "Oftalmología", "Otorrinolaringología (ORL)", "Psicología", "Traumatología", "Otros"
        ])
        
        archivo = st.file_uploader("Arrastrá el archivo PDF aquí", type=["pdf"])

        if st.button("Guardar y Subir Estudio"):
            if dni and tipo and archivo:
                nombre_seguro = f"{dni}_{tipo}_{archivo.name}".replace(" ", "_")
                ruta_completa = os.path.join(STORAGE_DIR, nombre_seguro)
                
                with open(ruta_completa, "wb") as f:
                    f.write(archivo.getbuffer())
                
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO estudios (dni_paciente, tipo_estudio, nombre_archivo) VALUES (?, ?, ?)", 
                               (dni, tipo, nombre_seguro))
                conn.commit()
                conn.close()
                
                st.success(f"✅ ¡Éxito! El estudio de {tipo} fue asignado al DNI {dni}.")
            else:
                st.error("⚠️ Por favor, completá todos los campos y subí un archivo.")

