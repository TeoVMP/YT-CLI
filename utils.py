"""
Utilidades para el bot de YouTube.
"""
import re
from typing import Optional


def extract_video_id(url_or_id: str) -> Optional[str]:
    """
    Extrae el ID del video de una URL de YouTube o retorna el ID si ya es un ID.
    
    Args:
        url_or_id: URL de YouTube o ID del video
        
    Returns:
        str: ID del video o None si no se puede extraer
    """
    # Si ya es un ID (solo caracteres alfanuméricos y guiones, longitud ~11)
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
        return url_or_id
    
    # Patrones comunes de URLs de YouTube
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    
    # Si no coincide con ningún patrón, intentar extraer cualquier ID de 11 caracteres
    match = re.search(r'([a-zA-Z0-9_-]{11})', url_or_id)
    if match:
        return match.group(1)
    
    return None
