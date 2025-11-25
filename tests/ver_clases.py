"""
Ver qué letras hay en el dataset
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

# Cargar mapping
mapping = {}
with open(DATA_DIR / "mapping.txt", 'r') as f:
    for line in f:
        label, letter = line.strip().split()
        mapping[int(label)] = letter

# Cargar dataset (tiene header!)
df = pd.read_csv(DATA_DIR / "train.csv", low_memory=False)

# Contar por label
counts = df['label'].value_counts().sort_index()

print("="*60)
print("LETRAS EN EL DATASET:")
print("="*60)

print("\nMAYÚSCULAS:")
for label in range(1, 27):
    if label in counts.index:
        letter = mapping.get(label, '?')
        print(f"  {letter} (label={label:2d}): {counts[label]:4d} muestras")

print("\nMINÚSCULAS:")
for label in range(27, 53):
    if label in counts.index:
        letter = mapping.get(label, '?')
        print(f"  {letter} (label={label:2d}): {counts[label]:4d} muestras")

print(f"\n{'='*60}")
print(f"TOTAL: {len(df)} muestras")
print(f"Clases con datos: {len(counts)}/{52}")
