"""
Módulo para descargar videos de YouTube en MP4 y extraer audio en MP3.
Usa yt-dlp para descargas.
"""
import os
import re
from pathlib import Path
from typing import Optional, Dict, Tuple
import yt_dlp
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC
import config


class YouTubeDownloader:
    """
    Clase para descargar videos de YouTube y extraer audio.
    """
    
    def __init__(self):
        """
        Inicializa el descargador con configuración por defecto.
        """
        self.videos_dir = config.VIDEOS_DIR
        self.audio_dir = config.AUDIO_DIR
        
        # Configuración de yt-dlp para videos MP4
        # Intentar formato combinado primero, si falla usar formato único
        self.video_ydl_opts = {
            'format': 'best[ext=mp4]/best[height<=720]/best',  # Formato único que no requiere merge
            'outtmpl': os.path.join(self.videos_dir, '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            'progress_hooks': [self._progress_hook],
            'noplaylist': True,  # No descargar playlists completas
            'merge_output_format': 'mp4',  # Formato de salida si se hace merge
        }
        
        # Configuración de yt-dlp para audio MP3
        self.audio_ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.audio_dir, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': config.AUDIO_QUALITY,
            }],
            'quiet': False,
            'no_warnings': False,
            'progress_hooks': [self._progress_hook],
            'embedthumbnail': True,
            'writethumbnail': True,
        }
    
    def _progress_hook(self, d: Dict):
        """
        Hook para mostrar progreso de descarga.
        
        Args:
            d: Diccionario con información de progreso de yt-dlp
        """
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                percent = (downloaded / total) * 100
                print(f"\r⏬ Descargando: {percent:.1f}% ({downloaded}/{total} bytes)", end='', flush=True)
        elif d['status'] == 'finished':
            print(f"\n✓ Descarga completada. Procesando...")
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Limpia el nombre de archivo para que sea válido en el sistema de archivos.
        
        Args:
            filename: Nombre de archivo original
            
        Returns:
            str: Nombre de archivo sanitizado
        """
        # Remover caracteres inválidos
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Limitar longitud
        if len(filename) > 200:
            filename = filename[:200]
        return filename.strip()
    
    def get_video_info(self, url: str) -> Optional[Dict]:
        """
        Obtiene información de un video sin descargarlo.
        
        Args:
            url: URL del video de YouTube
            
        Returns:
            dict: Información del video o None si hay error
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'id': info.get('id'),
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'uploader': info.get('uploader'),
                    'view_count': info.get('view_count'),
                    'thumbnail': info.get('thumbnail'),
                    'description': info.get('description', '')[:200],
                    'url': url
                }
        except Exception as e:
            print(f"✗ Error obteniendo información del video: {e}")
            return None
    
    def download_video(self, url: str, quality: str = None) -> Optional[str]:
        """
        Descarga un video de YouTube en formato MP4.
        
        Args:
            url: URL del video de YouTube
            quality: Calidad del video (best, worst, o formato específico)
            
        Returns:
            str: Ruta del archivo descargado o None si hay error
        """
        try:
            # Configurar calidad si se especifica
            ydl_opts = self.video_ydl_opts.copy()
            if quality:
                if quality == 'best':
                    # Intentar formato combinado primero, si falla usar formato único
                    ydl_opts['format'] = 'best[ext=mp4]/best[height<=1080]/best'
                elif quality == 'worst':
                    ydl_opts['format'] = 'worst[ext=mp4]/worst'
                else:
                    ydl_opts['format'] = quality
            
            print(f"\n📥 Descargando video: {url}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Obtener información primero
                info = ydl.extract_info(url, download=False)
                title = self._sanitize_filename(info.get('title', 'video'))
                
                print(f"📹 Título: {title}")
                print(f"⏱️  Duración: {info.get('duration', 0)} segundos")
                
                # Descargar
                ydl.download([url])
                
                # Buscar el archivo descargado
                downloaded_file = self._find_downloaded_file(title, self.videos_dir)
                
                if downloaded_file:
                    print(f"✓ Video descargado: {downloaded_file}")
                    return downloaded_file
                else:
                    print("⚠ No se pudo encontrar el archivo descargado")
                    return None
                    
        except yt_dlp.utils.DownloadError as e:
            print(f"✗ Error descargando video: {e}")
            return None
        except Exception as e:
            print(f"✗ Error inesperado: {e}")
            return None
    
    def download_audio(self, url: str, quality: str = None) -> Optional[str]:
        """
        Descarga el audio de un video de YouTube en formato MP3.
        
        Args:
            url: URL del video de YouTube
            quality: Calidad del audio en kbps (ej: '192', '320')
            
        Returns:
            str: Ruta del archivo MP3 descargado o None si hay error
        """
        try:
            # Configurar calidad de audio si se especifica
            ydl_opts = self.audio_ydl_opts.copy()
            if quality:
                ydl_opts['postprocessors'][0]['preferredquality'] = quality
            
            print(f"\n🎵 Descargando audio: {url}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Obtener información primero
                info = ydl.extract_info(url, download=False)
                title = self._sanitize_filename(info.get('title', 'audio'))
                
                print(f"🎶 Título: {title}")
                print(f"👤 Artista: {info.get('uploader', 'Desconocido')}")
                print(f"⏱️  Duración: {info.get('duration', 0)} segundos")
                
                # Descargar
                ydl.download([url])
                
                # Buscar el archivo MP3 descargado
                downloaded_file = self._find_downloaded_file(title, self.audio_dir, ext='mp3')
                
                if downloaded_file:
                    # Agregar metadata al MP3
                    self._add_mp3_metadata(downloaded_file, info)
                    print(f"✓ Audio descargado: {downloaded_file}")
                    return downloaded_file
                else:
                    print("⚠ No se pudo encontrar el archivo MP3 descargado")
                    return None
                    
        except yt_dlp.utils.DownloadError as e:
            print(f"✗ Error descargando audio: {e}")
            return None
        except Exception as e:
            print(f"✗ Error inesperado: {e}")
            return None
    
    def _find_downloaded_file(self, title: str, directory: str, ext: str = None) -> Optional[str]:
        """
        Busca un archivo descargado en el directorio.
        
        Args:
            title: Título del video/audio
            directory: Directorio donde buscar
            ext: Extensión esperada (opcional)
            
        Returns:
            str: Ruta del archivo encontrado o None
        """
        title_clean = self._sanitize_filename(title)
        
        # Buscar archivos que coincidan con el título
        for file in os.listdir(directory):
            if title_clean.lower() in file.lower():
                if ext is None or file.endswith(f'.{ext}'):
                    return os.path.join(directory, file)
        
        # Si no se encuentra, buscar el archivo más reciente
        files = [f for f in os.listdir(directory) if ext is None or f.endswith(f'.{ext}')]
        if files:
            files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)
            return os.path.join(directory, files[0])
        
        return None
    
    def _add_mp3_metadata(self, filepath: str, video_info: Dict):
        """
        Agrega metadata (título, artista, etc.) al archivo MP3.
        
        Args:
            filepath: Ruta del archivo MP3
            video_info: Información del video de yt-dlp
        """
        try:
            audio = MP3(filepath, ID3=ID3)
            
            # Agregar tags básicos
            audio['TIT2'] = TIT2(encoding=3, text=video_info.get('title', 'Unknown'))
            audio['TPE1'] = TPE1(encoding=3, text=video_info.get('uploader', 'Unknown'))
            audio['TALB'] = TALB(encoding=3, text='YouTube')
            
            # Guardar cambios
            audio.save()
            
        except Exception as e:
            print(f"⚠ No se pudo agregar metadata al MP3: {e}")
    
    def download_both(self, url: str, video_quality: str = None, audio_quality: str = None) -> Tuple[Optional[str], Optional[str]]:
        """
        Descarga tanto el video MP4 como el audio MP3.
        
        Args:
            url: URL del video de YouTube
            video_quality: Calidad del video
            audio_quality: Calidad del audio
            
        Returns:
            tuple: (ruta_video, ruta_audio)
        """
        print(f"\n📥 Descargando video y audio: {url}")
        
        video_path = self.download_video(url, video_quality)
        audio_path = self.download_audio(url, audio_quality)
        
        return video_path, audio_path
