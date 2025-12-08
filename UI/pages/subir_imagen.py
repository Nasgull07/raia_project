"""
Página: Subir Imagen
Permite al usuario subir una imagen desde su dispositivo
"""
import streamlit as st
from PIL import Image
import sys
sys.path.append('..')
from utils.api_utils import reconocer_texto_api, mostrar_resultados, verificar_api

st.title("📷 Subir Imagen")
st.markdown("### Sube una imagen con texto")

# Verificar API
if not verificar_api():
    st.error("❌ La API no está disponible. Por favor, iníciala primero.")
    st.stop()

# File uploader
uploaded_file = st.file_uploader(
    "Selecciona una imagen:",
    type=['png', 'jpg', 'jpeg', 'bmp'],
    help="Imagen con texto negro sobre fondo blanco"
)

if uploaded_file is not None:
    # Cargar imagen
    img = Image.open(uploaded_file).convert('L')
    
    # Mostrar información de la imagen
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📐 Ancho", f"{img.width}px")
    with col2:
        st.metric("📏 Alto", f"{img.height}px")
    with col3:
        st.metric("💾 Tamaño", f"{uploaded_file.size / 1024:.1f}KB")
    
    # Mostrar imagen
    st.markdown("#### 🖼️ Imagen Cargada:")
    st.image(img, use_container_width=True)
    
    # Botón de reconocimiento
    if st.button("🔍 Reconocer Texto", type="primary", use_container_width=True, key="btn_upload"):
        # Reconocer
        texto_reconocido, confidencias, idioma = reconocer_texto_api(img)
        
        if texto_reconocido is None:
            st.error("❌ No se pudieron detectar letras")
        else:
            # Guardar en historial
            from datetime import datetime
            import numpy as np
            st.session_state.historial_reconocimientos.append({
                'texto': texto_reconocido,
                'confianza_promedio': np.mean(confidencias),
                'idioma': idioma,
                'timestamp': datetime.now().strftime("%H:%M:%S")
            })
            
            # Actualizar estadísticas
            st.session_state.estadisticas['total_reconocimientos'] += 1
            st.session_state.estadisticas['total_caracteres'] += len(texto_reconocido)
            
            if idioma in st.session_state.estadisticas['idiomas_detectados']:
                st.session_state.estadisticas['idiomas_detectados'][idioma] += 1
            else:
                st.session_state.estadisticas['idiomas_detectados'][idioma] = 1
            
            # Mostrar resultados (sin texto original)
            mostrar_resultados(None, texto_reconocido, confidencias, idioma)

else:
    # Mostrar instrucciones cuando no hay archivo
    st.info("""
    ### 📋 Instrucciones:
    
    1. Haz clic en "Browse files" arriba
    2. Selecciona una imagen de tu dispositivo
    3. La imagen debe contener texto claro y legible
    4. Presiona "Reconocer Texto" para procesarla
    
    ### ✅ Mejores resultados con:
    - Texto negro sobre fondo blanco
    - Imágenes de alta calidad (mínimo 300 DPI)
    - Texto horizontal y bien alineado
    - Fuentes claras (Arial, Times, Calibri)
    
    ### ⚠️ Evita:
    - Imágenes borrosas o de baja calidad
    - Texto con sombras o efectos
    - Fondos con ruido o texturas
    - Letras muy juntas o superpuestas
    """)

# Información adicional
with st.expander("ℹ️ Información sobre esta función"):
    st.markdown("""
    Esta página permite:
    1. **Subir** imágenes desde tu dispositivo
    2. **Visualizar** la imagen antes de procesarla
    3. **Reconocer** el texto automáticamente
    4. **Analizar** la confianza de cada carácter
    
    Formatos soportados:
    - 🖼️ PNG (recomendado)
    - 📷 JPG/JPEG
    - 🎨 BMP
    
    La imagen se envía de forma segura a la API mediante protocolo HTTP POST con multipart/form-data.
    """)
