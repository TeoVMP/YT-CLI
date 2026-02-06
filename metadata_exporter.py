"""
Exportador de metadatos de videos de YouTube.
"""
import os
import json
from datetime import datetime
from typing import Dict, Optional
import config


class MetadataExporter:
    """
    Clase para exportar metadatos de videos a diferentes formatos.
    """
    
    def __init__(self):
        self.export_dir = os.path.join(config.DOWNLOAD_DIR, 'metadata')
        os.makedirs(self.export_dir, exist_ok=True)
    
    def export_to_json(self, video_stats: Dict, video_id: str) -> str:
        """
        Exporta los metadatos del video a un archivo JSON.
        
        Args:
            video_stats: Diccionario con las estadísticas del video
            video_id: ID del video
            
        Returns:
            str: Ruta del archivo creado
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Sanitizar título para nombre de archivo
        title = video_stats.get('title', 'unknown_video')
        sanitized_title = "".join([c for c in title if c.isalnum() or c in (' ', '-', '_')]).rstrip()
        sanitized_title = sanitized_title.replace(' ', '_')[:50]  # Limitar longitud
        
        filename = f"{sanitized_title}_{video_id}_{timestamp}.json"
        filepath = os.path.join(self.export_dir, filename)
        
        # Preparar datos para exportar
        export_data = {
            'video_id': video_id,
            'exported_at': datetime.now().isoformat(),
            'metadata': video_stats
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def export_to_text(self, video_stats: Dict, video_id: str) -> str:
        """
        Exporta los metadatos del video a un archivo de texto legible.
        
        Args:
            video_stats: Diccionario con las estadísticas del video
            video_id: ID del video
            
        Returns:
            str: Ruta del archivo creado
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Sanitizar título para nombre de archivo
        title = video_stats.get('title', 'unknown_video')
        sanitized_title = "".join([c for c in title if c.isalnum() or c in (' ', '-', '_')]).rstrip()
        sanitized_title = sanitized_title.replace(' ', '_')[:50]  # Limitar longitud
        
        filename = f"{sanitized_title}_{video_id}_{timestamp}.txt"
        filepath = os.path.join(self.export_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("METADATOS DEL VIDEO DE YOUTUBE\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"Video ID: {video_id}\n")
            f.write(f"Fecha de exportación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("\n" + "-"*80 + "\n\n")
            
            # Información básica
            f.write("INFORMACIÓN BÁSICA\n")
            f.write("-"*80 + "\n")
            f.write(f"Título: {video_stats.get('title', 'N/A')}\n")
            f.write(f"Canal: {video_stats.get('channel_title', 'N/A')}\n")
            f.write(f"Canal ID: {video_stats.get('channel_id', 'N/A')}\n")
            f.write(f"Fecha de publicación: {video_stats.get('published_at', 'N/A')}\n")
            f.write(f"Categoría ID: {video_stats.get('category_id', 'N/A')}\n")
            f.write(f"Idioma: {video_stats.get('default_language', 'N/A')}\n")
            
            # Descripción
            description = video_stats.get('description', '')
            if description:
                f.write("\nDESCRIPCIÓN\n")
                f.write("-"*80 + "\n")
                f.write(f"{description}\n")
            
            # Tags
            tags = video_stats.get('tags', [])
            if tags:
                f.write("\nTAGS\n")
                f.write("-"*80 + "\n")
                f.write(", ".join(tags) + "\n")
            
            # Estadísticas
            f.write("\nESTADÍSTICAS\n")
            f.write("-"*80 + "\n")
            f.write(f"Vistas: {video_stats.get('view_count', 0):,}\n")
            f.write(f"Likes: {video_stats.get('like_count', 0):,}\n")
            f.write(f"Dislikes: {video_stats.get('dislike_count', 0):,}\n")
            f.write(f"Comentarios: {video_stats.get('comment_count', 0):,}\n")
            f.write(f"Favoritos: {video_stats.get('favorite_count', 0):,}\n")
            
            # Duración
            f.write("\nDURACIÓN\n")
            f.write("-"*80 + "\n")
            f.write(f"Duración ISO: {video_stats.get('duration_iso', 'N/A')}\n")
            f.write(f"Duración en segundos: {video_stats.get('duration_seconds', 0)}\n")
            f.write(f"Duración formateada: {video_stats.get('duration_formatted', 'N/A')}\n")
            
            # Engagement Rate
            view_count = video_stats.get('view_count', 0)
            if view_count > 0:
                like_count = video_stats.get('like_count', 0)
                comment_count = video_stats.get('comment_count', 0)
                engagement = ((like_count + comment_count) / view_count) * 100
                f.write(f"Engagement Rate: {engagement:.2f}%\n")
            
            # Thumbnail
            thumbnail = video_stats.get('thumbnail')
            if thumbnail:
                f.write("\nTHUMBNAIL\n")
                f.write("-"*80 + "\n")
                f.write(f"URL: {thumbnail}\n")
            
            f.write("\n" + "="*80 + "\n")
        
        return filepath
    
    def export_metadata(self, video_stats: Dict, video_id: str, format_type: str = 'json') -> str:
        """
        Exporta los metadatos del video según el formato especificado.
        
        Args:
            video_stats: Diccionario con las estadísticas del video
            video_id: ID del video
            format_type: Formato de exportación ('json' o 'text')
            
        Returns:
            str: Ruta del archivo creado
        """
        if format_type.lower() == 'json':
            return self.export_to_json(video_stats, video_id)
        elif format_type.lower() == 'text':
            return self.export_to_text(video_stats, video_id)
        else:
            raise ValueError(f"Formato no soportado: {format_type}. Usa 'json' o 'text'")
