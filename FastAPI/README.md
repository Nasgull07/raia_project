# FastAPI - Servicio OCR

API REST para reconocimiento de texto utilizando FastAPI y el modelo SVM entrenado.

## 🚀 Inicio Rápido

### 1. Instalar dependencias

```bash
cd FastAPI
pip install -r requirements.txt
```

### 2. Iniciar el servidor

```bash
uvicorn main:app --reload
```

El servidor estará disponible en: `http://localhost:8000`

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

### POST `/reconocer`
Reconoce texto de una imagen.

**Parámetros:**
- `file`: Imagen en formato PNG, JPG, JPEG (multipart/form-data)

**Respuesta:**
```json
{
  "texto": "Hola mundo",
  "confianza_promedio": 0.95,
  "letras": ["H", "o", "l", "a", "ESPACIO", "m", "u", "n", "d", "o"],
  "confidencias": [0.98, 0.96, 0.94, 0.97, 0.99, 0.93, 0.95, 0.96, 0.94, 0.95]
}
```

## 🧪 Probar la API

### Usando curl:

```bash
curl -X POST "http://localhost:8000/reconocer" \
  -F "file=@imagen.png"
```

### Usando Python:

```python
import requests

url = "http://localhost:8000/reconocer"
files = {'file': open('imagen.png', 'rb')}
response = requests.post(url, files=files)
print(response.json())
```

## 📁 Estructura

```
FastAPI/
├── main.py              # Aplicación principal de FastAPI
├── requirements.txt     # Dependencias
└── README.md           # Este archivo
```

**Nota**: Los modelos se cargan desde la carpeta `../models/` en la raíz del proyecto.

## ⚙️ Configuración

La API se configura automáticamente al iniciar. El modelo se carga desde la carpeta `../models/` (raíz del proyecto) y el mapping desde `../data/mapping.txt`.

## 🔧 Desarrollo

Para ejecutar en modo desarrollo con recarga automática:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📖 Documentación Interactiva

FastAPI genera automáticamente documentación interactiva:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
