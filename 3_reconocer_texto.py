"""
Script 3: Reconocer texto de imagen
"""

import sys
from pathlib import Path
import numpy as np
import pickle
from PIL import Image
import argparse

# Importar segmentador y preprocessor
sys.path.insert(0, str(Path(__file__).parent.parent / "StreamlitApp" / "utils"))
sys.path.insert(0, str(Path(__file__).parent.parent / "FASE1_SingleCharacterRecognition" / "src"))
from simple_segmenter import SimpleImageSegmenter

# Paths
MODELS_DIR = Path(__file__).parent / "models"
DATA_DIR = Path(__file__).parent / "data"

def cargar_modelo():
    """Carga modelo y preprocessor."""
    model_path = MODELS_DIR / "modelo.pkl"
    preprocessor_path = MODELS_DIR / "preprocessor.pkl"
    mapping_path = DATA_DIR / "mapping.txt"
    
    if not model_path.exists():
        print("❌ Error: Modelo no existe")
        print()
        print("Ejecuta primero: python 2_entrenar_modelo.py")
        sys.exit(1)
    
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    with open(preprocessor_path, 'rb') as f:
        preprocessor = pickle.load(f)
    
    # Cargar mapping
    label_mapping = {}
    with open(mapping_path, 'r') as f:
        for line in f:
            label, letter = line.strip().split()
            label_mapping[int(label)] = letter
    
    return model, preprocessor, label_mapping

def reconocer_texto(image_path: Path):
    """Reconoce texto de una imagen."""
    
    # Cargar modelo
    print("🤖 Cargando modelo...")
    model, preprocessor, label_mapping = cargar_modelo()
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
    
    # DEBUG: Guardar letras segmentadas
    debug_dir = Path(__file__).parent / "debug_letters"
    debug_dir.mkdir(exist_ok=True)
    for idx, letra in enumerate(letras_segmentadas):
        Image.fromarray(letra.astype(np.uint8)).save(debug_dir / f"letra_{idx}_before.png")
    
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
        
        # DEBUG: Guardar letra invertida
        Image.fromarray(letra_img.astype(np.uint8)).save(debug_dir / f"letra_{i}_after.png")
        
        # Preprocesar
        letra_flat = letra_img.flatten().reshape(1, -1)
        
        # DEBUG
        if i == 0:
            print(f"\nDEBUG letra {i}:")
            print(f"  Shape flat: {letra_flat.shape}")
            print(f"  Min: {letra_flat.min()}, Max: {letra_flat.max()}, Mean: {letra_flat.mean():.1f}")
        
        letra_proc = preprocessor.transform(letra_flat)
        
        # DEBUG
        if i == 0:
            print(f"  Shape proc: {letra_proc.shape}")
            print(f"  Min proc: {letra_proc.min():.3f}, Max proc: {letra_proc.max():.3f}")
        
        # Predecir
        pred = model.predict(letra_proc)[0]
        proba = model.predict_proba(letra_proc)[0]
        
        letra = label_mapping[pred]
        pred_idx = np.where(model.classes_ == pred)[0][0]
        confianza = proba[pred_idx]
        
        texto_reconocido.append(letra)
        confidencias.append(confianza)
        
        print(f"   Letra {i+1}: '{letra}' ({confianza*100:.1f}%)")
    
    texto = ''.join(texto_reconocido)
    conf_promedio = np.mean(confidencias)
    
    print()
    print("=" * 70)
    print(f"📝 TEXTO RECONOCIDO: {texto}")
    print(f"📊 Confianza promedio: {conf_promedio*100:.1f}%")
    print("=" * 70)

def main():
    parser = argparse.ArgumentParser(description='Reconocer texto de imagen')
    parser.add_argument('imagen', type=str, help='Ruta a la imagen')
    args = parser.parse_args()
    
    image_path = Path(args.imagen)
    
    if not image_path.exists():
        print(f"❌ Error: No existe el archivo {image_path}")
        return
    
    reconocer_texto(image_path)

if __name__ == "__main__":
    main()
