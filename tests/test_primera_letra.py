"""
Probar con la primera letra S del dataset
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pickle
from PIL import Image
from sklearn.preprocessing import StandardScaler

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
MODELS_DIR = Path(__file__).parent.parent / "models"

# Cargar modelo
with open(MODELS_DIR / "modelo.pkl", 'rb') as f:
    model = pickle.load(f)

with open(MODELS_DIR / "scaler.pkl", 'rb') as f:
    scaler = pickle.load(f)

# Cargar mapping
mapping = {}
with open(DATA_DIR / "mapping.txt", 'r') as f:
    for line in f:
        label, letter = line.strip().split()
        mapping[int(label)] = letter

# Cargar dataset
df = pd.read_csv(DATA_DIR / "train.csv", low_memory=False)

# Buscar label de 'S' (debe ser 19)
label_S = None
for label, letter in mapping.items():
    if letter == 'S':
        label_S = label
        break

print(f"Label de 'S': {label_S}")

# Obtener primera muestra de S
muestras_S = df[df['label'] == label_S]
print(f"Muestras de 'S': {len(muestras_S)}")

if len(muestras_S) > 0:
    # Tomar primera
    primera_S = muestras_S.iloc[0]
    pixels = primera_S.iloc[1:].values.reshape(1, -1)
    
    print(f"\nPixels shape: {pixels.shape}")
    print(f"Min: {pixels.min()}, Max: {pixels.max()}, Mean: {pixels.mean():.1f}")
    
    # Normalizar con scaler
    proc = scaler.transform(pixels)
    print(f"Proc shape: {proc.shape}")
    print(f"Min proc: {proc.min():.3f}, Max proc: {proc.max():.3f}")
    
    # Predecir
    pred = model.predict(proc)[0]
    proba = model.predict_proba(proc)[0]
    pred_idx = np.where(model.classes_ == pred)[0][0]
    
    print(f"\nPredicción: {mapping[pred]} (label={pred})")
    print(f"Confianza: {proba[pred_idx]*100:.1f}%")
    print(f"Top 3 predicciones:")
    top3_idx = np.argsort(proba)[-3:][::-1]
    for idx in top3_idx:
        label = model.classes_[idx]
        print(f"  {mapping[label]}: {proba[idx]*100:.1f}%")
