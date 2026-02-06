"""
Cliente wrapper para múltiples cuentas.
Permite usar YouTubeClient con credenciales específicas sin modificar config global.
"""
import os
import json
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import config


class MultiAccountYouTubeClient:
    """
    Cliente de YouTube para una cuenta específica con credenciales propias.
    """
    
    def __init__(self, client_id: str, client_secret: str, token_file: str):
        """
        Inicializa el cliente con credenciales específicas.
        
        Args:
            client_id: Client ID de la cuenta
            client_secret: Client Secret de la cuenta
            token_file: Archivo donde guardar/cargar el token
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_file = token_file
        self.service = None
        self.credentials = None
        self._authenticate()
    
    def _authenticate(self):
        """
        Autentica con YouTube API usando OAuth2.
        """
        creds = None
        
        # Verificar si ya existe un token guardado
        if os.path.exists(self.token_file):
            try:
                creds = Credentials.from_authorized_user_file(
                    self.token_file, 
                    config.YOUTUBE_SCOPES
                )
            except Exception as e:
                print(f"⚠ Error cargando token de {self.token_file}: {e}")
                creds = None
        
        # Si no hay credenciales válidas, solicitar autorización
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # Intentar refrescar el token
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"⚠ Error refrescando token: {e}")
                    creds = None
            
            if not creds:
                # Iniciar flujo OAuth2
                flow = InstalledAppFlow.from_client_config(
                    {
                        "installed": {
                            "client_id": self.client_id,
                            "client_secret": self.client_secret,
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "redirect_uris": [config.REDIRECT_URI]
                        }
                    },
                    config.YOUTUBE_SCOPES
                )
                
                print(f"\n{'='*60}")
                print(f"AUTENTICACIÓN REQUERIDA - {self.token_file}")
                print("="*60)
                print("Se abrirá tu navegador para autorizar la aplicación.")
                print("\nIMPORTANTE:")
                print("- Solo se solicita acceso a YouTube (comentar)")
                print("- NO se solicita acceso a tu email/Gmail")
                print("="*60 + "\n")
                
                creds = flow.run_local_server(port=8080)
            
            # Guardar credenciales para uso futuro
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
            
            print(f"✓ Autenticación exitosa. Token guardado en {self.token_file}")
        
        self.credentials = creds
        self.service = build(config.API_SERVICE_NAME, config.API_VERSION, credentials=creds)
    
    def comment_video(self, video_id: str, comment_text: str) -> dict:
        """
        Comenta en un video.
        
        Args:
            video_id: ID del video
            comment_text: Texto del comentario
            
        Returns:
            dict: Resultado de la operación
        """
        if not self.service:
            self._authenticate()
        
        try:
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
            
            return {
                'success': True,
                'comment_id': response['id'],
                'message': 'Comentario publicado exitosamente'
            }
        
        except HttpError as e:
            error_details = json.loads(e.content.decode('utf-8'))
            error_message = error_details.get('error', {}).get('message', 'Error desconocido')
            return {
                'success': False,
                'error': error_message
            }
    
    def get_video_stats(self, video_id: str) -> dict:
        """
        Obtiene estadísticas de un video.
        
        Args:
            video_id: ID del video
            
        Returns:
            dict: Estadísticas del video
        """
        if not self.service:
            self._authenticate()
        
        try:
            request = self.service.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                return {}
            
            item = response['items'][0]
            snippet = item['snippet']
            statistics = item['statistics']
            content_details = item['contentDetails']
            
            return {
                'id': video_id,
                'title': snippet.get('title'),
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'comment_count': int(statistics.get('commentCount', 0)),
            }
        
        except HttpError as e:
            return {}
    
    def get_comments(self, video_id: str, max_results: int = 100) -> list:
        """
        Obtiene comentarios de un video.
        
        Args:
            video_id: ID del video
            max_results: Número máximo de comentarios
            
        Returns:
            list: Lista de comentarios
        """
        if not self.service:
            self._authenticate()
        
        try:
            request = self.service.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=min(max_results, 100)
            )
            response = request.execute()
            
            comments = []
            for item in response.get('items', []):
                top_comment = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    'id': item['id'],
                    'text': top_comment['textOriginal'],
                    'author': top_comment['authorDisplayName'],
                    'like_count': top_comment.get('likeCount', 0),
                })
            
            return comments
        
        except HttpError as e:
            return []
