"""
Interfaz Streamlit para probar el modelo OCR usando FastAPI
"""

import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
from langdetect import detect, DetectorFactory
import hashlib
from utils.sidebar_common import render_sidebar
from utils.api_utils import verificar_api, reconocer_texto_api

# Añadir directorio raíz del proyecto al path
project_root = Path(__file__).resolve().parent.parent

# Determinar el ejecutable de Python correcto
venv_python = project_root / ".venv" / "Scripts" / "python.exe"
if venv_python.exists():
    PYTHON_EXECUTABLE = str(venv_python)
else:
    PYTHON_EXECUTABLE = sys.executable  # Fallback al Python actual

# Paths para configuración inicial
MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

# Configuración de la página
st.set_page_config(
    page_title="OCR - Reconocedor de Texto",
    page_icon="🔤",
    layout="wide"
)

# Fijar semilla para resultados consistentes en langdetect
DetectorFactory.seed = 0

def calcular_hash_imagen(img):
    """Calcula un hash MD5 de una imagen PIL para usarlo como clave de caché."""
    # Convertir la imagen a bytes
    img_array = np.array(img)
    img_bytes = img_array.tobytes()
    # Calcular hash MD5
    return hashlib.md5(img_bytes).hexdigest()

@st.cache_data(max_entries=10, show_spinner=False)
def reconocer_texto_cacheado(img_hash, img_array_bytes, img_shape):
    """
    Versión cacheada de reconocer_texto_api.
    Cachea las últimas 10 predicciones basándose en el hash de la imagen.
    
    Args:
        img_hash: Hash MD5 de la imagen (para identificación única)
        img_array_bytes: Array de imagen como bytes (para reconstrucción)
        img_shape: Forma del array original
    
    Returns:
        Tupla (texto_reconocido, confidencias, idioma)
    """
    # Reconstruir la imagen PIL desde bytes
    img_array = np.frombuffer(img_array_bytes, dtype=np.uint8).reshape(img_shape)
    img = Image.fromarray(img_array, mode='L')
    
    # Llamar a la API
    return reconocer_texto_api(img)

# Función ya no necesaria, usamos verificar_api() de api_utils

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

def guardar_reconocimiento(texto_reconocido, confianza_promedio, idioma, num_caracteres):
    """Guarda el reconocimiento en el historial de session_state."""
    from datetime import datetime
    
    # Crear registro del reconocimiento
    reconocimiento = {
        'timestamp': datetime.now(),
        'texto': texto_reconocido,
        'confianza_promedio': confianza_promedio,
        'idioma': idioma,
        'num_caracteres': num_caracteres
    }
    
    # Agregar al historial
    st.session_state.historial_reconocimientos.append(reconocimiento)
    
    # Actualizar estadísticas
    st.session_state.estadisticas['total_reconocimientos'] += 1
    st.session_state.estadisticas['total_caracteres'] += num_caracteres
    
    # Actualizar idiomas detectados
    if idioma not in st.session_state.estadisticas['idiomas_detectados']:
        st.session_state.estadisticas['idiomas_detectados'][idioma] = 0
    st.session_state.estadisticas['idiomas_detectados'][idioma] += 1

# La función reconocer_texto ya no es necesaria, usamos la API

def main():
    # Inicializar session_state para el historial
    if 'historial_reconocimientos' not in st.session_state:
        st.session_state.historial_reconocimientos = []
    
    if 'estadisticas' not in st.session_state:
        st.session_state.estadisticas = {
            'total_reconocimientos': 0,
            'total_caracteres': 0,
            'idiomas_detectados': {}
        }
    
    # Título
    st.title("🔤 OCR - Reconocedor de Texto")
    st.markdown("### Prueba el modelo de reconocimiento de texto")
    
    # Verificar si el modelo existe
    model_path = MODELS_DIR / "modelo.pkl"
    
    # Panel de utilidades al inicio
    if not model_path.exists():
        st.warning("Modelo no encontrado. Necesitas configurar el proyecto.")
        
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
                        [PYTHON_EXECUTABLE, "generar_con_puntuacion.py"],
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
                        [PYTHON_EXECUTABLE, "generar_dataset.py"],
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
                        [PYTHON_EXECUTABLE, "entrenar_modelo.py"],
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
                            [PYTHON_EXECUTABLE, "generar_con_puntuacion.py"],
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
                            [PYTHON_EXECUTABLE, "generar_dataset.py"],
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
                            [PYTHON_EXECUTABLE, "entrenar_modelo.py"],
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
    
    # Verificar que la API esté disponible
    api_ok = verificar_api()
    if not api_ok:
        st.error("⚠️ La API FastAPI no está disponible. Inicia el servidor para continuar.")
        st.code("cd FastAPI && python main.py", language="bash")
        st.info("💡 La aplicación ahora usa FastAPI para todas las predicciones")
        st.stop()
    
    # Tabs para diferentes modos
    tab1, tab2, tab3 = st.tabs(["📝 Escribir Texto", "📷 Subir Imagen", "📁 Explorador de Archivos"])
    
    # Tab 1: Escribir texto
    with tab1:
        st.markdown("### Escribe texto para generar y reconocer")
        
        # Inicializar contadores de caché en session_state
        if 'cache_hits' not in st.session_state:
            st.session_state.cache_hits = 0
        if 'cache_misses' not in st.session_state:
            st.session_state.cache_misses = 0
        
        # Información de caché
        col_info1, col_info2, col_info3 = st.columns([2, 1, 1])
        with col_info1:
            st.info("💾 Las últimas 10 predicciones se guardan en caché para optimizar rendimiento")
        with col_info2:
            total = st.session_state.cache_hits + st.session_state.cache_misses
            if total > 0:
                tasa = (st.session_state.cache_hits / total) * 100
                st.metric("Tasa de aciertos", f"{tasa:.0f}%", 
                         delta=f"{st.session_state.cache_hits}/{total}")
        with col_info3:
            if st.button("🗑️ Limpiar Caché", help="Elimina todas las predicciones guardadas"):
                reconocer_texto_cacheado.clear()
                st.session_state.cache_hits = 0
                st.session_state.cache_misses = 0
                st.success("✅ Caché limpiada")
                st.rerun()
        
        # Expandible con información sobre caché
        with st.expander("ℹ️ ¿Cómo funciona el sistema de caché?"):
            st.markdown("""
            ### 💾 Sistema de Caché Inteligente
            
            **¿Qué es?**
            - El caché almacena las últimas **10 predicciones** realizadas
            - Usa el contenido de la imagen (hash MD5) como identificador único
            
            **¿Por qué es útil?**
            - ⚡ **Velocidad**: Si generas la misma imagen dos veces, no vuelve a llamar a la API
            - 🔄 **Eficiencia**: Ideal para imágenes sintéticas repetitivas (ej: "Hola" con mismo tamaño)
            - 📊 **Ahorro**: Reduce llamadas innecesarias a FastAPI
            
            **¿Cuándo se usa?**
            - Si escribes "Hola" con tamaño 60 → Se guarda en caché
            - Si vuelves a escribir "Hola" con tamaño 60 → ⚡ Carga instantánea desde caché
            - Si escribes "Hola" con tamaño 70 → Nueva predicción (diferente imagen)
            
            **Gestión:**
            - Usa el botón "🗑️ Limpiar Caché" para resetear todas las predicciones guardadas
            - El caché se limpia automáticamente al reiniciar la aplicación
            """)
        
        st.markdown("---")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            texto_input = st.text_area(
                "Texto a reconocer:",
                value="Dennis  y  Pol\n¿Cómo estáis?",
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
                    
                    # Calcular hash de la imagen para caché
                    img_hash = calcular_hash_imagen(img)
                    img_bytes = img_array.tobytes()
                    
                    # Verificar si ya está en caché usando el hash
                    cache_key = f"cache_{img_hash}"
                    fue_cache_hit = cache_key in st.session_state
                    
                    # Guardar estado del caché antes de la llamada
                    if fue_cache_hit:
                        st.session_state.cache_hits += 1
                    else:
                        st.session_state.cache_misses += 1
                        # Marcar que este hash fue procesado
                        st.session_state[cache_key] = True
                    
                    # Reconocer usando API con caché
                    with st.spinner("Reconociendo con API..."):
                        texto_reconocido, confidencias, idioma = reconocer_texto_cacheado(
                            img_hash, img_bytes, img_array.shape
                        )
                    
                    # Mostrar si se usó caché
                    if fue_cache_hit:
                        st.success("⚡ Predicción cargada desde caché (sin llamada a API)")
                    
                    if texto_reconocido is None or not texto_reconocido.strip():
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
                        
                        # Guardar reconocimiento en historial
                        num_caracteres = len([c for c in texto_reconocido_final if c != '\n'])
                        guardar_reconocimiento(texto_reconocido_final, confianza_promedio, idioma, num_caracteres)
                        
                        # Verificar si es correcto
                        es_correcto = texto_input == texto_reconocido_final
                        if es_correcto:
                            st.success("✅ ¡Reconocimiento correcto!")
                        else:
                            st.error("❌ Reconocimiento incorrecto")
                        
                        # Mostrar detalles de confianza
                        st.markdown("#### 📊 Detalles de Confianza")
                        if confidencias:
                            import pandas as pd
                            letras_sin_saltos = [c for c in texto_reconocido_final if c != '\n']
                            df_conf = pd.DataFrame({
                                'Posición': range(1, len(letras_sin_saltos) + 1),
                                'Carácter': [c if c != ' ' else '␣' for c in letras_sin_saltos],
                                'Confianza': [f"{c*100:.1f}%" for c in confidencias[:len(letras_sin_saltos)]]
                            })
                            st.dataframe(df_conf, use_container_width=True, hide_index=True)
    
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
                # Reconocer usando API
                with st.spinner("Reconociendo con API..."):
                    texto_reconocido_final, confidencias, idioma = reconocer_texto_api(img)
                
                if texto_reconocido_final is None or not texto_reconocido_final.strip():
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
                            texto_reconocido_final,
                            height=100,
                            label_visibility="collapsed"
                        )
                    with col2:
                        confianza_promedio = np.mean(confidencias)
                        st.metric("🎯 Confianza Promedio", f"{confianza_promedio*100:.1f}%")
                        st.metric("🌍 Idioma", idioma)
                    
                    # Guardar reconocimiento en historial
                    num_caracteres = len([c for c in texto_reconocido_final if c != '\n'])
                    guardar_reconocimiento(texto_reconocido_final, confianza_promedio, idioma, num_caracteres)
                    
                    # Mostrar tabla de confianzas
                    st.markdown("#### 📊 Tabla de Confianzas:")
                    import pandas as pd
                    letras_sin_saltos = [c for c in texto_reconocido_final if c != '\n']
                    df_conf = pd.DataFrame({
                        'Posición': range(1, len(letras_sin_saltos) + 1),
                        'Carácter': [c if c != ' ' else '␣' for c in letras_sin_saltos],
                        'Confianza': [f"{c*100:.1f}%" for c in confidencias[:len(letras_sin_saltos)]]
                    })
                    st.dataframe(df_conf, use_container_width=True, hide_index=True)
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
                        # Reconocer usando API
                        with st.spinner("Reconociendo con API..."):
                            texto_reconocido, confidencias, idioma = reconocer_texto_api(img)
                        
                        if texto_reconocido is None or not texto_reconocido.strip():
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
                                st.metric("🌍 Idioma", idioma)
                            
                            # Guardar reconocimiento en historial
                            num_caracteres = len([c for c in texto_reconocido if c != '\n'])
                            guardar_reconocimiento(texto_reconocido, confianza_promedio, idioma, num_caracteres)
                            
                            # Mostrar tabla de confianzas
                            st.markdown("#### 📊 Tabla de Confianzas:")
                            import pandas as pd
                            letras_sin_saltos = [c for c in texto_reconocido if c != '\n']
                            df_conf = pd.DataFrame({
                                'Posición': range(1, len(letras_sin_saltos) + 1),
                                'Carácter': [c if c != ' ' else '␣' for c in letras_sin_saltos],
                                'Confianza': [f"{c*100:.1f}%" for c in confidencias[:len(letras_sin_saltos)]]
                            })
                            st.dataframe(df_conf, use_container_width=True, hide_index=True)
                
                except Exception as e:
                    st.error(f"❌ Error al cargar la imagen: {str(e)}")
    
    # Número de clases del modelo (91 clases)
    st.session_state['num_clases'] = 91
    
    # Renderizar sidebar común
    render_sidebar()

if __name__ == "__main__":
    main()
