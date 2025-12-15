# 🔤 Sistema OCR Multiidioma - RAIA Project

Sistema completo de reconocimiento óptico de caracteres (OCR) con soporte para **Español**, **Catalán** e **Inglés**. Incluye generación automática de datasets, entrenamiento de modelos, API REST y múltiples interfaces de usuario interactivas.

## 📋 Tabla de Contenidos

- [Características Principales](#-características-principales)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Instalación y Configuración](#-instalación-y-configuración)
- [Uso del Sistema](#-uso-del-sistema)
- [Funcionalidades Detalladas](#-funcionalidades-detalladas)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Endpoints de la API](#-endpoints-de-la-api)

---

## ✨ Características Principales

### 🎯 Reconocimiento de Caracteres
- **91 clases de caracteres** soportadas:
  - Letras básicas: A-Z, a-z (52 caracteres)
  - Acentos agudos: áéíóú, ÁÉÍÓÚ (español/catalán)
  - Acentos graves: àèìòù, ÀÈÌÒÙ (catalán)
  - Diéresis: ïü, ÏÜ (español/catalán)
  - Especiales: ñÑ (español), çÇ (catalán), ' (inglés)
  - Puntuación: , . ; : ¿ ? ¡ ! -
  - Espacio

### 🌍 Detección Automática de Idioma
- Identifica automáticamente el idioma del texto reconocido
- Soporta español, catalán e inglés

### 📝 Segmentación Avanzada
- **Segmentación por líneas**: Detecta automáticamente múltiples líneas de texto
- **Segmentación por caracteres**: Separa cada letra individual
- Soporte para saltos de línea en texto sintético

### ⚙️ Configuración Automática
- **Botón "Configurar Proyecto Completo"**: Si el modelo no existe, un solo click ejecuta:
  1. Generación de imágenes sintéticas con puntuación
  2. Creación del dataset de entrenamiento
  3. Entrenamiento del modelo SVM
  4. Todo listo en minutos

### 📊 Precisión del Modelo
- **~96% de precisión** en test set
- Modelo SVM (Support Vector Machine) con kernel lineal
- Normalización con StandardScaler

---

## 🛠️ Tecnologías Utilizadas

### Backend
- **Python 3.13**
- **FastAPI**: API REST moderna y rápida
- **Uvicorn**: Servidor ASGI de alto rendimiento

### Machine Learning
- **scikit-learn**: SVM para clasificación de caracteres
- **PIL (Pillow)**: Procesamiento de imágenes
- **NumPy**: Operaciones numéricas
- **pandas**: Manipulación de datos

### Frontend
- **Streamlit**: Interfaces web interactivas
- **Plotly/Matplotlib**: Visualización de datos

### Procesamiento de Imágenes
- **scikit-image**: Filtros y binarización
- **scipy**: Operaciones morfológicas

### Detección de Idioma
- **langdetect**: Identificación automática de idiomas

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    USUARIO (Navegador)                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  STREAMLIT UI (Puerto 8501)                  │
│  ┌──────────────┬──────────────┬──────────────┬───────────┐ │
│  │ Página       │  Chatbot     │  Dashboard   │ Configurar│ │
│  │ Principal    │    OCR       │ Estadísticas │ Proyecto  │ │
│  └──────────────┴──────────────┴──────────────┴───────────┘ │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP REST API
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                FastAPI Server (Puerto 8000)                  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  Endpoints:                                             ││
│  │  • /health          - Estado del servidor              ││
│  │  • /upload-image/   - Reconocimiento OCR               ││
│  │  • /               - Info de la API                    ││
│  └─────────────────────────────────────────────────────────┘│
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    MODELO ML (SVM)                           │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  • Modelo entrenado (modelo.pkl)                        ││
│  │  • Scaler normalizado (scaler.pkl)                      ││
│  │  • Mapping de clases (mapping.txt)                      ││
│  │  • Segmentador de imágenes                              ││
│  └──────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### Flujo de Datos

1. **Usuario sube imagen** → Streamlit UI
2. **UI envía imagen** → FastAPI (HTTP POST)
3. **FastAPI procesa**:
   - Segmenta líneas de texto
   - Segmenta caracteres individuales
   - Normaliza a 28x28 píxeles
   - Predice con modelo SVM
4. **Respuesta JSON** → UI muestra resultados

---

## 📦 Instalación y Configuración

### 1. Clonar el Repositorio
```bash
git clone https://github.com/Nasgull07/raia_project.git
cd raia_project-main
```

### 2. Instalar Dependencias

#### FastAPI
```bash
cd FastAPI
pip install -r requirements.txt
```

#### Streamlit UI
```bash
cd UI
pip install -r requirements.txt
```

### 3. Configuración Automática (Recomendado)

**Opción más fácil**: Usa el botón en la interfaz de Streamlit

1. Inicia Streamlit:
   ```bash
   cd UI
   python -m streamlit run app.py
   ```

2. En la página principal, haz clic en **"⚙️ Configurar Proyecto Completo"**
3. Espera a que se complete (2-5 minutos)
4. ¡Listo! El modelo está entrenado

### 4. Configuración Manual (Opcional)

Si prefieres hacerlo paso a paso:

```bash
# 1. Generar imágenes sintéticas
cd modelo/fase1_dataset
python generar_con_puntuacion.py --palabras 100 --chars 50

# 2. Crear dataset
python generar_dataset.py

# 3. Entrenar modelo
cd ../fase2_entrenamiento
python entrenar_modelo.py
```

---

## 🚀 Uso del Sistema

### Iniciar el Sistema Completo

#### 1. Iniciar FastAPI (Terminal 1)
```bash
cd FastAPI
python main.py
```
- Servidor corriendo en `http://localhost:8000`
- Para acceso en red local: usa la IP que muestra

#### 2. Iniciar Streamlit (Terminal 2)
```bash
cd UI
python -m streamlit run app.py
```
- Interfaz web en `http://localhost:8501`

### Configuración de Red en la UI

En el sidebar de Streamlit, puedes configurar la conexión:

- **Localhost**: `http://localhost:8000` (por defecto)
- **IP Personalizada**: Introduce la IP de la máquina donde corre FastAPI
  - Ejemplo: `http://192.168.1.50:8000`
  - Útil para acceso desde otros dispositivos en la red

**Verificar Conexión**: Click en el botón **"🔍 Verificar Conexión"** para comprobar que la API esté disponible.

---

## 🎨 Funcionalidades Detalladas

### 1. Página Principal - Reconocimiento de Texto

#### Pestaña: Escribir Texto
- **Área de texto** con soporte para múltiples líneas (usa Enter)
- Generación de imagen sintética del texto
- Reconocimiento automático del texto generado
- Comparación visual entre texto original y reconocido
- Métricas de confianza por carácter
- Detección automática de idioma

**Características:**
- ✅ Saltos de línea soportados
- ✅ Validación de caracteres permitidos
- ✅ Ajuste de tamaño de fuente (30-100px)
- ✅ Visualización de caracteres individuales detectados

#### Pestaña: Subir Imagen
- Carga de imágenes desde tu dispositivo
- Formatos soportados: PNG, JPG, JPEG, BMP
- Reconocimiento de texto en la imagen
- Métricas de confianza y idioma detectado

**Consejos para mejores resultados:**
- ✏️ Texto negro sobre fondo blanco
- 📐 Imágenes de alta calidad (mínimo 300 DPI)
- ➡️ Texto horizontal y bien alineado
- 🔤 Fuentes claras (Arial, Times, Calibri)

#### Pestaña: Explorador de Archivos
- Introduce la ruta completa de una imagen
- Útil para procesar archivos específicos del sistema

### 2. Chatbot OCR Interactivo

Un asistente conversacional para reconocimiento de texto:

- **Interfaz de chat** estilo WhatsApp/ChatGPT
- Sube imágenes directamente en la conversación
- Respuestas instantáneas con texto reconocido
- Detección automática de idioma en cada imagen
- Historial de conversación persistente

**Casos de uso:**
- 📸 Procesar múltiples imágenes en secuencia
- 💬 Experiencia más natural e intuitiva
- 📝 Historial completo de reconocimientos

### 3. Dashboard de Estadísticas

Visualización avanzada de datos y métricas:

#### Métricas Generales
- Total de reconocimientos realizados
- Total de caracteres procesados
- Confianza promedio del sistema
- Distribución de idiomas detectados

#### Gráficos Interactivos
- **Historial de confianza**: Evolución temporal
- **Distribución de idiomas**: Gráfico de barras
- **Análisis de caracteres**: Frecuencia de aparición
- **Tabla de reconocimientos**: Historial completo con timestamps

**Funcionalidades:**
- 📊 Gráficos con Matplotlib/Plotly
- 📈 Métricas en tiempo real
- 🔄 Actualización automática
- 💾 Datos persistentes en session_state

### 4. Configuración Automática del Proyecto

Si el modelo no existe, aparece un panel especial:

**"⚙️ Configurar Proyecto Completo"**
- Un solo click ejecuta todo el pipeline:
  1. **Paso 1**: Genera 100 palabras + caracteres individuales
  2. **Paso 2**: Crea dataset train/test (85/15 split)
  3. **Paso 3**: Entrena modelo SVM

**Logs en tiempo real**: Ve el progreso de cada paso

**Alternativa Manual**: También puedes ejecutar cada paso individualmente

---

## 📁 Estructura del Proyecto

```
raia_project-main/
│
├── FastAPI/                      # Backend API REST
│   ├── main.py                   # Servidor FastAPI principal
│   ├── requirements.txt          # Dependencias de FastAPI
│   └── README.md                 # Documentación de la API
│
├── UI/                           # Frontend Streamlit
│   ├── app.py                    # Página principal
│   ├── streamlit_app.py          # Punto de entrada alternativo
│   ├── requirements.txt          # Dependencias de Streamlit
│   ├── pages/                    # Páginas adicionales
│   │   ├── chatbot.py           # Chatbot interactivo
│   │   └── dashboard.py         # Dashboard de estadísticas
│   └── utils/                    # Utilidades compartidas
│       ├── api_utils.py         # Comunicación con API
│       └── sidebar_common.py    # Sidebar común para todas las páginas
│
├── modelo/                       # Pipeline de Machine Learning
│   ├── fase1_dataset/           # Generación de datasets
│   │   ├── generar_con_puntuacion.py  # Generador de imágenes sintéticas
│   │   ├── generar_dataset.py         # Creador de CSV train/test
│   │   └── simple_segmenter.py        # Segmentador de pruebas
│   │
│   ├── fase2_entrenamiento/     # Entrenamiento del modelo
│   │   └── entrenar_modelo.py   # Entrenamiento SVM
│   │
│   └── fase3_evaluacion/        # Evaluación y reconocimiento
│       ├── reconocer_texto.py   # Script de reconocimiento CLI
│       └── simple_segmenter.py  # Segmentador de imágenes (líneas + chars)
│
├── models/                       # Modelos entrenados
│   ├── modelo.pkl               # Modelo SVM serializado
│   └── scaler.pkl               # StandardScaler serializado
│
├── data/                         # Datos y mappings
│   ├── train.csv                # Dataset de entrenamiento
│   ├── test.csv                 # Dataset de test
│   └── mapping.txt              # Mapeo label → caracter
│
├── imagenes/                     # Almacenamiento de imágenes
│   ├── puntuacion/              # Imágenes generadas con puntuación
│   └── verificacion/            # Imágenes para verificación
│
└── README.md                     # Este archivo
```

---

## 🔌 Endpoints de la API

### Base URL
```
http://localhost:8000
```

### 1. Health Check
```http
GET /health
```

**Respuesta:**
```json
{
  "status": "ok",
  "modelo_cargado": true
}
```

### 2. Información de la API
```http
GET /
```

**Respuesta:**
```json
{
  "mensaje": "API OCR funcionando",
  "version": "1.0.0",
  "endpoints": ["/upload-image/", "/health"]
}
```

### 3. Reconocimiento de Texto
```http
POST /upload-image/
Content-Type: multipart/form-data
```

**Parámetros:**
- `file`: Imagen (PNG, JPG, JPEG, BMP)

**Respuesta:**
```json
{
  "texto": "Hola mundo\nSegunda línea",
  "confianza_promedio": 0.95,
  "letras": ["H", "o", "l", "a", " ", "m", "u", "n", "d", "o"],
  "confidencias": [0.98, 0.96, 0.97, ...],
  "idioma": "🇪🇸 Español"
}
```

**Códigos de Estado:**
- `200`: Éxito
- `400`: Error en la imagen
- `500`: Error del servidor

---

## 🧪 Casos de Uso

### 1. Digitalizar Documentos Escritos a Mano
Aunque optimizado para texto impreso, puede reconocer escritura clara.

### 2. Extracción de Texto de Imágenes
Procesa capturas de pantalla, fotos de documentos, etc.

### 3. Traducción Automática
Combina con APIs de traducción para traducir texto en imágenes.

### 4. Accesibilidad
Convierte texto en imágenes a formato legible por lectores de pantalla.

### 5. Procesamiento por Lotes
Usa la API para procesar múltiples imágenes automáticamente.

---

## 📊 Rendimiento

### Precisión del Modelo
- **Test Accuracy**: ~96%
- **Mejores resultados**: Fuentes estándar (Arial, Times, Calibri)
- **Caracteres problemáticos**: I/l en algunas fuentes

### Velocidad
- **Generación de dataset**: ~10 segundos por 100 palabras
- **Entrenamiento**: 1-2 minutos (depende del hardware)
- **Reconocimiento**: <1 segundo por imagen

### Requisitos del Sistema
- **RAM**: Mínimo 4GB
- **CPU**: Cualquier procesador moderno
- **GPU**: No requerida
- **Disco**: ~100MB para el proyecto completo

---

## 🔧 Solución de Problemas

### La API no se conecta
1. Verifica que FastAPI esté corriendo: `python FastAPI/main.py`
2. Comprueba el puerto 8000 no esté ocupado
3. Usa el botón "Verificar Conexión" en el sidebar

### El modelo no se carga
1. Click en "Configurar Proyecto Completo" en Streamlit
2. O ejecuta manualmente los scripts de generación y entrenamiento

### Caracteres no reconocidos correctamente
1. Asegúrate de usar texto negro sobre fondo blanco
2. Aumenta la calidad/resolución de la imagen
3. Usa fuentes estándar sin efectos

### Error de emojis en Windows
Los archivos Python ya están configurados para usar `[OK]` en lugar de emojis en la terminal.

---

## 🚀 Próximas Mejoras

- [ ] Soporte para más idiomas (Francés, Alemán)
- [ ] Reconocimiento de escritura a mano mejorado
- [ ] Exportación de resultados a PDF/TXT
- [ ] API de procesamiento por lotes
- [ ] Modelo CNN para mayor precisión
- [ ] Soporte para OCR en tiempo real (webcam)

---

## 👥 Contribuciones

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

---

## 📧 Contacto

- **Repositorio**: [https://github.com/Nasgull07/raia_project](https://github.com/Nasgull07/raia_project)
- **Issues**: [GitHub Issues](https://github.com/Nasgull07/raia_project/issues)

---

## 🙏 Agradecimientos

- **scikit-learn** por las herramientas de ML
- **FastAPI** por el framework de API moderno
- **Streamlit** por la increíble biblioteca de UI
- **PIL/Pillow** por el procesamiento de imágenes

---

**Hecho con ❤️ para el proyecto RAIA**
