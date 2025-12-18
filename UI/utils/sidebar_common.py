"""
Sidebar común para todas las páginas de la aplicación
"""
import streamlit as st
import socket
import requests
import urllib3

# Desactivar advertencias de SSL para certificados autofirmados
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def verificar_conexion_api(api_url):
    """Verifica si la API FastAPI está disponible. Intenta HTTP primero, luego HTTPS."""
    # Asegurar que api_url no tenga protocolo duplicado
    api_url = api_url.strip()
    if api_url.startswith("http://") or api_url.startswith("https://"):
        base_url = api_url
    else:
        base_url = f"http://{api_url}"
    
    # Extraer host:puerto sin protocolo
    if "://" in base_url:
        host_port = base_url.split("://", 1)[1]
    else:
        host_port = base_url
    
    # Intentar HTTP primero
    for protocol in ["http", "https"]:
        url = f"{protocol}://{host_port}"
        try:
            response = requests.get(f"{url}/health", timeout=2, verify=False)
            if response.status_code == 200:
                data = response.json()
                # Actualizar session_state con la URL que funcionó
                st.session_state['api_url'] = url
                return True, data, url
        except requests.exceptions.ConnectionError:
            continue
        except requests.exceptions.Timeout:
            continue
        except Exception:
            continue
    
    # Si ninguno funcionó
    return False, {"error": "No se pudo conectar con HTTP ni HTTPS"}, base_url

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
            api_url = "localhost:8000"
            st.info("📍 API: localhost:8000\n💡 Se probará HTTP y HTTPS automáticamente")
        else:  # IP Personalizada
            # Sugerir la IP local como valor por defecto (solo IP:PUERTO)
            try:
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
                default_ip = f"{local_ip}:8000"
            except:
                default_ip = "192.168.1.100:8000"
            
            custom_ip = st.text_input(
                "Dirección de la API:",
                value=default_ip,
                placeholder="IP:PUERTO (ej: 192.168.1.100:8000)",
                help="Introduce solo la IP y puerto. La app probará HTTP y HTTPS automáticamente",
                key="custom_ip_sidebar"
            )
            # Limpiar y usar la IP ingresada
            api_url = custom_ip.strip() if custom_ip else "localhost:8000"
            st.info(f"📍 API: {api_url}\n💡 Se probará HTTP y HTTPS automáticamente")
        
        # Guardar en session_state temporalmente (sin protocolo)
        # La URL final con protocolo se guardará después de verificar conexión
        if 'api_url' not in st.session_state or st.session_state.get('api_base') != api_url:
            st.session_state['api_url'] = api_url
            st.session_state['api_base'] = api_url
        
        # Botón para verificar conexión
        if st.button("🔍 Verificar Conexión", use_container_width=True, key="verificar_conexion_sidebar"):
            with st.spinner("Verificando HTTP y HTTPS..."):
                conectado, data, url_final = verificar_conexion_api(api_url)
                
                if conectado:
                    protocol = "🔒 HTTPS" if url_final.startswith("https") else "🌐 HTTP"
                    st.success(f"✅ Conexión exitosa ({protocol})")
                    st.info(f"📍 URL final: {url_final}")
                    # Actualizar con la URL que funcionó (ya se hace en verificar_conexion_api)
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
