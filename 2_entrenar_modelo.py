"""
Script 2: Entrenar modelo SVM
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pickle
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report
from tqdm import tqdm

# Importar preprocessor
sys.path.insert(0, str(Path(__file__).parent.parent / "FASE1_SingleCharacterRecognition" / "src"))

# CRÍTICO: Inyectar config ANTES de importar
import config as fase1_config
fase1_config.PREPROCESSING_CONFIG = {
    "rotation_k": 0,
    "flip_lr": False,
    "normalize": True,
    "normalization_method": "standard",
    "use_hog": True,
    "hog_params": {
        "orientations": 9,
        "pixels_per_cell": (8, 8),
        "cells_per_block": (2, 2),
        "transform_sqrt": True,
        "feature_vector": True,
    }
}

from preprocessor import ImagePreprocessor

# Paths
DATA_DIR = Path(__file__).parent / "data"
MODELS_DIR = Path(__file__).parent / "models"
MODELS_DIR.mkdir(exist_ok=True)

def main():
    print("=" * 70)
    print("ENTRENAMIENTO MODELO SIMPLE")
    print("=" * 70)
    print()
    
    # Cargar datos
    print("📂 Cargando datos...")
    train_path = DATA_DIR / "train.csv"
    test_path = DATA_DIR / "test.csv"
    
    if not train_path.exists() or not test_path.exists():
        print(f"❌ Error: No existen los archivos CSV")
        print()
        print("Ejecuta primero: python 1_generar_dataset.py")
        return
    
    df_train = pd.read_csv(train_path)
    df_test = pd.read_csv(test_path)
    
    print(f"✅ Train: {len(df_train)} muestras")
    print(f"✅ Test: {len(df_test)} muestras")
    print()
    
    # Separar X, y
    X_train = df_train.iloc[:, 1:].values
    y_train = df_train.iloc[:, 0].values
    X_test = df_test.iloc[:, 1:].values
    y_test = df_test.iloc[:, 0].values
    
    # Preprocesar
    print("🔧 Preprocesando (HOG features)...")
    preprocessor = ImagePreprocessor()
    
    print("   Procesando TRAIN (fit_transform)...")
    X_train_proc = preprocessor.fit_transform(X_train)
    # Reshape si es necesario
    if len(X_train_proc.shape) == 3:
        X_train_proc = X_train_proc.reshape(len(X_train_proc), -1)
    
    print("   Procesando TEST (transform)...")
    X_test_proc = preprocessor.transform(X_test)
    if len(X_test_proc.shape) == 3:
        X_test_proc = X_test_proc.reshape(len(X_test_proc), -1)
    
    print(f"✅ Train: {X_train_proc.shape}")
    print(f"✅ Test: {X_test_proc.shape}")
    print()
    
    # Entrenar SVM
    print("🤖 Entrenando SVM (C=1.0, kernel=linear)...")
    print("   Esto puede tardar 1-2 minutos...")
    
    model = SVC(C=1.0, kernel='linear', probability=True, random_state=42)
    model.fit(X_train_proc, y_train)
    
    print("✅ Entrenamiento completado")
    print()
    
    # Evaluar
    print("📊 Evaluando modelo...")
    
    y_train_pred = model.predict(X_train_proc)
    train_acc = accuracy_score(y_train, y_train_pred)
    
    y_test_pred = model.predict(X_test_proc)
    test_acc = accuracy_score(y_test, y_test_pred)
    
    print(f"   Train Accuracy: {train_acc*100:.2f}%")
    print(f"   Test Accuracy:  {test_acc*100:.2f}%")
    print()
    
    # Guardar modelo
    print("💾 Guardando modelo...")
    model_path = MODELS_DIR / "modelo.pkl"
    preprocessor_path = MODELS_DIR / "preprocessor.pkl"
    
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    with open(preprocessor_path, 'wb') as f:
        pickle.dump(preprocessor, f)
    
    print(f"✅ Modelo: {model_path}")
    print(f"✅ Preprocessor: {preprocessor_path}")
    print()
    
    print("=" * 70)
    print("✅ ENTRENAMIENTO COMPLETADO")
    print("=" * 70)
    print()
    print(f"📊 Test Accuracy: {test_acc*100:.2f}%")
    print()
    print("Siguiente paso: python 3_reconocer_texto.py imagen.png")

if __name__ == "__main__":
    main()
