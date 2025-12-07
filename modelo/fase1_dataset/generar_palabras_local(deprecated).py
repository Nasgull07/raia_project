"""
Script para generar imágenes de palabras aleatorias usando una lista local
"""

from PIL import Image, ImageDraw, ImageFont
import numpy as np
from pathlib import Path
import random

class GeneradorPalabrasLocal:
    """Genera imágenes de palabras aleatorias desde una lista local."""
    
    # Lista de palabras en español (puedes ampliarla)
    PALABRAS = [
        "casa", "perro", "gato", "mesa", "silla", "libro", "agua", "sol", "luna", "estrella",
        "computadora", "telefono", "ventana", "puerta", "calle", "coche", "bicicleta", "tren", "avion", "barco",
        "familia", "madre", "padre", "hijo", "hija", "hermano", "hermana", "abuelo", "abuela", "tio",
        "escuela", "profesor", "estudiante", "examen", "libro", "cuaderno", "lapiz", "boligrafo", "papel", "pizarra",
        "comida", "pan", "agua", "leche", "cafe", "arroz", "pasta", "carne", "pescado", "pollo",
        "fruta", "manzana", "naranja", "platano", "fresa", "uva", "pera", "sandia", "melon", "cereza",
        "verdura", "lechuga", "tomate", "cebolla", "zanahoria", "papa", "ajo", "pepino", "pimiento", "brocoli",
        "ciudad", "pais", "mundo", "tierra", "cielo", "mar", "rio", "montana", "bosque", "desierto",
        "tiempo", "dia", "noche", "manana", "tarde", "hora", "minuto", "segundo", "semana", "mes",
        "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
        "lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo", "ayer", "hoy", "manana",
        "trabajo", "oficina", "empresa", "proyecto", "reunion", "correo", "email", "mensaje", "llamada", "telefono",
        "color", "rojo", "azul", "verde", "amarillo", "negro", "blanco", "gris", "rosa", "morado",
        "numero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve",
        "animal", "perro", "gato", "caballo", "vaca", "cerdo", "gallina", "pato", "pez", "pajaro",
        "grande", "pequeno", "alto", "bajo", "largo", "corto", "ancho", "estrecho", "gordo", "delgado",
        "bueno", "malo", "feliz", "triste", "alegre", "contento", "enfadado", "serio", "divertido", "aburrido",
        "caliente", "frio", "tibio", "helado", "templado", "ardiente", "fresco", "congelado", "caluroso", "glacial",
        "rapido", "lento", "veloz", "pausado", "ligero", "pesado", "agil", "torpe", "dinamico", "estatico",
        "nuevo", "viejo", "antiguo", "moderno", "reciente", "pasado", "futuro", "actual", "contemporaneo", "arcaico",
        "facil", "dificil", "simple", "complejo", "sencillo", "complicado", "accesible", "arduo", "trivial", "enrevesado",
        "limpio", "sucio", "ordenado", "desordenado", "pulcro", "mugriento", "inmaculado", "manchado", "aseado", "descuidado",
        "lleno", "vacio", "completo", "incompleto", "repleto", "hueco", "colmado", "despoblado", "saturado", "desierto",
        "abierto", "cerrado", "accesible", "clausurado", "disponible", "bloqueado", "franco", "hermético", "libre", "sellado",
        "claro", "oscuro", "luminoso", "tenebroso", "brillante", "sombrio", "radiante", "lobrego", "resplandeciente", "opaco",
        "fuerte", "debil", "poderoso", "fragil", "robusto", "delicado", "vigoroso", "endeble", "potente", "feble",
        "bonito", "feo", "hermoso", "horrible", "bello", "espantoso", "precioso", "horroroso", "lindo", "deforme",
        "cerca", "lejos", "proximo", "distante", "cercano", "remoto", "contiguo", "alejado", "inmediato", "lejano",
        "arriba", "abajo", "encima", "debajo", "sobre", "bajo", "superior", "inferior", "alto", "profundo",
        "dentro", "fuera", "interior", "exterior", "adentro", "afuera", "interno", "externo", "intimo", "foraneo",
        "delante", "detras", "adelante", "atras", "frontal", "trasero", "anterior", "posterior", "primero", "ultimo",
        "aqui", "ahi", "alla", "aca", "donde", "cuando", "como", "que", "quien", "cual",
        "porque", "si", "no", "quiza", "tal", "vez", "acaso", "probablemente", "posiblemente", "ciertamente",
        "literatura", "poesia", "prosa", "novela", "cuento", "verso", "rima", "estrofa", "poema", "relato",
        "musica", "cancion", "melodia", "ritmo", "armonia", "nota", "acorde", "tono", "sonido", "silencio",
        "arte", "pintura", "escultura", "dibujo", "fotografia", "imagen", "cuadro", "lienzo", "retrato", "paisaje",
        "ciencia", "fisica", "quimica", "biologia", "matematica", "geografia", "historia", "lengua", "idioma", "ingles",
        "deporte", "futbol", "baloncesto", "tenis", "natacion", "atletismo", "ciclismo", "boxeo", "gimnasia", "voleibol",
        "persona", "hombre", "mujer", "nino", "nina", "adulto", "joven", "anciano", "bebe", "adolescente",
        "profesion", "doctor", "enfermero", "profesor", "ingeniero", "arquitecto", "abogado", "policia", "bombero", "cocinero",
        "casa", "habitacion", "dormitorio", "cocina", "bano", "salon", "comedor", "jardin", "patio", "terraza",
        "mueble", "mesa", "silla", "sofa", "cama", "armario", "estanteria", "escritorio", "cajon", "lampara",
        "ropa", "camisa", "pantalon", "vestido", "falda", "zapato", "calcetines", "abrigo", "chaqueta", "bufanda",
        "tecnologia", "computadora", "ordenador", "portatil", "telefono", "tablet", "internet", "software", "hardware", "programa",
        "oficina", "escritorio", "ordenador", "impresora", "papel", "archivo", "carpeta", "documento", "teclado", "raton",
        "transporte", "coche", "autobus", "tren", "avion", "barco", "bicicleta", "moto", "metro", "taxi",
        "edificio", "casa", "apartamento", "piso", "oficina", "hotel", "hospital", "escuela", "iglesia", "museo",
        "naturaleza", "arbol", "flor", "hierba", "hoja", "rama", "raiz", "semilla", "fruto", "planta",
        "clima", "lluvia", "nieve", "viento", "sol", "nube", "niebla", "tormenta", "trueno", "relampago",
        "sentimiento", "amor", "odio", "alegria", "tristeza", "miedo", "valentia", "esperanza", "desesperacion", "confianza",
        "accion", "correr", "saltar", "caminar", "nadar", "volar", "caer", "subir", "bajar", "entrar",
        "comunicacion", "hablar", "escuchar", "leer", "escribir", "mirar", "ver", "oir", "decir", "contar",
        "objeto", "cosa", "elemento", "articulo", "producto", "mercancia", "utensilio", "herramienta", "instrumento", "aparato",
        "medida", "metro", "centimetro", "kilometro", "litro", "gramo", "kilogramo", "tonelada", "grado", "porcentaje",
        "forma", "circulo", "cuadrado", "triangulo", "rectangulo", "esfera", "cubo", "piramide", "cilindro", "cono",
        "direccion", "norte", "sur", "este", "oeste", "arriba", "abajo", "izquierda", "derecha", "centro",
        "cantidad", "mucho", "poco", "todo", "nada", "algo", "bastante", "demasiado", "suficiente", "escaso",
        "calidad", "bueno", "malo", "excelente", "pesimo", "regular", "aceptable", "inaceptable", "optimo", "deficiente",
        "lugar", "sitio", "espacio", "zona", "area", "region", "territorio", "paraje", "rincon", "esquina",
        "momento", "instante", "rato", "periodo", "epoca", "era", "fase", "etapa", "temporada", "estacion",
        "relacion", "amigo", "enemigo", "companero", "colega", "socio", "pareja", "novio", "novia", "esposo",
        "estado", "feliz", "triste", "cansado", "descansado", "enfermo", "sano", "vivo", "muerto", "despierto",
        "texto", "palabra", "frase", "oracion", "parrafo", "pagina", "capitulo", "libro", "documento", "escrito",
        "medio", "periodico", "revista", "television", "radio", "internet", "red", "noticia", "informacion", "dato",
        "espacio", "lugar", "sitio", "zona", "area", "superficie", "extension", "dimension", "distancia", "separacion",
        "material", "madera", "metal", "plastico", "vidrio", "papel", "tela", "cuero", "goma", "cemento",
        "alimento", "comida", "bebida", "desayuno", "almuerzo", "cena", "merienda", "aperitivo", "postre", "plato",
        "bebida", "agua", "leche", "cafe", "te", "jugo", "refresco", "vino", "cerveza", "licor",
        "utensilio", "cuchillo", "tenedor", "cuchara", "plato", "vaso", "taza", "olla", "sarten", "cazo",
        "herramienta", "martillo", "destornillador", "llave", "alicate", "sierra", "taladro", "nivel", "metro", "broca",
        "electronico", "television", "radio", "computadora", "telefono", "camara", "video", "audio", "altavoz", "microfono",
        "juego", "pelota", "juguete", "muneca", "coche", "puzzle", "carta", "dado", "ficha", "tablero",
        "musica", "instrumento", "guitarra", "piano", "violin", "flauta", "trompeta", "tambor", "saxofon", "clarinete",
        "medicina", "pastilla", "jarabe", "inyeccion", "vacuna", "cura", "tratamiento", "terapia", "remedio", "medicina",
        "educacion", "leccion", "clase", "curso", "asignatura", "materia", "tema", "capitulo", "ejercicio", "tarea",
        "matematica", "numero", "suma", "resta", "multiplicacion", "division", "fraccion", "decimal", "porcentaje", "ecuacion",
        "cuerpo", "cabeza", "brazo", "pierna", "mano", "pie", "ojo", "oreja", "nariz", "boca",
        "salud", "enfermedad", "medicina", "doctor", "hospital", "clinica", "consulta", "diagnostico", "sintoma", "tratamiento",
        "economia", "dinero", "precio", "costo", "valor", "gasto", "ingreso", "ganancia", "perdida", "ahorro",
        "comercio", "tienda", "mercado", "supermercado", "compra", "venta", "cliente", "vendedor", "producto", "servicio",
        "gobierno", "presidente", "ministro", "diputado", "senador", "alcalde", "concejal", "juez", "fiscal", "abogado",
        "ley", "derecho", "justicia", "tribunal", "juicio", "sentencia", "delito", "crimen", "pena", "castigo",
        "religion", "dios", "iglesia", "templo", "sacerdote", "monje", "rezar", "oracion", "fe", "creencia",
        "filosofia", "pensamiento", "idea", "concepto", "teoria", "razon", "logica", "verdad", "mentira", "conocimiento",
        "psicologia", "mente", "pensamiento", "emocion", "sentimiento", "conciencia", "inconsciente", "personalidad", "caracter", "temperamento",
        "sociedad", "comunidad", "grupo", "sociedad", "pueblo", "ciudad", "nacion", "pais", "estado", "gobierno",
        "cultura", "tradicion", "costumbre", "habito", "ritual", "ceremonia", "fiesta", "celebracion", "festival", "evento",
        "entretenimiento", "cine", "teatro", "concierto", "espectaculo", "show", "pelicula", "serie", "programa", "documental",
        "viaje", "turismo", "vacaciones", "destino", "hotel", "aeropuerto", "estacion", "terminal", "pasaje", "boleto",
        "geografia", "continente", "oceano", "isla", "peninsula", "cabo", "bahia", "golfo", "estrecho", "canal",
        "astronomia", "estrella", "planeta", "luna", "sol", "cometa", "asteroide", "galaxia", "universo", "cosmos",
        "geologia", "roca", "mineral", "tierra", "suelo", "arena", "piedra", "montana", "volcan", "terremoto",
        "botanica", "planta", "arbol", "flor", "hoja", "raiz", "tallo", "fruto", "semilla", "polen",
        "zoologia", "animal", "mamifero", "ave", "reptil", "anfibio", "pez", "insecto", "aracnido", "molusco",
        "informatica", "programa", "software", "hardware", "codigo", "algoritmo", "dato", "base", "red", "internet",
        "programacion", "codigo", "lenguaje", "python", "java", "javascript", "variable", "funcion", "clase", "objeto",
        "desarrollo", "proyecto", "aplicacion", "sistema", "plataforma", "framework", "libreria", "modulo", "paquete", "version",
        "diseno", "grafico", "imagen", "foto", "ilustracion", "logo", "icono", "banner", "poster", "flyer",
        "arquitectura", "edificio", "construccion", "estructura", "plano", "proyecto", "obra", "fachada", "techo", "pared",
        "ingenieria", "puente", "tunel", "carretera", "autopista", "via", "camino", "sendero", "ruta", "trayecto",
        "mecanica", "motor", "engranaje", "piston", "valvula", "eje", "rueda", "llanta", "freno", "acelerador",
        "electrica", "corriente", "voltaje", "circuito", "cable", "enchufe", "interruptor", "fusible", "bombilla", "luz",
        "quimica", "elemento", "compuesto", "molecula", "atomo", "ion", "proton", "neutron", "electron", "nucleo",
        "biologia", "celula", "tejido", "organo", "sistema", "organismo", "ser", "vida", "especie", "poblacion",
        "ecologia", "ambiente", "ecosistema", "habitat", "biosfera", "cadena", "equilibrio", "conservacion", "biodiversidad", "sustentabilidad",
        "meteorologia", "clima", "tiempo", "temperatura", "humedad", "presion", "viento", "precipitacion", "atmosfera", "pronostico",
        "oceanografia", "mar", "oceano", "agua", "ola", "corriente", "marea", "profundidad", "costa", "playa",
        "gastronomia", "receta", "ingrediente", "preparacion", "coccion", "sabor", "textura", "aroma", "presentacion", "degustacion",
        "agricultura", "cultivo", "cosecha", "siembra", "campo", "granja", "huerto", "invernadero", "riego", "abono",
        "ganaderia", "ganado", "rebanio", "pasto", "corral", "establo", "granja", "rancho", "hacienda", "finca",
        "pesca", "pescar", "red", "cana", "anzuelo", "carnada", "barco", "puerto", "muelle", "embarcadero",
        "mineria", "mina", "mineral", "excavacion", "pozo", "tunel", "veta", "yacimiento", "extraccion", "refinacion",
        "industria", "fabrica", "planta", "produccion", "manufactura", "proceso", "maquina", "equipo", "herramienta", "operario",
        "construccion", "obra", "edificio", "casa", "estructura", "cemento", "ladrillo", "arena", "grua", "andamio",
        "transporte", "vehiculo", "carga", "pasajero", "ruta", "viaje", "traslado", "envio", "entrega", "distribucion",
        "comunicacion", "mensaje", "informacion", "dato", "noticia", "aviso", "anuncio", "publicidad", "propaganda", "difusion",
        "administracion", "gestion", "direccion", "organizacion", "planificacion", "coordinacion", "control", "supervision", "evaluacion", "auditoria",
        "finanzas", "dinero", "capital", "inversion", "credito", "prestamo", "interes", "banco", "bolsa", "mercado",
        "marketing", "mercado", "cliente", "consumidor", "producto", "marca", "publicidad", "promocion", "venta", "distribucion",
        "recursos", "humanos", "personal", "empleado", "trabajador", "contratacion", "capacitacion", "evaluacion", "desempeno", "salario",
        "produccion", "fabricacion", "manufactura", "proceso", "linea", "cadena", "montaje", "ensamble", "calidad", "control",
        "logistica", "almacen", "bodega", "inventario", "stock", "distribucion", "transporte", "entrega", "envio", "recepcion",
        "calidad", "control", "estandar", "norma", "especificacion", "requisito", "cumplimiento", "conformidad", "certificacion", "auditoria",
        "seguridad", "proteccion", "prevencion", "riesgo", "peligro", "accidente", "incidente", "emergencia", "evacuacion", "rescate",
        "medio", "ambiente", "naturaleza", "ecosistema", "contaminacion", "reciclaje", "conservacion", "sostenibilidad", "ecologia", "verde",
        "energia", "electricidad", "potencia", "fuerza", "poder", "consumo", "ahorro", "eficiencia", "renovable", "sostenible",
        "investigacion", "estudio", "analisis", "experimento", "prueba", "ensayo", "observacion", "medicion", "evaluacion", "conclusion",
        "innovacion", "creatividad", "invencion", "descubrimiento", "desarrollo", "mejora", "avance", "progreso", "evolucion", "revolucion",
        "tecnologia", "avance", "desarrollo", "innovacion", "digital", "electronico", "automatico", "inteligente", "artificial", "virtual",
        "internet", "red", "web", "sitio", "pagina", "portal", "blog", "foro", "chat", "email",
        "social", "red", "comunidad", "grupo", "perfil", "publicacion", "comentario", "like", "compartir", "seguidor",
        "multimedia", "imagen", "video", "audio", "animacion", "grafico", "interactivo", "digital", "streaming", "descarga",
        "entretenimiento", "juego", "diversi on", "pasatiempo", "hobby", "aficion", "recreacion", "ocio", "descanso", "relajacion",
        "deportivo", "equipo", "jugador", "entrenador", "arbitro", "partido", "competencia", "torneo", "campeonato", "liga",
        "cultural", "arte", "museo", "galeria", "exposicion", "obra", "artista", "creador", "pintor", "escultor",
        "literario", "libro", "novela", "cuento", "poesia", "autor", "escritor", "poeta", "editor", "publicacion",
        "musical", "concierto", "banda", "orquesta", "musico", "cantante", "compositor", "interprete", "disco", "album",
        "cinematografico", "pelicula", "cine", "director", "actor", "actriz", "produccion", "estreno", "taquilla", "critica",
        "teatral", "obra", "teatro", "escena", "actor", "actriz", "director", "guion", "dialogo", "monólogo",
        "festividad", "fiesta", "celebracion", "aniversario", "cumpleanos", "boda", "navidad", "ano", "pascua", "carnaval",
        "tradicional", "costumbre", "ritual", "ceremonia", "folklore", "leyenda", "mito", "cuento", "historia", "relato",
        "gastronomico", "plato", "receta", "cocina", "chef", "restaurante", "menu", "carta", "especialidad", "delicia",
        "bebida", "refresco", "jugo", "batido", "smoothie", "cocktail", "licuado", "infusion", "tisana", "malta",
        "dulce", "postre", "pastel", "tarta", "galleta", "helado", "caramelo", "chocolate", "merengue", "flan",
        "salado", "aperitivo", "botana", "tapa", "pincho", "canape", "entremés", "bocadillo", "sandwich", "emparedado",
        "saludable", "nutritivo", "vitaminico", "proteico", "energetico", "organico", "natural", "fresco", "integral", "light",
        "cocina", "preparacion", "coccion", "hervir", "freir", "asar", "hornear", "cocer", "saltear", "gratinar",
        "sabor", "dulce", "salado", "amargo", "acido", "picante", "suave", "fuerte", "delicioso", "sabroso",
        "textura", "suave", "crujiente", "cremoso", "liquido", "solido", "pastoso", "gelatinoso", "espeso", "ligero",
        "presentacion", "decoracion", "guarnicion", "acompanamiento", "porcion", "racion", "servicio", "emplatado", "montaje", "disposicion",
        "utensilio", "cocina", "cuchillo", "tabla", "olla", "sarten", "espatula", "cucharon", "batidor", "colador",
        "electrodomestico", "nevera", "horno", "microondas", "lavadora", "secadora", "lavavajillas", "licuadora", "batidora", "tostadora",
        "limpieza", "limpiar", "lavar", "fregar", "barrer", "trapear", "aspirar", "sacudir", "pulir", "desinfectar",
        "higiene", "asearse", "banarse", "ducharse", "lavarse", "cepillarse", "peinarse", "afeitarse", "cortarse", "arreglarse",
        "cuidado", "personal", "belleza", "estetica", "maquillaje", "cosmetico", "crema", "locion", "perfume", "colonia",
        "salon", "peluqueria", "barberia", "spa", "masaje", "facial", "manicura", "pedicura", "depilacion", "tratamiento",
        "moda", "ropa", "prenda", "vestimenta", "atuendo", "outfit", "look", "estilo", "tendencia", "diseno",
        "accesorio", "bolso", "cartera", "cinturon", "corbata", "bufanda", "gorra", "sombrero", "guantes", "panuelo",
        "calzado", "zapato", "zapatilla", "sandalia", "bota", "mocasin", "tacon", "plataforma", "deportivo", "casual",
        "joyeria", "joya", "anillo", "collar", "pulsera", "pendiente", "arete", "broche", "medalla", "cadena",
        "relojeria", "reloj", "cronometro", "temporizador", "alarma", "pulsera", "digital", "analogico", "automatico", "manual",
        "optica", "gafas", "lentes", "anteojos", "montura", "cristal", "graduacion", "sol", "lectura", "contacto",
        "libreria", "libro", "estanteria", "ejemplar", "edicion", "tomo", "volumen", "coleccion", "biblioteca", "lectura",
        "papeleria", "papel", "cuaderno", "libreta", "carpeta", "archivador", "sobre", "tarjeta", "etiqueta", "adhesivo",
        "arte", "pincel", "paleta", "lienzo", "oleo", "acuarela", "pastel", "carboncillo", "tinta", "aerografo",
        "musica", "partitura", "pentagrama", "nota", "clave", "compas", "ritmo", "melodia", "armonia", "acorde",
        "fotografia", "camara", "objetivo", "lente", "flash", "tripode", "obturador", "apertura", "exposicion", "enfoque",
        "video", "camara", "grabacion", "edicion", "montaje", "corte", "transicion", "efecto", "filtro", "rendering",
        "jardineria", "planta", "flor", "semilla", "maceta", "tierra", "abono", "poda", "riego", "cultivo",
        "mascota", "perro", "gato", "pajaro", "pez", "hamster", "conejo", "tortuga", "iguana", "loro",
        "veterinaria", "veterinario", "clinica", "consulta", "vacuna", "tratamiento", "cirugia", "medicina", "cura", "revision",
        "zoo", "zoologico", "animal", "jaula", "recinto", "habitat", "cuidador", "alimentacion", "reproduccion", "conservacion",
        "acuario", "pez", "marino", "tropical", "agua", "tanque", "filtro", "oxigeno", "alimento", "decoracion",
        "botanico", "jardin", "invernadero", "especie", "planta", "arbol", "flor", "cactus", "suculenta", "orquidea",
        "parque", "jardin", "plaza", "espacio", "verde", "banco", "fuente", "estatua", "sendero", "juegos",
        "playa", "arena", "mar", "ola", "sol", "sombrilla", "toalla", "bano", "salvavidas", "surf",
        "montana", "cumbre", "pico", "cima", "ladera", "falda", "valle", "barranco", "desfiladero", "sendero",
        "camping", "tienda", "campamento", "mochila", "saco", "dormir", "fogata", "linterna", "brujula", "mapa",
        "senderismo", "caminar", "excursion", "ruta", "trail", "montana", "naturaleza", "aventura", "exploracion", "trekking",
        "escalada", "escalar", "pared", "roca", "cuerda", "arnes", "mosqueton", "casco", "magnesio", "reunion",
        "ciclismo", "bicicleta", "ruta", "carretera", "montana", "pedalear", "cadencia", "marcha", "cambio", "freno",
        "natacion", "piscina", "agua", "estilo", "libre", "espalda", "pecho", "mariposa", "brazada", "patada",
        "atletismo", "carrera", "maraton", "velocidad", "resistencia", "salto", "lanzamiento", "valla", "relevo", "pista",
        "gimnasia", "ejercicio", "rutina", "aparato", "barra", "paralelas", "anillas", "potro", "suelo", "barra",
        "yoga", "postura", "asana", "meditacion", "respiracion", "flexibilidad", "equilibrio", "concentracion", "relajacion", "esterilla",
        "pilates", "ejercicio", "core", "abdomen", "postura", "flexibilidad", "fuerza", "resistencia", "control", "precision",
        "boxeo", "golpe", "punetazo", "jab", "directo", "gancho", "uppercut", "guardia", "esquiva", "ring",
        "artes", "marciales", "karate", "judo", "taekwondo", "kung", "fu", "aikido", "jiujitsu", "capoeira",
        "baile", "danza", "coreografia", "paso", "movimiento", "ritmo", "musica", "pareja", "salon", "espectaculo",
        "canto", "cantar", "voz", "tono", "afinacion", "registro", "melodia", "letra", "estribillo", "verso",
        "instrumento", "tocar", "interpretar", "ejecutar", "practicar", "ensayar", "afinar", "templar", "acordar", "melodia",
        "teatro", "actuar", "interpretar", "personaje", "papel", "rol", "escena", "dialogo", "monologo", "improvisacion",
        "cine", "rodar", "filmar", "grabar", "escena", "toma", "plano", "secuencia", "montaje", "edicion",
        "lectura", "leer", "libro", "pagina", "capitulo", "parrafo", "linea", "palabra", "comprension", "analisis",
        "escritura", "escribir", "texto", "redaccion", "composicion", "ensayo", "articulo", "carta", "correo", "mensaje",
        "dibujo", "dibujar", "trazo", "linea", "sombra", "perspectiva", "proporcion", "boceto", "esbozo", "croquis",
        "pintura", "pintar", "color", "pigmento", "mezcla", "pincelada", "capa", "textura", "acabado", "barniz",
        "escultura", "esculpir", "modelar", "tallar", "cincelar", "moldear", "forma", "volumen", "relieve", "bulto",
        "ceramica", "arcilla", "barro", "torno", "modelar", "hornear", "esmalte", "vidriar", "decorar", "vasija",
        "fotografia", "fotografiar", "capturar", "encuadrar", "enfocar", "exponer", "revelar", "positivar", "ampliar", "retocar",
        "video", "grabar", "filmar", "capturar", "registrar", "documentar", "editar", "montar", "cortar", "empalmar",
        "animacion", "animar", "movimiento", "secuencia", "fotograma", "cuadro", "frame", "interpolacion", "tweening", "rendering",
        "diseno", "disenar", "crear", "concebir", "proyectar", "planificar", "bosquejar", "esquematizar", "delinear", "trazar",
        "arquitectura", "proyectar", "planear", "disenar", "construir", "edificar", "levantar", "erigir", "estructurar", "cimentar",
        "ingenieria", "calcular", "disenar", "proyectar", "desarrollar", "implementar", "optimizar", "mejorar", "innovar", "resolver",
        "programacion", "programar", "codificar", "desarrollar", "implementar", "debuguear", "testear", "compilar", "ejecutar", "desplegar",
        "reparacion", "reparar", "arreglar", "componer", "restaurar", "recomponer", "reconstruir", "renovar", "rehabilitar", "subsanar",
        "mantenimiento", "mantener", "conservar", "preservar", "cuidar", "proteger", "limpiar", "lubricar", "ajustar", "calibrar",
        "instalacion", "instalar", "montar", "ensamblar", "armar", "colocar", "fijar", "anclar", "sujetar", "asegurar",
        "configuracion", "configurar", "ajustar", "establecer", "definir", "parametrizar", "personalizar", "adaptar", "modificar", "cambiar",
        "operacion", "operar", "manejar", "controlar", "dirigir", "gestionar", "administrar", "supervisar", "coordinar", "organizar",
        "produccion", "producir", "fabricar", "manufacturar", "elaborar", "confeccionar", "realizar", "ejecutar", "llevar", "cabo",
        "distribucion", "distribuir", "repartir", "entregar", "enviar", "despachar", "remitir", "expedir", "transportar", "trasladar",
        "venta", "vender", "comercializar", "negociar", "ofertar", "promocionar", "ofrecer", "proponer", "sugerir", "recomendar",
        "compra", "comprar", "adquirir", "conseguir", "obtener", "procurar", "mercar", "abastecer", "surtir", "aprovisionar",
        "pago", "pagar", "abonar", "cancelar", "liquidar", "saldar", "satisfacer", "retribuir", "remunerar", "compensar",
        "cobro", "cobrar", "recaudar", "percibir", "recibir", "ingresar", "embolsar", "facturar", "cargar", "debitar",
        "ahorro", "ahorrar", "economizar", "guardar", "reservar", "atesorar", "acumular", "capitalizar", "invertir", "rentabilizar",
        "gasto", "gastar", "invertir", "desembolsar", "erogar", "costear", "sufragar", "pagar", "abonar", "cancelar",
        "inversion", "invertir", "colocar", "depositar", "destinar", "dedicar", "aplicar", "emplear", "utilizar", "aprovechar",
        "ganancia", "ganar", "lucrar", "beneficiar", "obtener", "conseguir", "lograr", "alcanzar", "rentar", "producir",
        "perdida", "perder", "extraviar", "olvidar", "desprender", "dejar", "abandonar", "soltar", "ceder", "renunciar",
        "contrato", "contratar", "acordar", "pactar", "convenir", "estipular", "establecer", "fijar", "determinar", "concertar",
        "acuerdo", "acordar", "convenir", "concertar", "pactar", "consensuar", "transigir", "ceder", "aceptar", "aprobar", 
        "ajedrez", "ajeno", "trajinar", "viajar", "bajamar", "bajar", "trabajar", "ajustar", "abajarse", "atajador", "ajuar", 
        "bajante", "bajito", "bajón", "bajel", "bajista", "bajón", "bajío", "trajín", "trajear", "trajeron"
    ]
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path(__file__).parent.parent.parent / "imagenes" / "entrenamiento"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuración de fuentes
        self.font_sizes = [40, 50, 60, 70]
        self.fonts = self._cargar_fuentes()
        
        # Obtener último número de imagen
        self.ultimo_numero = self._obtener_ultimo_numero()
    
    def _cargar_fuentes(self):
        """Carga diferentes fuentes disponibles en el sistema."""
        fuentes = []
        fuentes_a_probar = [
            "C:\\Windows\\Fonts\\Arial.ttf",
            "C:\\Windows\\Fonts\\Times.ttf",
            "C:\\Windows\\Fonts\\Calibri.ttf",
            "C:\\Windows\\Fonts\\Verdana.ttf",
            "C:\\Windows\\Fonts\\Georgia.ttf",
        ]
        
        for font_path in fuentes_a_probar:
            try:
                for size in self.font_sizes:
                    fuentes.append(ImageFont.truetype(font_path, size))
            except:
                continue
        
        # Si no se cargó ninguna fuente, usar la predeterminada
        if not fuentes:
            fuentes = [ImageFont.load_default() for _ in range(4)]
        
        return fuentes
    
    def _obtener_ultimo_numero(self):
        """Obtiene el último número de imagen existente."""
        archivos = list(self.output_dir.glob("palabra_*.png"))
        if not archivos:
            return 5000  # Empezar desde 5000
        
        numeros = []
        for archivo in archivos:
            try:
                partes = archivo.stem.split('_')
                if len(partes) >= 2:
                    numeros.append(int(partes[1]))
            except:
                continue
        
        return max(numeros) if numeros else 5000
    
    def obtener_palabra_aleatoria(self):
        """Obtiene una palabra aleatoria de la lista."""
        return random.choice(self.PALABRAS)
    
    def generar_imagen_palabra(self, palabra: str, estilo_mayusculas: str = "random"):
        """Genera una imagen con la palabra."""
        # Aplicar estilo de mayúsculas
        if estilo_mayusculas == "upper":
            palabra_procesada = palabra.upper()
        elif estilo_mayusculas == "lower":
            palabra_procesada = palabra.lower()
        elif estilo_mayusculas == "title":
            palabra_procesada = palabra.title()
        else:  # random
            estilos = ["upper", "lower", "title"]
            estilo = random.choice(estilos)
            if estilo == "upper":
                palabra_procesada = palabra.upper()
            elif estilo == "lower":
                palabra_procesada = palabra.lower()
            else:
                palabra_procesada = palabra.title()
        
        # Seleccionar fuente aleatoria
        font = random.choice(self.fonts)
        
        # Calcular tamaño de imagen
        width = max(300, len(palabra_procesada) * 60)
        height = 100
        
        # Crear imagen blanca
        img = Image.new('L', (width, height), color=255)
        draw = ImageDraw.Draw(img)
        
        # Dibujar texto negro
        draw.text((20, 20), palabra_procesada, fill=0, font=font)
        
        return img, palabra_procesada
    
    def guardar_imagen(self, img: Image, palabra: str):
        """Guarda la imagen con el formato correcto."""
        self.ultimo_numero += 1
        filename = f"palabra_{self.ultimo_numero:05d}_{palabra}.png"
        filepath = self.output_dir / filename
        img.save(filepath)
        return filepath
    

    def generar_imagenes(self, cantidad: int = 10):
        """Genera múltiples imágenes de palabras aleatorias y combinaciones especiales."""
        print(f"Generando {cantidad} imágenes de palabras aleatorias...")
        print(f"Directorio de salida: {self.output_dir}")
        print(f"Número inicial: {self.ultimo_numero + 1}")
        print()

        exitosas = 0

        # --- Generar imágenes para combinaciones especiales ---
        combinaciones_especiales = ["aj", "ff", "Aj"]
        print("Generando imágenes para combinaciones especiales: aj, ff, Aj")
        for comb in combinaciones_especiales:
            for estilo in ["upper", "lower", "title"]:
                img, texto = self.generar_imagen_palabra(comb, estilo)
                filepath = self.guardar_imagen(img, texto)
                print(f"     ✅ {filepath.name}")
                exitosas += 1

        # --- Generar imágenes para palabras aleatorias ---
        for i in range(cantidad):
            palabra = self.obtener_palabra_aleatoria()
            print(f"[{i+1}/{cantidad}] Palabra: {palabra}")
            for j in range(2):
                estilo = random.choice(["upper", "lower", "title"])
                img, palabra_procesada = self.generar_imagen_palabra(palabra, estilo)
                filepath = self.guardar_imagen(img, palabra_procesada)
                print(f"     ✅ {filepath.name}")
                exitosas += 1

        print()
        print(f"✨ Proceso completado!")
        print(f"   Total de imágenes generadas: {exitosas}")


def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Genera imágenes de palabras aleatorias desde lista local")
    parser.add_argument("-n", "--cantidad", type=int, default=10, 
                       help="Número de palabras a generar (default: 10)")
    parser.add_argument("-o", "--output", type=str, default=None,
                       help="Directorio de salida (default: imagenes/entrenamiento)")
    
    args = parser.parse_args()
    
    # Crear directorio de salida si se especifica
    output_dir = Path(args.output) if args.output else None
    
    # Crear generador
    generador = GeneradorPalabrasLocal(output_dir)
    
    # Generar imágenes
    generador.generar_imagenes(args.cantidad)


if __name__ == "__main__":
    main()
