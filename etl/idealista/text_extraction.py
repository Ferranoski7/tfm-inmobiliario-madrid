import re
import unidecode
from datetime import datetime


def normalize_text(text: str) -> str:
    """
    Convierte texto a minúsculas, elimina tildes y normaliza espacios.
    """
    if not text:
        return ""
    return unidecode.unidecode(text.lower().strip())

def is_on_top_floor(description: str) -> int:
    """Determina si la descripción indica que el piso está en la última planta.
    Ej: "ático", "última planta", "en la última planta"
    """
    text = normalize_text(description)
    keywords = ["ático", "última planta", "en la última planta", "en la última planta"]
    return int(any(k in text for k in keywords))

def has_terrace(description: str) -> int:
    text = normalize_text(description)
    keywords = ["terraza", "balcon", "patio", "solarium"]
    return int(any(k in text for k in keywords))


def has_boxroom(description: str) -> int:
    text = normalize_text(description)
    return int("trastero" in text)


def has_wardrobe(description: str) -> int:
    text = normalize_text(description)
    return int("armario empotrado" in text or "armarios empotrados" in text)


def has_doorman(description: str) -> int:
    text = normalize_text(description)
    return int("portero" in text or "conserje" in text)


def has_garden(description: str) -> int:
    text = normalize_text(description)
    keywords = ["jardin", "zona ajardinada", "patio con plantas"]
    return int(any(k in text for k in keywords))


def has_orientation(description: str, direction: str) -> int:
    """
    Detecta orientación cardinal en la descripción.
    Ej: has_orientation(desc, 'sur') => 1 si contiene 'orientacion sur'
    """
    text = normalize_text(description)
    return int(f"orientacion {direction}" in text)
    
def has_pool(description: str) -> int:
    """
    Detecta si hay piscina en el anuncio.
    Ej: has_pool(desc) => 1 si contiene 'piscina'
    """
    text = normalize_text(description)
    return int("piscina" in text)

def extract_construction_year(description: str) -> int | None:
    text = normalize_text(description)
    # Busca expresiones como "construido en 2002"
    match = re.search(r"(construid[ao]?|construccion) en (\d{4})", text)
    if match:
        year = int(match.group(2))
        if 1800 < year <= datetime.now().year:
            return year
    return None


def extract_max_building_floors(description: str) -> int | None:
    """
    Ejemplo de patrón: 'edificio de 5 plantas'
    """
    text = normalize_text(description)
    match = re.search(r"edificio de (\d{1,2}) plantas?", text)
    return int(match.group(1)) if match else None


def extract_dwelling_count(description: str) -> int | None:
    """
    Ejemplo de patrón: 'conjunto de 20 viviendas'
    """
    text = normalize_text(description)
    match = re.search(r"(conjunto|bloque|edificio) de (\d{1,3}) viviendas", text)
    return int(match.group(2)) if match else None
