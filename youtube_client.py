"""
Cliente para interactuar con YouTube Data API v3.
Implementa autenticación OAuth2 con scopes limitados a YouTube (sin acceso a email).
"""
import os
import json
import pickle
from typing import Optional, Dict
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import config

# Importar protección solo si está disponible
try:
    from account_protection import AccountProtection
    PROTECTION_ENABLED = True
except ImportError:
    PROTECTION_ENABLED = False
    AccountProtection = None


class YouTubeClient:
    """
    Cliente para YouTube API con autenticación OAuth2.
    
    IMPORTANTE: Solo solicita permisos de YouTube, NO tiene acceso al email.
    Los scopes están limitados a youtube.force-ssl únicamente.
    """
    
    def __init__(self):
        self.service = None
        self.credentials = None
        # Inicializar protección si está disponible
        if PROTECTION_ENABLED and AccountProtection:
            self.protection = AccountProtection()
        else:
            self.protection = None
        self._authenticate()
    
    def _authenticate(self):
        """
        Autentica con YouTube API usando OAuth2.
        Solo solicita permisos de YouTube (sin acceso a email).
        """
        creds = None
        
        # Verificar si ya existe un token guardado
        if os.path.exists(config.TOKEN_FILE):
            try:
                creds = Credentials.from_authorized_user_file(
                    config.TOKEN_FILE, 
                    config.YOUTUBE_SCOPES
                )
            except Exception as e:
                print(f"Error cargando token: {e}")
                creds = None
        
        # Si no hay credenciales válidas, solicitar autorización
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # Intentar refrescar el token
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refrescando token: {e}")
                    creds = None
            
            if not creds:
                # Iniciar flujo OAuth2
                # IMPORTANTE: Solo solicita scopes de YouTube
                flow = InstalledAppFlow.from_client_config(
                    {
                        "installed": {
                            "client_id": config.CLIENT_ID,
                            "client_secret": config.CLIENT_SECRET,
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "redirect_uris": [config.REDIRECT_URI]
                        }
                    },
                    config.YOUTUBE_SCOPES  # Solo scopes de YouTube
                )
                
                print("\n" + "="*60)
                print("AUTENTICACIÓN REQUERIDA")
                print("="*60)
                print("Se abrirá tu navegador para autorizar la aplicación.")
                print("\n📝 INICIA SESIÓN CON TU CUENTA PERSONAL DE GOOGLE")
                print("\nIMPORTANTE:")
                print("- Solo se solicita acceso a YouTube (comentar)")
                print("- NO se solicita acceso a tu email/Gmail")
                print("- Puedes verificar los permisos antes de autorizar")
                print("- El token se guarda localmente en tu computadora")
                print("="*60 + "\n")
                
                creds = flow.run_local_server(port=8080)
            
            # Guardar credenciales para uso futuro
            with open(config.TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
            
            print("✓ Autenticación exitosa. Token guardado.")
        
        self.credentials = creds
        
        # Construir servicio de YouTube API
        try:
            self.service = build(
                config.API_SERVICE_NAME,
                config.API_VERSION,
                credentials=creds
            )
            print("✓ Conexión con YouTube API establecida.")
        except Exception as e:
            raise Exception(f"Error conectando con YouTube API: {e}")
    
    def comment_video(self, video_id: str, comment_text: str) -> dict:
        """
        Publica un comentario en un video de YouTube.
        
        Args:
            video_id: ID del video de YouTube
            comment_text: Texto del comentario
            
        Returns:
            dict: Información del comentario creado
        """
        if not self.service:
            raise Exception("Servicio de YouTube no inicializado. Autentica primero.")
        
        # Validar con protección si está disponible
        if self.protection:
            details = {
                'video_id': video_id,
                'text': comment_text,
                'text_length': len(comment_text)
            }
            if not self.protection.log_and_protect('comment', details):
                return {
                    'success': False,
                    'error': 'Acción bloqueada por sistema de protección'
                }
        
        try:
            # Crear comentario usando commentThreads.insert
            request = self.service.commentThreads().insert(
                part='snippet',
                body={
                    'snippet': {
                        'videoId': video_id,
                        'topLevelComment': {
                            'snippet': {
                                'textOriginal': comment_text
                            }
                        }
                    }
                }
            )
            
            response = request.execute()
            
            comment_id = response['id']
            comment_text_posted = response['snippet']['topLevelComment']['snippet']['textOriginal']
            
            print(f"✓ Comentario publicado exitosamente!")
            print(f"  Video ID: {video_id}")
            print(f"  Comentario ID: {comment_id}")
            print(f"  Texto: {comment_text_posted[:50]}...")
            
            result = {
                'success': True,
                'comment_id': comment_id,
                'video_id': video_id,
                'text': comment_text_posted,
                'response': response
            }
            
            # Registrar acción exitosa si hay protección
            if self.protection:
                self.protection.monitor.log_action('comment_success', {
                    'video_id': video_id,
                    'comment_id': comment_id,
                    'text_length': len(comment_text_posted)
                })
            
            return result
            
        except HttpError as e:
            error_details = json.loads(e.content.decode('utf-8'))
            error_message = error_details.get('error', {}).get('message', 'Error desconocido')
            
            print(f"✗ Error publicando comentario: {error_message}")
            
            return {
                'success': False,
                'error': error_message,
                'error_code': e.resp.status
            }
        except Exception as e:
            print(f"✗ Error inesperado: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_comments(self, video_id: str = None, max_results: int = 50, order: str = 'time') -> list:
        """
        Obtiene comentarios de un video.
        
        Args:
            video_id: ID del video
            max_results: Número máximo de comentarios a obtener
            order: Orden de los comentarios ('time', 'relevance')
            
        Returns:
            list: Lista de comentarios
        """
        if not self.service:
            raise Exception("Servicio de YouTube no inicializado.")
        
        if not video_id:
            raise ValueError("video_id es requerido")
        
        try:
            comments = []
            next_page_token = None
            
            # Obtener comentarios en lotes (máximo 100 por request)
            while len(comments) < max_results:
                request_max = min(100, max_results - len(comments))
                
                request = self.service.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    maxResults=request_max,
                    order=order,
                    pageToken=next_page_token
                )
                
                response = request.execute()
                
                for item in response.get('items', []):
                    comment = item['snippet']['topLevelComment']['snippet']
                    comments.append({
                        'id': item['id'],
                        'video_id': item['snippet']['videoId'],
                        'text': comment['textOriginal'],
                        'author': comment['authorDisplayName'],
                        'author_channel_id': comment.get('authorChannelId', {}).get('value'),
                        'published_at': comment['publishedAt'],
                        'updated_at': comment.get('updatedAt'),
                        'like_count': comment.get('likeCount', 0),
                        'reply_count': item['snippet'].get('totalReplyCount', 0),
                        'is_pinned': item['snippet'].get('isPublic', False)
                    })
                
                # Verificar si hay más páginas
                next_page_token = response.get('nextPageToken')
                if not next_page_token or len(comments) >= max_results:
                    break
            
            return comments[:max_results]
            
        except HttpError as e:
            error_details = json.loads(e.content.decode('utf-8'))
            error_message = error_details.get('error', {}).get('message', 'Error desconocido')
            print(f"✗ Error obteniendo comentarios: {error_message}")
            return []
        except Exception as e:
            print(f"✗ Error obteniendo comentarios: {str(e)}")
            return []
    
    def get_top_comments(self, video_id: str, max_results: int = 10) -> list:
        """
        Obtiene los comentarios más destacados (con más likes) de un video.
        
        Args:
            video_id: ID del video
            max_results: Número máximo de comentarios a obtener
            
        Returns:
            list: Lista de comentarios destacados ordenados por likes
        """
        # Obtener más comentarios y ordenarlos por likes
        all_comments = self.get_comments(video_id, max_results=200, order='relevance')
        
        # Ordenar por número de likes (descendente)
        sorted_comments = sorted(all_comments, key=lambda x: x['like_count'], reverse=True)
        
        return sorted_comments[:max_results]
    
    def get_video_stats(self, video_id: str) -> Optional[Dict]:
        """
        Obtiene estadísticas completas de un video.
        
        Args:
            video_id: ID del video de YouTube
            
        Returns:
            dict: Estadísticas del video o None si hay error
        """
        if not self.service:
            raise Exception("Servicio de YouTube no inicializado.")
        
        try:
            request = self.service.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            )
            
            response = request.execute()
            
            if not response.get('items'):
                print(f"✗ Video no encontrado: {video_id}")
                return None
            
            item = response['items'][0]
            snippet = item['snippet']
            stats = item['statistics']
            content = item['contentDetails']
            
            # Convertir duración ISO 8601 a segundos
            duration_iso = content.get('duration', 'PT0S')
            duration_seconds = self._parse_duration(duration_iso)
            
            return {
                'id': item['id'],
                'title': snippet.get('title'),
                'description': snippet.get('description', ''),
                'channel_title': snippet.get('channelTitle'),
                'channel_id': snippet.get('channelId'),
                'published_at': snippet.get('publishedAt'),
                'tags': snippet.get('tags', []),
                'category_id': snippet.get('categoryId'),
                'default_language': snippet.get('defaultLanguage'),
                'view_count': int(stats.get('viewCount', 0)),
                'like_count': int(stats.get('likeCount', 0)),
                'dislike_count': int(stats.get('dislikeCount', 0)),  # Puede no estar disponible
                'comment_count': int(stats.get('commentCount', 0)),
                'favorite_count': int(stats.get('favoriteCount', 0)),
                'duration_iso': duration_iso,
                'duration_seconds': duration_seconds,
                'duration_formatted': self._format_duration(duration_seconds),
                'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url'),
            }
            
        except HttpError as e:
            error_details = json.loads(e.content.decode('utf-8'))
            error_message = error_details.get('error', {}).get('message', 'Error desconocido')
            print(f"✗ Error obteniendo estadísticas: {error_message}")
            return None
        except Exception as e:
            print(f"✗ Error obteniendo estadísticas: {str(e)}")
            return None
    
    def _parse_duration(self, duration_iso: str) -> int:
        """
        Convierte duración ISO 8601 a segundos.
        
        Args:
            duration_iso: Duración en formato ISO 8601 (ej: PT3M30S)
            
        Returns:
            int: Duración en segundos
        """
        import re
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_iso)
        
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds
    
    def _format_duration(self, seconds: int) -> str:
        """
        Formatea duración en segundos a formato legible.
        
        Args:
            seconds: Duración en segundos
            
        Returns:
            str: Duración formateada (ej: "3:30" o "1:23:45")
        """
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"
    
    def delete_comment(self, comment_id: str) -> bool:
        """
        Elimina un comentario.
        
        Args:
            comment_id: ID del comentario a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente, False en caso contrario
        """
        if not self.service:
            raise Exception("Servicio de YouTube no inicializado.")
        
        try:
            self.service.comments().delete(id=comment_id).execute()
            print(f"✓ Comentario {comment_id} eliminado exitosamente.")
            return True
            
        except HttpError as e:
            error_details = json.loads(e.content.decode('utf-8'))
            error_message = error_details.get('error', {}).get('message', 'Error desconocido')
            print(f"✗ Error eliminando comentario: {error_message}")
            return False
        except Exception as e:
            print(f"✗ Error eliminando comentario: {str(e)}")
            return False
