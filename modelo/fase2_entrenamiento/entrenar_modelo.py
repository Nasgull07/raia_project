"""
Script 2: Entrenar modelo SVM con pixeles crudos
"""

import numpy as np
import pandas as pd
import pickle
from pathlib import Path
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler

# Paths
DATA_DIR = Path(__file__).parent.parent.parent / "data"
MODELS_DIR = Path(__file__).parent.parent.parent / "models"
MODELS_DIR.mkdir(exist_ok=True)

def main():
    print("="*70)
    print("ENTRENAMIENTO SIMPLE (PIXELES CRUDOS - SIN HOG)")
    print("="*70)
    print()
    
    # Cargar datos
    print("[INFO] Cargando datos...")
    train_path = DATA_DIR / "train.csv"
    test_path = DATA_DIR / "test.csv"
    
    df_train = pd.read_csv(train_path)
    df_test = pd.read_csv(test_path)
    
    print(f"[OK] Train: {len(df_train)} muestras")
    print(f"[OK] Test: {len(df_test)} muestras")
    print()
    
    # Duplicar datos para usar el doble
    df_train = pd.concat([df_train, df_train], ignore_index=True)
    df_test = pd.concat([df_test, df_test], ignore_index=True)

    print(f"[OK] Train duplicado: {len(df_train)} muestras")
    print(f"[OK] Test duplicado: {len(df_test)} muestras")
    print()
    
    # Separar X, y
    X_train = df_train.iloc[:, 1:].values
    y_train = df_train.iloc[:, 0].values
    X_test = df_test.iloc[:, 1:].values
    y_test = df_test.iloc[:, 0].values
    
    # Normalizar
    print("[INFO] Normalizando (StandardScaler)...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print(f"[OK] Train: {X_train_scaled.shape}")
    print(f"[OK] Test: {X_test_scaled.shape}")
    print()
    
    # Entrenar SVM
    print("[INFO] Entrenando SVM (C=1.0, kernel=linear)...")
    print("   Esto puede tardar 1-2 minutos...")
    
    model = SVC(C=1.0, kernel='linear', probability=True, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    print("[OK] Entrenamiento completado")
    print()
    
    # Evaluar
    print("[INFO] Evaluando modelo...")
    
    y_train_pred = model.predict(X_train_scaled)
    train_acc = accuracy_score(y_train, y_train_pred)
    
    y_test_pred = model.predict(X_test_scaled)
    test_acc = accuracy_score(y_test, y_test_pred)
    
    print(f"   Train Accuracy: {train_acc*100:.2f}%")
    print(f"   Test Accuracy:  {test_acc*100:.2f}%")
    print()
    
    # Guardar modelo
    print("[INFO] Guardando modelo...")
    model_path = MODELS_DIR / "modelo.pkl"
    scaler_path = MODELS_DIR / "scaler.pkl"
    
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    
    print(f"[OK] Modelo: {model_path}")
    print(f"[OK] Scaler: {scaler_path}")
    print()
    
    print("="*70)
    print("[OK] ENTRENAMIENTO COMPLETADO")
    print("="*70)
    print()
    print(f"[INFO] Test Accuracy: {test_acc*100:.2f}%")
    print()
    print("Siguiente paso: python ../fase3_evaluacion/reconocer_texto.py imagen.png")

if __name__ == "__main__":
    main()
