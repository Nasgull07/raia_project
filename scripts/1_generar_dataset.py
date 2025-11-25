"""
Script 1: Generar dataset desde imágenes de palabras
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image
from tqdm import tqdm

# Importar segmentador desde utils
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
from simple_segmenter import SimpleImageSegmenter

# Configuración
IMAGES_DIR = Path(__file__).parent.parent / "imagenes" / "entrenamiento"
OUTPUT_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

# Mapeo letras
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
LETTER_TO_LABEL = {letter: i+1 for i, letter in enumerate(LETTERS)}

def procesar_imagen(image_path: Path, segmenter):
    """Procesa una imagen y extrae letras."""
    try:
        # Cargar imagen
        img = Image.open(image_path).convert('L')
        img_array = np.array(img)
        
        # Segmentar
        letras_segmentadas = segmenter.segment_word(img_array)
        
        if not letras_segmentadas:
            return []
        
        # Extraer palabra del nombre
        filename = image_path.stem
        parts = filename.split('_')
        if len(parts) >= 3:
            palabra = '_'.join(parts[2:])
        else:
            return []
        
        # Verificar coincidencia
        if len(letras_segmentadas) != len(palabra):
            return []
        
        # Procesar cada letra
        samples = []
        for i, letra_img in enumerate(letras_segmentadas):
            letra_real = palabra[i]
            
            if not letra_real.isalpha() or letra_real not in LETTER_TO_LABEL:
                continue
            
            # Asegurar 28x28
            if letra_img.shape != (28, 28):
                img_pil = Image.fromarray(letra_img.astype(np.uint8))
                img_pil = img_pil.resize((28, 28), Image.LANCZOS)
                letra_img = np.array(img_pil)
            
            # INVERTIR COLORES (segmentador: fondo=0, modelo espera: fondo=255)
            letra_img = 255 - letra_img
            
            # Verificar no vacía
            if np.sum(letra_img < 255) < 10:
                continue
            
            # Crear muestra
            label = LETTER_TO_LABEL[letra_real]
            pixels = letra_img.flatten()
            sample = [label] + pixels.tolist()
            samples.append(sample)
        
        return samples
    except:
        return []

def main():
    print("=" * 70)
    print("GENERADOR DE DATASET SIMPLE")
    print("=" * 70)
    print()
    
    if not IMAGES_DIR.exists():
        print(f"❌ Error: No existe {IMAGES_DIR}")
        print()
        print("Ejecuta primero en FASE3_PrintedTextRecognition:")
        print("  python download_palabras_web.py")
        return
    
    # Obtener imágenes
    image_files = list(IMAGES_DIR.glob("*.png"))
    print(f"🖼️  Imágenes encontradas: {len(image_files)}")
    
    if len(image_files) == 0:
        print("❌ No hay imágenes para procesar")
        return
    
    print("🔄 Procesando imágenes...")
    print()
    
    # Segmentador
    segmenter = SimpleImageSegmenter()
    
    # Procesar todas las imágenes
    all_samples = []
    
    for img_path in tqdm(image_files, desc="Procesando"):
        samples = procesar_imagen(img_path, segmenter)
        all_samples.extend(samples)
    
    print()
    print(f"✅ Total muestras: {len(all_samples)}")
    
    if len(all_samples) == 0:
        print("❌ No se generaron muestras")
        return
    
    # Crear DataFrame
    print("📦 Creando CSV...")
    columns = ['label'] + [f'pixel{i}' for i in range(784)]
    df = pd.DataFrame(all_samples, columns=columns)
    
    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Split 85/15
    split_idx = int(len(df) * 0.85)
    df_train = df[:split_idx]
    df_test = df[split_idx:]
    
    # Guardar
    train_path = OUTPUT_DIR / "train.csv"
    test_path = OUTPUT_DIR / "test.csv"
    mapping_path = OUTPUT_DIR / "mapping.txt"
    
    df_train.to_csv(train_path, index=False)
    df_test.to_csv(test_path, index=False)
    
    with open(mapping_path, 'w') as f:
        for i, letter in enumerate(LETTERS, 1):
            f.write(f"{i} {letter}\n")
    
    print(f"✅ Train: {len(df_train)} muestras → {train_path}")
    print(f"✅ Test: {len(df_test)} muestras → {test_path}")
    print(f"✅ Mapping: {mapping_path}")
    print()
    print("=" * 70)
    print("✅ DATASET GENERADO")
    print("=" * 70)
    print()
    print("Siguiente paso: python 2_entrenar_modelo.py")

if __name__ == "__main__":
    main()
