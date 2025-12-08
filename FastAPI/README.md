# FastAPI - Servicio OCR

API REST para reconocimiento de texto utilizando FastAPI y el modelo SVM entrenado.

## 🚀 Inicio Rápido

### 1. Instalar dependencias

```bash
cd FastAPI
pip install -r requirements.txt
```

### 2. Iniciar el servidor

**Modo local (solo este PC):**
```bash
python main.py
```
Acceso: `http://localhost:8000`

**Modo red local (compartir con otros dispositivos):**
```bash
python main.py -g
```
Mostrará la IP para acceder desde otros dispositivos, ej: `http://192.168.1.217:8000`

### 3. Configurar firewall (solo para `-g`)

**Windows (cmd como Administrador):**
```cmd
netsh advfirewall firewall add rule name="FastAPI OCR Server" dir=in action=allow protocol=TCP localport=8000
```

**Para cerrar el puerto:**
```cmd
netsh advfirewall firewall delete rule name="FastAPI OCR Server"
```

## 📚 Endpoints

### GET `/`
Información básica de la API.

**Respuesta:**
```json
{
  "mensaje": "API OCR funcionando",
  "version": "1.0.0",
  "endpoints": ["/reconocer", "/health"]
}
```

### GET `/health`
Verifica el estado de la API y si el modelo está cargado.

**Respuesta:**
```json
{
  "status": "ok",
  "modelo_cargado": true
}
```

### POST `/upload-image/`
Reconoce texto de una imagen.

**Parámetros:**
- `file`: Imagen en formato PNG, JPG, JPEG (multipart/form-data)

**Respuesta:**
```json
{
  "filename": "imagen.png",
  "size": 12345,
  "texto": "Hola mundo",
  "confianza_promedio": 0.95,
  "letras": ["H", "o", "l", "a", "ESPACIO", "m", "u", "n", "d", "o"],
  "confidencias": [0.98, 0.96, 0.94, 0.97, 0.99, 0.93, 0.95, 0.96, 0.94, 0.95],
  "idioma": "🇪🇸 Español"
}
```

## 🧪 Probar la API

### Usando curl:

```bash
curl -X POST "http://localhost:8000/upload-image/" \
  -F "file=@imagen.png"
```

### Usando Python:

```python
import requests

url = "http://localhost:8000/upload-image/"
files = {'file': open('imagen.png', 'rb')}
response = requests.post(url, files=files)
print(response.json())
```

### Documentación interactiva:

Accede a `http://localhost:8000/docs` para ver Swagger UI automático.

## 📁 Estructura

```
FastAPI/
├── main.py              # Aplicación principal de FastAPI
├── requirements.txt     # Dependencias
└── README.md           # Este archivo
```

**Nota**: Los modelos se cargan desde la carpeta `../models/` en la raíz del proyecto.

## 🌐 Uso en Red Local

1. **PC con la API** ejecuta: `python main.py -g`
2. Copia la IP mostrada (ej: `192.168.1.217`)
3. Abre el puerto 8000 en el firewall (ver comandos arriba)
4. **Otro PC/dispositivo**: Usa la IP y puerto en la UI de Streamlit

## ⚙️ Configuración

- **Host local**: `127.0.0.1` (sin `-g`)
- **Host red**: `0.0.0.0` (con `-g`)
- **Puerto**: `8000` (fijo)
- **Modelo**: Se carga desde `../models/modelo.pkl`
- **Mapping**: Se carga desde `../data/mapping.txt`

## 🔧 Desarrollo

Para ejecutar con recarga automática (solo desarrollo local):

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📖 Documentación Interactiva

FastAPI genera automáticamente documentación interactiva:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
