"""
Debug: Ver muestras del dataset de entrenamiento
"""

import pandas as pd
import numpy as np
from PIL import Image
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
OUTPUT_DIR = Path(__file__).parent / "debug_letters"
OUTPUT_DIR.mkdir(exist_ok=True)

# Cargar mapping
mapping = {}
with open(DATA_DIR / "mapping.txt", 'r') as f:
    for line in f:
        label, letter = line.strip().split()
        mapping[int(label)] = letter

# Cargar train
df = pd.read_csv(DATA_DIR / "train.csv", header=None)

# Buscar muestras de S, o, f, a (Sofa)
letters_wanted = ['S', 'o', 'f', 'a']
label_to_letter = {v: k for k, v in mapping.items()}

for letter in letters_wanted:
    if letter not in label_to_letter:
        continue
    
    label = label_to_letter[letter]
    samples = df[df.iloc[:, 0] == label]
    
    if len(samples) > 0:
        # Tomar primera muestra
        sample = samples.iloc[0]
        pixels = sample.iloc[1:].values.reshape(28, 28)
        img = Image.fromarray(pixels.astype(np.uint8))
        img.save(OUTPUT_DIR / f"dataset_{letter}_label{label}.png")
        print(f"✅ Guardada muestra de '{letter}' (label={label})")

print(f"\n📁 Imágenes guardadas en: {OUTPUT_DIR}")
