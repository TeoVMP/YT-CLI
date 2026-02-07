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
    
    def __init__(self, auto_authenticate=True):
        self.service = None
        self.credentials = None
        # Inicializar protección si está disponible
        if PROTECTION_ENABLED and AccountProtection:
            self.protection = AccountProtection()
        else:
            self.protection = None
        if auto_authenticate:
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
                print("🔐 AUTENTICACIÓN REQUERIDA")
                print("="*60)
                print("\n💡 Esta función requiere autenticación con tu cuenta de Google.")
                print("   Solo se solicita acceso a YouTube (comentar/gestionar comentarios).")
                print("   NO se solicita acceso a tu email/Gmail.\n")
                
                # Detectar si estamos en Termux (Android)
                is_termux = os.environ.get('TERMUX_VERSION') is not None
                
                if is_termux:
                    print("📱 Detectado Termux (Android)")
                    print("   Se usará autenticación manual (sin navegador automático).\n")
                    print("📝 Pasos:")
                    print("   1. Se mostrará una URL - cópiala")
                    print("   2. Ábrela en tu navegador móvil")
                    print("   3. Inicia sesión y autoriza")
                    print("   4. Después de autorizar, verás un error de conexión (ES NORMAL)")
                    print("   5. Copia TODA la URL completa de la barra de direcciones")
                    print("   6. Pégalo aquí (el código está en la URL)\n")
                    print("="*60 + "\n")
                    
                    # En Termux, usar redirect_uri que esté configurado en Google Cloud Console
                    # Primero intentar con el redirect_uri configurado
                    redirect_uri_to_use = config.REDIRECT_URI
                    
                    # Crear flow con redirect_uri explícito
                    flow_mobile = InstalledAppFlow.from_client_config(
                        {
                            "installed": {
                                "client_id": config.CLIENT_ID,
                                "client_secret": config.CLIENT_SECRET,
                                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                                "token_uri": "https://oauth2.googleapis.com/token",
                                "redirect_uris": [redirect_uri_to_use]
                            }
                        },
                        config.YOUTUBE_SCOPES
                    )
                    
                    # Generar URL de autorización con redirect_uri explícito
                    auth_url, state = flow_mobile.authorization_url(
                        prompt='consent',
                        access_type='offline',
                        include_granted_scopes='true'
                    )
                    
                    # Asegurar que redirect_uri esté en la URL (agregarlo si falta)
                    from urllib.parse import urlencode, parse_qs, urlparse, urlunparse
                    parsed = urlparse(auth_url)
                    params = parse_qs(parsed.query)
                    
                    # Si redirect_uri no está en los parámetros, agregarlo
                    if 'redirect_uri' not in params:
                        params['redirect_uri'] = [redirect_uri_to_use]
                        new_query = urlencode(params, doseq=True)
                        auth_url = urlunparse(parsed._replace(query=new_query))
                    
                    print(f"\n📋 Por favor, visita esta URL en tu navegador:")
                    print(f"\n{auth_url}\n")
                    print("⚠️  IMPORTANTE:")
                    print("   - Después de autorizar, verás un error 'This site can't be reached'")
                    print("   - Esto es NORMAL en móviles/Termux")
                    print("   - Copia TODA la URL de la barra de direcciones")
                    print("   - La URL contiene el código de autorización")
                    print("\n💡 Ejemplo de URL a copiar:")
                    print("   http://localhost:8080/?code=4/0AeanS...&scope=...")
                    print("   O")
                    print("   urn:ietf:wg:oauth:2.0:oob?code=4/0AeanS...")
                    
                    # Pedir la URL completa o solo el código
                    user_input = input("\n📋 Pega la URL completa o solo el código: ").strip()
                    
                    # Extraer el código de la URL si el usuario pegó la URL completa
                    code = None
                    if 'code=' in user_input:
                        from urllib.parse import urlparse, parse_qs
                        # Si es una URL completa, extraer el código
                        if user_input.startswith('http://') or user_input.startswith('https://') or user_input.startswith('urn:'):
                            parsed = urlparse(user_input)
                            params = parse_qs(parsed.query)
                            if 'code' in params:
                                code = params['code'][0]
                            else:
                                # Intentar extraer de fragmento
                                if '#' in user_input:
                                    fragment = user_input.split('#')[1]
                                    fragment_params = parse_qs(fragment)
                                    if 'code' in fragment_params:
                                        code = fragment_params['code'][0]
                    
                    # Si no se extrajo código de la URL, usar el input directamente
                    if not code:
                        code = user_input
                    
                    # Limpiar el código (remover espacios, saltos de línea, etc.)
                    code = code.strip().replace('\n', '').replace('\r', '').replace(' ', '')
                    
                    # Validar que el código tenga la longitud mínima esperada
                    if len(code) < 30:
                        raise Exception(
                            f"El código parece estar incompleto (solo {len(code)} caracteres).\n"
                            f"   Por favor, copia la URL COMPLETA después de autorizar.\n"
                            f"   Ejemplo: http://localhost:8080/?code=4/0ASc3gC...&scope=...\n"
                            f"   El código debe tener al menos 30 caracteres."
                        )
                    
                    print(f"\n🔑 Código extraído: {code[:20]}...")
                    print(f"🔗 Usando redirect_uri: {redirect_uri_to_use}")
                    
                    # Intercambiar código por token
                    # IMPORTANTE: El redirect_uri debe ser EXACTAMENTE el mismo que se usó en la URL de autorización
                    try:
                        # Intentar primero con el método estándar
                        creds = flow_mobile.fetch_token(code=code)
                    except Exception as e:
                        # Si falla, usar método directo con requests
                        error_msg = str(e)
                        print("⚠️  Usando método alternativo para obtener token...")
                        import requests
                        
                        # Verificar que el código esté completo (debe tener al menos 50 caracteres)
                        if len(code) < 50:
                            raise Exception(
                                f"El código parece estar incompleto (solo {len(code)} caracteres).\n"
                                f"   Por favor, copia la URL COMPLETA después de autorizar, no solo el código.\n"
                                f"   El código debe tener al menos 50 caracteres."
                            )
                        
                        token_url = 'https://oauth2.googleapis.com/token'
                        token_data = {
                            'code': code,
                            'client_id': config.CLIENT_ID,
                            'client_secret': config.CLIENT_SECRET,
                            'redirect_uri': redirect_uri_to_use,  # DEBE ser exactamente el mismo
                            'grant_type': 'authorization_code'
                        }
                        
                        print(f"📤 Enviando solicitud de token...")
                        print(f"   Client ID: {config.CLIENT_ID[:20]}...")
                        print(f"   Redirect URI: {redirect_uri_to_use}")
                        print(f"   Código: {code[:30]}... (longitud: {len(code)} caracteres)")
                        
                        response = requests.post(token_url, data=token_data)
                        
                        if response.status_code == 200:
                            token_info = response.json()
                            # Crear credenciales desde el token
                            from google.oauth2.credentials import Credentials
                            creds = Credentials(
                                token=token_info.get('access_token'),
                                refresh_token=token_info.get('refresh_token'),
                                token_uri='https://oauth2.googleapis.com/token',
                                client_id=config.CLIENT_ID,
                                client_secret=config.CLIENT_SECRET,
                                scopes=config.YOUTUBE_SCOPES
                            )
                            print("✓ Token obtenido exitosamente")
                        else:
                            error_response = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                            error_detail = error_response.get('error_description', '') if isinstance(error_response, dict) else str(error_response)
                            
                            if 'invalid_grant' in str(error_response).lower():
                                raise Exception(
                                    f"Error: Código de autorización inválido o expirado.\n"
                                    f"   - El código puede haber sido usado ya\n"
                                    f"   - O puede haber expirado (los códigos expiran en ~10 minutos)\n"
                                    f"   - O el redirect_uri no coincide exactamente\n\n"
                                    f"   Solución: Vuelve a ejecutar 'python main.py --login' y copia el código inmediatamente después de autorizar."
                                )
                            else:
                                raise Exception(f"Error obteniendo token: {response.status_code} - {error_detail}")
                else:
                    print("🌐 Se abrirá tu navegador automáticamente...")
                    print("   Si no se abre, copia la URL que aparecerá.\n")
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
    
    def logout(self) -> bool:
        """
        Cierra sesión revocando el token y eliminando el archivo de token.
        
        Returns:
            bool: True si se cerró sesión exitosamente, False en caso contrario
        """
        try:
            # Intentar revocar el token si existe
            if self.credentials and self.credentials.token:
                try:
                    from google.auth.transport.requests import Request
                    revoke_url = 'https://oauth2.googleapis.com/revoke'
                    # Usar httplib2 que ya está disponible en las dependencias
                    import httplib2
                    http = httplib2.Http()
                    response, content = http.request(
                        revoke_url + '?token=' + self.credentials.token,
                        'POST',
                        headers={'content-type': 'application/x-www-form-urlencoded'}
                    )
                    if response.status == 200:
                        print("✓ Token revoked on server.")
                except Exception as e:
                    print(f"⚠ Could not revoke token on server: {e}")
                    print("   Token will be deleted locally anyway.")
            
            # Eliminar archivo de token local
            if os.path.exists(config.TOKEN_FILE):
                os.remove(config.TOKEN_FILE)
                print(f"✓ Token eliminado: {config.TOKEN_FILE}")
            
            # Limpiar credenciales en memoria
            self.credentials = None
            self.service = None
            
            print("✓ Sesión cerrada exitosamente.")
            return True
            
        except Exception as e:
            print(f"✗ Error cerrando sesión: {str(e)}")
            return False
    
    def is_authenticated(self) -> bool:
        """
        Verifica si hay una sesión activa autenticada.
        
        Returns:
            bool: True si hay una sesión activa, False en caso contrario
        """
        if not self.credentials:
            return False
        
        # Verificar si el token es válido
        if self.credentials.valid:
            return True
        
        # Verificar si se puede refrescar
        if self.credentials.expired and self.credentials.refresh_token:
            try:
                from google.auth.transport.requests import Request
                self.credentials.refresh(Request())
                return True
            except:
                return False
        
        return False
    
    def get_auth_info(self) -> dict:
        """
        Obtiene información sobre la autenticación actual.
        
        Returns:
            dict: Información de autenticación
        """
        info = {
            'authenticated': False,
            'token_file': config.TOKEN_FILE,
            'token_exists': os.path.exists(config.TOKEN_FILE),
            'has_credentials': self.credentials is not None,
            'token_valid': False,
            'token_expired': False,
            'has_refresh_token': False
        }
        
        if self.credentials:
            info['authenticated'] = True
            info['token_valid'] = self.credentials.valid
            info['token_expired'] = self.credentials.expired
            info['has_refresh_token'] = self.credentials.refresh_token is not None
            
            if self.credentials.expired and self.credentials.refresh_token:
                info['can_refresh'] = True
            else:
                info['can_refresh'] = False
        
        return info
    
    def search_videos(self, query: str, max_results: int = 10, order: str = 'relevance', use_api_key: bool = False) -> list:
        """
        Busca videos de YouTube por palabras clave.
        Puede usar API key (sin autenticación) o OAuth2.
        
        Args:
            query: Palabras clave para buscar
            max_results: Número máximo de resultados (default: 10, max: 50)
            order: Orden de resultados ('relevance', 'date', 'rating', 'title', 'viewCount')
            use_api_key: Si True, usa API key en lugar de OAuth2 (no requiere login)
            
        Returns:
            list: Lista de videos encontrados
        """
        try:
            # Limitar max_results a 50 (límite de la API)
            max_results = min(max_results, 50)
            
            # Para búsqueda, priorizar API key (sin autenticación)
            # Si no hay API key, intentar usar OAuth2 solo si ya hay token guardado (sin forzar login)
            if config.API_KEY:
                service = build(
                    config.API_SERVICE_NAME,
                    config.API_VERSION,
                    developerKey=config.API_KEY
                )
            else:
                # Sin API key, intentar usar OAuth2 solo si ya hay token (sin forzar login)
                if os.path.exists(config.TOKEN_FILE):
                    try:
                        from google.oauth2.credentials import Credentials
                        creds = Credentials.from_authorized_user_file(
                            config.TOKEN_FILE,
                            config.YOUTUBE_SCOPES
                        )
                        # Si el token está expirado, intentar refrescarlo
                        if creds.expired and creds.refresh_token:
                            creds.refresh(Request())
                        # Si las credenciales son válidas, usarlas
                        if creds.valid:
                            if not self.service:
                                self.credentials = creds
                                self.service = build(
                                    config.API_SERVICE_NAME,
                                    config.API_VERSION,
                                    credentials=creds
                                )
                            service = self.service
                        else:
                            raise Exception("Token inválido. Ejecuta: python main.py --login")
                    except Exception as e:
                        raise Exception(
                            f"Error usando token guardado: {str(e)}\n"
                            "Ejecuta: python main.py --login\n"
                            "O configura YOUTUBE_API_KEY en .env para búsqueda sin login"
                        )
                else:
                    # Sin API key ni token, no se puede buscar
                    raise Exception(
                        "API key no configurada y no hay sesión activa.\n\n"
                        "Opciones:\n"
                        "1. Configura YOUTUBE_API_KEY en .env (recomendado, no requiere login)\n"
                        "   Obtén una en: https://console.cloud.google.com/apis/credentials\n\n"
                        "2. O inicia sesión primero:\n"
                        "   python main.py --login\n"
                        "   Luego podrás buscar sin API key"
                    )
            
            # Construir request según el método de autenticación
            if use_api_key and config.API_KEY:
                request = service.search().list(
                    part='snippet',
                    q=query,
                    type='video',
                    maxResults=max_results,
                    order=order
                )
            else:
                request = service.search().list(
                    part='snippet',
                    q=query,
                    type='video',
                    maxResults=max_results,
                    order=order
                )
            
            response = request.execute()
            
            videos = []
            for item in response.get('items', []):
                video_id = item['id']['videoId']
                snippet = item['snippet']
                
                videos.append({
                    'video_id': video_id,
                    'title': snippet.get('title'),
                    'description': snippet.get('description', '')[:200],  # Primeros 200 caracteres
                    'channel_title': snippet.get('channelTitle'),
                    'channel_id': snippet.get('channelId'),
                    'published_at': snippet.get('publishedAt'),
                    'thumbnail': snippet.get('thumbnails', {}).get('default', {}).get('url'),
                    'url': f"https://www.youtube.com/watch?v={video_id}"
                })
            
            return videos
            
        except HttpError as e:
            error_details = json.loads(e.content.decode('utf-8'))
            error_message = error_details.get('error', {}).get('message', 'Error desconocido')
            print(f"✗ Error buscando videos: {error_message}")
            return []
        except Exception as e:
            print(f"✗ Error buscando videos: {str(e)}")
            return []
    
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
    
    def get_my_comments(self, video_id: str = None, max_results: int = 50) -> list:
        """
        Obtiene tus propios comentarios en un video o en todos los videos.
        
        Args:
            video_id: ID del video (opcional, si no se proporciona busca en todos)
            max_results: Número máximo de comentarios a obtener
            
        Returns:
            list: Lista de tus comentarios
        """
        if not self.service:
            raise Exception("Servicio de YouTube no inicializado.")
        
        try:
            # Obtener información del canal del usuario autenticado
            channels_response = self.service.channels().list(
                part='contentDetails',
                mine=True
            ).execute()
            
            if not channels_response.get('items'):
                print("✗ No se pudo obtener información de tu canal.")
                return []
            
            channel_id = channels_response['items'][0]['id']
            
            comments = []
            next_page_token = None
            
            # Obtener comentarios del canal
            while len(comments) < max_results:
                request_max = min(100, max_results - len(comments))
                
                request_params = {
                    'part': 'snippet',
                    'allThreadsRelatedToChannelId': channel_id,
                    'maxResults': request_max,
                    'pageToken': next_page_token
                }
                
                # Si se especifica video_id, filtrar por video
                if video_id:
                    request_params['videoId'] = video_id
                
                request = self.service.commentThreads().list(**request_params)
                response = request.execute()
                
                for item in response.get('items', []):
                    comment = item['snippet']['topLevelComment']['snippet']
                    item_video_id = item['snippet'].get('videoId')
                    
                    # Si se especificó video_id, solo incluir comentarios de ese video
                    if video_id and item_video_id != video_id:
                        continue
                    
                    comments.append({
                        'id': item['id'],
                        'video_id': item_video_id,
                        'text': comment['textOriginal'],
                        'author': comment['authorDisplayName'],
                        'published_at': comment['publishedAt'],
                        'updated_at': comment.get('updatedAt'),
                        'like_count': comment.get('likeCount', 0),
                        'reply_count': item['snippet'].get('totalReplyCount', 0),
                        'is_mine': True
                    })
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token or len(comments) >= max_results:
                    break
            
            return comments[:max_results]
            
        except HttpError as e:
            error_details = json.loads(e.content.decode('utf-8'))
            error_message = error_details.get('error', {}).get('message', 'Error desconocido')
            print(f"✗ Error obteniendo tus comentarios: {error_message}")
            return []
        except Exception as e:
            print(f"✗ Error obteniendo tus comentarios: {str(e)}")
            return []
    
    def reply_to_comment(self, comment_id: str, reply_text: str) -> dict:
        """
        Responde a un comentario.
        
        Args:
            comment_id: ID del comentario al que responder (thread ID)
            reply_text: Texto de la respuesta
            
        Returns:
            dict: Resultado de la operación
        """
        if not self.service:
            raise Exception("Servicio de YouTube no inicializado.")
        
        try:
            request = self.service.comments().insert(
                part='snippet',
                body={
                    'snippet': {
                        'parentId': comment_id,
                        'textOriginal': reply_text
                    }
                }
            )
            
            response = request.execute()
            
            reply_id = response['id']
            reply_text_posted = response['snippet']['textOriginal']
            
            print(f"✓ Respuesta publicada exitosamente!")
            print(f"  Comentario padre: {comment_id}")
            print(f"  Respuesta ID: {reply_id}")
            print(f"  Texto: {reply_text_posted[:50]}...")
            
            return {
                'success': True,
                'reply_id': reply_id,
                'parent_id': comment_id,
                'text': reply_text_posted
            }
            
        except HttpError as e:
            error_details = json.loads(e.content.decode('utf-8'))
            error_message = error_details.get('error', {}).get('message', 'Error desconocido')
            print(f"✗ Error publicando respuesta: {error_message}")
            return {
                'success': False,
                'error': error_message
            }
        except Exception as e:
            print(f"✗ Error publicando respuesta: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_comment(self, comment_id: str, new_text: str) -> dict:
        """
        Actualiza/edita un comentario existente.
        
        Args:
            comment_id: ID del comentario a actualizar
            new_text: Nuevo texto del comentario
            
        Returns:
            dict: Resultado de la operación
        """
        if not self.service:
            raise Exception("Servicio de YouTube no inicializado.")
        
        try:
            # Primero obtener el comentario actual para mantener otros datos
            comment_response = self.service.comments().list(
                part='snippet',
                id=comment_id
            ).execute()
            
            if not comment_response.get('items'):
                return {
                    'success': False,
                    'error': 'Comentario no encontrado'
                }
            
            comment = comment_response['items'][0]
            
            # Actualizar el comentario
            request = self.service.comments().update(
                part='snippet',
                body={
                    'id': comment_id,
                    'snippet': {
                        'textOriginal': new_text
                    }
                }
            )
            
            response = request.execute()
            
            updated_text = response['snippet']['textOriginal']
            
            print(f"✓ Comentario actualizado exitosamente!")
            print(f"  Comentario ID: {comment_id}")
            print(f"  Nuevo texto: {updated_text[:50]}...")
            
            return {
                'success': True,
                'comment_id': comment_id,
                'text': updated_text
            }
            
        except HttpError as e:
            error_details = json.loads(e.content.decode('utf-8'))
            error_message = error_details.get('error', {}).get('message', 'Error desconocido')
            print(f"✗ Error actualizando comentario: {error_message}")
            return {
                'success': False,
                'error': error_message
            }
        except Exception as e:
            print(f"✗ Error actualizando comentario: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_comment_replies(self, comment_id: str, max_results: int = 20) -> list:
        """
        Obtiene las respuestas (replies) de un comentario.
        
        Args:
            comment_id: ID del comentario (thread ID)
            max_results: Número máximo de respuestas a obtener
            
        Returns:
            list: Lista de respuestas
        """
        if not self.service:
            raise Exception("Servicio de YouTube no inicializado.")
        
        try:
            replies = []
            next_page_token = None
            
            while len(replies) < max_results:
                request_max = min(100, max_results - len(replies))
                
                request = self.service.comments().list(
                    part='snippet',
                    parentId=comment_id,
                    maxResults=request_max,
                    pageToken=next_page_token
                )
                
                response = request.execute()
                
                for item in response.get('items', []):
                    reply = item['snippet']
                    replies.append({
                        'id': item['id'],
                        'parent_id': comment_id,
                        'text': reply['textOriginal'],
                        'author': reply['authorDisplayName'],
                        'published_at': reply['publishedAt'],
                        'updated_at': reply.get('updatedAt'),
                        'like_count': reply.get('likeCount', 0)
                    })
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token or len(replies) >= max_results:
                    break
            
            return replies[:max_results]
            
        except HttpError as e:
            error_details = json.loads(e.content.decode('utf-8'))
            error_message = error_details.get('error', {}).get('message', 'Error desconocido')
            print(f"✗ Error obteniendo respuestas: {error_message}")
            return []
        except Exception as e:
            print(f"✗ Error obteniendo respuestas: {str(e)}")
            return []
    
    def get_comment_info(self, comment_id: str) -> Optional[Dict]:
        """
        Obtiene información detallada de un comentario específico.
        
        Args:
            comment_id: ID del comentario
            
        Returns:
            dict: Información del comentario o None
        """
        if not self.service:
            raise Exception("Servicio de YouTube no inicializado.")
        
        try:
            request = self.service.comments().list(
                part='snippet',
                id=comment_id
            )
            
            response = request.execute()
            
            if not response.get('items'):
                print(f"✗ Comentario no encontrado: {comment_id}")
                return None
            
            item = response['items'][0]
            snippet = item['snippet']
            
            return {
                'id': item['id'],
                'text': snippet['textOriginal'],
                'author': snippet['authorDisplayName'],
                'author_channel_id': snippet.get('authorChannelId', {}).get('value'),
                'published_at': snippet['publishedAt'],
                'updated_at': snippet.get('updatedAt'),
                'like_count': snippet.get('likeCount', 0),
                'moderation_status': snippet.get('moderationStatus'),
                'viewer_rating': snippet.get('viewerRating')
            }
            
        except HttpError as e:
            error_details = json.loads(e.content.decode('utf-8'))
            error_message = error_details.get('error', {}).get('message', 'Error desconocido')
            print(f"✗ Error obteniendo información del comentario: {error_message}")
            return None
        except Exception as e:
            print(f"✗ Error obteniendo información del comentario: {str(e)}")
            return None
    
    def get_my_playlists(self, max_results: int = 50) -> list:
        """
        Obtiene las playlists personales del usuario autenticado.
        
        Args:
            max_results: Número máximo de playlists a obtener
            
        Returns:
            list: Lista de playlists personales
        """
        if not self.service:
            raise Exception("Servicio de YouTube no inicializado.")
        
        try:
            playlists = []
            next_page_token = None
            
            while len(playlists) < max_results:
                request_max = min(50, max_results - len(playlists))
                
                request = self.service.playlists().list(
                    part='snippet,contentDetails',
                    mine=True,
                    maxResults=request_max,
                    pageToken=next_page_token
                )
                
                response = request.execute()
                
                for item in response.get('items', []):
                    snippet = item['snippet']
                    content_details = item.get('contentDetails', {})
                    
                    playlists.append({
                        'id': item['id'],
                        'title': snippet.get('title'),
                        'description': snippet.get('description', ''),
                        'published_at': snippet.get('publishedAt'),
                        'thumbnail': snippet.get('thumbnails', {}).get('default', {}).get('url'),
                        'item_count': content_details.get('itemCount', 0),
                        'channel_id': snippet.get('channelId'),
                        'channel_title': snippet.get('channelTitle'),
                        'privacy_status': snippet.get('privacyStatus', 'private')
                    })
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token or len(playlists) >= max_results:
                    break
            
            return playlists[:max_results]
            
        except HttpError as e:
            error_details = json.loads(e.content.decode('utf-8'))
            error_message = error_details.get('error', {}).get('message', 'Error desconocido')
            print(f"✗ Error obteniendo playlists: {error_message}")
            return []
        except Exception as e:
            print(f"✗ Error obteniendo playlists: {str(e)}")
            return []
    
    def search_song_on_youtube(self, artist: str, song_title: str, max_results: int = 1) -> Optional[Dict]:
        """
        Busca una canción específica en YouTube.
        
        Args:
            artist: Nombre del artista
            song_title: Título de la canción
            max_results: Número máximo de resultados (default: 1 para obtener el mejor match)
            
        Returns:
            dict: Información del video encontrado o None si no se encuentra
        """
        # Construir query de búsqueda
        query = f"{artist} {song_title}"
        
        # Buscar videos
        videos = self.search_videos(query, max_results=max_results, order='relevance', use_api_key=bool(config.API_KEY))
        
        if videos:
            # Retornar el primer resultado (más relevante)
            return videos[0]
        
        return None
    
    def get_playlist_videos(self, playlist_id: str, max_results: int = 50) -> list:
        """
        Obtiene los videos de una playlist.
        
        Args:
            playlist_id: ID de la playlist
            max_results: Número máximo de videos a obtener
            
        Returns:
            list: Lista de videos en la playlist
        """
        if not self.service:
            raise Exception("Servicio de YouTube no inicializado.")
        
        try:
            videos = []
            next_page_token = None
            
            while len(videos) < max_results:
                request_max = min(50, max_results - len(videos))
                
                request = self.service.playlistItems().list(
                    part='snippet,contentDetails',
                    playlistId=playlist_id,
                    maxResults=request_max,
                    pageToken=next_page_token
                )
                
                response = request.execute()
                
                for item in response.get('items', []):
                    snippet = item['snippet']
                    content_details = item.get('contentDetails', {})
                    video_id = content_details.get('videoId')
                    
                    if not video_id:
                        continue
                    
                    videos.append({
                        'playlist_item_id': item['id'],
                        'video_id': video_id,
                        'title': snippet.get('title'),
                        'description': snippet.get('description', ''),
                        'channel_title': snippet.get('videoOwnerChannelTitle'),
                        'channel_id': snippet.get('videoOwnerChannelId'),
                        'published_at': snippet.get('publishedAt'),
                        'position': snippet.get('position'),
                        'thumbnail': snippet.get('thumbnails', {}).get('default', {}).get('url'),
                        'url': f"https://www.youtube.com/watch?v={video_id}"
                    })
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token or len(videos) >= max_results:
                    break
            
            return videos[:max_results]
            
        except HttpError as e:
            error_details = json.loads(e.content.decode('utf-8'))
            error_message = error_details.get('error', {}).get('message', 'Error desconocido')
            print(f"✗ Error obteniendo videos de la playlist: {error_message}")
            return []
        except Exception as e:
            print(f"✗ Error obteniendo videos de la playlist: {str(e)}")
            return []