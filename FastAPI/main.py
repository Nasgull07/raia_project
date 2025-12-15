"""
API FastAPI para reconocimiento de texto OCR
"""
import sys
from pathlib import Path
import numpy as np
import pickle
from PIL import Image
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import io
import base64
from typing import List
from langdetect import detect, DetectorFactory

# Fijar semilla para resultados consistentes en langdetect
DetectorFactory.seed = 0

# Añadir directorio raíz al path
project_root = Path(__file__).resolve().parent.parent
segmenter_path = project_root / "modelo" / "fase3_evaluacion"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(segmenter_path))

# Importar segmentador
import importlib.util
spec = importlib.util.spec_from_file_location(
    "simple_segmenter", 
    str(segmenter_path / "simple_segmenter.py")
)
simple_segmenter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(simple_segmenter)
SimpleImageSegmenter = simple_segmenter.SimpleImageSegmenter

# Inicializar FastAPI
app = FastAPI(title="OCR API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables globales para el modelo
model = None
scaler = None
label_mapping = None

# Modelos de datos
class RecognitionResponse(BaseModel):
    texto: str
    confianza_promedio: float
    letras: List[str]
    confidencias: List[float]
    idioma: str

@app.on_event("startup")
async def cargar_modelo():
    """Carga el modelo al iniciar la aplicación."""
    global model, scaler, label_mapping
    
    # Usar la carpeta models de la raíz del proyecto
    models_dir = Path(__file__).parent.parent / "models"
    data_dir = Path(__file__).parent.parent / "data"
    
    model_path = models_dir / "modelo.pkl"
    scaler_path = models_dir / "scaler.pkl"
    mapping_path = data_dir / "mapping.txt"
    
    if not model_path.exists():
        raise FileNotFoundError(f"Modelo no encontrado en {model_path}")
    
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
    
    print("[OK] Modelo cargado correctamente")

def detectar_idioma(texto):
    """Detecta el idioma del texto reconocido."""
    try:
        if len(texto.strip()) < 3:
            return "Desconocido"
        
        lang_code = detect(texto)
        
        idiomas = {
            'es': '🇪🇸 Español',
            'en': '🇬🇧 Inglés',
            'ca': '🇪🇸 Catalán',
            'fr': '🇫🇷 Francés',
            'de': '🇩🇪 Alemán',
            'it': '🇮🇹 Italiano',
            'pt': '🇵🇹 Portugués'
        }
        
        return idiomas.get(lang_code, f"Otro ({lang_code})")
    except:
        return "Desconocido"

def reconocer_texto(img_array):
    """Reconoce texto de una imagen."""
    # Segmentar
    segmenter = SimpleImageSegmenter()
    letras_segmentadas = segmenter.segment_word(img_array)
    
    if not letras_segmentadas:
        return None
    
    # Predecir cada letra
    texto_reconocido = []
    confidencias = []
    
    for letra_img in letras_segmentadas:
        # Asegurar 28x28
        if letra_img.shape != (28, 28):
            img_pil = Image.fromarray(letra_img.astype(np.uint8))
            img_pil = img_pil.resize((28, 28), Image.LANCZOS)
            letra_img = np.array(img_pil)
        
        # Invertir colores
        letra_img = 255 - letra_img
        
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
        confidencias.append(float(confianza))
    
    # Reemplazar 'ESPACIO' por espacio real
    texto_final = ''.join([' ' if l == 'ESPACIO' else l for l in texto_reconocido])
    confianza_promedio = float(np.mean(confidencias))
    
    # Detectar idioma
    idioma = detectar_idioma(texto_final)
    
    return {
        "texto": texto_final,
        "confianza_promedio": confianza_promedio,
        "letras": texto_reconocido,
        "confidencias": confidencias,
        "idioma": idioma
    }

@app.get("/")
async def root():
    """Endpoint raíz."""
    return {
        "mensaje": "API OCR funcionando",
        "version": "1.0.0",
        "endpoints": ["/upload-image/", "/health"]
    }

@app.get("/health")
async def health():
    """Verificar estado de la API."""
    return {
        "status": "ok",
        "modelo_cargado": model is not None
    }

@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    """
    Recibe una imagen desde Streamlit y reconoce el texto.
    Endpoint compatible con el patrón de enviarFitxerStreamlit-ServerAPI.py
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Modelo no cargado")
    
    try:
        # Nombre del archivo
        filename = file.filename
        print(f"📥 Recibiendo imagen: {filename}")
        
        # Leer contenido en bytes
        contents = await file.read()
        print(f"📦 Tamaño: {len(contents)} bytes")
        
        # Convertir bytes a imagen PIL en escala de grises
        img = Image.open(io.BytesIO(contents)).convert('L')
        img_array = np.array(img)
        print(f"🖼️  Imagen cargada: {img_array.shape}")
        
        # Guardar imagen recibida para debug
        debug_dir = Path(__file__).parent / "debug_images"
        debug_dir.mkdir(exist_ok=True)
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        debug_path = debug_dir / f"{timestamp}_{filename}"
        img.save(debug_path)
        print(f"💾 Imagen guardada en: {debug_path}")
        
        # Procesar con el modelo OCR
        resultado = reconocer_texto(img_array)
        
        if resultado is None:
            raise HTTPException(status_code=400, detail="No se pudieron detectar letras en la imagen")
        
        print(f"✅ Texto reconocido: {resultado['texto']}")
        
        # Retornar JSON con resultados
        return JSONResponse(content={
            "filename": filename,
            "size": len(contents),
            "texto": resultado["texto"],
            "confianza_promedio": resultado["confianza_promedio"],
            "letras": resultado["letras"],
            "confidencias": resultado["confidencias"],
            "idioma": resultado["idioma"]
        })
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"❌ ERROR: {error_detail}")
        raise HTTPException(status_code=500, detail=f"Error al procesar imagen: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    import argparse
    
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description='Servidor API OCR')
    parser.add_argument('-g', '--global', dest='global_access', action='store_true',
                        help='Ejecutar en la red local (accesible desde otros dispositivos)')
    parser.add_argument('--https', action='store_true',
                        help='Habilitar HTTPS (requiere cert.pem y key.pem)')
    args = parser.parse_args()
    
    # Determinar host según el argumento
    if args.global_access:
        import socket
        import platform
        
        # Obtener todas las IPs de red (filtrar WSL/Hyper-V/Loopback)
        hostname = socket.gethostname()
        
        # Obtener IP real de la red local
        try:
            # Conectar a un servidor externo para obtener la IP de red activa
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except:
            # Fallback al método antiguo
            local_ip = socket.gethostbyname(hostname)
        
        print(f"[RED] Ejecutando en red local")
        print(f"   - Acceso local: http://localhost:8000")
        print(f"   - Acceso en red: http://{local_ip}:8000")
        print(f"\n[AVISO] Asegúrate de que el firewall permita conexiones en el puerto 8000")
        if platform.system() == "Windows":
            print(f"   Ejecuta como Admin: netsh advfirewall firewall add rule name=\"FastAPI OCR\" dir=in action=allow protocol=TCP localport=8000")
        host = "0.0.0.0"
    else:
        print(f"🏠 Ejecutando en modo local")
        print(f"   - Acceso: http://localhost:8000")
        host = "127.0.0.1"
    
    # Configurar HTTPS si se solicita
    ssl_keyfile = None
    ssl_certfile = None
    protocol = "http"
    
    if args.https:
        cert_path = Path(__file__).parent / "cert.pem"
        key_path = Path(__file__).parent / "key.pem"
        
        if cert_path.exists() and key_path.exists():
            ssl_keyfile = str(key_path)
            ssl_certfile = str(cert_path)
            protocol = "https"
            print(f"\n HTTPS habilitado")
            print(f"     Los navegadores mostrarán advertencia de seguridad")
            print(f"     Acepta el riesgo manualmente en tu navegador")
        else:
            print(f"\n Certificados no encontrados. Genera con:")
            print(f"   python generar_certificados.py")
            sys.exit(1)
    
    # Mostrar URLs finales
    if args.global_access and protocol == "https":
        print(f"\n URLs de acceso HTTPS:")
        print(f"   - Local: https://localhost:8000")
        print(f"   - Red local: https://{local_ip}:8000")
    elif protocol == "http":
        print(f"\n Para usar HTTPS, ejecuta: python main.py -g --https")
    
    uvicorn.run(app, host=host, port=8000, ssl_keyfile=ssl_keyfile, ssl_certfile=ssl_certfile)
