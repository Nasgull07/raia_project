# RAIA Project - OCR

Sistema de reconocimiento optico de caracteres (OCR) con interfaz web.

## Requisitos

- Python 3.8+
- `cd FastAPI` `cd UI`
- Dependencias: `pip install -r requirements.txt`

## Ejecucion

### 1. Iniciar API (FastAPI)

```bash
cd FastAPI
python main.py   (local)
python main.py -g   (http)
python main.py -g -hhtps  (https) és la unica que funciona con unity
```

La API estara disponible en `http://localhost:8000` o `http://IP:8000` o `https://IP:8000`


### 2. Iniciar Interfaz Web (Streamlit)

```bash
cd UI
python -m streamlit run app.py
```

La interfaz estara disponible en `http://localhost:8501` o `http://IP:8501`

## Estructura

- `FastAPI/` - Backend API REST
- `UI/` - Interfaz web Streamlit
- `modelo/` - Scripts de entrenamiento y evaluacion
- `models/` - Modelos entrenados
- `data/` - Datasets

## Configuracion Inicial

Si es la primera vez, usa el boton "Configurar Proyecto Completo" en la interfaz web para generar el dataset y entrenar el modelo.
