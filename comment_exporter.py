"""
Exportador de comentarios a archivo de texto plano formateado.
Crea archivos ligeros y fáciles de leer/grepear.
"""
import os
from datetime import datetime
from typing import List, Dict
import config


class CommentExporter:
    """
    Exporta comentarios a archivo de texto plano formateado.
    """
    
    def __init__(self):
        """
        Inicializa el exportador.
        """
        self.export_dir = os.path.join(config.DOWNLOAD_DIR, 'comments')
        os.makedirs(self.export_dir, exist_ok=True)
    
    def export_to_text(self, comments: List[Dict], video_id: str, video_title: str = None) -> str:
        """
        Exporta comentarios a un archivo de texto plano formateado.
        
        Args:
            comments: Lista de comentarios
            video_id: ID del video
            video_title: Título del video (opcional)
            
        Returns:
            str: Ruta del archivo creado
        """
        # Crear nombre de archivo seguro
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_title = self._sanitize_filename(video_title or video_id)
        filename = f"{safe_title}_{video_id}_{timestamp}.txt"
        filepath = os.path.join(self.export_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # Encabezado
            f.write("=" * 80 + "\n")
            f.write(f"COMENTARIOS DE YOUTUBE\n")
            f.write("=" * 80 + "\n")
            f.write(f"Video ID: {video_id}\n")
            if video_title:
                f.write(f"Título: {video_title}\n")
            f.write(f"Fecha de exportación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total de comentarios: {len(comments)}\n")
            f.write("=" * 80 + "\n\n")
            
            # Comentarios
            for i, comment in enumerate(comments, 1):
                f.write(f"[{i}] " + "-" * 76 + "\n")
                f.write(f"Autor: {comment['author']}\n")
                f.write(f"Fecha: {self._format_date(comment['published_at'])}\n")
                f.write(f"Likes: {comment['like_count']}\n")
                if comment.get('reply_count', 0) > 0:
                    f.write(f"Respuestas: {comment['reply_count']}\n")
                f.write("-" * 80 + "\n")
                f.write(f"{comment['text']}\n")
                f.write("\n")
            
            # Pie de página
            f.write("=" * 80 + "\n")
            f.write(f"Fin del archivo - {len(comments)} comentarios exportados\n")
            f.write("=" * 80 + "\n")
        
        return filepath
    
    def export_to_grep_format(self, comments: List[Dict], video_id: str, video_title: str = None) -> str:
        """
        Exporta comentarios en formato optimizado para grep.
        Formato: AUTHOR|DATE|LIKES|TEXT
        
        Args:
            comments: Lista de comentarios
            video_id: ID del video
            video_title: Título del video (opcional)
            
        Returns:
            str: Ruta del archivo creado
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_title = self._sanitize_filename(video_title or video_id)
        filename = f"{safe_title}_{video_id}_{timestamp}_grep.txt"
        filepath = os.path.join(self.export_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # Encabezado mínimo
            f.write(f"# Video ID: {video_id}\n")
            if video_title:
                f.write(f"# Título: {video_title}\n")
            f.write(f"# Exportado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Total: {len(comments)} comentarios\n")
            f.write("# Formato: AUTHOR|DATE|LIKES|TEXT\n")
            f.write("# " + "-" * 76 + "\n\n")
            
            # Comentarios en formato grep-friendly
            for comment in comments:
                # Escapar pipes y saltos de línea en el texto
                text = comment['text'].replace('|', '\\|').replace('\n', ' ').replace('\r', ' ')
                author = comment['author'].replace('|', '\\|')
                date = self._format_date(comment['published_at'])
                
                f.write(f"{author}|{date}|{comment['like_count']}|{text}\n")
        
        return filepath
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Limpia el nombre de archivo para que sea válido.
        
        Args:
            filename: Nombre original
            
        Returns:
            str: Nombre sanitizado
        """
        import re
        # Remover caracteres inválidos
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Reemplazar espacios con guiones bajos
        filename = filename.replace(' ', '_')
        # Limitar longitud
        if len(filename) > 100:
            filename = filename[:100]
        return filename.strip()
    
    def _format_date(self, date_str: str) -> str:
        """
        Formatea fecha ISO a formato legible.
        
        Args:
            date_str: Fecha en formato ISO 8601
            
        Returns:
            str: Fecha formateada
        """
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return date_str
