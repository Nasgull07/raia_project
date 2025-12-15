"""
Script para generar imágenes con signos de puntuación y letras acentuadas
"""

from PIL import Image, ImageDraw, ImageFont
import numpy as np
from pathlib import Path
import random

class GeneradorConPuntuacion:
    """Genera imágenes de caracteres individuales incluyendo puntuación y acentos (Español, Catalán, Inglés)."""
    
    # Caracteres a generar
    LETRAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    ACENTOS_AGUDOS = "ÁÉÍÓÚáéíóú"  # Español y Catalán
    ACENTOS_GRAVES = "ÀÈÌÒÙàèìòù"  # Catalán
    DIERESIS = "ÏÜïü"  # Español (ü) y Catalán (ï, ü)
    ESPECIALES_CATALAN = "Çç"  # ç cedilla catalana
    ESPECIALES_ESPANOL = "Ññ"  # ñ española
    APOSTROFE = "'"  # Inglés
    PUNTUACION = ",.;:¿?¡!-"  # Signos comunes
    ESPACIO = " "
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path(__file__).parent.parent.parent / "imagenes" / "entrenamiento_puntuacion"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuración de fuentes
        self.font_sizes = [40, 50, 60, 70]
        self.fonts = self._cargar_fuentes()
        
        # Todos los caracteres
        self.todos_caracteres = (self.LETRAS + self.ACENTOS_AGUDOS + self.ACENTOS_GRAVES + 
                                self.DIERESIS + self.ESPECIALES_CATALAN + self.ESPECIALES_ESPANOL + 
                                self.APOSTROFE + self.PUNTUACION + self.ESPACIO)
    
    def _cargar_fuentes(self):
        """Carga diferentes fuentes disponibles en el sistema."""
        fuentes = []
        fuentes_a_probar = [
            "C:\\Windows\\Fonts\\Arial.ttf",          # Sans-serif
            "C:\\Windows\\Fonts\\Times.ttf",          # Serif - ayuda a diferenciar I/l
            "C:\\Windows\\Fonts\\Calibri.ttf",        # Sans-serif moderna
            "C:\\Windows\\Fonts\\Verdana.ttf",        # Sans-serif ancha
            "C:\\Windows\\Fonts\\Georgia.ttf",        # Serif elegante
            "C:\\Windows\\Fonts\\Consola.ttf",        # Monospace - muy distinta
            "C:\\Windows\\Fonts\\Courier.ttf",        # Monospace clásica
            "C:\\Windows\\Fonts\\Tahoma.ttf",         # Sans-serif compacta
        ]
        
        for font_path in fuentes_a_probar:
            try:
                for size in self.font_sizes:
                    fuentes.append(ImageFont.truetype(font_path, size))
            except:
                continue
        
        if not fuentes:
            fuentes = [ImageFont.load_default() for _ in range(4)]
        
        return fuentes
    
    def generar_imagen_caracter(self, caracter: str):
        """Genera una imagen de 28x28 con un solo caracter."""
        # Seleccionar fuente aleatoria
        font = random.choice(self.fonts)
        
        # Para espacio, generar imagen completamente blanca
        if caracter == " ":
            img = Image.new('L', (28, 28), color=255)
            return img
        
        # Crear imagen temporal más grande
        temp_size = 100
        temp_img = Image.new('L', (temp_size, temp_size), color=255)
        draw = ImageDraw.Draw(temp_img)
        
        # Dibujar caracter negro centrado
        bbox = draw.textbbox((0, 0), caracter, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (temp_size - text_width) // 2
        y = (temp_size - text_height) // 2
        
        draw.text((x, y), caracter, fill=0, font=font)
        
        # Recortar el contenido (eliminar espacios en blanco excesivos)
        img_array = np.array(temp_img)
        rows = np.any(img_array < 255, axis=1)
        cols = np.any(img_array < 255, axis=0)
        
        if not rows.any() or not cols.any():
            # Si no hay contenido, devolver imagen blanca
            return Image.new('L', (28, 28), color=255)
        
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]
        
        # Añadir pequeño margen
        margin = 5
        rmin = max(0, rmin - margin)
        rmax = min(temp_size, rmax + margin)
        cmin = max(0, cmin - margin)
        cmax = min(temp_size, cmax + margin)
        
        cropped = temp_img.crop((cmin, rmin, cmax, rmax))
        
        # Redimensionar a 28x28 manteniendo aspect ratio
        cropped.thumbnail((28, 28), Image.LANCZOS)
        
        # Centrar en imagen 28x28
        final_img = Image.new('L', (28, 28), color=255)
        offset = ((28 - cropped.width) // 2, (28 - cropped.height) // 2)
        final_img.paste(cropped, offset)
        
        return final_img
    

    def generar_palabras_con_puntuacion(self, cantidad: int = 100):
        """Genera palabras con puntuación intercalada y guarda el mapeo en un txt."""
        palabras_base = [
            # Palabras con todas las letras del abecedario
            "Abajo", "Bebé", "Casa", "Dado", "Elefante", "Fácil", "Gato", "Hacer",
            "Iglesia", "Jardín", "Kilo", "Luna", "Madre", "Niño", "Ñoño", "Ojo",
            "Padre", "Quemar", "Rápido", "Salud", "Tiempo", "Uva", "Vino", "Watt",
            "Xilófono", "Yate", "Zapato",
            # Mayúsculas variadas
            "ALTO", "BAJO", "CASA", "DATO", "ENORME", "FELIZ", "GRANDE", "HOTEL",
            "IDEA", "JUEGO", "KIWI", "LIBRE", "MUNDO", "NUEVO", "OESTE", "PAÍS",
            "QUIEN", "RUIDO", "SABOR", "TARDE", "ÚNICO", "VOLAR", "WIFI", "XIXI",
            "YOGA", "ZONA",
            # Combinaciones de mayúsculas y minúsculas
            "Pablo", "María", "José", "Sofía", "Diego", "Carmen", "Miguel", "Laura",
            "España", "México", "París", "Berlín", "Londres", "Madrid", "Roma",
            # Palabras con acentos agudos
            "árbol", "café", "música", "español", "año", "José", "María", "Ángel",
            "programación", "información", "comunicación", "educación", "atención",
            "médico", "público", "básico", "técnico", "práctico", "cómodo", "rápido",
            "último", "único", "teléfono", "canción", "creación", "nación", "razón",
            # Palabras con acentos graves (menos comunes pero válidas)
            "però", "àrea", "òpera", "ès", "allà", "què", "dòna", "mès", "demà",
            # Palabras comunes
            "hola", "mundo", "Python", "datos", "codigo", "test", "ejemplo", "libro",
            "agua", "tierra", "fuego", "aire", "luz", "color", "forma", "linea",
            "punto", "circulo", "cuadrado", "triangulo", "rectangulo", "estrella",
            # Palabras técnicas
            "programa", "archivo", "carpeta", "sistema", "memoria", "disco", "red",
            "servidor", "cliente", "base", "tabla", "campo", "registro", "índice",
        ]

        print(f"Generando {cantidad} palabras con puntuación...")
        contador = 0

        # Abrir archivo de mapeo
        mapping_path = self.output_dir / "palabras_generadas.txt"
        with open(mapping_path, "a", encoding="utf-8") as mapping_file:
            for i in range(cantidad):
                # Elegir palabra base
                palabra = random.choice(palabras_base)

                # 50% de chance de añadir puntuación al final
                if random.random() < 0.5:
                    palabra += random.choice(",.;:!?")

                # 30% de chance de añadir puntuación al inicio (interrogación/exclamación)
                if random.random() < 0.3:
                    if palabra.endswith("?"):
                        palabra = "¿" + palabra
                    elif palabra.endswith("!"):
                        palabra = "¡" + palabra

                # Limpiar nombre para archivo (quitar caracteres prohibidos)
                palabra_limpia = ''.join(c for c in palabra if c not in '\\/*?:"<>|')
                filename = f"palabra_{5000+contador:05d}_{palabra_limpia}.png"
                filepath = self.output_dir / filename

                # Crear imagen de la palabra completa
                font = random.choice(self.fonts)
                width = max(300, len(palabra) * 60)
                height = 100

                img = Image.new('L', (width, height), color=255)
                draw = ImageDraw.Draw(img)
                draw.text((20, 20), palabra, fill=0, font=font)

                img.save(filepath)
                print(f"  ✅ {filename}")
                # Guardar mapeo palabra original → archivo
                mapping_file.write(f"{filename}\t{palabra}\n")
                contador += 1

        print(f"✅ Generadas {contador} palabras con puntuación")
    
    def generar_caracteres_individuales(self, repeticiones: int = 50):
        """Genera imágenes individuales de cada caracter."""
        print(f"Generando caracteres individuales (base: {repeticiones} repeticiones)...")
        
        # Caracteres problemáticos que necesitan más muestras
        caracteres_dificiles = "',çpIl"
        repeticiones_extra = 200  # Triple de muestras para caracteres problemáticos
        
        caracteres_sin_espacio = (self.LETRAS + self.ACENTOS_AGUDOS + self.ACENTOS_GRAVES + 
                                 self.DIERESIS + self.ESPECIALES_CATALAN + 
                                 self.ESPECIALES_ESPANOL + self.APOSTROFE + self.PUNTUACION)
        
        for caracter in caracteres_sin_espacio:
            # Determinar número de repeticiones
            num_reps = repeticiones_extra if caracter in caracteres_dificiles else repeticiones
            print(f"  Generando: {caracter} ({num_reps} muestras)")
            
            for rep in range(num_reps):
                img = self.generar_imagen_caracter(caracter)
                
                # Nombre del archivo
                nombre_car = caracter
                if caracter in ",.;:¿?¡!-":
                    nombres = {
                        ",": "coma",
                        ".": "punto",
                        ";": "puntocoma",
                        ":": "dospuntos",
                        "¿": "abreinterrog",
                        "?": "cierrainterrog",
                        "¡": "abreexclam",
                        "!": "cierraexclam",
                        "-": "guion",
                        "'": "apostrofe"
                    }
                    nombre_car = nombres.get(caracter, caracter)
                elif caracter in "ÇçÑñÏÜïü":
                    nombres_especiales = {
                        "Ç": "C_cedilla_may",
                        "ç": "c_cedilla",
                        "Ñ": "N_tilde_may", 
                        "ñ": "n_tilde",
                        "Ï": "I_dieresis_may",
                        "ï": "i_dieresis",
                        "Ü": "U_dieresis_may",
                        "ü": "u_dieresis"
                    }
                    nombre_car = nombres_especiales.get(caracter, caracter)
                
                filename = f"char_{nombre_car}_{rep:03d}.png"
                filepath = self.output_dir / filename
                
                img.save(filepath)
        
        # Generar espacios (imágenes blancas)
        print("  Generando: ESPACIO")
        for rep in range(repeticiones):
            img = Image.new('L', (28, 28), color=255)
            filename = f"char_espacio_{rep:03d}.png"
            filepath = self.output_dir / filename
            img.save(filepath)
        
        print(f"[OK] Caracteres individuales generados")


def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Genera imágenes con signos de puntuación")
    parser.add_argument("-w", "--palabras", type=int, default=100,
                       help="Número de palabras con puntuación a generar (default: 100)")
    parser.add_argument("-c", "--chars", type=int, default=50,
                       help="Repeticiones de cada caracter individual (default: 50)")
    parser.add_argument("-o", "--output", type=str, default=None,
                       help="Directorio de salida")
    
    args = parser.parse_args()
    
    output_dir = Path(args.output) if args.output else None
    generador = GeneradorConPuntuacion(output_dir)
    
    print("=" * 70)
    print("GENERADOR DE IMÁGENES CON PUNTUACIÓN Y ACENTOS")
    print("=" * 70)
    print()
    
    # Generar palabras completas con puntuación
    generador.generar_palabras_con_puntuacion(args.palabras)
    print()
    
    # Generar caracteres individuales
    generador.generar_caracteres_individuales(args.chars)
    print()
    
    print("=" * 70)
    print("[OK] GENERACIÓN COMPLETADA")
    print("=" * 70)
    print()
    print(f"Directorio de salida: {generador.output_dir}")
    print()
    print("Siguiente paso:")
    print("  1. Ejecuta: python scripts/1_generar_dataset.py")
    print("  2. Ejecuta: python scripts/2_entrenar_modelo.py")


if __name__ == "__main__":
    main()
