"""
Reproductor de videos usando VLC.
Permite reproducir videos de YouTube directamente o desde archivos locales.
"""
import os
import subprocess
import platform
from typing import Optional
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
            ]
        }
        
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
        return self.vlc_path is not None
    
    def play_youtube_url(self, youtube_url: str, fullscreen: bool = False) -> bool:
        """
        Reproduce un video de YouTube directamente usando VLC.
        
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
            cmd = [self.vlc_path]
            
            # Opciones de VLC
            if fullscreen:
                cmd.append('--fullscreen')
            
            # Reproducir directamente desde URL
            cmd.append('--play-and-exit')  # Cerrar VLC cuando termine
            cmd.append(youtube_url)
            
            print(f"\n▶ Reproduciendo video con VLC...")
            print(f"   URL: {youtube_url}")
            
            # Ejecutar VLC en segundo plano
            subprocess.Popen(cmd, 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            
            print("✓ VLC iniciado. El video debería comenzar a reproducirse.")
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
            
            # Opciones de VLC
            if fullscreen:
                cmd.append('--fullscreen')
            
            cmd.append('--play-and-exit')
            cmd.append(file_path)
            
            print(f"\n▶ Reproduciendo archivo con VLC...")
            print(f"   Archivo: {file_path}")
            
            # Ejecutar VLC en segundo plano
            subprocess.Popen(cmd,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
            
            print("✓ VLC iniciado. El video debería comenzar a reproducirse.")
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
