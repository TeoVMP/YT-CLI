"""
Reproductor de videos usando VLC.
Permite reproducir videos de YouTube directamente o desde archivos locales.
Soporta control remoto vía HTTP para avanzar a la siguiente canción.
"""
import os
import subprocess
import platform
import time
import threading
import json
from typing import Optional, List
import yt_dlp
import config

# Intentar importar requests para control HTTP de VLC
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class VLCPlayer:
    """
    Reproductor de videos usando VLC Media Player.
    """
    
    def __init__(self):
        """
        Inicializa el reproductor VLC.
        """
        self.vlc_path = self._find_vlc()
        self.vlc_process = None
        self.vlc_http_port = 8080
        self.vlc_http_password = 'vlc'  # Contraseña por defecto para HTTP
        self.current_playlist = []
        self.current_index = 0
        self.playlist_thread = None
        self.is_playing = False
        self.playlist_state_file = os.path.join(os.path.dirname(__file__), '.playlist_state.json')
        self.audio_only = False  # Modo solo audio para playlists
    
    def _find_vlc(self) -> Optional[str]:
        """
        Encuentra la ruta de VLC en el sistema.
        
        Returns:
            str: Ruta de VLC o None si no se encuentra
        """
        system = platform.system()
        
        # Rutas comunes de VLC en diferentes sistemas
        common_paths = {
            'Windows': [
                r'C:\Program Files\VideoLAN\VLC\vlc.exe',
                r'C:\Program Files (x86)\VideoLAN\VLC\vlc.exe',
                os.path.expanduser(r'~\AppData\Local\Programs\VideoLAN\VLC\vlc.exe'),
            ],
            'Darwin': [  # macOS
                '/Applications/VLC.app/Contents/MacOS/VLC',
                '/usr/local/bin/vlc',
            ],
            'Linux': [
                '/usr/bin/vlc',
                '/usr/local/bin/vlc',
                '/data/data/org.videolan.vlc/files/bin/vlc',  # Android VLC
            ],
            'Android': [  # Termux/Android
                '/data/data/org.videolan.vlc/files/bin/vlc',
                '/data/data/org.videolan.vlc/exec/vlc',
                'vlc',  # Si está en PATH
            ]
        }
        
        # Detectar Android/Termux
        if os.environ.get('TERMUX_VERSION') or os.path.exists('/data/data/com.termux'):
            system = 'Android'
        
        # Buscar en PATH primero
        try:
            result = subprocess.run(['vlc', '--version'], 
                                  capture_output=True, 
                                  timeout=2)
            if result.returncode == 0:
                return 'vlc'
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Buscar en rutas comunes
        paths = common_paths.get(system, [])
        for path in paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def is_available(self) -> bool:
        """
        Verifica si VLC está disponible en el sistema.
        
        Returns:
            bool: True si VLC está disponible
        """
        if self.vlc_path is None:
            # En Android, verificar si VLC está instalado como app
            if os.environ.get('TERMUX_VERSION') or os.path.exists('/data/data/com.termux'):
                # Intentar usar am (Activity Manager) para abrir VLC
                try:
                    result = subprocess.run(['am', 'start', '-n', 'org.videolan.vlc/.gui.MainActivity'],
                                          capture_output=True, timeout=2)
                    if result.returncode == 0:
                        return True
                except:
                    pass
            return False
        return True
    
    def _get_youtube_stream_url(self, youtube_url: str, audio_only: bool = False) -> Optional[str]:
        """
        Obtiene la URL del stream real de YouTube usando yt-dlp.
        Intenta múltiples formatos si el primero falla.
        
        Args:
            youtube_url: URL del video de YouTube
            audio_only: Si True, extrae solo audio (MP3)
            
        Returns:
            str: URL del stream real o None si hay error
        """
        cookies_file = os.path.join(os.path.dirname(__file__), 'youtube_cookies.txt')
        
        # Si es solo audio, usar formatos de audio
        if audio_only:
            strategies = [
                # Estrategia 1: Mejor audio disponible (sin video)
                {'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best[acodec!=none][vcodec=none]/best'},
                # Estrategia 2: Cualquier formato con audio (aunque tenga video, VLC puede extraer solo audio)
                {'format': 'best[acodec!=none]/bestaudio/best'},
                # Estrategia 3: Audio en formato específico
                {'format': 'bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio[ext=opus]/bestaudio'},
                # Estrategia 4: Cualquier audio disponible
                {'format': 'worstaudio/worst[acodec!=none]'},
            ]
        else:
            # Intentar múltiples estrategias para video
            strategies = [
                # Estrategia 1: Formato worst (más compatible)
                {'format': 'worst'},
                # Estrategia 2: Sin formato específico
                {},
                # Estrategia 3: Formato best
                {'format': 'best'},
            ]
        
        for strategy in strategies:
            try:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'noplaylist': True,
                    'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
                    'logger': None,  # Suprimir todos los logs
                }
                
                # Agregar formato si está en la estrategia
                if 'format' in strategy:
                    ydl_opts['format'] = strategy['format']
                
                # Usar cookies si están disponibles
                if os.path.exists(cookies_file):
                    ydl_opts['cookiefile'] = cookies_file
                
                # Redirigir stderr para suprimir errores
                import sys
                from io import StringIO
                
                old_stderr = sys.stderr
                sys.stderr = StringIO()
                
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(youtube_url, download=False)
                        
                        # Si hay URL directa, verificarla según el modo
                        if 'url' in info and info['url']:
                            if audio_only:
                                # Para audio-only, SOLO usar si no tiene video
                                if info.get('vcodec') == 'none' and info.get('acodec') != 'none':
                                    sys.stderr = old_stderr
                                    return info['url']
                            else:
                                # Para video, verificar que no sea solo una imagen
                                if info.get('vcodec') != 'none' or info.get('_type') != 'playlist':
                                    sys.stderr = old_stderr
                                    return info['url']
                        
                        # Si hay formatos disponibles, buscar uno válido
                        if 'formats' in info and info['formats']:
                            formats = info['formats']
                            
                            if audio_only:
                                # Para audio-only, SOLO buscar formatos de solo audio (sin video)
                                # Esto ahorra datos al usuario
                                audio_formats = ['m4a', 'mp3', 'opus', 'webm']
                                for ext in audio_formats:
                                    for fmt in formats:
                                        if (fmt.get('acodec') != 'none' and 
                                            fmt.get('vcodec') == 'none' and  # SOLO audio, sin video
                                            fmt.get('url') and
                                            ext in fmt.get('ext', '').lower()):
                                            sys.stderr = old_stderr
                                            return fmt['url']
                                
                                # Si no hay formato específico, buscar cualquier formato de solo audio
                                for fmt in formats:
                                    if (fmt.get('acodec') != 'none' and 
                                        fmt.get('vcodec') == 'none' and  # CRÍTICO: solo audio, sin video
                                        fmt.get('url') and
                                        'mhtml' not in fmt.get('ext', '').lower()):
                                        sys.stderr = old_stderr
                                        return fmt['url']
                                
                                # NO usar formatos con video, solo audio puro para ahorrar datos
                            else:
                                # Para video, buscar formatos con video y audio
                                # Intentar encontrar formato con video y audio
                                for fmt in formats:
                                    if (fmt.get('vcodec') != 'none' and 
                                        fmt.get('acodec') != 'none' and 
                                        fmt.get('url') and
                                        'mhtml' not in fmt.get('ext', '').lower()):
                                        sys.stderr = old_stderr
                                        return fmt['url']
                                
                                # Si no hay formato combinado, buscar cualquier formato con video
                                for fmt in formats:
                                    if (fmt.get('vcodec') != 'none' and 
                                        fmt.get('url') and
                                        'mhtml' not in fmt.get('ext', '').lower()):
                                        sys.stderr = old_stderr
                                        return fmt['url']
                                
                                # Último recurso: cualquier formato con URL (excepto imágenes)
                                for fmt in formats:
                                    if (fmt.get('url') and 
                                        'mhtml' not in fmt.get('ext', '').lower() and
                                        fmt.get('vcodec') != 'none'):
                                        sys.stderr = old_stderr
                                        return fmt['url']
                finally:
                    sys.stderr = old_stderr
            
            except Exception as e:
                # Capturar el error pero continuar con la siguiente estrategia
                error_msg = str(e)
                # Solo mostrar errores relevantes (no todos los errores de formato)
                if 'format' not in error_msg.lower() and 'not available' not in error_msg.lower():
                    # Guardar el último error para debug si todas las estrategias fallan
                    pass
                continue
        
        # Si todas las estrategias fallaron, retornar None
        return None
    
    def play_youtube_url(self, youtube_url: str, fullscreen: bool = False, audio_only: bool = False) -> bool:
        """
        Reproduce un video de YouTube directamente usando VLC.
        Obtiene la URL del stream real usando yt-dlp.
        
        Args:
            youtube_url: URL del video de YouTube
            fullscreen: Si True, reproduce en pantalla completa
            audio_only: Si True, reproduce solo el audio (MP3)
            
        Returns:
            bool: True si se inició la reproducción exitosamente
        """
        if not self.is_available():
            print("✗ VLC no está instalado o no se encuentra en el PATH.")
            print("\n📥 Instalación de VLC:")
            print("   Windows: https://www.videolan.org/vlc/download-windows.html")
            print("   macOS: https://www.videolan.org/vlc/download-macos.html")
            print("   Linux: sudo apt-get install vlc (Ubuntu/Debian)")
            return False
        
        try:
            mode_text = "audio (MP3)" if audio_only else "video"
            print(f"\n📺 Obteniendo URL del stream de YouTube ({mode_text})...")
            print(f"   URL: {youtube_url}")
            
            # Obtener URL del stream real
            stream_url = self._get_youtube_stream_url(youtube_url, audio_only=audio_only)
            
            if not stream_url:
                # Si es audio-only y falla, intentar método alternativo
                if audio_only:
                    print("⚠ No se pudo obtener stream URL directo, intentando método alternativo...")
                    return self._play_audio_alternative(youtube_url, fullscreen)
                else:
                    print("✗ No se pudo obtener la URL del stream.")
                    print("   Intenta descargar el video primero con --download-and-play")
                    return False
            
            print("✓ URL del stream obtenida.")
            print(f"\n▶ Iniciando VLC...")
            
            cmd = [self.vlc_path]
            
            # Opciones de VLC - usar interfaz gráfica normal para poder cerrar fácilmente
            if fullscreen:
                cmd.append('--fullscreen')
            
            # Configurar interfaz según el sistema y modo
            cmd.append('--intf')
            if os.environ.get('TERMUX_VERSION') or os.path.exists('/data/data/com.termux'):
                # Termux/Android: usar interfaz dummy (sin GUI) para solo audio
                if audio_only:
                    cmd.append('dummy')  # Interfaz dummy para solo audio (ahorra recursos)
                else:
                    cmd.append('minimal')  # Interfaz minimal para video
            else:
                system = platform.system()
                if system == 'Darwin':
                    cmd.append('macosx')  # Interfaz nativa de macOS
                else:
                    cmd.append('qt')  # Interfaz Qt (por defecto en Windows/Linux)
            
            cmd.append('--no-video-title-show')  # No mostrar título del video encima
            
            # Si es solo audio, deshabilitar video completamente (ahorra datos)
            if audio_only:
                cmd.append('--no-video')  # Solo audio, sin video
            
            # Agregar la URL del stream
            cmd.append(stream_url)
            
            # Ejecutar VLC en segundo plano pero con interfaz gráfica
            process = subprocess.Popen(cmd,
                                     stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
            
            print("✓ VLC iniciado con interfaz gráfica.")
            print("   Puedes cerrar VLC normalmente desde la ventana o presionando Alt+F4 (Windows) / Cmd+Q (Mac)")
            return True
        
        except Exception as e:
            print(f"✗ Error iniciando VLC: {e}")
            return False
    
    def _play_audio_alternative(self, youtube_url: str, fullscreen: bool = False) -> bool:
        """
        Método alternativo para reproducir audio cuando falla la extracción del stream.
        Usa yt-dlp para extraer el stream URL de audio y lo reproduce con VLC.
        
        Args:
            youtube_url: URL del video de YouTube
            fullscreen: Si True, reproduce en pantalla completa
            
        Returns:
            bool: True si se inició la reproducción exitosamente
        """
        try:
            print("   Intentando extraer stream de audio con yt-dlp...")
            
            cookies_file = os.path.join(os.path.dirname(__file__), 'youtube_cookies.txt')
            
            # Intentar múltiples estrategias para obtener el stream URL de audio
            audio_strategies = [
                {'format': 'bestaudio[ext=m4a]/bestaudio/best'},
                {'format': 'bestaudio[ext=webm]/bestaudio'},
                {'format': 'bestaudio'},
                {'format': 'best[acodec!=none][vcodec=none]/bestaudio/best'},
            ]
            
            import sys
            from io import StringIO
            
            for strategy in audio_strategies:
                try:
                    ydl_opts = {
                        'quiet': True,
                        'no_warnings': True,
                        'noplaylist': True,
                        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
                        'logger': None,
                    }
                    
                    if 'format' in strategy:
                        ydl_opts['format'] = strategy['format']
                    
                    if os.path.exists(cookies_file):
                        ydl_opts['cookiefile'] = cookies_file
                    
                    old_stderr = sys.stderr
                    sys.stderr = StringIO()
                    
                    try:
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            info = ydl.extract_info(youtube_url, download=False)
                            
                            audio_url = None
                            
                            # Si hay URL directa en info y tiene audio, usarla
                            if 'url' in info and info['url']:
                                if info.get('acodec') != 'none':
                                    audio_url = info['url']
                            
                            # Buscar en formatos disponibles
                            if not audio_url and 'formats' in info and info['formats']:
                                # Priorizar formatos de solo audio
                                for fmt in info['formats']:
                                    if (fmt.get('acodec') != 'none' and 
                                        fmt.get('vcodec') == 'none' and
                                        fmt.get('url') and
                                        'mhtml' not in fmt.get('ext', '').lower()):
                                        audio_url = fmt['url']
                                        break
                                
                                # NO buscar formatos con video, solo audio puro para ahorrar datos
                                # Si no se encuentra formato de solo audio, el método fallará
                                # y se intentará descargar el audio temporalmente
                            
                            if audio_url:
                                sys.stderr = old_stderr
                                print("✓ Stream de audio obtenido (método alternativo)")
                                print(f"   Reproduciendo stream de audio...")
                                
                                # Reproducir directamente con VLC
                                cmd = [self.vlc_path]
                                
                                if fullscreen:
                                    cmd.append('--fullscreen')
                                
                                # Configurar interfaz (compatible con Termux)
                                if os.environ.get('TERMUX_VERSION') or os.path.exists('/data/data/com.termux'):
                                    cmd.extend(['--intf', 'dummy'])  # Interfaz dummy para Termux
                                else:
                                    system = platform.system()
                                    if system == 'Darwin':
                                        cmd.extend(['--intf', 'macosx'])
                                    else:
                                        cmd.extend(['--intf', 'qt'])
                                
                                cmd.append('--no-video-title-show')
                                cmd.append('--no-video')  # Solo audio, sin video
                                cmd.append(audio_url)
                                
                                process = subprocess.Popen(
                                    cmd,
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL
                                )
                                
                                print("✓ VLC iniciado en modo solo audio.")
                                print("   El audio debería comenzar a reproducirse ahora.")
                                return True
                    
                    finally:
                        sys.stderr = old_stderr
                
                except Exception as e:
                    # Continuar con la siguiente estrategia
                    continue
            
            # Si todas las estrategias fallan, intentar descargar temporalmente
            print("   No se pudo obtener stream URL, descargando audio temporalmente...")
            return self._download_and_play_audio(youtube_url, fullscreen)
                
        except Exception as e:
            print(f"✗ Error en método alternativo: {e}")
            # Último intento: descargar y reproducir
            return self._download_and_play_audio(youtube_url, fullscreen)
    
    def _download_and_play_audio(self, youtube_url: str, fullscreen: bool = False) -> bool:
        """
        Descarga el audio temporalmente y lo reproduce con VLC.
        
        Args:
            youtube_url: URL del video de YouTube
            fullscreen: Si True, reproduce en pantalla completa
            
        Returns:
            bool: True si se inició la reproducción exitosamente
        """
        import tempfile
        import shutil
        
        try:
            cookies_file = os.path.join(os.path.dirname(__file__), 'youtube_cookies.txt')
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, f"yt_audio_{int(time.time())}")
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': temp_file + '.%(ext)s',
                'quiet': False,
                'no_warnings': False,
                'noplaylist': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            
            if os.path.exists(cookies_file):
                ydl_opts['cookiefile'] = cookies_file
            
            print("   Descargando audio (esto puede tomar unos momentos)...")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
            
            # Buscar el archivo descargado
            downloaded_file = None
            for ext in ['mp3', 'm4a', 'webm', 'opus']:
                test_file = temp_file + '.' + ext
                if os.path.exists(test_file):
                    downloaded_file = test_file
                    break
            
            if not downloaded_file:
                # Buscar cualquier archivo que empiece con el nombre temporal
                for file in os.listdir(temp_dir):
                    if file.startswith(os.path.basename(temp_file)):
                        downloaded_file = os.path.join(temp_dir, file)
                        break
            
            if downloaded_file:
                print(f"✓ Audio descargado, reproduciendo...")
                
                # Reproducir con VLC
                cmd = [self.vlc_path]
                
                if fullscreen:
                    cmd.append('--fullscreen')
                
                # Configurar interfaz (compatible con Termux)
                if os.environ.get('TERMUX_VERSION') or os.path.exists('/data/data/com.termux'):
                    cmd.extend(['--intf', 'dummy'])  # Interfaz dummy para Termux
                else:
                    system = platform.system()
                    if system == 'Darwin':
                        cmd.extend(['--intf', 'macosx'])
                    else:
                        cmd.extend(['--intf', 'qt'])
                
                cmd.append('--no-video-title-show')
                cmd.append('--no-video')  # Solo audio, sin video
                cmd.append(downloaded_file)
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
                print("✓ VLC iniciado en modo solo audio.")
                print(f"   Archivo temporal: {downloaded_file}")
                print("   (El archivo se eliminará cuando cierres VLC)")
                return True
            else:
                print("✗ No se pudo encontrar el archivo descargado.")
                return False
                
        except Exception as e:
            print(f"✗ Error descargando audio: {e}")
            return False
    
    def _play_youtube_direct(self, youtube_url: str, fullscreen: bool = False, audio_only: bool = False) -> bool:
        """
        Reproduce directamente la URL de YouTube en VLC (VLC intentará extraer el stream).
        
        Args:
            youtube_url: URL del video de YouTube
            fullscreen: Si True, reproduce en pantalla completa
            audio_only: Si True, reproduce solo el audio
            
        Returns:
            bool: True si se inició la reproducción exitosamente
        """
        try:
            cmd = [self.vlc_path]
            
            if fullscreen:
                cmd.append('--fullscreen')
            
            # Configurar interfaz
            system = platform.system()
            if system == 'Darwin':
                cmd.extend(['--intf', 'macosx'])
            else:
                cmd.extend(['--intf', 'qt'])
            
            cmd.append('--no-video-title-show')
            
            if audio_only:
                cmd.append('--no-video')  # Solo audio
            
            cmd.append(youtube_url)
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            mode_text = "solo audio" if audio_only else "video"
            print(f"✓ VLC iniciado en modo {mode_text} (usando URL directa).")
            print("   Nota: VLC intentará extraer el stream automáticamente.")
            return True
            
        except Exception as e:
            print(f"✗ Error iniciando VLC con URL directa: {e}")
            return False
    
    def play_file(self, file_path: str, fullscreen: bool = False) -> bool:
        """
        Reproduce un archivo de video local usando VLC.
        
        Args:
            file_path: Ruta al archivo de video
            fullscreen: Si True, reproduce en pantalla completa
            
        Returns:
            bool: True si se inició la reproducción exitosamente
        """
        if not self.is_available():
            print("✗ VLC no está instalado o no se encuentra en el PATH.")
            return False
        
        if not os.path.exists(file_path):
            print(f"✗ Archivo no encontrado: {file_path}")
            return False
        
        try:
            cmd = [self.vlc_path]
            
            # Opciones de VLC - usar interfaz gráfica normal
            if fullscreen:
                cmd.append('--fullscreen')
            
            # Usar interfaz gráfica normal para poder cerrar fácilmente
            cmd.append('--intf')
            system = platform.system()
            if system == 'Darwin':
                cmd.append('macosx')
            else:
                cmd.append('qt')
            
            cmd.append('--no-video-title-show')
            cmd.append(file_path)
            
            print(f"\n▶ Reproduciendo archivo con VLC...")
            print(f"   Archivo: {file_path}")
            
            # Ejecutar VLC en segundo plano con interfaz gráfica
            subprocess.Popen(cmd,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
            
            print("✓ VLC iniciado con interfaz gráfica.")
            print("   Puedes cerrar VLC normalmente desde la ventana o presionando Alt+F4 (Windows) / Cmd+Q (Mac)")
            return True
        
        except Exception as e:
            print(f"✗ Error iniciando VLC: {e}")
            return False
    
    def _get_youtube_stream_url_with_retry(self, youtube_url: str, max_retries: int = 2) -> Optional[str]:
        """
        Obtiene la URL del stream con reintentos y mejor manejo de errores.
        
        Args:
            youtube_url: URL del video de YouTube
            max_retries: Número máximo de reintentos
            
        Returns:
            str: URL del stream real o None si hay error
        """
        for attempt in range(max_retries):
            url = self._get_youtube_stream_url(youtube_url)
            if url:
                return url
            # Esperar un poco antes de reintentar
            if attempt < max_retries - 1:
                import time
                time.sleep(1)
        return None
    
    def _start_vlc_with_http(self, fullscreen: bool = False) -> bool:
        """
        Inicia VLC con interfaz HTTP habilitada para control remoto.
        
        Args:
            fullscreen: Si True, reproduce en pantalla completa
            
        Returns:
            bool: True si VLC se inició correctamente
        """
        try:
            cmd = [self.vlc_path]
            
            # Habilitar interfaz HTTP para control remoto (como interfaz adicional)
            cmd.extend([
                '--extraintf', 'http',  # Interfaz HTTP adicional (no reemplaza la GUI)
                '--http-port', str(self.vlc_http_port),
                '--http-password', self.vlc_http_password,
            ])
            
            # Opciones de VLC
            if fullscreen:
                cmd.append('--fullscreen')
            
            # Usar interfaz gráfica normal
            cmd.append('--intf')
            system = platform.system()
            if system == 'Darwin':
                cmd.append('macosx')
            else:
                cmd.append('qt')
            
            cmd.append('--no-video-title-show')
            
            # Ejecutar VLC
            self.vlc_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Esperar un poco para que VLC inicie
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"✗ Error iniciando VLC con HTTP: {e}")
            return False
    
    def _start_vlc_with_http_and_video(self, video_url: str, fullscreen: bool = False) -> bool:
        """
        Inicia VLC con interfaz HTTP habilitada y reproduce un video inmediatamente.
        
        Args:
            video_url: URL del video a reproducir
            fullscreen: Si True, reproduce en pantalla completa
            
        Returns:
            bool: True si VLC se inició correctamente
        """
        try:
            cmd = [self.vlc_path]
            
            # Habilitar interfaz HTTP para control remoto (como interfaz adicional)
            cmd.extend([
                '--extraintf', 'http',  # Interfaz HTTP adicional (no reemplaza la GUI)
                '--http-port', str(self.vlc_http_port),
                '--http-password', self.vlc_http_password,
            ])
            
            # Opciones de VLC
            if fullscreen:
                cmd.append('--fullscreen')
            
            # Configurar interfaz según el sistema y modo (compatible con Termux)
            cmd.append('--intf')
            if os.environ.get('TERMUX_VERSION') or os.path.exists('/data/data/com.termux'):
                if self.audio_only:
                    cmd.append('dummy')  # Interfaz dummy para solo audio
                else:
                    cmd.append('minimal')  # Interfaz minimal para video
            else:
                system = platform.system()
                if system == 'Darwin':
                    cmd.append('macosx')
                else:
                    cmd.append('qt')
            
            cmd.append('--no-video-title-show')
            
            # Si es solo audio, deshabilitar video (ahorra datos)
            if self.audio_only:
                cmd.append('--no-video')
            
            # Agregar el video directamente al comando
            cmd.append(video_url)
            
            # Ejecutar VLC
            self.vlc_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Verificar que el proceso se inició
            if self.vlc_process.poll() is not None:
                print(f"✗ VLC se cerró inmediatamente después de iniciar.")
                return False
            
            # Esperar un poco para que VLC inicie y cargue el video
            time.sleep(3)
            
            # Verificar que VLC sigue corriendo
            if self.vlc_process.poll() is not None:
                print(f"✗ VLC se cerró durante la inicialización.")
                return False
            
            return True
            
        except Exception as e:
            print(f"✗ Error iniciando VLC con HTTP: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _vlc_http_request(self, command: str, params: dict = None) -> Optional[dict]:
        """
        Envía un comando HTTP a VLC.
        
        Args:
            command: Comando a ejecutar (ej: 'status', 'playlist', 'next')
            params: Parámetros adicionales
            
        Returns:
            dict: Respuesta de VLC o None si hay error
        """
        if not REQUESTS_AVAILABLE:
            return None
        
        try:
            url = f"http://localhost:{self.vlc_http_port}/requests/status.json"
            if params:
                url += '?' + '&'.join([f"{k}={v}" for k, v in params.items()])
            
            response = requests.get(
                url,
                auth=('', self.vlc_http_password),
                timeout=2
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception:
            return None
    
    def _vlc_command(self, command: str) -> bool:
        """
        Ejecuta un comando en VLC vía HTTP.
        
        Args:
            command: Comando a ejecutar (play, pause, stop, next, prev, etc.)
            
        Returns:
            bool: True si el comando se ejecutó correctamente
        """
        if not REQUESTS_AVAILABLE:
            return False
        
        try:
            url = f"http://localhost:{self.vlc_http_port}/requests/status.json"
            params = {'command': command}
            
            response = requests.get(
                url,
                params=params,
                auth=('', self.vlc_http_password),
                timeout=2
            )
            
            return response.status_code == 200
            
        except Exception:
            return False
    
    def _vlc_add_playlist(self, video_url: str) -> bool:
        """
        Agrega un video a la playlist de VLC vía HTTP.
        
        Args:
            video_url: URL del video a agregar
            
        Returns:
            bool: True si se agregó correctamente
        """
        if not REQUESTS_AVAILABLE:
            return False
        
        try:
            url = f"http://localhost:{self.vlc_http_port}/requests/status.json"
            params = {
                'command': 'in_enqueue',
                'input': video_url
            }
            
            response = requests.get(
                url,
                params=params,
                auth=('', self.vlc_http_password),
                timeout=5
            )
            
            return response.status_code == 200
            
        except Exception:
            return False
    
    def _save_playlist_state(self):
        """Guarda el estado actual de la playlist en un archivo."""
        try:
            state = {
                'playlist': self.current_playlist,
                'current_index': self.current_index,
                'is_playing': self.is_playing
            }
            with open(self.playlist_state_file, 'w') as f:
                json.dump(state, f)
        except Exception:
            pass
    
    def _load_playlist_state(self) -> bool:
        """Carga el estado de la playlist desde un archivo."""
        try:
            if os.path.exists(self.playlist_state_file):
                with open(self.playlist_state_file, 'r') as f:
                    state = json.load(f)
                    self.current_playlist = state.get('playlist', [])
                    self.current_index = state.get('current_index', 0)
                    self.is_playing = state.get('is_playing', False)
                    return True
        except Exception:
            pass
        return False
    
    def _monitor_playlist(self, video_urls: List[str], fullscreen: bool = False):
        """
        Monitorea la reproducción de la playlist y avanza al siguiente video cuando termina.
        
        Args:
            video_urls: Lista de URLs de videos
            fullscreen: Si True, reproduce en pantalla completa
        """
        self.current_playlist = video_urls
        self.current_index = 0
        self.is_playing = True
        self._save_playlist_state()
        
        # Reproducir el primer video
        if self.current_index < len(self.current_playlist):
            self._play_next_video(fullscreen)
        
        # Monitorear reproducción
        consecutive_failures = 0
        last_state = None
        
        while self.is_playing and self.current_index < len(self.current_playlist):
            time.sleep(5)  # Verificar cada 5 segundos (más tiempo para evitar falsos positivos)
            
            # Verificar estado de VLC
            if REQUESTS_AVAILABLE:
                status = self._vlc_http_request('status')
                if status:
                    consecutive_failures = 0
                    state = status.get('state', '')
                    length = status.get('length', 0)
                    time_pos = status.get('time', 0)
                    
                    # Solo avanzar si el estado cambió de 'playing' a 'stopped' o 'ended'
                    # Y si el video realmente terminó (no solo se detuvo momentáneamente)
                    if state == 'stopped' or state == 'ended':
                        # Verificar que el video realmente terminó (no solo se pausó)
                        if last_state == 'playing' or (length > 0 and abs(time_pos - length) < 2):
                            # El video terminó realmente
                            self.current_index += 1
                            self._save_playlist_state()
                            if self.current_index < len(self.current_playlist):
                                item_text = "audio" if self.audio_only else "video"
                                print(f"\n▶ Reproduciendo siguiente {item_text} [{self.current_index + 1}/{len(self.current_playlist)}]...")
                                self._play_next_video(fullscreen)
                            else:
                                print(f"\n✓ Playlist completada.")
                                self.is_playing = False
                                # Limpiar archivo de estado
                                try:
                                    if os.path.exists(self.playlist_state_file):
                                        os.remove(self.playlist_state_file)
                                except:
                                    pass
                                break
                    
                    last_state = state
                else:
                    consecutive_failures += 1
                    if consecutive_failures > 10:  # Más intentos antes de considerar que falló
                        # Si no hay respuesta HTTP después de muchos intentos, verificar proceso
                        if self.vlc_process and self.vlc_process.poll() is not None:
                            # VLC se cerró - avanzar al siguiente
                            self.current_index += 1
                            if self.current_index < len(self.current_playlist):
                                item_text = "audio" if self.audio_only else "video"
                                print(f"\n▶ VLC se cerró. Reproduciendo siguiente {item_text} [{self.current_index + 1}/{len(self.current_playlist)}]...")
                                self._play_next_video(fullscreen)
                            else:
                                self.is_playing = False
                                break
            else:
                # Sin HTTP, verificar solo el proceso
                if self.vlc_process and self.vlc_process.poll() is not None:
                    # VLC se cerró - avanzar al siguiente
                    self.current_index += 1
                    if self.current_index < len(self.current_playlist):
                        item_text = "audio" if self.audio_only else "video"
                        print(f"\n▶ Reproduciendo siguiente {item_text} [{self.current_index + 1}/{len(self.current_playlist)}]...")
                        self._play_next_video(fullscreen)
                    else:
                        print(f"\n✓ Playlist completada.")
                        self.is_playing = False
                        break
    
    def _play_next_video(self, fullscreen: bool = False):
        """
        Reproduce el siguiente video en la playlist.
        
        Args:
            fullscreen: Si True, reproduce en pantalla completa
        """
        if self.current_index >= len(self.current_playlist):
            return
        
        youtube_url = self.current_playlist[self.current_index]
        mode_text = "audio" if self.audio_only else "stream"
        print(f"\n[{self.current_index + 1}/{len(self.current_playlist)}] Obteniendo URL del {mode_text}...")
        
        # Agregar un pequeño retraso para evitar rate limiting
        if self.current_index > 0:
            time.sleep(2)
        
        # Obtener URL del stream usando yt-dlp
        stream_url = self._get_youtube_stream_url(youtube_url, audio_only=self.audio_only)
        
        # Si no se pudo obtener stream URL, intentar con método alternativo
        if not stream_url:
            print(f"⚠ No se pudo obtener stream URL con yt-dlp")
            print(f"   Esto puede deberse a:")
            print(f"   - YouTube está limitando solicitudes (espera unos minutos)")
            print(f"   - Las cookies pueden estar expiradas (actualiza youtube_cookies.txt)")
            print(f"   - El video puede estar restringido")
            print(f"   Omitiendo este video y continuando con el siguiente...")
            # Avanzar al siguiente video
            self.current_index += 1
            self._save_playlist_state()
            if self.current_index < len(self.current_playlist):
                self._play_next_video(fullscreen)
            return
        
        # Si es el primer video, iniciar VLC con el video directamente
        if self.current_index == 0:
            if not self._start_vlc_with_http_and_video(stream_url, fullscreen):
                print("✗ Error iniciando VLC")
                # Si falla, intentar con URL directa de YouTube
                if stream_url != youtube_url:
                    print("   Intentando con URL directa de YouTube...")
                    if not self._start_vlc_with_http_and_video(youtube_url, fullscreen):
                        print("✗ Error iniciando VLC con URL directa")
                        return
                else:
                    return
            item_text = "audio" if self.audio_only else "video"
            print(f"✓ Reproduciendo {item_text} [{self.current_index + 1}/{len(self.current_playlist)}]")
        else:
            # Para videos siguientes, agregar a la playlist y avanzar
            if self._vlc_add_playlist(stream_url):
                time.sleep(0.5)
                self._vlc_command('next')
                item_text = "audio" if self.audio_only else "video"
                print(f"✓ Reproduciendo {item_text} [{self.current_index + 1}/{len(self.current_playlist)}]")
            else:
                # Si falla, reproducir directamente
                self._play_video_directly(stream_url, fullscreen)
                item_text = "audio" if self.audio_only else "video"
                print(f"✓ Reproduciendo {item_text} [{self.current_index + 1}/{len(self.current_playlist)}]")
    
    def _play_video_directly(self, video_url: str, fullscreen: bool = False):
        """
        Reproduce un video directamente en VLC (método alternativo).
        
        Args:
            video_url: URL del video
            fullscreen: Si True, reproduce en pantalla completa
        """
        try:
            cmd = [self.vlc_path]
            
            if fullscreen:
                cmd.append('--fullscreen')
            
            # Configurar interfaz según el sistema y modo (compatible con Termux)
            cmd.append('--intf')
            if os.environ.get('TERMUX_VERSION') or os.path.exists('/data/data/com.termux'):
                if self.audio_only:
                    cmd.append('dummy')  # Interfaz dummy para solo audio
                else:
                    cmd.append('minimal')  # Interfaz minimal para video
            else:
                system = platform.system()
                if system == 'Darwin':
                    cmd.append('macosx')
                else:
                    cmd.append('qt')
            
            cmd.append('--no-video-title-show')
            
            # Si es solo audio, deshabilitar video (ahorra datos)
            if self.audio_only:
                cmd.append('--no-video')
            
            cmd.append(video_url)
            
            # Si ya hay un proceso, cerrarlo primero
            if self.vlc_process:
                try:
                    self.vlc_process.terminate()
                    self.vlc_process.wait(timeout=2)
                except:
                    pass
            
            self.vlc_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
        except Exception as e:
            print(f"⚠ Error reproduciendo video directamente: {e}")
    
    def next_track(self) -> bool:
        """
        Avanza a la siguiente canción en la playlist.
        
        Returns:
            bool: True si se avanzó correctamente
        """
        # Cargar estado de la playlist
        if not self._load_playlist_state():
            return False
        
        if not self.is_playing or len(self.current_playlist) == 0:
            print("✗ No hay playlist reproduciéndose.")
            return False
        
        self.current_index += 1
        if self.current_index < len(self.current_playlist):
            item_text = "canción" if self.audio_only else "video"
            print(f"\n⏭️  Saltando a siguiente {item_text} [{self.current_index + 1}/{len(self.current_playlist)}]...")
            self._save_playlist_state()
            
            # Intentar avanzar vía HTTP
            if REQUESTS_AVAILABLE and self._vlc_command('next'):
                return True
            else:
                # Si HTTP no funciona, reproducir directamente el siguiente
                item_text = "audio" if self.audio_only else "video"
                print(f"   Reproduciendo siguiente {item_text} directamente...")
                self._play_video_directly(self.current_playlist[self.current_index])
                return True
        else:
            print("ℹ Ya estás en el último video de la playlist.")
            return False
    
    def play_playlist(self, video_urls: list, fullscreen: bool = False, audio_only: bool = False) -> bool:
        """
        Reproduce una lista de videos de YouTube secuencialmente usando VLC.
        Solo reproduce un video a la vez y espera a que termine antes del siguiente.
        Soporta control remoto para avanzar a la siguiente canción.
        
        Args:
            video_urls: Lista de URLs de videos de YouTube
            fullscreen: Si True, reproduce en pantalla completa
            audio_only: Si True, reproduce solo el audio (MP3) de cada video
            
        Returns:
            bool: True si se inició la reproducción exitosamente
        """
        if not self.is_available():
            print("✗ VLC no está instalado o no se encuentra en el PATH.")
            print("\n📥 Instalación de VLC:")
            print("   Windows: https://www.videolan.org/vlc/download-windows.html")
            print("   macOS: https://www.videolan.org/vlc/download-macos.html")
            print("   Linux: sudo apt-get install vlc (Ubuntu/Debian)")
            return False
        
        if not video_urls:
            print("✗ La lista de videos está vacía.")
            return False
        
        # Verificar si requests está disponible para control HTTP
        if not REQUESTS_AVAILABLE:
            print("⚠ Advertencia: 'requests' no está instalado.")
            print("   Instálalo con: pip install requests")
            print("   Sin esto, no podrás usar el control remoto (botón siguiente).")
            print("   Continuando sin control remoto...\n")
        
        try:
            # Guardar configuración de audio_only
            self.audio_only = audio_only
            
            mode_text = "audio (MP3)" if audio_only else "videos"
            print(f"\n📺 Reproduciendo playlist con {len(video_urls)} {mode_text}...")
            print(f"   ℹ Modo: Un {mode_text[:-1]} a la vez (espera a que termine antes del siguiente)")
            
            # Verificar si hay archivo de cookies
            cookies_file = os.path.join(os.path.dirname(__file__), 'youtube_cookies.txt')
            has_cookies = os.path.exists(cookies_file)
            
            if not has_cookies:
                print(f"\n   ⚠ ADVERTENCIA: No se encontró archivo de cookies.")
                print(f"   Algunos videos pueden no reproducirse correctamente.")
                print(f"   📖 Ver: INSTRUCCIONES_COOKIES.md para configurar cookies\n")
            
            print(f"\n▶ Iniciando VLC con control remoto...")
            print(f"   Puerto HTTP: {self.vlc_http_port}")
            print(f"   Contraseña: {self.vlc_http_password}")
            print(f"\n💡 Para saltar a la siguiente canción, ejecuta:")
            print(f"   py main.py --playlist-next")
            print(f"   O presiona Ctrl+C y vuelve a ejecutar este comando\n")
            
            # Iniciar monitoreo en un hilo separado
            self.playlist_thread = threading.Thread(
                target=self._monitor_playlist,
                args=(video_urls, fullscreen),
                daemon=True
            )
            self.playlist_thread.start()
            
            # Esperar un poco para que el hilo inicie
            time.sleep(2)
            
            print("✓ Reproducción iniciada.")
            item_text = "Canción actual" if audio_only else "Video actual"
            print(f"   {item_text}: [1/{len(video_urls)}]")
            print("   VLC se abrirá automáticamente...")
            print("\n💡 Presiona Ctrl+C para detener la reproducción")
            
            # Mantener el programa corriendo para que el hilo pueda funcionar
            try:
                while self.is_playing:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n⏹️  Deteniendo reproducción...")
                self.is_playing = False
                if self.vlc_process:
                    try:
                        self.vlc_process.terminate()
                    except:
                        pass
            
            return True
        
        except Exception as e:
            print(f"✗ Error iniciando reproducción: {e}")
            return False
    
    def get_vlc_info(self) -> dict:
        """
        Obtiene información sobre la instalación de VLC.
        
        Returns:
            dict: Información de VLC
        """
        info = {
            'available': self.is_available(),
            'path': self.vlc_path,
        }
        
        if self.is_available():
            try:
                result = subprocess.run([self.vlc_path, '--version'],
                                      capture_output=True,
                                      timeout=2,
                                      text=True)
                if result.returncode == 0:
                    # Extraer versión de la salida
                    version_line = result.stdout.split('\n')[0] if result.stdout else ''
                    info['version'] = version_line
            except:
                info['version'] = 'Desconocida'
        
        return info
