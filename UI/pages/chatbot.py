"""
Página: Chatbot OCR Interactivo
Chatbot que procesa imágenes y devuelve texto reconocido + idioma

Elementos de Streamlit:
- ✅ st.chat_message: Mensajes de chat con roles
- ✅ st.file_uploader: Subir imágenes en el chat
- ✅ st.image: Mostrar imagen subida
- ✅ Session State: Mantener historial de conversación
- ✅ Integración con API OCR
"""
import streamlit as st
import sys
sys.path.append('..')
from utils.api_utils import verificar_api, reconocer_texto_api
from utils.sidebar_common import render_sidebar
from datetime import datetime
from PIL import Image
import io

st.title("💬 OCR Chat")
st.markdown("Sube una imagen para reconocer el texto 🔍")

# Renderizar sidebar común
render_sidebar()

# Justificación: Session state para mantener historial de chat y estado de espera de imagen
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

if 'esperando_imagen' not in st.session_state:
    st.session_state.esperando_imagen = False

# Inicializar historial de reconocimientos si no existe (para el dashboard)
if 'historial_reconocimientos' not in st.session_state:
    st.session_state.historial_reconocimientos = []

if 'estadisticas' not in st.session_state:
    st.session_state.estadisticas = {
        'total_reconocimientos': 0,
        'total_caracteres': 0,
        'idiomas_detectados': {}
    }

# Función para agregar mensajes
def agregar_mensaje(rol, contenido, imagen=None):
    """
    Justificación: Función helper para mantener consistencia en el formato
    Soporta mensajes con texto e imágenes
    """
    st.session_state.chat_messages.append({
        "rol": rol,
        "contenido": contenido,
        "imagen": imagen,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

# Mensaje inicial del asistente
if len(st.session_state.chat_messages) == 0:
    agregar_mensaje("assistant", "👋 Sube una imagen para reconocer texto + idioma")

# Verificar estado de la API
api_ok = verificar_api()
if not api_ok:
    st.error("⚠️ La API no está disponible. Inicia FastAPI para usar el chatbot.")
    st.code("cd FastAPI && uvicorn main:app --reload", language="bash")
    st.stop()

# Mostrar historial de chat
# Justificación: Visualización de conversación con contexto completo
st.markdown("---")
for msg in st.session_state.chat_messages:
    with st.chat_message(msg["rol"]):
        st.markdown(msg["contenido"])
        st.caption(f"🕐 {msg['timestamp']}")
        
        # Mostrar imagen si existe en el mensaje
        if msg.get("imagen"):
            st.image(msg["imagen"], use_container_width=True)

# File uploader para imágenes en el chat
st.markdown("---")
st.markdown("#### 📤 Subir imagen:")

uploaded_file = st.file_uploader(
    "Imagen:",
    type=['png', 'jpg', 'jpeg', 'bmp'],
    help="PNG, JPG, JPEG o BMP",
    key="chat_uploader"
)

if uploaded_file is not None:
    # Convertir a imagen PIL
    try:
        img = Image.open(uploaded_file)
        
        # Agregar mensaje del usuario con la imagen
        agregar_mensaje("user", f"📷 `{uploaded_file.name}`", imagen=img)
        
        # Reconocer texto usando la API (devuelve tupla: texto, confidencias, idioma)
        texto, confidencias, idioma = reconocer_texto_api(img)
        
        if texto and texto.strip():  # Verificar que no esté vacío
            # Calcular confianza promedio
            import numpy as np
            confianza_promedio = np.mean(confidencias) if confidencias else 0
            
            # Respuesta minimalista del asistente
            respuesta = f"""📝 **Texto:** {texto}

🌍 **Idioma:** {idioma}
📊 **Confianza:** {confianza_promedio*100:.0f}%"""
            
            agregar_mensaje("assistant", respuesta)
            
            # Guardar en historial (igual que en app.py)
            if 'historial_reconocimientos' in st.session_state:
                from datetime import datetime
                num_caracteres = len([c for c in texto if c != '\n'])
                reconocimiento = {
                    'timestamp': datetime.now(),
                    'texto': texto,
                    'confianza_promedio': confianza_promedio,
                    'idioma': idioma,
                    'num_caracteres': num_caracteres
                }
                st.session_state.historial_reconocimientos.append(reconocimiento)
                
                # Actualizar estadísticas
                st.session_state.estadisticas['total_reconocimientos'] += 1
                st.session_state.estadisticas['total_caracteres'] += num_caracteres
                if idioma not in st.session_state.estadisticas['idiomas_detectados']:
                    st.session_state.estadisticas['idiomas_detectados'][idioma] = 0
                st.session_state.estadisticas['idiomas_detectados'][idioma] += 1
        else:
            # Agregar información de debug
            import numpy as np
            img_array = np.array(img.convert('L'))
            debug_info = f"\n\n🔍 **Debug:**\n- Tamaño: {img.size}\n- Shape: {img_array.shape}\n- Min/Max: {np.min(img_array)}/{np.max(img_array)}"
            agregar_mensaje("assistant", f"❌ No se detectó texto en la imagen.{debug_info}\n\n💡 **Consejos:**\n- Texto negro sobre fondo blanco\n- Imagen clara y legible\n- Revisa los logs de FastAPI para más detalles")
    
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        agregar_mensaje("assistant", f"⚠️ Error al procesar la imagen:\n```\n{str(e)}\n```\n\n🔍 Ver terminal de FastAPI para más detalles.")
        print(f"Error en chatbot: {error_detail}")
    
    # Limpiar el uploader y rerun
    st.session_state.pop('chat_uploader', None)
    st.rerun()

# Botón para limpiar chat
st.markdown("---")
col_clear, col_stats = st.columns(2)

with col_clear:
    if st.button("🗑️ Limpiar", use_container_width=True):
        st.session_state.chat_messages = []
        st.rerun()

with col_stats:
    # Mostrar conteo de mensajes
    st.metric("💬 Mensajes", len(st.session_state.chat_messages))

# Información sobre el chatbot
with st.expander("ℹ️ Info"):
    st.markdown("""
    **Chatbot OCR**
    
    Sube imágenes → Reconoce texto + idioma
    
    **Formatos:** PNG, JPG, JPEG, BMP  
    **Idiomas:** Español, Catalán, Inglés  
    **Modelo:** SVM (91 clases de caracteres)
    """)
