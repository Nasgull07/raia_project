# UI - Interfaz Streamlit

Interfaz gráfica para probar el modelo OCR.

## 🚀 Ejecutar la Aplicación

```bash
cd UI
streamlit run app.py
```

O desde la raíz del proyecto:
```bash
streamlit run UI/app.py
```

## 📋 Requisitos Adicionales

Si aún no tienes Streamlit instalado:
```bash
pip install streamlit
```

## 🎯 Características

### Modo 1: Escribir Texto
- Escribe cualquier texto (letras A-Z, a-z)
- Ajusta el tamaño de fuente
- La aplicación genera una imagen y la reconoce
- Compara el texto original con el reconocido
- Muestra cada letra detectada con su confianza

### Modo 2: Subir Imagen
- Sube una imagen PNG, JPG o JPEG
- Debe tener texto negro sobre fondo blanco
- Reconoce el texto automáticamente
- Muestra cada letra con su nivel de confianza

## 📊 Interfaz

La aplicación muestra:
- ✅ Texto reconocido
- ✅ Confianza promedio del reconocimiento
- ✅ Letras individuales detectadas
- ✅ Comparación con texto original (modo escritura)
- ✅ Detalles de confianza por letra

## 💡 Consejos de Uso

- **Texto claro**: Usa fuentes simples y legibles
- **Contraste**: Texto negro sobre fondo blanco
- **Horizontal**: El texto debe estar en horizontal
- **Tamaño**: Letras no muy pequeñas

## 🔧 Requisitos Técnicos

La aplicación requiere:
- ✅ Modelo entrenado (`models/modelo.pkl`)
- ✅ Scaler (`models/scaler.pkl`)
- ✅ Mapping de clases (`data/mapping.txt`)
- ✅ Segmentador (`utils/simple_segmenter.py`)

Si falta alguno, ejecuta primero:
```bash
cd scripts
python 1_generar_dataset.py
python 2_entrenar_modelo.py
```
