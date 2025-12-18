"""
Utilidades para comunicación con la API FastAPI
Incluye cache para optimizar rendimiento
"""
import streamlit as st
import requests
import io
from PIL import Image
import urllib3

# Desactivar advertencias de SSL para certificados autofirmados
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_api_url():
    """Obtiene la URL de la API desde session_state o usa el default."""
    if 'api_url' not in st.session_state:
        st.session_state.api_url = "localhost:8000"
    return st.session_state.api_url

# Compatibilidad con código existente
@property
def API_URL():
    return get_api_url()

# Función para uso directo
def get_api_base_url():
    return get_api_url()

def _probar_conexion(api_url, endpoint="/health", method="get", **kwargs):
    """Intenta conectar con HTTP primero, luego HTTPS."""
    # Si la URL ya tiene protocolo (de verificación previa), usarla directamente primero
    if "://" in api_url:
        url = f"{api_url}{endpoint}"
        try:
            if method == "get":
                response = requests.get(url, timeout=kwargs.get('timeout', 2), verify=False)
            elif method == "post":
                response = requests.post(url, timeout=kwargs.get('timeout', 30), verify=False, **kwargs)
            
            if response.status_code in [200, 201]:
                return response
        except Exception as e:
            # Si falla con el protocolo conocido, intentar los otros
            print(f"Falló con URL guardada: {e}")
    
    # Extraer host:puerto sin protocolo
    if "://" in api_url:
        host_port = api_url.split("://", 1)[1]
    else:
        host_port = api_url
    
    # Intentar HTTP primero, luego HTTPS
    for protocol in ["http", "https"]:
        url = f"{protocol}://{host_port}{endpoint}"
        try:
            if method == "get":
                response = requests.get(url, timeout=kwargs.get('timeout', 2), verify=False)
            elif method == "post":
                response = requests.post(url, timeout=kwargs.get('timeout', 30), verify=False, **kwargs)
            
            if response.status_code in [200, 201]:
                # Actualizar session_state con protocolo que funcionó
                st.session_state['api_url'] = f"{protocol}://{host_port}"
                return response
        except Exception as e:
            print(f"Falló {protocol}: {e}")
            continue
    
    return None

@st.cache_data(ttl=30)  # Cache por 30 segundos
def verificar_api(api_url=None):
    """Verifica si la API está disponible."""
    if api_url is None:
        api_url = get_api_url()
    
    response = _probar_conexion(api_url, endpoint="/health", method="get")
    return response is not None and response.status_code == 200

def reconocer_texto_api(img):
    """
    Reconoce texto usando la API de FastAPI.
    
    Args:
        img: Imagen PIL
        
    Returns:
        tuple: (texto, confidencias, idioma)
    """
    api_url = get_api_url()
    
    # Debug: mostrar qué URL se está usando
    debug_info = st.empty()
    debug_info.caption(f"🔗 Intentando conectar a: `{api_url}`")
    
    try:
        # Convertir imagen PIL a bytes en formato PNG
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        # Preparar el archivo para envío multipart/form-data
        files = {'file': ('image.png', img_byte_arr, 'image/png')}
        
        # Enviar petición POST a FastAPI con progreso (prueba HTTP y HTTPS)
        with st.spinner('🔄 Procesando imagen en el servidor...'):
            response = _probar_conexion(api_url, endpoint="/upload-image/", method="post", files=files)
        
        # Limpiar debug
        debug_info.empty()
        
        if response and response.status_code == 200:
            resultado = response.json()
            
            # El idioma ya viene detectado desde la API
            idioma = resultado.get('idioma', 'Desconocido')
            texto = resultado.get('texto', '')
            confidencias = resultado.get('confidencias', [])
            
            return texto, confidencias, idioma
        elif response and response.status_code == 400:
            # No se detectaron letras
            return None, [], "Error"
        elif response:
            st.error(f"❌ Error {response.status_code}: {response.text}")
            return None, [], "Error"
        else:
            st.error("❌ No se pudo conectar a la API con HTTP ni HTTPS")
            return None, [], "Error"
            
    except requests.exceptions.Timeout:
        st.error("⏱️ Timeout: La API tardó demasiado en responder (>30s)")
        return None, [], "Error"
    except requests.exceptions.ConnectionError:
        st.error("🔌 Error de conexión: No se puede conectar con la API. ¿Está ejecutándose FastAPI en http://localhost:8000?")
        return None, [], "Error"
    except Exception as e:
        st.error(f"❌ Error inesperado: {str(e)}")
        import traceback
        with st.expander("🔍 Ver detalles del error"):
            st.code(traceback.format_exc())
        return None, [], "Error"

def mostrar_resultados(texto_original, texto_reconocido, confidencias, idioma):
    """
    Muestra los resultados del reconocimiento de forma organizada.
    
    Args:
        texto_original: Texto original (None si no aplica)
        texto_reconocido: Texto reconocido por OCR
        confidencias: Lista de confianzas
        idioma: Idioma detectado
    """
    st.markdown("---")
    st.markdown("### 📊 Resultados")
    
    if texto_original:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📝 Texto Original:**")
            st.text_area("Original", texto_original, height=100, label_visibility="collapsed", key="orig")
        with col2:
            st.markdown("**✅ Texto Reconocido:**")
            st.text_area("Reconocido", texto_reconocido, height=100, label_visibility="collapsed", key="rec")
    else:
        st.markdown("**✅ Texto Reconocido:**")
        st.text_area("Reconocido", texto_reconocido, height=100, label_visibility="collapsed", key="rec_solo")
    
    # Métricas
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        import numpy as np
        confianza_promedio = np.mean(confidencias)
        st.metric("🎯 Confianza Promedio", f"{confianza_promedio*100:.1f}%")
    with col_m2:
        st.metric("🌍 Idioma Detectado", idioma)
    with col_m3:
        st.metric("📏 Longitud", len(texto_reconocido))
    
    # Verificar si es correcto (si hay original)
    if texto_original:
        es_correcto = texto_original == texto_reconocido
        if es_correcto:
            st.success("✅ ¡Reconocimiento correcto!")
        else:
            st.error("❌ Reconocimiento incorrecto")
            
            # Mostrar diferencias
            with st.expander("🔍 Ver diferencias"):
                st.markdown("**Diferencias encontradas:**")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.text(f"Original:   '{texto_original}'")
                with col_b:
                    st.text(f"Reconocido: '{texto_reconocido}'")
    
    # Detalles de confianza
    st.markdown("#### 📊 Confianza por letra:")
    st.markdown(f"**Total de letras reconocidas: {len(texto_reconocido)}**")
    
    with st.expander("📋 Ver detalles de cada letra"):
        # Mostrar en tabla
        import pandas as pd
        
        data = {
            "Posición": list(range(1, len(texto_reconocido) + 1)),
            "Letra": list(texto_reconocido.replace(' ', '␣')),  # Usar símbolo visible para espacios
            "Confianza": [f"{conf*100:.1f}%" for conf in confidencias]
        }
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)
