"""
Página: Escribir Texto
Permite al usuario escribir texto y reconocerlo
"""
import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import sys
sys.path.append('..')
from utils.api_utils import reconocer_texto_api, mostrar_resultados, verificar_api
import re

st.title("📝 Escribir Texto")
st.markdown("### Escribe texto para generar y reconocer")

# Verificar API
if not verificar_api():
    st.error("❌ La API no está disponible. Por favor, iníciala primero.")
    st.stop()

@st.cache_data
def generar_imagen_texto(texto, font_size=60):
    """Genera una imagen con el texto proporcionado."""
    # Calcular tamaño de imagen
    width = max(300, len(texto) * font_size)
    height = font_size + 40
    
    # Crear imagen blanca
    img = Image.new('L', (width, height), color=255)
    draw = ImageDraw.Draw(img)
    
    # Intentar usar una fuente
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Dibujar texto negro
    draw.text((20, 10), texto, fill=0, font=font)
    
    return img

# Formulario de entrada
col1, col2 = st.columns([2, 1])

with col1:
    texto_input = st.text_input(
        "Texto a reconocer:",
        value="Hola mundo",
        max_chars=50,
        help="Solo letras (A-Z, a-z), acentos y signos de puntuación"
    )

with col2:
    font_size = st.slider("Tamaño de fuente:", 30, 100, 60)

# Botón de reconocimiento
if st.button("🔍 Generar y Reconocer", type="primary", use_container_width=True):
    if not texto_input:
        st.warning("⚠️ Escribe algo primero")
    else:
        # Validar caracteres permitidos
        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÀÈÌÒÙàèìòùÏÜïüÇçÑñ',.;:!?¿¡\- ]+", texto_input):
            st.warning("⚠️ Solo se permiten letras, acentos, apóstrofe, espacios y signos de puntuación")
        else:
            # Generar imagen
            with st.spinner('🎨 Generando imagen...'):
                img = generar_imagen_texto(texto_input, font_size)
            
            # Mostrar imagen generada
            st.markdown("#### 🖼️ Imagen Generada:")
            st.image(img, use_container_width=False)
            
            # Reconocer
            texto_reconocido, confidencias, idioma = reconocer_texto_api(img)
            
            if texto_reconocido is None:
                st.error("❌ No se pudieron detectar letras")
            else:
                # Guardar en historial (Session State para Dashboard)
                from datetime import datetime
                st.session_state.historial_reconocimientos.append({
                    'texto': texto_reconocido,
                    'confianza_promedio': np.mean(confidencias),
                    'idioma': idioma,
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                })
                
                # Actualizar estadísticas
                st.session_state.estadisticas['total_reconocimientos'] += 1
                st.session_state.estadisticas['total_caracteres'] += len(texto_reconocido)
                
                # Contar idiomas
                if idioma in st.session_state.estadisticas['idiomas_detectados']:
                    st.session_state.estadisticas['idiomas_detectados'][idioma] += 1
                else:
                    st.session_state.estadisticas['idiomas_detectados'][idioma] = 1
                
                # Mostrar resultados
                mostrar_resultados(texto_input, texto_reconocido, confidencias, idioma)

# Información adicional
with st.expander("ℹ️ Información sobre esta función"):
    st.markdown("""
    Esta página permite:
    1. **Escribir** cualquier texto (español, catalán, inglés)
    2. **Generar** una imagen sintética del texto
    3. **Reconocer** el texto de la imagen usando OCR
    4. **Comparar** el texto original con el reconocido
    
    Es útil para:
    - 🧪 Probar el modelo con diferentes textos
    - 📊 Ver la precisión en diferentes fuentes y tamaños
    - 🔍 Identificar caracteres problemáticos
    """)
