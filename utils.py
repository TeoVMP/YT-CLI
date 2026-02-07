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


def extract_playlist_id(url_or_id: str) -> Optional[str]:
    """
    Extrae el ID de la playlist de una URL de YouTube o retorna el ID si ya es un ID.
    
    Args:
        url_or_id: URL de YouTube con parámetro list= o ID de la playlist
        
    Returns:
        str: ID de la playlist o None si no se puede extraer
    """
    # Si ya es un ID de playlist (empieza con PL y tiene ~34 caracteres)
    if re.match(r'^PL[a-zA-Z0-9_-]{32}$', url_or_id):
        return url_or_id
    
    # Patrones comunes de URLs de YouTube con playlist
    patterns = [
        r'[?&]list=([a-zA-Z0-9_-]{34})',  # list=PL...
        r'youtube\.com\/playlist\?list=([a-zA-Z0-9_-]{34})',  # youtube.com/playlist?list=PL...
        r'youtube\.com\/watch\?.*list=([a-zA-Z0-9_-]{34})',  # youtube.com/watch?v=...&list=PL...
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    
    return None