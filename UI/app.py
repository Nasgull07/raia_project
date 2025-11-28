"""
Interfaz Streamlit para probar el modelo OCR
"""

import sys
import os
from pathlib import Path
import numpy as np
import pickle
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

# Añadir directorio raíz del proyecto al path
project_root = Path(__file__).resolve().parent.parent
utils_path = project_root / "utils"

# Debug: verificar que los paths existen
if not utils_path.exists():
    raise ImportError(f"Utils directory not found at: {utils_path}")

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(utils_path))

# Importar usando importlib para mejor control
import importlib.util
spec = importlib.util.spec_from_file_location(
    "simple_segmenter", 
    str(utils_path / "simple_segmenter.py")
)
simple_segmenter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(simple_segmenter)
SimpleImageSegmenter = simple_segmenter.SimpleImageSegmenter

# Paths
MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Configuración de la página
st.set_page_config(
    page_title="OCR - Reconocedor de Texto",
    page_icon="🔤",
    layout="wide"
)

@st.cache_resource
def cargar_modelo():
    """Carga el modelo y el scaler."""
    model_path = MODELS_DIR / "modelo.pkl"
    scaler_path = MODELS_DIR / "scaler.pkl"
    mapping_path = DATA_DIR / "mapping.txt"
    
    if not model_path.exists():
        st.error("❌ Modelo no encontrado. Ejecuta primero: `python scripts/2_entrenar_modelo.py`")
        st.stop()
    
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    with open(scaler_path, 'rb') as f:
        scaler = pickle.load(f)
    
    # Cargar mapping
    label_mapping = {}
    with open(mapping_path, 'r', encoding='utf-8') as f:
        for line in f:
            label, letter = line.strip().split()
            label_mapping[int(label)] = letter
    
    return model, scaler, label_mapping

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

def reconocer_texto(img_array, model, scaler, label_mapping):
    """Reconoce texto de una imagen."""
    # Segmentar
    segmenter = SimpleImageSegmenter()
    letras_segmentadas = segmenter.segment_word(img_array)
    
    if not letras_segmentadas:
        return None, [], []
    
    # Predecir cada letra
    texto_reconocido = []
    confidencias = []
    letras_imgs = []
    
    for letra_img in letras_segmentadas:
        # Asegurar 28x28
        if letra_img.shape != (28, 28):
            img_pil = Image.fromarray(letra_img.astype(np.uint8))
            img_pil = img_pil.resize((28, 28), Image.LANCZOS)
            letra_img = np.array(img_pil)
        
        # INVERTIR COLORES
        letra_img = 255 - letra_img
        
        # Guardar para visualización
        letras_imgs.append(letra_img)
        
        # Aplanar y normalizar
        letra_flat = letra_img.flatten().reshape(1, -1)
        letra_scaled = scaler.transform(letra_flat)
        
        # Predecir
        pred = model.predict(letra_scaled)[0]
        proba = model.predict_proba(letra_scaled)[0]
        
        letra = label_mapping[pred]
        pred_idx = np.where(model.classes_ == pred)[0][0]
        confianza = proba[pred_idx]
        
        texto_reconocido.append(letra)
        confidencias.append(confianza)
    
    texto_final = ''.join(texto_reconocido)
    confianza_promedio = np.mean(confidencias)
    
    return texto_final, confidencias, letras_imgs

def main():
    # Título
    st.title("🔤 OCR - Reconocedor de Texto")
    st.markdown("### Prueba el modelo de reconocimiento de texto")
    st.markdown("---")
    
    # Cargar modelo
    with st.spinner("Cargando modelo..."):
        model, scaler, label_mapping = cargar_modelo()
    
    # Tabs para diferentes modos
    tab1, tab2, tab3 = st.tabs(["📝 Escribir Texto", "📷 Subir Imagen", "📁 Explorador de Archivos"])
    
    # Tab 1: Escribir texto
    with tab1:
        st.markdown("### Escribe texto para generar y reconocer")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            texto_input = st.text_input(
                "Texto a reconocer:",
                value="Hola",
                max_chars=50,
                help="Solo letras (A-Z, a-z)"
            )
        
        with col2:
            font_size = st.slider("Tamaño de fuente:", 30, 100, 60)
        
        if st.button("🔍 Generar y Reconocer", type="primary"):
            if not texto_input:
                st.warning("⚠️ Escribe algo primero")
            else:
                # Validar que solo haya letras, acentos y signos permitidos
                import re
                texto_validado = texto_input
                if not re.fullmatch(r'[A-Za-zÁÉÍÓÚáéíóúÑñÜü,.;:!?¿¡ ]+', texto_validado):
                    st.warning("⚠️ Solo se permiten letras, acentos, espacios y signos de puntuación (,.;:!?¿¡)")
                else:
                    # Generar imagen
                    img = generar_imagen_texto(texto_input, font_size)
                    img_array = np.array(img)
                    # Mostrar imagen generada
                    st.markdown("#### 🖼️ Imagen Generada:")
                st.image(img, use_container_width=False)
                
                # Reconocer
                with st.spinner("Reconociendo..."):
                    texto_reconocido, confidencias, letras_imgs = reconocer_texto(
                        img_array, model, scaler, label_mapping
                    )
                
                if texto_reconocido is None:
                    st.error("❌ No se pudieron detectar letras")
                else:
                    # Resultados
                    st.markdown("---")
                    st.markdown("### 📊 Resultados")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**📝 Texto Original:**")
                        st.text_area(
                            "Original",
                            texto_input.replace(' ', ''),
                            height=100,
                            label_visibility="collapsed"
                        )
                    
                    with col2:
                        st.markdown("**✅ Texto Reconocido:**")
                        st.text_area(
                            "Reconocido",
                            texto_reconocido,
                            height=100,
                            label_visibility="collapsed"
                        )
                    
                    # Confianza promedio
                    confianza_promedio = np.mean(confidencias)
                    st.metric("🎯 Confianza Promedio", f"{confianza_promedio*100:.1f}%")
                    
                    # Verificar si es correcto
                    es_correcto = texto_input.replace(' ', '') == texto_reconocido
                    if es_correcto:
                        st.success("✅ ¡Reconocimiento correcto!")
                    else:
                        st.error("❌ Reconocimiento incorrecto")
                    
                    # Mostrar letras individuales
                    st.markdown("#### 🔤 Letras Detectadas:")
                    st.markdown(f"**Total de letras reconocidas: {len(texto_reconocido)}**")
                    
                    # Mostrar todas las letras en filas de 10
                    num_letras = len(letras_imgs)
                    for fila in range(0, num_letras, 10):
                        cols = st.columns(min(10, num_letras - fila))
                        for i, col in enumerate(cols):
                            idx = fila + i
                            if idx < num_letras:
                                with col:
                                    st.image(letras_imgs[idx], caption=f"{texto_reconocido[idx]}\n{confidencias[idx]*100:.0f}%", width=50)
    
    # Tab 2: Subir imagen
    with tab2:
        st.markdown("### Sube una imagen con texto")
        
        uploaded_file = st.file_uploader(
            "Selecciona una imagen:",
            type=['png', 'jpg', 'jpeg'],
            help="Imagen con texto negro sobre fondo blanco"
        )
        
        if uploaded_file is not None:
            # Cargar imagen
            img = Image.open(uploaded_file).convert('L')
            img_array = np.array(img)
            
            # Mostrar imagen
            st.markdown("#### 🖼️ Imagen Cargada:")
            st.image(img, use_container_width=False)
            
            # Reconocer
            if st.button("🔍 Reconocer Texto", type="primary", key="btn_upload"):
                with st.spinner("Reconociendo..."):
                    texto_reconocido, confidencias, letras_imgs = reconocer_texto(
                        img_array, model, scaler, label_mapping
                    )
                
                if texto_reconocido is None:
                    st.error("❌ No se pudieron detectar letras")
                else:
                    # Resultados
                    st.markdown("---")
                    st.markdown("### 📊 Resultados")
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown("**✅ Texto Reconocido:**")
                        st.text_area(
                            "Reconocido",
                            texto_reconocido,
                            height=100,
                            label_visibility="collapsed"
                        )
                    
                    with col2:
                        confianza_promedio = np.mean(confidencias)
                        st.metric("🎯 Confianza Promedio", f"{confianza_promedio*100:.1f}%")
                    
                    # Mostrar letras individuales
                    st.markdown("#### 🔤 Letras Detectadas:")
                    st.markdown(f"**Total de letras reconocidas: {len(texto_reconocido)}**")
                    
                    # Mostrar todas las letras en filas de 10
                    num_letras = len(letras_imgs)
                    for fila in range(0, num_letras, 10):
                        cols = st.columns(min(10, num_letras - fila))
                        for i, col in enumerate(cols):
                            idx = fila + i
                            if idx < num_letras:
                                with col:
                                    st.image(letras_imgs[idx], caption=f"{texto_reconocido[idx]}\n{confidencias[idx]*100:.0f}%", width=50)
                    
                    # Detalles de cada letra
                    with st.expander("📋 Detalles de cada letra"):
                        for i, (letra, conf) in enumerate(zip(texto_reconocido, confidencias)):
                            st.write(f"**Letra {i+1}:** `{letra}` - Confianza: **{conf*100:.1f}%**")
    
    # Tab 3: Explorador de archivos
    with tab3:
        st.markdown("### Selecciona una imagen desde el explorador de archivos")
        
        # Input para la ruta del archivo
        file_path_input = st.text_input(
            "Ruta completa de la imagen:",
            placeholder=r"C:\ruta\a\tu\imagen.png",
            help="Ingresa la ruta completa del archivo de imagen"
        )
        
        # Botón para examinar (instrucciones)
        st.info("💡 **Consejo**: Copia y pega la ruta completa de tu imagen desde el explorador de Windows")
        
        if file_path_input:
            # Verificar que el archivo existe
            file_path = Path(file_path_input)
            
            if not file_path.exists():
                st.error(f"❌ El archivo no existe: {file_path_input}")
            elif file_path.suffix.lower() not in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
                st.error("❌ Formato no soportado. Use: PNG, JPG, JPEG, BMP o GIF")
            else:
                try:
                    # Cargar imagen
                    img = Image.open(file_path).convert('L')
                    img_array = np.array(img)
                    
                    # Mostrar imagen
                    st.markdown("#### 🖼️ Imagen Cargada:")
                    st.image(img, use_container_width=False)
                    st.success(f"✅ Imagen cargada: {file_path.name}")
                    
                    # Reconocer
                    if st.button("🔍 Reconocer Texto", type="primary", key="btn_file"):
                        with st.spinner("Reconociendo..."):
                            texto_reconocido, confidencias, letras_imgs = reconocer_texto(
                                img_array, model, scaler, label_mapping
                            )
                        
                        if texto_reconocido is None:
                            st.error("❌ No se pudieron detectar letras")
                        else:
                            # Resultados
                            st.markdown("---")
                            st.markdown("### 📊 Resultados")
                            
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown("**✅ Texto Reconocido:**")
                                st.text_area(
                                    "Reconocido",
                                    texto_reconocido,
                                    height=100,
                                    label_visibility="collapsed"
                                )
                            
                            with col2:
                                confianza_promedio = np.mean(confidencias)
                                st.metric("🎯 Confianza Promedio", f"{confianza_promedio*100:.1f}%")
                            
                            # Mostrar letras individuales
                            st.markdown("#### 🔤 Letras Detectadas:")
                            st.markdown(f"**Total de letras reconocidas: {len(texto_reconocido)}**")
                            
                            # Mostrar todas las letras en filas de 10
                            num_letras = len(letras_imgs)
                            for fila in range(0, num_letras, 10):
                                cols = st.columns(min(10, num_letras - fila))
                                for i, col in enumerate(cols):
                                    idx = fila + i
                                    if idx < num_letras:
                                        with col:
                                            st.image(letras_imgs[idx], caption=f"{texto_reconocido[idx]}\n{confidencias[idx]*100:.0f}%", width=50)
                            
                            # Detalles de cada letra
                            with st.expander("📋 Detalles de cada letra"):
                                for i, (letra, conf) in enumerate(zip(texto_reconocido, confidencias)):
                                    st.write(f"**Letra {i+1}:** `{letra}` - Confianza: **{conf*100:.1f}%**")
                
                except Exception as e:
                    st.error(f"❌ Error al cargar la imagen: {str(e)}")
    
    # Sidebar con información
    with st.sidebar:
        st.markdown("### ℹ️ Información")
        st.markdown("""
        Este modelo OCR reconoce:
        - **52 clases**: A-Z, a-z
        - **Precisión**: ~99%
        - **Letras individuales**: 28x28 píxeles
        
        ### 📝 Consejos
        - Usa texto negro sobre fondo blanco
        - Evita fuentes muy decorativas
        - El texto debe estar horizontal
        """)
        
        st.markdown("---")
        st.markdown("### 📊 Estadísticas del Modelo")
        st.info(f"**Clases**: {len(label_mapping)}\n\n**Modelo**: SVM Linear")

if __name__ == "__main__":
    main()
