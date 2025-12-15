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
from langdetect import detect, DetectorFactory
import requests
from utils.sidebar_common import render_sidebar

# Añadir directorio raíz del proyecto al path
project_root = Path(__file__).resolve().parent.parent
segmenter_path = project_root / "modelo" / "fase3_evaluacion"

# Debug: verificar que los paths existen
if not segmenter_path.exists():
    raise ImportError(f"Segmenter directory not found at: {segmenter_path}")

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(segmenter_path))

# Importar usando importlib para mejor control
import importlib.util
spec = importlib.util.spec_from_file_location(
    "simple_segmenter", 
    str(segmenter_path / "simple_segmenter.py")
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

# Fijar semilla para resultados consistentes en langdetect
DetectorFactory.seed = 0

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
    """Genera una imagen con el texto proporcionado (soporta saltos de línea)."""
    # Dividir texto en líneas
    lineas = texto.split('\n')
    
    # Intentar usar una fuente
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Calcular dimensiones necesarias
    max_width = 0
    line_heights = []
    
    for linea in lineas:
        try:
            # Para fuentes TrueType
            bbox = font.getbbox(linea)
            line_width = bbox[2] - bbox[0]
            line_height = bbox[3] - bbox[1]
        except:
            # Fallback para fuentes sin getbbox
            line_width = len(linea) * (font_size // 2)
            line_height = font_size
        
        max_width = max(max_width, line_width)
        line_heights.append(line_height)
    
    # Dimensiones de la imagen
    width = max(300, max_width + 40)
    total_height = sum(line_heights) + (len(lineas) + 1) * 20  # Espaciado entre líneas
    
    # Crear imagen blanca
    img = Image.new('L', (width, total_height), color=255)
    draw = ImageDraw.Draw(img)
    
    # Dibujar cada línea
    y_offset = 20
    for i, linea in enumerate(lineas):
        draw.text((20, y_offset), linea, fill=0, font=font)
        y_offset += line_heights[i] + 20
    
    return img

def detectar_idioma(texto):
    """Detecta el idioma del texto (español o inglés)."""
    try:
        # Requiere al menos 3 caracteres
        if len(texto.strip()) < 3:
            return "Desconocido"
        
        lang_code = detect(texto)
        
        # Mapear código a nombre
        idiomas = {
            'es': '🇪🇸 Español',
            'en': '🇬🇧 Inglés'
        }
        
        return idiomas.get(lang_code, f"Otro ({lang_code})")
    except:
        return "Desconocido"

def reconocer_texto(img_array, model, scaler, label_mapping):
    """Reconoce texto de una imagen (soporta múltiples líneas)."""
    # Segmentar (ahora devuelve lista de líneas)
    segmenter = SimpleImageSegmenter()
    lineas_segmentadas = segmenter.segment_image(img_array)
    
    if not lineas_segmentadas:
        return None, [], [], None
    
    # Procesar cada línea
    todas_las_lineas = []
    todas_confidencias = []
    todas_letras_imgs = []
    
    for linea_chars in lineas_segmentadas:
        texto_linea = []
        confidencias_linea = []
        
        for letra_img in linea_chars:
            # Asegurar 28x28
            if letra_img.shape != (28, 28):
                img_pil = Image.fromarray(letra_img.astype(np.uint8))
                img_pil = img_pil.resize((28, 28), Image.LANCZOS)
                letra_img = np.array(img_pil)
            
            # INVERTIR COLORES
            letra_img = 255 - letra_img
            
            # Guardar para visualización
            todas_letras_imgs.append(letra_img)
            
            # Aplanar y normalizar
            letra_flat = letra_img.flatten().reshape(1, -1)
            letra_scaled = scaler.transform(letra_flat)
            
            # Predecir
            pred = model.predict(letra_scaled)[0]
            proba = model.predict_proba(letra_scaled)[0]
            
            letra = label_mapping[pred]
            pred_idx = np.where(model.classes_ == pred)[0][0]
            confianza = proba[pred_idx]
            
            texto_linea.append(letra)
            confidencias_linea.append(confianza)
        
        # Reemplazar 'ESPACIO' por espacio real en la línea
        texto_linea_final = ''.join([' ' if l == 'ESPACIO' else l for l in texto_linea])
        todas_las_lineas.append(texto_linea_final)
        todas_confidencias.extend(confidencias_linea)
    
    # Unir líneas con salto de línea
    texto_final = '\n'.join(todas_las_lineas)
    confianza_promedio = np.mean(todas_confidencias) if todas_confidencias else 0
    
    # Detectar idioma
    idioma = detectar_idioma(texto_final)
    
    return texto_final, todas_confidencias, todas_letras_imgs, idioma

def main():
    # Título
    st.title("🔤 OCR - Reconocedor de Texto")
    st.markdown("### Prueba el modelo de reconocimiento de texto")
    
    # Verificar si el modelo existe
    model_path = MODELS_DIR / "modelo.pkl"
    
    # Panel de utilidades al inicio
    if not model_path.exists():
        st.warning("⚠️ Modelo no encontrado. Necesitas configurar el proyecto.")
        
        st.markdown("### 🛠️ Configuración Inicial del Proyecto")
        st.info("""
        Este proceso ejecutará automáticamente:
        1. **Generar imágenes** sintéticas de caracteres (200 para difíciles, 50 para resto)
        2. **Procesar dataset** y crear archivos CSV de entrenamiento
        3. **Entrenar modelo** SVM con los datos generados
        
        ⏱️ Tiempo estimado: 3-5 minutos
        """)
        
        if st.button("🚀 Configurar Proyecto Completo", type="primary", use_container_width=True):
            import subprocess
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            log_expander = st.expander("📋 Ver logs detallados", expanded=True)
            
            try:
                # Paso 1: Generar imágenes
                status_text.text("🎨 Paso 1/3: Generando imágenes...")
                progress_bar.progress(10)
                
                fase1_dir = project_root / "modelo" / "fase1_dataset"
                with log_expander:
                    st.markdown("#### 🎨 Generando Imágenes")
                    result1 = subprocess.run(
                        ["python", "generar_con_puntuacion.py"],
                        cwd=str(fase1_dir),
                        capture_output=True,
                        text=True
                    )
                    st.code(result1.stdout[-1000:] if len(result1.stdout) > 1000 else result1.stdout, language="text")
                    
                    if result1.returncode != 0:
                        st.error(f"❌ Error:\n{result1.stderr}")
                        st.stop()
                
                progress_bar.progress(40)
                
                # Paso 2: Generar dataset
                status_text.text("📊 Paso 2/3: Generando dataset...")
                
                with log_expander:
                    st.markdown("#### 📊 Generando Dataset")
                    result2 = subprocess.run(
                        ["python", "generar_dataset.py"],
                        cwd=str(fase1_dir),
                        capture_output=True,
                        text=True
                    )
                    st.code(result2.stdout[-1000:] if len(result2.stdout) > 1000 else result2.stdout, language="text")
                    
                    if result2.returncode != 0:
                        st.error(f"❌ Error:\n{result2.stderr}")
                        st.stop()
                
                progress_bar.progress(70)
                
                # Paso 3: Entrenar modelo
                status_text.text("🤖 Paso 3/3: Entrenando modelo...")
                
                fase2_dir = project_root / "modelo" / "fase2_entrenamiento"
                with log_expander:
                    st.markdown("#### 🤖 Entrenando Modelo")
                    result3 = subprocess.run(
                        ["python", "entrenar_modelo.py"],
                        cwd=str(fase2_dir),
                        capture_output=True,
                        text=True
                    )
                    st.code(result3.stdout, language="text")
                    
                    if result3.returncode != 0:
                        st.error(f"❌ Error:\n{result3.stderr}")
                        st.stop()
                
                progress_bar.progress(100)
                status_text.text("✅ Configuración completada!")
                
                st.success("🎉 ¡Proyecto configurado exitosamente!")
                st.balloons()
                st.info("🔄 **Recarga la página** para comenzar a usar el modelo")
                
            except Exception as e:
                st.error(f"❌ Error inesperado: {str(e)}")
        
        st.markdown("---")
        st.markdown("### 📝 Pasos Manuales (Opcional)")
        
        with st.expander("⚙️ Ejecutar pasos individuales"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🎨 Solo Imágenes", use_container_width=True):
                    with st.spinner("Generando..."):
                        import subprocess
                        fase1_dir = project_root / "modelo" / "fase1_dataset"
                        result = subprocess.run(
                            ["python", "generar_con_puntuacion.py"],
                            cwd=str(fase1_dir),
                            capture_output=True,
                            text=True
                        )
                        if result.returncode == 0:
                            st.success("✅ Imágenes generadas")
                        else:
                            st.error(f"❌ Error:\n{result.stderr}")
            
            with col2:
                if st.button("📊 Solo Dataset", use_container_width=True):
                    with st.spinner("Procesando..."):
                        import subprocess
                        fase1_dir = project_root / "modelo" / "fase1_dataset"
                        result = subprocess.run(
                            ["python", "generar_dataset.py"],
                            cwd=str(fase1_dir),
                            capture_output=True,
                            text=True
                        )
                        if result.returncode == 0:
                            st.success("✅ Dataset generado")
                        else:
                            st.error(f"❌ Error:\n{result.stderr}")
            
            with col3:
                if st.button("🤖 Solo Entrenar", use_container_width=True):
                    with st.spinner("Entrenando..."):
                        import subprocess
                        fase2_dir = project_root / "modelo" / "fase2_entrenamiento"
                        result = subprocess.run(
                            ["python", "entrenar_modelo.py"],
                            cwd=str(fase2_dir),
                            capture_output=True,
                            text=True
                        )
                        if result.returncode == 0:
                            st.success("✅ Modelo entrenado")
                            st.info("🔄 Recarga la página")
                        else:
                            st.error(f"❌ Error:\n{result.stderr}")
        
        st.stop()
    
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
            texto_input = st.text_area(
                "Texto a reconocer:",
                value="Hola",
                max_chars=200,
                height=100,
                help="Escribe tu texto. Usa Enter para saltos de línea"
            )
        
        with col2:
            font_size = st.slider("Tamaño de fuente:", 30, 100, 60)
        
        if st.button("🔍 Generar y Reconocer", type="primary"):
            if not texto_input:
                st.warning("⚠️ Escribe algo primero")
            else:
                # Validar que solo haya letras, acentos, signos permitidos y saltos de línea (Español, Catalán, Inglés)
                import re
                texto_validado = texto_input
                # Incluye: letras básicas, acentos agudos/graves, diéresis, ñ, ç, apóstrofe, puntuación, saltos de línea
                if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÀÈÌÒÙàèìòùÏÜïüÇçÑñ',.;:!?¿¡\- \n]+", texto_validado):
                    st.warning("⚠️ Solo se permiten letras, acentos, apóstrofe, espacios, saltos de línea y signos de puntuación")
                else:
                    # Generar imagen
                    img = generar_imagen_texto(texto_input, font_size)
                    img_array = np.array(img)
                    
                    # Mostrar imagen generada
                    st.markdown("#### 🖼️ Imagen Generada:")
                    st.image(img, use_container_width=False)
                    
                    # Reconocer
                    with st.spinner("Reconociendo..."):
                        texto_reconocido, confidencias, letras_imgs, idioma = reconocer_texto(
                            img_array, model, scaler, label_mapping
                        )
                    
                    if texto_reconocido is None:
                        st.error("❌ No se pudieron detectar letras")
                    else:
                        # El texto reconocido ya viene con saltos de línea desde segment_image
                        texto_reconocido_final = texto_reconocido
                        
                        # Resultados
                        st.markdown("---")
                        st.markdown("### 📊 Resultados")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**📝 Texto Original:**")
                            st.text_area(
                                "Original",
                                texto_input,
                                height=100,
                                label_visibility="collapsed"
                            )
                        with col2:
                            st.markdown("**✅ Texto Reconocido:**")
                            st.text_area(
                                "Reconocido",
                                texto_reconocido_final,
                                height=100,
                                label_visibility="collapsed"
                            )
                        # Confianza promedio e idioma
                        col_m1, col_m2 = st.columns(2)
                        with col_m1:
                            confianza_promedio = np.mean(confidencias)
                            st.metric("🎯 Confianza Promedio", f"{confianza_promedio*100:.1f}%")
                        with col_m2:
                            st.metric("🌍 Idioma Detectado", idioma)
                        # Verificar si es correcto
                        es_correcto = texto_input == texto_reconocido_final
                        if es_correcto:
                            st.success("✅ ¡Reconocimiento correcto!")
                        else:
                            st.error("❌ Reconocimiento incorrecto")
                        
                        # Mostrar letras individuales
                        st.markdown("#### 🔤 Letras Detectadas:")
                        # Crear lista de letras sin saltos de línea para emparejar con imágenes
                        letras_sin_saltos = [c for c in texto_reconocido_final if c != '\n']
                        st.markdown(f"**Total de caracteres reconocidos: {len(letras_sin_saltos)}**")
                        
                        # Mostrar todas las letras en filas de 10
                        num_letras = len(letras_imgs)
                        for fila in range(0, num_letras, 10):
                            cols = st.columns(min(10, num_letras - fila))
                            for i, col in enumerate(cols):
                                idx = fila + i
                                if idx < num_letras:
                                    with col:
                                        letra_display = letras_sin_saltos[idx] if idx < len(letras_sin_saltos) else "?"
                                        st.image(letras_imgs[idx], caption=f"{letra_display}\n{confidencias[idx]*100:.0f}%", width=50)
    
    # Tab 2: Subir imagen
    with tab2:
        st.markdown("### Sube una imagen con texto")
        
        uploaded_file = st.file_uploader(
            "Selecciona una imagen:",
            type=['png', 'jpg', 'jpeg', 'bmp'],
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
                    texto_reconocido, confidencias, letras_imgs, idioma = reconocer_texto(
                        img_array, model, scaler, label_mapping
                    )
                
                if texto_reconocido is None:
                    st.error("❌ No se pudieron detectar letras")
                else:
                    # Reemplazar 'ESPACIO' por espacio real
                    texto_reconocido_final = ''.join([' ' if l == 'ESPACIO' else l for l in texto_reconocido])
                    # Resultados
                    st.markdown("---")
                    st.markdown("### 📊 Resultados")
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown("**✅ Texto Reconocido:**")
                        st.text_area(
                            "Reconocido",
                            texto_reconocido_final,
                            height=100,
                            label_visibility="collapsed"
                        )
                    with col2:
                        confianza_promedio = np.mean(confidencias)
                        st.metric("🎯 Confianza Promedio", f"{confianza_promedio*100:.1f}%")
                        st.metric("🌍 Idioma", idioma)
                    # Mostrar letras individuales
                    st.markdown("#### 🔤 Letras Detectadas:")
                    # Filtrar saltos de línea para emparejar correctamente con imágenes
                    letras_sin_saltos = [c for c in texto_reconocido_final if c != '\n']
                    st.markdown(f"**Total de caracteres reconocidos: {len(letras_sin_saltos)}**")
                    # Mostrar todas las letras en filas de 10
                    num_letras = len(letras_imgs)
                    for fila in range(0, num_letras, 10):
                        cols = st.columns(min(10, num_letras - fila))
                        for i, col in enumerate(cols):
                            idx = fila + i
                            if idx < num_letras:
                                with col:
                                    letra_display = letras_sin_saltos[idx] if idx < len(letras_sin_saltos) else "?"
                                    st.image(letras_imgs[idx], caption=f"{letra_display}\n{confidencias[idx]*100:.0f}%", width=50)
        else:
            # Mostrar consejos cuando no hay archivo cargado
            st.info("""
            ### 📋 Instrucciones:
            
            1. Haz clic en **"Browse files"** arriba
            2. Selecciona una imagen de tu dispositivo
            3. La imagen debe contener texto claro y legible
            4. Presiona **"Reconocer Texto"** para procesarla
            
            ### ✅ Mejores resultados con:
            - ✏️ Texto negro sobre fondo blanco
            - 📐 Imágenes de alta calidad (mínimo 300 DPI)
            - ➡️ Texto horizontal y bien alineado
            - 🔤 Fuentes claras (Arial, Times, Calibri)
            
            ### ⚠️ Evita:
            - 🌫️ Imágenes borrosas o de baja calidad
            - 👥 Texto con sombras o efectos
            - 🎨 Fondos con ruido o texturas
            - 🔤 Letras muy juntas o superpuestas
            """)
    
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
    
    # Guardar número de clases en session_state para el sidebar
    st.session_state['num_clases'] = len(label_mapping)
    
    # Renderizar sidebar común
    render_sidebar()

if __name__ == "__main__":
    main()
