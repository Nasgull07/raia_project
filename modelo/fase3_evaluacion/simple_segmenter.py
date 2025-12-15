"""
Segmentador de imagenes simplificado para Streamlit
Version standalone sin dependencias de FASE2
"""

import numpy as np
from typing import List
from PIL import Image
from skimage import filters
from scipy import ndimage


class SimpleImageSegmenter:
    """Segmentador simple de imagenes en caracteres."""
    
    def __init__(self):
        self.min_char_width = 5
        self.min_spacing = 2
        self.debug = False  # Activar para debug
    
    def segment_image(self, image: np.ndarray) -> List[List[np.ndarray]]:
        """
        Segmentar imagen en líneas y luego en caracteres individuales.
        
        Args:
            image: Imagen en escala de grises (numpy array)
        
        Returns:
            Lista de líneas, cada una con una lista de imágenes de caracteres (28x28 cada una)
        """
        if image.size == 0:
            return []
        
        # Asegurar que es escala de grises
        if len(image.shape) == 3:
            image = np.mean(image, axis=2).astype(np.uint8)
        
        # Verificar que la imagen tiene contenido
        if np.max(image) == np.min(image):
            return []  # Imagen uniforme, sin contenido
        
        # Binarizar
        binary = self._binarize(image)
        
        # Verificar que hay contenido después de binarizar
        white_pixels = np.sum(binary > 0)
        if self.debug:
            print(f"DEBUG - Pixeles blancos después de binarizar: {white_pixels}")
            print(f"DEBUG - Shape imagen: {image.shape}")
            print(f"DEBUG - Min/Max binaria: {np.min(binary)}/{np.max(binary)}")
        
        if white_pixels < 10:
            if self.debug:
                print("DEBUG - Muy pocos pixeles blancos, retornando vacio")
            return []
        
        # Encontrar límites de líneas
        line_boundaries = self._find_line_boundaries(binary)
        
        if self.debug:
            print(f"DEBUG - Líneas encontradas: {len(line_boundaries)}")
            print(f"DEBUG - Line boundaries: {line_boundaries}")
        
        if not line_boundaries:
            return []
        
        # Segmentar cada línea en caracteres
        all_lines = []
        for y_start, y_end in line_boundaries:
            line_img = self._extract_line(binary, y_start, y_end)
            characters = self.segment_line(line_img)
            if characters:  # Solo agregar si tiene caracteres
                all_lines.append(characters)
        
        return all_lines
    
    def segment_line(self, image: np.ndarray) -> List[np.ndarray]:
        """
        Segmentar una línea de texto en caracteres individuales.
        
        Args:
            image: Imagen de una línea en escala de grises (numpy array)
        
        Returns:
            Lista de imagenes de caracteres (28x28 cada una)
        """
        if image.size == 0:
            return []
        
        # Asegurar que es escala de grises
        if len(image.shape) == 3:
            image = np.mean(image, axis=2).astype(np.uint8)
        
        # Si no está binarizada, binarizar
        if not np.array_equal(np.unique(image), [0, 255]) and len(np.unique(image)) > 2:
            binary = self._binarize(image)
        else:
            binary = image
        
        # Encontrar limites de caracteres
        boundaries = self._find_boundaries(binary)
        # Detectar espacios entre letras
        chars_with_spaces = []
        min_space_width = 15  # Ajusta este valor según el tamaño de fuente/imágenes
        last_end = 0
        for idx, (x_start, x_end) in enumerate(boundaries):
            # Si hay un hueco grande entre el final anterior y el inicio actual, agregar espacio
            if x_start - last_end >= min_space_width and idx > 0:
                # Imagen blanca 28x28 para espacio
                chars_with_spaces.append(np.ones((28, 28), dtype=np.uint8) * 255)
            char_img = self._extract_char(binary, x_start, x_end)
            normalized = self._normalize_to_28x28(char_img)
            chars_with_spaces.append(normalized)
            last_end = x_end
        return chars_with_spaces
        
        if self.debug:
            print(f"DEBUG - Boundaries encontrados: {len(boundaries)}")
            print(f"DEBUG - Boundaries: {boundaries}")
        
        if not boundaries:
            return []
        
        # Extraer y normalizar caracteres
        characters = []
        for x_start, x_end in boundaries:
            char_img = self._extract_char(binary, x_start, x_end)
            normalized = self._normalize_to_28x28(char_img)
            characters.append(normalized)
        
        return characters
    
    def _binarize(self, image: np.ndarray) -> np.ndarray:
        """Binarizar imagen (texto oscuro = 255, fondo claro = 0)."""
        try:
            # Verificar si la imagen es mayormente clara (fondo blanco) o oscura
            mean_val = np.mean(image)
            
            # Para imagenes con fondo blanco (mean > 200), usar threshold más conservador
            if mean_val > 200:
                # Usar un threshold fijo más bajo para detectar texto negro
                threshold = 127  # Cualquier cosa más oscura que gris medio es texto
                binary = (image < threshold).astype(np.uint8) * 255
            elif mean_val > 127:
                # Fondo claro normal, usar Otsu
                threshold = filters.threshold_otsu(image)
                binary = (image < threshold).astype(np.uint8) * 255
            else:
                # Fondo oscuro, texto claro
                threshold = filters.threshold_otsu(image)
                binary = (image > threshold).astype(np.uint8) * 255
            
            return binary
        except:
            # Fallback simple
            mean_val = np.mean(image)
            threshold = 127
            if mean_val > 127:
                binary = (image < threshold).astype(np.uint8) * 255
            else:
                binary = (image > threshold).astype(np.uint8) * 255
            return binary
    
    def _find_boundaries(self, binary: np.ndarray) -> List[tuple]:
        """Encontrar limites de caracteres usando proyeccion vertical."""
        # Proyeccion vertical (contar pixeles blancos por columna)
        projection = np.sum(binary > 0, axis=0)
        
        if self.debug:
            print(f"DEBUG - Projection shape: {projection.shape}")
            print(f"DEBUG - Projection max: {np.max(projection)}, min: {np.min(projection)}")
            print(f"DEBUG - Projection non-zero columns: {np.sum(projection > 0)}")
        
        # Detectar columnas con contenido vs columnas vacías
        # Una columna está vacía si tiene 0 píxeles blancos
        has_content = projection > 0
        
        if self.debug:
            print(f"DEBUG - Columns with content: {np.sum(has_content)}")
        
        # Encontrar regiones continuas de contenido
        boundaries = []
        in_char = False
        start = 0
        
        for i, has_pixel in enumerate(has_content):
            if has_pixel and not in_char:
                # Inicio de una letra (primera columna con contenido)
                start = i
                in_char = True
            elif not has_pixel and in_char:
                # Fin de una letra (primera columna vacía después de contenido)
                boundaries.append((start, i))
                in_char = False
        
        # Si termina con contenido
        if in_char:
            boundaries.append((start, len(has_content)))
        
        if self.debug:
            print(f"DEBUG - Boundaries encontrados: {len(boundaries)}")
            print(f"DEBUG - Boundaries: {boundaries}")
        
        # Filtrar regiones muy pequeñas (ruido)
        min_char_width = 3
        boundaries = [(s, e) for s, e in boundaries if (e - s) >= min_char_width]
        
        if self.debug:
            print(f"DEBUG - Boundaries después de filtrar: {len(boundaries)}")
        
        return boundaries
        in_char = False
        start = 0
        
        for i, has_pixel in enumerate(has_content):
            if has_pixel and not in_char:
                # Inicio de una letra (primera columna con contenido)
                start = i
                in_char = True
            elif not has_pixel and in_char:
                # Fin de una letra (primera columna vacía después de contenido)
                boundaries.append((start, i))
                in_char = False
        
        # Si termina con contenido
        if in_char:
            boundaries.append((start, len(has_content)))
        
        if self.debug:
            print(f"DEBUG - Boundaries encontrados: {len(boundaries)}")
            print(f"DEBUG - Boundaries: {boundaries}")
        
        # Filtrar regiones muy pequeñas (ruido)
        min_char_width = 3
        boundaries = [(s, e) for s, e in boundaries if (e - s) >= min_char_width]
        
        if self.debug:
            print(f"DEBUG - Boundaries después de filtrar: {len(boundaries)}")
        
        return boundaries
    
    def _extract_char(self, image: np.ndarray, x_start: int, x_end: int) -> np.ndarray:
        """Extraer un caracter de la imagen."""
        # Extraer columnas
        char_img = image[:, x_start:x_end]
        
        # Recortar filas vacias arriba y abajo
        rows_with_content = np.any(char_img > 0, axis=1)
        if not np.any(rows_with_content):
            return np.zeros((28, 28), dtype=np.uint8)
        
        first_row = np.argmax(rows_with_content)
        last_row = len(rows_with_content) - np.argmax(rows_with_content[::-1]) - 1
        
        char_img = char_img[first_row:last_row+1, :]
        
        return char_img
    
    def _normalize_to_28x28(self, char_img: np.ndarray) -> np.ndarray:
        """Normalizar caracter a 28x28 manteniendo aspect ratio."""
        if char_img.size == 0:
            return np.zeros((28, 28), dtype=np.uint8)
        
        # Crear canvas 28x28 con fondo negro
        canvas = np.zeros((28, 28), dtype=np.uint8)
        
        h, w = char_img.shape
        
        # Calcular escala para que quepa en el canvas con margen
        max_dim = 24  # Dejar 2 pixeles de margen a cada lado
        scale = min(max_dim / h, max_dim / w)
        
        if scale < 1.0:  # Solo escalar si es muy grande
            new_h = int(h * scale)
            new_w = int(w * scale)
            
            # Redimensionar usando PIL
            img = Image.fromarray(char_img)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            char_img = np.array(img)
            h, w = new_h, new_w
        
        # Centrar en canvas
        y_offset = (28 - h) // 2
        x_offset = (28 - w) // 2
        
        # Asegurar que no se salga de los limites
        y_offset = max(0, min(y_offset, 28 - h))
        x_offset = max(0, min(x_offset, 28 - w))
        
        canvas[y_offset:y_offset+h, x_offset:x_offset+w] = char_img
        
        return canvas
    
    def _find_line_boundaries(self, binary: np.ndarray) -> List[tuple]:
        """Encontrar límites de líneas usando proyección horizontal."""
        # Proyección horizontal (contar píxeles blancos por fila)
        projection = np.sum(binary > 0, axis=1)
        
        if self.debug:
            print(f"DEBUG - Projection horizontal shape: {projection.shape}")
            print(f"DEBUG - Projection max: {np.max(projection)}, min: {np.min(projection)}")
        
        # Detectar filas con contenido vs filas vacías
        has_content = projection > 0
        
        # Encontrar regiones continuas de contenido (líneas)
        boundaries = []
        in_line = False
        start = 0
        min_line_height = 5  # Altura mínima de una línea
        
        for i, has_pixel in enumerate(has_content):
            if has_pixel and not in_line:
                # Inicio de una línea
                start = i
                in_line = True
            elif not has_pixel and in_line:
                # Fin de una línea
                if (i - start) >= min_line_height:
                    boundaries.append((start, i))
                in_line = False
        
        # Si termina con contenido
        if in_line and (len(has_content) - start) >= min_line_height:
            boundaries.append((start, len(has_content)))
        
        if self.debug:
            print(f"DEBUG - Line boundaries encontrados: {len(boundaries)}")
        
        return boundaries
    
    def _extract_line(self, image: np.ndarray, y_start: int, y_end: int) -> np.ndarray:
        """Extraer una línea de la imagen."""
        line_img = image[y_start:y_end, :]
        
        # Recortar columnas vacías a los lados
        cols_with_content = np.any(line_img > 0, axis=0)
        if not np.any(cols_with_content):
            return np.zeros((1, 1), dtype=np.uint8)
        
        first_col = np.argmax(cols_with_content)
        last_col = len(cols_with_content) - np.argmax(cols_with_content[::-1]) - 1
        
        line_img = line_img[:, first_col:last_col+1]
        
        return line_img
