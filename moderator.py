"""
Sistema de moderación automática de comentarios.
Monitorea y elimina comentarios que violen reglas éticas.
"""
import time
import json
import os
from datetime import datetime
from typing import List, Dict
from youtube_client import YouTubeClient
from content_analyzer import ContentAnalyzer
import config


class Moderator:
    """
    Sistema de moderación que monitorea y elimina comentarios automáticamente.
    """
    
    def __init__(self, youtube_client: YouTubeClient):
        """
        Inicializa el moderador.
        
        Args:
            youtube_client: Cliente de YouTube API
        """
        self.youtube_client = youtube_client
        self.analyzer = ContentAnalyzer(config.ETHICS_RULES_FILE)
        self.log_file = config.MODERATION_LOG_FILE
        self._ensure_log_file()
    
    def _ensure_log_file(self):
        """
        Asegura que el archivo de log existe.
        """
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def _log_action(self, action: str, comment_id: str, video_id: str, 
                    comment_text: str, reason: str = None):
        """
        Registra una acción de moderación en el log.
        
        Args:
            action: Tipo de acción ('deleted', 'checked', etc.)
            comment_id: ID del comentario
            video_id: ID del video
            comment_text: Texto del comentario
            reason: Razón de la acción (si aplica)
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'comment_id': comment_id,
            'video_id': video_id,
            'comment_text': comment_text[:100],  # Limitar longitud
            'reason': reason
        }
        
        try:
            # Leer log existente
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            # Agregar nueva entrada
            logs.append(log_entry)
            
            # Mantener solo últimas 1000 entradas
            if len(logs) > 1000:
                logs = logs[-1000:]
            
            # Guardar log
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            print(f"⚠ Error guardando log: {e}")
    
    def check_comment(self, comment: Dict) -> bool:
        """
        Verifica un comentario contra las reglas éticas.
        
        Args:
            comment: Diccionario con información del comentario
            
        Returns:
            bool: True si debe eliminarse, False si es válido
        """
        comment_text = comment.get('text', '')
        comment_id = comment.get('id')
        video_id = comment.get('video_id')
        
        # Analizar contenido
        violates, reasons = self.analyzer.analyze(comment_text)
        
        if violates:
            reason_str = '; '.join(reasons)
            print(f"\n⚠ Comentario viola reglas éticas:")
            print(f"  ID: {comment_id}")
            print(f"  Video: {video_id}")
            print(f"  Texto: {comment_text[:50]}...")
            print(f"  Razones: {reason_str}")
            
            # Eliminar si auto_delete está habilitado
            if self.analyzer.rules.get('auto_delete', True):
                if self.youtube_client.delete_comment(comment_id):
                    self._log_action('deleted', comment_id, video_id, comment_text, reason_str)
                    print(f"✓ Comentario eliminado automáticamente.")
                    return True
                else:
                    self._log_action('delete_failed', comment_id, video_id, comment_text, reason_str)
                    return False
            else:
                self._log_action('flagged', comment_id, video_id, comment_text, reason_str)
                return False
        
        return False
    
    def monitor_video_comments(self, video_id: str, max_comments: int = 50):
        """
        Monitorea comentarios de un video específico.
        
        Args:
            video_id: ID del video a monitorear
            max_comments: Número máximo de comentarios a revisar
        """
        print(f"\n🔍 Monitoreando comentarios del video: {video_id}")
        
        comments = self.youtube_client.get_comments(video_id, max_comments)
        
        if not comments:
            print("  No se encontraron comentarios.")
            return
        
        print(f"  Encontrados {len(comments)} comentarios.")
        
        deleted_count = 0
        for comment in comments:
            if self.check_comment(comment):
                deleted_count += 1
        
        print(f"\n✓ Monitoreo completado. Eliminados: {deleted_count}/{len(comments)}")
    
    def start_monitoring(self, video_ids: List[str] = None, interval: int = None):
        """
        Inicia monitoreo continuo de comentarios.
        
        Args:
            video_ids: Lista de IDs de videos a monitorear (opcional)
            interval: Intervalo entre verificaciones en segundos
        """
        if interval is None:
            interval = config.MODERATION_CHECK_INTERVAL
        
        print("\n" + "="*60)
        print("SISTEMA DE MODERACIÓN AUTOMÁTICA")
        print("="*60)
        print(f"Intervalo de verificación: {interval} segundos")
        print("Presiona Ctrl+C para detener")
        print("="*60 + "\n")
        
        try:
            while True:
                if video_ids:
                    for video_id in video_ids:
                        self.monitor_video_comments(video_id)
                else:
                    print("⚠ No se especificaron videos para monitorear.")
                    print("   Usa monitor_video_comments() con un video_id específico.")
                
                print(f"\n⏳ Esperando {interval} segundos hasta próxima verificación...")
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n\n✓ Monitoreo detenido por el usuario.")
