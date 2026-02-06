"""
Reproductor de videos usando VLC.
Permite reproducir videos de YouTube directamente o desde archivos locales.
"""
import os
import subprocess
import platform
from typing import Optional
import yt_dlp
import config


class VLCPlayer:
    """
    Reproductor de videos usando VLC Media Player.
    """
    
    def __init__(self):
        """
        Inicializa el reproductor VLC.
        """
        self.vlc_path = self._find_vlc()
    
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
    
    def _get_youtube_stream_url(self, youtube_url: str) -> Optional[str]:
        """
        Obtiene la URL del stream real de YouTube usando yt-dlp.
        
        Args:
            youtube_url: URL del video de YouTube
            
        Returns:
            str: URL del stream real o None si hay error
        """
        try:
            ydl_opts = {
                'format': 'best[ext=mp4]/best',  # Preferir MP4
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                
                # Obtener la URL del formato mejor disponible
                if 'url' in info:
                    return info['url']
                elif 'formats' in info and info['formats']:
                    # Buscar el mejor formato disponible
                    for format_info in info['formats']:
                        if format_info.get('vcodec') != 'none' and format_info.get('url'):
                            return format_info['url']
            
            return None
        
        except Exception as e:
            print(f"⚠ Error obteniendo URL del stream: {e}")
            return None
    
    def play_youtube_url(self, youtube_url: str, fullscreen: bool = False) -> bool:
        """
        Reproduce un video de YouTube directamente usando VLC.
        Obtiene la URL del stream real usando yt-dlp.
        
        Args:
            youtube_url: URL del video de YouTube
            fullscreen: Si True, reproduce en pantalla completa
            
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
            print(f"\n📺 Obteniendo URL del stream de YouTube...")
            print(f"   URL: {youtube_url}")
            
            # Obtener URL del stream real
            stream_url = self._get_youtube_stream_url(youtube_url)
            
            if not stream_url:
                print("✗ No se pudo obtener la URL del stream.")
                print("   Intenta descargar el video primero con --download-and-play")
                return False
            
            print("✓ URL del stream obtenida.")
            print(f"\n▶ Iniciando VLC...")
            
            cmd = [self.vlc_path]
            
            # Opciones de VLC - usar interfaz gráfica normal para poder cerrar fácilmente
            if fullscreen:
                cmd.append('--fullscreen')
            
            # Usar interfaz gráfica normal (qt por defecto en Windows/Linux, macosx en macOS)
            # Esto permite cerrar VLC normalmente desde la ventana
            cmd.append('--intf')
            system = platform.system()
            if system == 'Darwin':
                cmd.append('macosx')  # Interfaz nativa de macOS
            else:
                cmd.append('qt')  # Interfaz Qt (por defecto en Windows/Linux)
            
            cmd.append('--no-video-title-show')  # No mostrar título del video encima
            
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
