"""
Script 3: Reconocer texto (versión RAW - sin HOG)
"""

import sys
from pathlib import Path
import numpy as np
import pickle
from PIL import Image
import argparse

# Importar segmentador desde utils
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
from simple_segmenter import SimpleImageSegmenter

# Paths
MODELS_DIR = Path(__file__).parent.parent / "models"
DATA_DIR = Path(__file__).parent.parent / "data"

def cargar_modelo():
    """Carga modelo y scaler."""
    model_path = MODELS_DIR / "modelo.pkl"
    scaler_path = MODELS_DIR / "scaler.pkl"
    mapping_path = DATA_DIR / "mapping.txt"
    
    if not model_path.exists():
        print("❌ Error: Modelo no existe")
        print()
        print("Ejecuta primero: python 2_entrenar_modelo.py")
        sys.exit(1)
    
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    with open(scaler_path, 'rb') as f:
        scaler = pickle.load(f)
    
    # Cargar mapping
    label_mapping = {}
    with open(mapping_path, 'r') as f:
        for line in f:
            label, letter = line.strip().split()
            label_mapping[int(label)] = letter
    
    return model, scaler, label_mapping

def reconocer_texto(image_path: Path):
    """Reconoce texto de una imagen."""
    
    # Cargar modelo
    print("🤖 Cargando modelo...")
    model, scaler, label_mapping = cargar_modelo()
    print("✅ Modelo cargado")
    print()
    
    # Cargar imagen
    print(f"📷 Cargando imagen: {image_path.name}")
    img = Image.open(image_path).convert('L')
    img_array = np.array(img)
    print(f"   Dimensiones: {img_array.shape}")
    print()
    
    # Segmentar
    print("✂️  Segmentando letras...")
    segmenter = SimpleImageSegmenter()
    letras_segmentadas = segmenter.segment_word(img_array)
    
    if not letras_segmentadas:
        print("❌ No se detectaron letras")
        return
    
    print(f"✅ {len(letras_segmentadas)} letras detectadas")
    print()
    
    # Predecir cada letra
    print("🔍 Reconociendo...")
    texto_reconocido = []
    confidencias = []
    
    for i, letra_img in enumerate(letras_segmentadas):
        # Asegurar 28x28
        if letra_img.shape != (28, 28):
            img_pil = Image.fromarray(letra_img.astype(np.uint8))
            img_pil = img_pil.resize((28, 28), Image.LANCZOS)
            letra_img = np.array(img_pil)
        
        # INVERTIR COLORES
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
        confidencias.append(confianza)
        
        print(f"   Letra {i+1}: '{letra}' ({confianza*100:.1f}%)")
    
    # Resultado final
    texto_final = ''.join(texto_reconocido)
    confianza_promedio = np.mean(confidencias)
    
    print()
    print("="*70)
    print(f"📝 TEXTO RECONOCIDO: {texto_final}")
    print(f"📊 Confianza promedio: {confianza_promedio*100:.1f}%")
    print("="*70)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path", help="Ruta a la imagen")
    args = parser.parse_args()
    
    image_path = Path(args.image_path)
    if not image_path.exists():
        print(f"❌ Error: No existe {image_path}")
        return
    
    reconocer_texto(image_path)

if __name__ == "__main__":
    main()
