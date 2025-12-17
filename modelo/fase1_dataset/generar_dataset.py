"""
Script 1 (MEJORADO): Generar dataset incluyendo puntuación, acentos y espacios
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image
from tqdm import tqdm

# Importar segmentador desde la misma carpeta
from simple_segmenter import SimpleImageSegmenter

# Configuración
IMAGES_DIR = Path(__file__).parent.parent.parent / "imagenes" / "entrenamiento"
IMAGES_PUNTUACION_DIR = Path(__file__).parent.parent.parent / "imagenes" / "entrenamiento_puntuacion"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

# Mapeo de caracteres EXPANDIDO (Español, Catalán, Inglés)
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
ACENTOS_AGUDOS = "ÁÉÍÓÚáéíóú"  # Español y Catalán
ACENTOS_GRAVES = "ÀÈÌÒÙàèìòù"  # Catalán
DIERESIS = "ÏÜïü"  # Español (ü) y Catalán (ï, ü)
ESPECIALES_CATALAN = "Çç"  # ç cedilla catalana
ESPECIALES_ESPANOL = "Ññ"  # ñ española
APOSTROFE = "'"  # Inglés (apóstrofe)
PUNTUACION = ",.;:¿?¡!-"  # Signos de puntuación comunes
ESPACIO = " "

# Nota: La ela geminada catalana (l·l) se trata como secuencia de caracteres individuales
TODOS_CARACTERES = (LETTERS + ACENTOS_AGUDOS + ACENTOS_GRAVES + DIERESIS + 
                    ESPECIALES_CATALAN + ESPECIALES_ESPANOL + APOSTROFE + 
                    PUNTUACION + ESPACIO)
LETTER_TO_LABEL = {char: i+1 for i, char in enumerate(TODOS_CARACTERES)}

print("=" * 70)
print("MAPEO DE CARACTERES:")
print("=" * 70)
for char, label in LETTER_TO_LABEL.items():
    if char == " ":
        print(f"{label}: ESPACIO")
    else:
        print(f"{label}: {char}")
print("=" * 70)
print()

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
        
        # Verificar coincidencia (ahora permite puntuación y acentos)
        if len(letras_segmentadas) != len(palabra):
            return []
        
        # Procesar cada letra
        samples = []
        for i, letra_img in enumerate(letras_segmentadas):
            letra_real = palabra[i]
            
            # Verificar que el caracter esté en nuestro mapeo
            if letra_real not in LETTER_TO_LABEL:
                continue
            
            # Asegurar 28x28
            if letra_img.shape != (28, 28):
                img_pil = Image.fromarray(letra_img.astype(np.uint8))
                img_pil = img_pil.resize((28, 28), Image.LANCZOS)
                letra_img = np.array(img_pil)
            
            # INVERTIR COLORES (segmentador: fondo=0, modelo espera: fondo=255)
            letra_img = 255 - letra_img
            
            # Para espacios, permitir imágenes más vacías
            if letra_real == " ":
                # Imagen de espacio debe ser mayormente blanca
                pass  # No verificar contenido para espacios
            else:
                # Verificar no vacía para otros caracteres
                if np.sum(letra_img < 255) < 5:
                    continue
            
            # Crear muestra
            label = LETTER_TO_LABEL[letra_real]
            pixels = letra_img.flatten()
            sample = [label] + pixels.tolist()
            samples.append(sample)
        
        return samples
    except Exception as e:
        print(f"Error procesando {image_path}: {e}")
        return []

def procesar_caracteres_individuales(chars_dir: Path, segmenter):
    """Procesa caracteres individuales pasándolos por el segmentador para consistencia."""
    samples = []
    
    if not chars_dir.exists():
        return samples
    
    image_files = list(chars_dir.glob("char_*.png"))
    print(f"[INFO] Encontrados {len(image_files)} caracteres individuales")
    
    for img_path in tqdm(image_files, desc="Procesando caracteres"):
        try:
            # Extraer el caracter del nombre del archivo
            filename = img_path.stem  # Ejemplo: char_A_001 o char_c_cedilla_001
            parts = filename.split('_')
            
            if len(parts) < 2:
                continue
            
            # Obtener nombre del caracter (puede ser multipalabra como c_cedilla)
            # El formato es char_NOMBRE_NUMERO, donde NOMBRE puede tener _ adicionales
            # Quitamos 'char_' del inicio y el número del final
            char_name = '_'.join(parts[1:-1]) if len(parts) > 3 else parts[1]
            
            # Mapear nombre a caracter real
            char_map = {
                "coma": ",",
                "punto": ".",
                "puntocoma": ";",
                "dospuntos": ":",
                "abreinterrog": "¿",
                "cierrainterrog": "?",
                "abreexclam": "¡",
                "cierraexclam": "!",
                "guion": "-",
                "apostrofe": "'",
                "n_tilde": "ñ",
                "N_tilde": "Ñ",
                "c_cedilla": "ç",
                "C_cedilla_may": "Ç",
                "a_aguda": "á",
                "e_aguda": "é",
                "i_aguda": "í",
                "o_aguda": "ó",
                "u_aguda": "ú",
                "A_aguda": "Á",
                "E_aguda": "É",
                "I_aguda": "Í",
                "O_aguda": "Ó",
                "U_aguda": "Ú",
                "a_grave": "à",
                "e_grave": "è",
                "i_grave": "ì",
                "o_grave": "ò",
                "u_grave": "ù",
                "A_grave": "À",
                "E_grave": "È",
                "I_grave": "Ì",
                "O_grave": "Ò",
                "U_grave": "Ù",
                "i_dieresis": "ï",
                "u_dieresis": "ü",
                "I_dieresis": "Ï",
                "U_dieresis": "Ü",
                "espacio": " "
            }
            
            if char_name in char_map:
                char_real = char_map[char_name]
            else:
                char_real = char_name  # Para letras normales y acentos
            
            if char_real not in LETTER_TO_LABEL:
                continue
            
            # Cargar imagen
            img = Image.open(img_path).convert('L')
            img_array = np.array(img)
            
            # PASAR POR SEGMENTADOR para aplicar las mismas transformaciones
            # que se aplicarán durante el reconocimiento
            letras_segmentadas = segmenter.segment_word(img_array)
            
            # Si el segmentador no detecta nada o detecta más de 1 letra, usar método directo
            if not letras_segmentadas or len(letras_segmentadas) != 1:
                # Fallback: procesamiento directo
                img = img.resize((28, 28), Image.LANCZOS)
                letra_img = np.array(img)
                letra_img = 255 - letra_img
            else:
                # Usar la letra segmentada (ya viene en 28x28 desde el segmentador)
                letra_img = letras_segmentadas[0]
                # El segmentador ya invierte los colores internamente,
                # pero necesitamos invertirlos de nuevo para que coincida con el procesamiento
                letra_img = 255 - letra_img
            
            # Crear muestra
            label = LETTER_TO_LABEL[char_real]
            pixels = letra_img.flatten()
            sample = [label] + pixels.tolist()
            samples.append(sample)
            
        except Exception as e:
            print(f"Error procesando {img_path}: {e}")
            continue
    
    return samples

def main():
    print("=" * 70)
    print("GENERADOR DE DATASET CON PUNTUACIÓN Y ACENTOS")
    print("=" * 70)
    print()
    
    all_samples = []
    
    # Procesar imágenes de palabras originales
    if IMAGES_DIR.exists():
        image_files = list(IMAGES_DIR.glob("*.png"))
        print(f"🖼️  Imágenes de palabras originales: {len(image_files)}")
        
        segmenter = SimpleImageSegmenter()
        
        for img_path in tqdm(image_files, desc="Procesando palabras originales"):
            samples = procesar_imagen(img_path, segmenter)
            all_samples.extend(samples)
        
        print(f"[OK] Muestras de palabras originales: {len(all_samples)}")
    else:
        print("[AVISO] No se encontró directorio de imágenes originales")
    
    print()
    
    # Procesar imágenes con puntuación
    if IMAGES_PUNTUACION_DIR.exists():
        image_files_punt = list(IMAGES_PUNTUACION_DIR.glob("palabra_*.png"))
        print(f"[INFO] Imágenes de palabras con puntuación: {len(image_files_punt)}")
        
        segmenter = SimpleImageSegmenter()
        samples_antes = len(all_samples)
        
        for img_path in tqdm(image_files_punt, desc="Procesando palabras con puntuación"):
            samples = procesar_imagen(img_path, segmenter)
            all_samples.extend(samples)
        
        print(f"[OK] Nuevas muestras con puntuación: {len(all_samples) - samples_antes}")
        
        # Procesar caracteres individuales (ahora también pasan por el segmentador)
        samples_chars = procesar_caracteres_individuales(IMAGES_PUNTUACION_DIR, segmenter)
        all_samples.extend(samples_chars)
        print(f"[OK] Muestras de caracteres individuales: {len(samples_chars)}")
    else:
        print("[AVISO] No se encontró directorio de puntuación")
        print("    Ejecuta primero: python generar_con_puntuacion.py")
    
    print()
    print(f"[OK] Total muestras: {len(all_samples)}")
    
    if len(all_samples) == 0:
        print("[ERROR] No se generaron muestras")
        return
    
    # Crear DataFrame
    print("[INFO] Creando CSV...")
    columns = ['label'] + [f'pixel{i}' for i in range(784)]
    df = pd.DataFrame(all_samples, columns=columns)
    
    # Mostrar distribución de clases
    print()
    print("[INFO] Distribución de caracteres:")
    label_counts = df['label'].value_counts().sort_index()
    
    # Mapeo inverso
    LABEL_TO_CHAR = {v: k for k, v in LETTER_TO_LABEL.items()}
    
    for label, count in label_counts.items():
        char = LABEL_TO_CHAR.get(label, "?")
        char_display = "ESPACIO" if char == " " else char
        print(f"  {label:3d} ({char_display}): {count:5d} muestras")
    
    print()
    
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
    
    # Duplicar datos generados
    df_train = pd.concat([df_train, df_train], ignore_index=True)
    df_test = pd.concat([df_test, df_test], ignore_index=True)

    # Guardar conjuntos duplicados
    df_train.to_csv(train_path, index=False)
    df_test.to_csv(test_path, index=False)

    print(f"[OK] Train duplicado: {len(df_train)} muestras -> {train_path}")
    print(f"[OK] Test duplicado: {len(df_test)} muestras -> {test_path}")
    
    # Guardar mapping completo
    with open(mapping_path, 'w', encoding='utf-8') as f:
        for char, label in LETTER_TO_LABEL.items():
            if char == " ":
                f.write(f"{label} ESPACIO\n")
            else:
                f.write(f"{label} {char}\n")
    
    print(f"[OK] Train: {len(df_train)} muestras -> {train_path}")
    print(f"[OK] Test: {len(df_test)} muestras -> {test_path}")
    print(f"[OK] Mapping: {mapping_path}")
    print()
    print("=" * 70)
    print("[OK] DATASET GENERADO CON ÉXITO")
    print("=" * 70)
    print()
    print(f"Total de clases: {len(LETTER_TO_LABEL)}")
    print(f"  - Letras básicas: 52 (A-Z, a-z)")
    print(f"  - Acentos agudos: 10 (Á, É, Í, Ó, Ú, á, é, í, ó, ú) [Español/Catalán]")
    print(f"  - Acentos graves: 10 (À, È, Ì, Ò, Ù, à, è, ì, ò, ù) [Catalán]")
    print(f"  - Diéresis: 4 (Ï, Ü, ï, ü) [Español/Catalán]")
    print(f"  - Especiales Catalán: 2 (Ç, ç)")
    print(f"  - Especiales Español: 2 (Ñ, ñ)")
    print(f"  - Apóstrofe: 1 (') [Inglés]")
    print(f"  - Puntuación: 10 (, . ; : ¿ ? ¡ ! -)")
    print(f"  - Espacio: 1")
    print(f"  TOTAL: {len(LETTER_TO_LABEL)} clases (Español, Catalán, Inglés)")
    print()
    print("Siguiente paso: python ../fase2_entrenamiento/entrenar_modelo.py")

if __name__ == "__main__":
    main()
