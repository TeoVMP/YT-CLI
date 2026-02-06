"""
Cliente para interactuar con Spotify API.
Permite obtener información de playlists y buscar canciones.
"""
import os
import re
from typing import Optional, List, Dict
import config

# Intentar importar spotipy
try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    from spotipy.oauth2 import SpotifyOAuth
    SPOTIPY_AVAILABLE = True
except ImportError:
    SPOTIPY_AVAILABLE = False
    spotipy = None
    SpotifyClientCredentials = None
    SpotifyOAuth = None


class SpotifyClient:
    """
    Cliente para interactuar con Spotify API.
    Puede funcionar con o sin autenticación (para playlists públicas).
    """
    
    def __init__(self, use_auth: bool = False):
        """
        Inicializa el cliente de Spotify.
        
        Args:
            use_auth: Si True, usa autenticación OAuth (requiere credenciales)
        """
        if not SPOTIPY_AVAILABLE:
            raise ImportError(
                "spotipy no está instalado. Instálalo con: pip install spotipy"
            )
        
        self.use_auth = use_auth
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Inicializa el cliente de Spotify."""
        if self.use_auth:
            # Usar autenticación OAuth (para playlists privadas)
            client_id = os.getenv('SPOTIFY_CLIENT_ID')
            client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
            redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:8080')
            
            if not client_id or not client_secret:
                raise ValueError(
                    "\n" + "="*70 + "\n"
                    "⚠️  CREDENCIALES DE SPOTIFY NO CONFIGURADAS\n"
                    "="*70 + "\n\n"
                    "Para usar playlists de Spotify, necesitas configurar credenciales.\n\n"
                    "📋 Pasos para obtener credenciales:\n\n"
                    "1. Ve a: https://developer.spotify.com/dashboard\n"
                    "2. Inicia sesión con tu cuenta de Spotify\n"
                    "3. Haz clic en 'Create app'\n"
                    "4. Completa el formulario:\n"
                    "   - App name: (cualquier nombre, ej: 'YTLikesBot')\n"
                    "   - App description: (opcional)\n"
                    "   - Redirect URI: http://localhost:8080\n"
                    "   - Marca 'I understand and agree...'\n"
                    "5. Haz clic en 'Save'\n"
                    "6. En la página de tu app, verás:\n"
                    "   - Client ID (cópialo)\n"
                    "   - Client Secret (haz clic en 'View client secret' y cópialo)\n\n"
                    "📝 Agrega estas credenciales a tu archivo .env:\n\n"
                    "SPOTIFY_CLIENT_ID=tu_client_id_aqui\n"
                    "SPOTIFY_CLIENT_SECRET=tu_client_secret_aqui\n"
                    "SPOTIFY_REDIRECT_URI=http://localhost:8080\n\n"
                    "💡 Nota: Para playlists públicas, solo necesitas Client ID y Secret.\n"
                    "   Para playlists privadas, también necesitarás autenticación OAuth.\n"
                    "="*70 + "\n"
                )
            
            scope = "playlist-read-private playlist-read-collaborative"
            auth_manager = SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope=scope
            )
            self.client = spotipy.Spotify(auth_manager=auth_manager)
        else:
            # Usar Client Credentials (solo para playlists públicas)
            client_id = os.getenv('SPOTIFY_CLIENT_ID')
            client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
            
            if client_id and client_secret:
                auth_manager = SpotifyClientCredentials(
                    client_id=client_id,
                    client_secret=client_secret
                )
                self.client = spotipy.Spotify(auth_manager=auth_manager)
            else:
                # Sin credenciales, mostrar error claro
                raise ValueError(
                    "\n" + "="*70 + "\n"
                    "⚠️  CREDENCIALES DE SPOTIFY NO CONFIGURADAS\n"
                    "="*70 + "\n\n"
                    "Para usar playlists de Spotify, necesitas configurar credenciales.\n\n"
                    "📋 Pasos rápidos:\n\n"
                    "1. Ve a: https://developer.spotify.com/dashboard\n"
                    "2. Inicia sesión y crea una nueva app\n"
                    "3. Copia el Client ID y Client Secret\n"
                    "4. Agrégalos a tu archivo .env:\n\n"
                    "   SPOTIFY_CLIENT_ID=tu_client_id\n"
                    "   SPOTIFY_CLIENT_SECRET=tu_client_secret\n\n"
                    "📖 Guía completa: Lee el README.md o ejecuta:\n"
                    "   python main.py --help\n"
                    "="*70 + "\n"
                )
    
    def extract_playlist_id(self, playlist_url: str) -> Optional[str]:
        """
        Extrae el ID de playlist de una URL de Spotify.
        
        Args:
            playlist_url: URL de la playlist de Spotify
            
        Returns:
            str: ID de la playlist o None si no se puede extraer
        """
        # Patrones comunes de URLs de Spotify
        patterns = [
            r'spotify\.com/playlist/([a-zA-Z0-9]+)',
            r'playlist/([a-zA-Z0-9]+)',
            r'^([a-zA-Z0-9]{22})$'  # ID directo (22 caracteres)
        ]
        
        for pattern in patterns:
            match = re.search(pattern, playlist_url)
            if match:
                return match.group(1)
        
        return None
    
    def get_playlist_tracks(self, playlist_id: str) -> List[Dict]:
        """
        Obtiene las canciones de una playlist de Spotify.
        
        Args:
            playlist_id: ID de la playlist de Spotify
            
        Returns:
            list: Lista de canciones con información (artista, título, etc.)
        """
        if not self.client:
            raise ValueError(
                "Cliente de Spotify no inicializado. Configura SPOTIFY_CLIENT_ID y "
                "SPOTIFY_CLIENT_SECRET en tu archivo .env"
            )
        
        try:
            tracks = []
            results = self.client.playlist_tracks(playlist_id)
            
            while results:
                for item in results['items']:
                    track = item.get('track')
                    if track and track.get('id'):
                        # Extraer información de la canción
                        artists = [artist['name'] for artist in track.get('artists', [])]
                        artist_name = ', '.join(artists) if artists else 'Unknown Artist'
                        track_name = track.get('name', 'Unknown Track')
                        
                        tracks.append({
                            'name': track_name,
                            'artist': artist_name,
                            'artists': artists,
                            'album': track.get('album', {}).get('name', 'Unknown Album'),
                            'duration_ms': track.get('duration_ms', 0),
                            'spotify_id': track.get('id'),
                            'search_query': f"{artist_name} {track_name}"  # Query para buscar en YouTube
                        })
                
                # Obtener siguiente página si existe
                if results['next']:
                    results = self.client.next(results)
                else:
                    break
            
            return tracks
            
        except Exception as e:
            error_msg = str(e)
            if '404' in error_msg or 'not found' in error_msg.lower():
                raise ValueError(f"Playlist no encontrada: {playlist_id}")
            elif '401' in error_msg or 'unauthorized' in error_msg.lower():
                raise ValueError(
                    "No autorizado. La playlist puede ser privada. "
                    "Configura autenticación OAuth con use_auth=True"
                )
            else:
                raise Exception(f"Error obteniendo tracks de Spotify: {error_msg}")
    
    def get_playlist_info(self, playlist_id: str) -> Optional[Dict]:
        """
        Obtiene información básica de una playlist.
        
        Args:
            playlist_id: ID de la playlist de Spotify
            
        Returns:
            dict: Información de la playlist o None si hay error
        """
        if not self.client:
            raise ValueError(
                "Cliente de Spotify no inicializado. Configura SPOTIFY_CLIENT_ID y "
                "SPOTIFY_CLIENT_SECRET en tu archivo .env"
            )
        
        try:
            playlist = self.client.playlist(playlist_id)
            
            return {
                'id': playlist.get('id'),
                'name': playlist.get('name'),
                'description': playlist.get('description', ''),
                'owner': playlist.get('owner', {}).get('display_name', 'Unknown'),
                'tracks_count': playlist.get('tracks', {}).get('total', 0),
                'public': playlist.get('public', False),
                'image': playlist.get('images', [{}])[0].get('url') if playlist.get('images') else None
            }
            
        except Exception as e:
            print(f"⚠ Error obteniendo información de la playlist: {str(e)}")
            return None
