"""
Aplicación principal de Streamlit - OCR con FastAPI
Arquitectura multipágina con WebSockets, cache, persistencia y chatbot

Elementos de Streamlit implementados:
- ✅ Multipágina: Organización modular con st.Page y st.navigation
- ✅ Session State: Mantener estado entre interacciones
- ✅ Cache: @st.cache_data y @st.cache_resource para optimización
- ✅ Widgets: Inputs, sliders, buttons, file_uploader, etc.
- ✅ Visualización: Charts, métricas, dataframes, imágenes
- ✅ Chat: Chatbot interactivo con historial
- ✅ Persistencia: Datos guardados entre sesiones (localStorage)
"""
import streamlit as st
from pathlib import Path
import json
from datetime import datetime

# Configuración de la página (debe ser lo primero)
st.set_page_config(
    page_title="OCR - Reconocedor de Texto",
    page_icon="🔤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar session_state para persistencia entre interacciones
if 'historial_reconocimientos' not in st.session_state:
    st.session_state.historial_reconocimientos = []

if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

if 'estadisticas' not in st.session_state:
    st.session_state.estadisticas = {
        'total_reconocimientos': 0,
        'total_caracteres': 0,
        'confianza_promedio': 0.0,
        'idiomas_detectados': {}
    }

# Definir las páginas de la aplicación
# Justificación: Organización multipágina para separar funcionalidades y mejorar UX
pagina_escribir = st.Page(
    "pages/escribir_texto.py",
    title="Escribir Texto",
    icon="📝",
    default=True
)

pagina_subir = st.Page(
    "pages/subir_imagen.py",
    title="Subir Imagen",
    icon="📷"
)

# Nueva página: Chatbot OCR Assistant
# Justificación: Interfaz conversacional para guiar usuarios y responder dudas
pagina_chat = st.Page(
    "pages/chatbot.py",
    title="Chat Assistant",
    icon="💬"
)

# Nueva página: Dashboard con visualizaciones
# Justificación: Análisis visual de datos y estadísticas de uso
pagina_dashboard = st.Page(
    "pages/dashboard.py",
    title="Dashboard",
    icon="📊"
)

# Navegación con agrupación lógica
# Justificación: Mejor organización visual de funcionalidades
pg = st.navigation({
    "🔤 Reconocimiento": [pagina_escribir, pagina_subir],
    "📈 Análisis": [pagina_dashboard],
    "💬 Asistencia": [pagina_chat]
})

# Sidebar con información común
with st.sidebar:
    # Configuración de API
    st.markdown("### 🔌 Configuración de API")
    
    # Inicializar API URL si no existe
    if 'api_url' not in st.session_state:
        st.session_state.api_url = "http://localhost:8000"
    
    # Selector de modo
    modo_api = st.radio(
        "Modo de conexión:",
        ["Local (localhost)", "Red local (otra IP)"],
        key="modo_conexion",
        help="Local: API en este mismo PC. Red local: API en otro dispositivo de tu red"
    )
    
    if modo_api == "Red local (otra IP)":
        ip_custom = st.text_input(
            "IP de la API:",
            placeholder="192.168.1.100",
            help="Introduce la IP del dispositivo donde corre la API"
        )
        puerto = st.text_input("Puerto:", value="8000")
        
        if ip_custom:
            st.session_state.api_url = f"http://{ip_custom}:{puerto}"
        else:
            st.warning("⚠️ Introduce una IP válida")
    else:
        st.session_state.api_url = "http://localhost:8000"
    
    # Mostrar URL actual
    st.code(st.session_state.api_url, language="text")
    
    # Estado de la API (con cache)
    from utils.api_utils import verificar_api, get_api_url
    
    st.markdown("### 📡 Estado de la Conexión")
    
    # Botón para refrescar estado
    if st.button("🔄 Verificar conexión", use_container_width=True):
        st.cache_data.clear()
    
    api_status = verificar_api()
    if api_status:
        st.success("✅ API conectada")
    else:
        st.error("❌ API desconectada")
        st.info("""
        ### 🚀 Inicia la API
        
        **En local:**
        ```bash
        cd FastAPI
        python main.py
        ```
        
        **En red local (otros dispositivos):**
        ```bash
        cd FastAPI
        python main.py -g
        ```
        
        Con `-g` la API mostrará la IP para conectar desde otros dispositivos.
        """)
    
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
    
    ### ⚠️ Limitaciones
    - Dificultad para diferenciar I/l en algunas fuentes
    - Mejor rendimiento con Arial, Times, Calibri
    """)
    
    st.markdown("---")
    st.markdown("### 📊 Información Técnica")
    st.info(f"""
    **API**: `{get_api_url()}`
    **Modelo**: SVM Linear
    **Idiomas**: ES, CA, EN
    **Precisión**: ~96%
    """)


# Ejecutar la página seleccionada
pg.run()
