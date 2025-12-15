"""
Sidebar común para todas las páginas de la aplicación
"""
import streamlit as st
import socket
import requests

def verificar_conexion_api(api_url):
    """Verifica si la API FastAPI está disponible."""
    try:
        response = requests.get(f"{api_url}/health", timeout=2)
        if response.status_code == 200:
            data = response.json()
            return True, data
        else:
            return False, None
    except requests.exceptions.ConnectionError:
        return False, {"error": "No se pudo conectar"}
    except requests.exceptions.Timeout:
        return False, {"error": "Timeout"}
    except Exception as e:
        return False, {"error": str(e)}

def render_sidebar():
    """Renderiza el sidebar común para todas las páginas."""
    with st.sidebar:
        st.markdown("### 🌐 Conexión con API")
        modo_red = st.radio(
            "Modo de conexión:",
            ["Localhost", "IP Personalizada"],
            help="Selecciona cómo conectarte a la API FastAPI",
            key="modo_red_sidebar"
        )
        
        if modo_red == "Localhost":
            api_url = "http://localhost:8000"
            st.info("📍 API: localhost:8000")
        else:  # IP Personalizada
            # Sugerir la IP local como valor por defecto
            try:
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
                default_ip = f"http://{local_ip}:8000"
            except:
                default_ip = "http://192.168.1.100:8000"
            
            custom_ip = st.text_input(
                "Dirección de la API:",
                value=default_ip,
                placeholder="http://IP:PUERTO",
                help="Introduce la URL completa de la API (incluye http:// y el puerto)",
                key="custom_ip_sidebar"
            )
            api_url = custom_ip if custom_ip else "http://localhost:8000"
            st.info(f"📍 API: {api_url}")
        
        # Guardar en session_state para uso en otras páginas
        st.session_state['api_url'] = api_url
        
        # Botón para verificar conexión
        if st.button("🔍 Verificar Conexión", use_container_width=True, key="verificar_conexion_sidebar"):
            with st.spinner("Verificando..."):
                conectado, data = verificar_conexion_api(api_url)
                
                if conectado:
                    st.success("✅ Conexión exitosa")
                    if data.get('modelo_cargado'):
                        st.success("✅ Modelo cargado en API")
                    else:
                        st.warning("⚠️ API conectada pero modelo no cargado")
                else:
                    st.error("❌ No se pudo conectar a la API")
                    if data and 'error' in data:
                        st.caption(f"Error: {data['error']}")
                    st.info("💡 Asegúrate de ejecutar: `python FastAPI/main.py`")
        
        st.markdown("---")
        st.markdown("### ℹ️ Información del Modelo")
        st.markdown("""
        Este modelo OCR reconoce:
        - **91 clases de caracteres**
        - **Español**: A-Z, a-z, áéíóú, ñ, ü, puntuación
        - **Catalán**: àèò, ï, ç
        - **Inglés**: apóstrofe (')
        - **Precisión**: ~96%
        - **Resolución**: 28x28 píxeles
        
        ### 📝 Consejos
        - Usa texto negro sobre fondo blanco
        - Fuente clara y legible
        - El texto debe estar horizontal
        - Evita letras muy juntas
        - **Usa \\n para saltos de línea**
        
        ### ⚠️ Limitaciones
        - Dificultad para diferenciar I/l en algunas fuentes
        - Mejor rendimiento con Arial, Times, Calibri
        """)
        
        st.markdown("---")
        st.markdown("### 📊 Estadísticas")
        # Intentar obtener el número de clases desde session_state
        num_clases = st.session_state.get('num_clases', 91)
        st.info(f"**Clases**: {num_clases}\n**Modelo**: SVM Linear\n**Idiomas**: ES, CA, EN")
        
        st.markdown("---")
        st.markdown("### 🛠️ Utilidades")
        if st.button("🔄 Reentrenar Modelo", use_container_width=True, key="reentrenar_modelo_sidebar"):
            st.info("Para reentrenar, ejecuta en terminal:\n\n1. `cd modelo/fase1_dataset`\n2. `python generar_con_puntuacion.py`\n3. `python generar_dataset.py`\n4. `cd ../fase2_entrenamiento`\n5. `python entrenar_modelo.py`")
