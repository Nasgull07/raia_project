"""
Comparar letras segmentadas vs dataset
"""

import numpy as np
from PIL import Image
from pathlib import Path

DEBUG_DIR = Path(__file__).parent / "debug_letters"

def print_ascii(img_array, title):
    """Imprime imagen como ASCII"""
    print(f"\n{title}")
    print("=" * 30)
    h, w = img_array.shape
    for i in range(0, h, 2):  # Cada 2 filas
        row = ""
        for j in range(0, w, 1):
            val = img_array[i, j]
            if val < 50:
                row += "█"
            elif val < 100:
                row += "▓"
            elif val < 150:
                row += "▒"
            elif val < 200:
                row += "░"
            else:
                row += " "
        print(row)

def analyze_image(path):
    """Analiza una imagen"""
    img = np.array(Image.open(path))
    print(f"\n{path.name}:")
    print(f"  Shape: {img.shape}")
    print(f"  Min: {img.min()}, Max: {img.max()}, Mean: {img.mean():.1f}")
    print(f"  Pixeles blancos (>200): {np.sum(img > 200)}")
    print(f"  Pixeles negros (<50): {np.sum(img < 50)}")
    return img

print("="*60)
print("ANÁLISIS DE LETRAS")
print("="*60)

# Analizar letra segmentada de Sofa (primera letra = S)
print("\n📷 LETRA SEGMENTADA #0 (debería ser 'S'):")
letra_before = analyze_image(DEBUG_DIR / "letra_0_before.png")
letra_after = analyze_image(DEBUG_DIR / "letra_0_after.png")

print_ascii(letra_before, "BEFORE (del segmentador)")
print_ascii(letra_after, "AFTER (invertida)")

# Analizar S del dataset
print("\n\n📚 LETRA DEL DATASET 'S' (label=19):")
dataset_S = analyze_image(DEBUG_DIR / "dataset_S_label19.png")
print_ascii(dataset_S, "DATASET S")

print("\n" + "="*60)
print("COMPARACIÓN:")
print("="*60)
print(f"Segmentada AFTER mean: {letra_after.mean():.1f}")
print(f"Dataset S mean: {dataset_S.mean():.1f}")
print(f"Diferencia: {abs(letra_after.mean() - dataset_S.mean()):.1f}")
