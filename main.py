"""
Bot principal para comentar, ver y descargar videos de YouTube.
Incluye sistema de moderación automática y descarga de videos/audio.
"""
import sys
import os
import argparse

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        # Si reconfigure no está disponible, usar setdefaultencoding
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from downloader import YouTubeDownloader
from comment_exporter import CommentExporter
from metadata_exporter import MetadataExporter
from utils import extract_video_id
import config

# Importar ofuscador si está disponible
try:
    from obfuscator import DataObfuscator
    OBFUSCATION_AVAILABLE = True
except ImportError:
    OBFUSCATION_AVAILABLE = False
    DataObfuscator = None

# Importar monitoreo si está disponible
try:
    from activity_monitor import ActivityMonitor
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False
    ActivityMonitor = None

# Importaciones condicionales (solo cuando se necesiten para comentarios)
YouTubeClient = None
Moderator = None


def main():
    """
    Función principal del bot.
    """
    parser = argparse.ArgumentParser(
        description='Bot para comentar, ver y descargar videos de YouTube',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Comentar en un video
  python main.py --video-id dQw4w9WgXcQ --comment "¡Excelente video!"
  
  # Listar mis comentarios en un video
  python main.py --my-comments dQw4w9WgXcQ
  
  # Listar todos mis comentarios
  python main.py --my-comments
  
  # Eliminar un comentario
  python main.py --delete-comment COMMENT_ID
  
  # Responder a un comentario
  python main.py --reply COMMENT_ID --reply-text "Mi respuesta"
  
  # Actualizar un comentario
  python main.py --update-comment COMMENT_ID --new-text "Texto actualizado"
  
  # Ver respuestas de un comentario
  python main.py --comment-replies COMMENT_ID
  
  # Ver información de un comentario
  python main.py --comment-info COMMENT_ID
  
  # Obtener comentarios de un video
  python main.py --video-id dQw4w9WgXcQ --get-comments
  
  # Ver estadísticas de un video
  python main.py --stats dQw4w9WgXcQ
  
  # Ver comentarios destacados
  python main.py --top-comments dQw4w9WgXcQ
  
  # Exportar comentarios
  python main.py --export-comments dQw4w9WgXcQ --grep-format
  
  # Descargar video MP4
  python main.py --download-video "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  
  # Descargar audio MP3
  python main.py --download-audio "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  
  # Ver información del video
  python main.py --info "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  
  # Descargar metadatos del video (JSON)
  python main.py --download-metadata "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  
  # Descargar metadatos del video (texto)
  python main.py --download-metadata dQw4w9WgXcQ --metadata-format text
        """
    )
    
    parser.add_argument(
        '--video-id',
        type=str,
        help='ID del video de YouTube donde comentar'
    )
    
    parser.add_argument(
        '--comment',
        type=str,
        help='Texto del comentario a publicar'
    )
    
    parser.add_argument(
        '--moderate',
        action='store_true',
        help='Activar moderación automática después de comentar'
    )
    
    parser.add_argument(
        '--monitor',
        action='store_true',
        help='Iniciar monitoreo continuo de comentarios'
    )
    
    parser.add_argument(
        '--get-comments',
        action='store_true',
        help='Obtener comentarios de un video'
    )
    
    # Argumentos para descarga
    parser.add_argument(
        '--download-video',
        type=str,
        metavar='URL',
        help='Descargar video en MP4 (proporciona URL de YouTube)'
    )
    
    parser.add_argument(
        '--download-audio',
        type=str,
        metavar='URL',
        help='Descargar audio en MP3 (proporciona URL de YouTube)'
    )
    
    parser.add_argument(
        '--download-both',
        type=str,
        metavar='URL',
        help='Descargar tanto video MP4 como audio MP3'
    )
    
    parser.add_argument(
        '--info',
        type=str,
        metavar='URL',
        help='Mostrar información de un video sin descargarlo'
    )
    
    parser.add_argument(
        '--video-quality',
        type=str,
        default='best',
        choices=['best', 'worst'],
        help='Calidad del video a descargar (default: best)'
    )
    
    parser.add_argument(
        '--audio-quality',
        type=str,
        default='192',
        help='Calidad del audio en kbps (default: 192)'
    )
    
    # Argumentos para estadísticas y comentarios
    parser.add_argument(
        '--stats',
        type=str,
        metavar='VIDEO_ID',
        help='Mostrar estadísticas completas de un video'
    )
    
    parser.add_argument(
        '--top-comments',
        type=str,
        metavar='VIDEO_ID',
        help='Mostrar comentarios más destacados (con más likes)'
    )
    
    parser.add_argument(
        '--export-comments',
        type=str,
        metavar='VIDEO_ID',
        help='Exportar todos los comentarios a archivo de texto'
    )
    
    parser.add_argument(
        '--max-comments',
        type=int,
        default=1000,
        help='Número máximo de comentarios a obtener/exportar (default: 1000)'
    )
    
    parser.add_argument(
        '--grep-format',
        action='store_true',
        help='Usar formato optimizado para grep al exportar comentarios'
    )
    
    parser.add_argument(
        '--activity-report',
        action='store_true',
        help='Mostrar reporte de actividad de la cuenta colectiva'
    )
    
    parser.add_argument(
        '--generate-account',
        action='store_true',
        help='Generar nombres de cuenta ofuscados y genéricos'
    )
    
    parser.add_argument(
        '--play',
        type=str,
        metavar='URL_OR_FILE',
        help='Reproducir video de YouTube o archivo local con VLC'
    )
    
    parser.add_argument(
        '--play-fullscreen',
        action='store_true',
        help='Reproducir en pantalla completa (usar con --play)'
    )
    
    parser.add_argument(
        '--download-and-play',
        type=str,
        metavar='URL',
        help='Descargar video y reproducirlo automáticamente con VLC'
    )
    
    # Authentication management
    parser.add_argument(
        '--login',
        action='store_true',
        help='Login/authenticate with your Google account'
    )
    
    parser.add_argument(
        '--logout',
        action='store_true',
        help='Logout and revoke current session'
    )
    
    parser.add_argument(
        '--auth-status',
        action='store_true',
        help='Check authentication status'
    )
    
    parser.add_argument(
        '--search',
        type=str,
        metavar='QUERY',
        help='Search YouTube videos by keywords'
    )
    
    parser.add_argument(
        '--search-max',
        type=int,
        default=10,
        help='Maximum number of search results (default: 10, max: 50)'
    )
    
    parser.add_argument(
        '--search-order',
        type=str,
        default='relevance',
        choices=['relevance', 'date', 'rating', 'title', 'viewCount'],
        help='Order of search results (default: relevance)'
    )
    
    args = parser.parse_args()
    
    # Modo: Generar nombres de cuenta
    if args.generate_account:
        from generate_account import main as generate_main
        generate_main()
        sys.exit(0)
    
    # Modo: Reproducir video con VLC (NO requiere autenticación)
    if args.play:
        from vlc_player import VLCPlayer
        
        print("\n" + "="*60)
        print("REPRODUCTOR VLC")
        print("="*60 + "\n")
        
        player = VLCPlayer()
        
        # Verificar si es una URL o un archivo local
        if args.play.startswith('http://') or args.play.startswith('https://'):
            # Es una URL de YouTube
            print(f"📺 Reproduciendo desde URL de YouTube...")
            success = player.play_youtube_url(args.play, fullscreen=args.play_fullscreen)
        else:
            # Es un archivo local
            print(f"📁 Reproduciendo archivo local...")
            success = player.play_file(args.play, fullscreen=args.play_fullscreen)
        
        if not success:
            sys.exit(1)
        else:
            sys.exit(0)
    
    # Modo: Descargar y reproducir
    if args.download_and_play:
        from vlc_player import VLCPlayer
        
        print("\n" + "="*60)
        print("DESCARGAR Y REPRODUCIR")
        print("="*60 + "\n")
        
        print("⚠ ADVERTENCIA: Descargar videos puede violar los términos de servicio")
        print("   de YouTube y leyes de derechos de autor. Usa responsablemente.")
        print("="*60 + "\n")
        
        downloader = YouTubeDownloader()
        player = VLCPlayer()
        
        if not player.is_available():
            print("✗ VLC no está disponible. Descargando video sin reproducir...")
            result = downloader.download_video(args.download_and_play)
            if result:
                print(f"\n✓ Video descargado: {result}")
            sys.exit(0)
        
        print(f"📥 Descargando video: {args.download_and_play}")
        video_path = downloader.download_video(args.download_and_play)
        
        if video_path:
            print(f"\n✓ Video descargado: {video_path}")
            print("\n▶ Iniciando reproducción automática...")
            success = player.play_file(video_path, fullscreen=args.play_fullscreen)
            
            if success:
                print("\n✓ Reproducción iniciada. VLC se cerrará automáticamente al terminar.")
            else:
                print("\n⚠ Video descargado pero no se pudo iniciar VLC.")
        else:
            print("\n✗ Error descargando el video.")
            sys.exit(1)
        
        sys.exit(0)
    
    # Verificar si necesita configuración (solo para funciones que realmente la requieren)
    # NO bloquear búsqueda, descarga, info, etc.
    functions_requiring_auth = [args.stats, args.top_comments, args.export_comments, 
                                args.comment, args.monitor, args.get_comments,
                                args.delete_comment, args.my_comments, args.reply,
                                args.update_comment, args.comment_replies, args.comment_info,
                                args.download_metadata]
    
    if not os.path.exists('.env') and any(functions_requiring_auth):
        print("\n" + "="*70)
        print("⚠ CONFIGURACIÓN REQUERIDA")
        print("="*70)
        print("\nPara usar funciones de comentarios/estadísticas necesitas configurar credenciales.")
        print("\nOpciones:")
        print("1. Ejecuta el script de configuración interactiva:")
        print("   python setup.py")
        print("\n2. O copia y edita manualmente:")
        print("   cp env.example .env")
        print("   # Luego edita .env con tus credenciales")
        print("\n3. O usa solo funciones de descarga/búsqueda (no requieren configuración):")
        print("   python main.py --download-video URL")
        print("   python main.py --info URL")
        print("   python main.py --search 'query'")
        print("\n" + "="*70 + "\n")
        sys.exit(1)
    
    try:
        # Modo: Login/Autenticación
        if args.login:
            # Verificar si existe archivo .env
            if not os.path.exists('.env'):
                print("\n" + "="*70)
                print("⚠ CONFIGURATION REQUIRED")
                print("="*70)
                print("\nYou need to configure OAuth2 credentials first.")
                print("\nOptions:")
                print("1. Run the interactive setup script:")
                print("   python setup.py")
                print("\n2. Or copy and edit manually:")
                print("   copy env.example .env")
                print("   # Then edit .env with your credentials")
                print("\n" + "="*70 + "\n")
                sys.exit(1)
            
            # Importar módulos de YouTube API
            from youtube_client import YouTubeClient
            
            # Validar credenciales antes de inicializar cliente
            try:
                config.validate_credentials()
            except ValueError as e:
                print("\n" + "="*70)
                print("⚠ CONFIGURATION ERROR")
                print("="*70)
                print(f"\n{e}")
                print("\n📋 Quick fix:")
                print("   python setup.py")
                print("\nOr edit the .env file manually with your credentials.")
                print("="*70 + "\n")
                sys.exit(1)
            
            print("\n" + "="*60)
            print("LOGIN / AUTHENTICATION")
            print("="*60)
            print("\n📝 You will use your personal Google account")
            print("✓ Only YouTube API access will be requested")
            print("✓ NO access to Gmail/email")
            print("✓ Tokens only allow YouTube actions")
            print("="*60 + "\n")
            
            print("Initializing YouTube client...")
            print("💡 Your browser will open to sign in with your personal account")
            
            try:
                youtube_client = YouTubeClient()
                
                # Verificar autenticación
                auth_info = youtube_client.get_auth_info()
                
                if auth_info['authenticated']:
                    print("\n✓ Login successful!")
                    print(f"  Token file: {auth_info['token_file']}")
                    print(f"  Token valid: {auth_info['token_valid']}")
                    if auth_info['has_refresh_token']:
                        print(f"  Refresh token: Available")
                    print("\nYou can now use all YouTube features.")
                else:
                    print("\n⚠ Authentication completed but token may need refresh.")
                    
            except Exception as e:
                print(f"\n✗ Error during login: {str(e)}")
                sys.exit(1)
            
            sys.exit(0)
        
        # Modo: Logout
        elif args.logout:
            # Verificar si existe archivo .env
            if not os.path.exists('.env'):
                print("\n" + "="*70)
                print("⚠ CONFIGURATION REQUIRED")
                print("="*70)
                print("\nNo credentials configured. Nothing to logout from.")
                print("="*70 + "\n")
                sys.exit(0)
            
            # Importar módulos de YouTube API
            from youtube_client import YouTubeClient
            
            print("\n" + "="*60)
            print("LOGOUT")
            print("="*60 + "\n")
            
            # Verificar si hay sesión activa
            token_exists = os.path.exists(config.TOKEN_FILE)
            
            if not token_exists:
                print("ℹ No active session found.")
                print("  You are already logged out.")
                sys.exit(0)
            
            # Confirmar logout
            confirm = input("Are you sure you want to logout? (y/n): ").strip().lower()
            
            if confirm not in ['y', 'yes']:
                print("✗ Logout cancelled.")
                sys.exit(0)
            
            # Intentar cargar cliente para revocar token
            try:
                config.validate_credentials()
                youtube_client = YouTubeClient()
                success = youtube_client.logout()
                
                if success:
                    print("\n✓ Logout successful!")
                    print("  Your session has been closed.")
                    print("  Token has been revoked and deleted.")
                else:
                    print("\n⚠ Logout completed with warnings.")
                    print("  Token file deleted locally.")
                    
            except Exception as e:
                # Si hay error, al menos eliminar token local
                if os.path.exists(config.TOKEN_FILE):
                    os.remove(config.TOKEN_FILE)
                    print(f"\n✓ Token file deleted: {config.TOKEN_FILE}")
                    print("⚠ Could not revoke token on server, but local session is closed.")
                else:
                    print(f"\n✗ Error during logout: {str(e)}")
            
            sys.exit(0)
        
        # Modo: Ver estado de autenticación
        elif args.auth_status:
            print("\n" + "="*60)
            print("AUTHENTICATION STATUS")
            print("="*60 + "\n")
            
            # Verificar configuración
            config_exists = os.path.exists('.env')
            token_exists = os.path.exists(config.TOKEN_FILE)
            
            print(f"Configuration file (.env): {'✓ Found' if config_exists else '✗ Not found'}")
            print(f"Token file ({config.TOKEN_FILE}): {'✓ Found' if token_exists else '✗ Not found'}")
            
            if not config_exists:
                print("\n⚠ OAuth2 credentials not configured.")
                print("   Run: python setup.py")
                sys.exit(0)
            
            if not token_exists:
                print("\nℹ No active session.")
                print("   Run: python main.py --login")
                sys.exit(0)
            
            # Importar y verificar autenticación
            try:
                from youtube_client import YouTubeClient
                config.validate_credentials()
                
                youtube_client = YouTubeClient()
                auth_info = youtube_client.get_auth_info()
                
                print(f"\nAuthentication Status:")
                print(f"  Authenticated: {'✓ Yes' if auth_info['authenticated'] else '✗ No'}")
                print(f"  Token valid: {'✓ Yes' if auth_info['token_valid'] else '✗ No'}")
                print(f"  Token expired: {'⚠ Yes' if auth_info['token_expired'] else '✓ No'}")
                print(f"  Refresh token: {'✓ Available' if auth_info['has_refresh_token'] else '✗ Not available'}")
                
                if auth_info['authenticated'] and auth_info['token_valid']:
                    print("\n✓ You are logged in and ready to use YouTube features.")
                elif auth_info['authenticated'] and auth_info['can_refresh']:
                    print("\n⚠ Token expired but can be refreshed automatically.")
                else:
                    print("\n⚠ Session may need re-authentication.")
                    print("   Run: python main.py --login")
                    
            except Exception as e:
                print(f"\n✗ Error checking authentication: {str(e)}")
                print("   You may need to login again: python main.py --login")
            
            sys.exit(0)
        
        # Modo: Buscar videos (NO requiere autenticación - puede usar API key o OAuth2)
        elif args.search:
            print("\n" + "="*60)
            print("SEARCH YOUTUBE VIDEOS")
            print("="*60 + "\n")
            
            print(f"🔍 Searching for: '{args.search}'")
            print(f"📊 Max results: {args.search_max}")
            print(f"📋 Order: {args.search_order}")
            print()
            
            # Intentar usar API key primero (sin autenticación)
            from youtube_client import YouTubeClient
            
            use_api_key = False
            if config.API_KEY:
                print("ℹ Using API key (no login required)")
                use_api_key = True
                youtube_client = YouTubeClient(auto_authenticate=False)
            elif os.path.exists('.env'):
                # Si hay credenciales OAuth2, usarlas (requiere login)
                try:
                    config.validate_credentials()
                    print("ℹ Using OAuth2 (login may be required)")
                    youtube_client = YouTubeClient()
                except ValueError:
                    print("⚠ No OAuth2 credentials found. Searching without authentication...")
                    print("   Note: Some features may be limited without API key or OAuth2")
                    use_api_key = False
                    youtube_client = YouTubeClient(auto_authenticate=False)
            else:
                print("ℹ No credentials configured. Searching without authentication...")
                print("   Note: For better results, configure YOUTUBE_API_KEY in .env")
                use_api_key = False
                youtube_client = YouTubeClient(auto_authenticate=False)
            
            videos = youtube_client.search_videos(
                query=args.search,
                max_results=args.search_max,
                order=args.search_order,
                use_api_key=use_api_key
            )
            
            if videos:
                print(f"✓ Found {len(videos)} videos:\n")
                for i, video in enumerate(videos, 1):
                    print(f"[{i}] " + "-"*76)
                    print(f"📹 Title: {video['title']}")
                    print(f"👤 Channel: {video['channel_title']}")
                    print(f"🆔 Video ID: {video['video_id']}")
                    print(f"📅 Published: {video['published_at']}")
                    print(f"🔗 URL: {video['url']}")
                    if video.get('description'):
                        desc = video['description'][:100] + "..." if len(video['description']) > 100 else video['description']
                        print(f"📝 Description: {desc}")
                    print()
                
                print(f"\n💡 Tip: Use the Video ID or URL to:")
                print(f"   View stats: python main.py --stats {videos[0]['video_id']}")
                print(f"   Download: python main.py --download-video {videos[0]['url']}")
                print(f"   Comment: python main.py --video-id {videos[0]['video_id']} --comment 'Your comment'")
            else:
                print("✗ No videos found for your search query.")
                sys.exit(1)
            
            sys.exit(0)
        
        # Modo: Reporte de actividad
        elif args.activity_report:
            if MONITORING_AVAILABLE and ActivityMonitor:
                monitor = ActivityMonitor()
                monitor.print_report()
            else:
                print("⚠ Sistema de monitoreo no disponible.")
            sys.exit(0)
        
        # Modo: Descargar video (NO requiere autenticación OAuth2)
        if args.download_video:
            print("\n" + "="*60)
            print("DESCARGADOR DE VIDEOS YOUTUBE")
            print("="*60)
            print("⚠ ADVERTENCIA: Descargar videos puede violar los términos de servicio")
            print("   de YouTube y leyes de derechos de autor. Usa responsablemente.")
            print("="*60 + "\n")
            
            downloader = YouTubeDownloader()
            result = downloader.download_video(args.download_video, args.video_quality)
            
            if result:
                print(f"\n✓ Video descargado exitosamente en: {result}")
            else:
                print("\n✗ Error descargando el video.")
                sys.exit(1)
        
        # Modo: Descargar audio (NO requiere autenticación OAuth2)
        elif args.download_audio:
            print("\n" + "="*60)
            print("DESCARGADOR DE AUDIO YOUTUBE")
            print("="*60)
            print("⚠ ADVERTENCIA: Descargar audio puede violar los términos de servicio")
            print("   de YouTube y leyes de derechos de autor. Usa responsablemente.")
            print("="*60 + "\n")
            
            downloader = YouTubeDownloader()
            result = downloader.download_audio(args.download_audio, args.audio_quality)
            
            if result:
                print(f"\n✓ Audio descargado exitosamente en: {result}")
            else:
                print("\n✗ Error descargando el audio.")
                sys.exit(1)
        
        # Modo: Descargar ambos (NO requiere autenticación OAuth2)
        elif args.download_both:
            print("\n" + "="*60)
            print("DESCARGADOR DE VIDEO Y AUDIO")
            print("="*60)
            print("⚠ ADVERTENCIA: Descargar contenido puede violar los términos de servicio")
            print("   de YouTube y leyes de derechos de autor. Usa responsablemente.")
            print("="*60 + "\n")
            
            downloader = YouTubeDownloader()
            video_path, audio_path = downloader.download_both(
                args.download_both, 
                args.video_quality, 
                args.audio_quality
            )
            
            if video_path and audio_path:
                print(f"\n✓ Video descargado: {video_path}")
                print(f"✓ Audio descargado: {audio_path}")
            else:
                print("\n✗ Error descargando contenido.")
                sys.exit(1)
        
        # Modo: Ver información del video (NO requiere autenticación OAuth2)
        elif args.info:
            print("\n" + "="*60)
            print("INFORMACIÓN DEL VIDEO")
            print("="*60 + "\n")
            
            downloader = YouTubeDownloader()
            info = downloader.get_video_info(args.info)
            
            if info:
                print(f"📹 Título: {info['title']}")
                print(f"👤 Canal: {info['uploader']}")
                print(f"⏱️  Duración: {info['duration']} segundos")
                print(f"👁️  Vistas: {info['view_count']:,}")
                print(f"🆔 ID: {info['id']}")
                print(f"🔗 URL: {info['url']}")
                if info['description']:
                    print(f"📝 Descripción: {info['description']}...")
            else:
                print("✗ Error obteniendo información del video.")
                sys.exit(1)
        
        # Modos que requieren autenticación OAuth2 (estadísticas y comentarios)
        elif args.stats or args.top_comments or args.export_comments:
            # Verificar si existe archivo .env
            if not os.path.exists('.env'):
                print("\n" + "="*70)
                print("⚠ CONFIGURACIÓN REQUERIDA")
                print("="*70)
                print("\nPara usar esta función necesitas configurar credenciales OAuth2.")
                print("\n📋 Opciones de configuración:")
                print("\n1. Configuración interactiva (RECOMENDADO):")
                print("   py setup.py")
                print("\n2. Configuración manual:")
                print("   copy env.example .env")
                print("   # Luego edita .env con tus credenciales de Google Cloud Console")
                print("\n📖 Guía completa: Lee QUICK_START.md")
                print("\n" + "="*70 + "\n")
                sys.exit(1)
            
            # Importar módulos de YouTube API solo cuando se necesiten
            from youtube_client import YouTubeClient
            
            # Validar credenciales antes de inicializar cliente
            try:
                config.validate_credentials()
            except ValueError as e:
                print("\n" + "="*70)
                print("⚠ ERROR DE CONFIGURACIÓN")
                print("="*70)
                print(f"\n{e}")
                print("\n📋 Solución rápida:")
                print("   py setup.py")
                print("\nO edita manualmente el archivo .env con tus credenciales.")
                print("="*70 + "\n")
                sys.exit(1)
            
            # Inicializar cliente de YouTube
            print("Inicializando cliente de YouTube...")
            youtube_client = YouTubeClient()
            
            # Modo: Estadísticas del video
            if args.stats:
                print("\n" + "="*60)
                print("ESTADÍSTICAS DEL VIDEO")
                print("="*60 + "\n")
                
                # Extraer ID del video si es una URL
                video_id = extract_video_id(args.stats)
                if not video_id:
                    print(f"✗ No se pudo extraer el ID del video de: {args.stats}")
                    print("   Asegúrate de usar una URL válida de YouTube o un ID de video.")
                    sys.exit(1)
                
                stats = youtube_client.get_video_stats(video_id)
                
                if stats:
                    print(f"📹 Título: {stats['title']}")
                    print(f"👤 Canal: {stats['channel_title']}")
                    print(f"📅 Publicado: {stats['published_at']}")
                    print(f"⏱️  Duración: {stats['duration_formatted']} ({stats['duration_seconds']} segundos)")
                    print("\n" + "-"*60)
                    print("ESTADÍSTICAS:")
                    print("-"*60)
                    print(f"👁️  Vistas: {stats['view_count']:,}")
                    print(f"👍 Likes: {stats['like_count']:,}")
                    if stats.get('dislike_count', 0) > 0:
                        print(f"👎 Dislikes: {stats['dislike_count']:,}")
                    print(f"💬 Comentarios: {stats['comment_count']:,}")
                    print(f"⭐ Favoritos: {stats['favorite_count']:,}")
                    
                    # Calcular engagement rate si es posible
                    if stats['view_count'] > 0:
                        engagement = ((stats['like_count'] + stats['comment_count']) / stats['view_count']) * 100
                        print(f"\n📊 Engagement Rate: {engagement:.2f}%")
                else:
                    print("✗ Error obteniendo estadísticas del video.")
                    sys.exit(1)
            
            # Modo: Comentarios destacados
            elif args.top_comments:
                print("\n" + "="*60)
                print("COMENTARIOS MÁS DESTACADOS")
                print("="*60 + "\n")
                
                # Extraer ID del video si es una URL
                video_id = extract_video_id(args.top_comments)
                if not video_id:
                    print(f"✗ No se pudo extraer el ID del video de: {args.top_comments}")
                    print("   Asegúrate de usar una URL válida de YouTube o un ID de video.")
                    sys.exit(1)
                
                top_comments = youtube_client.get_top_comments(video_id, max_results=args.max_comments)
                
                if top_comments:
                    print(f"✓ Encontrados {len(top_comments)} comentarios destacados:\n")
                    for i, comment in enumerate(top_comments, 1):
                        print(f"[{i}] " + "-"*76)
                        print(f"👤 Autor: {comment['author']}")
                        print(f"👍 Likes: {comment['like_count']}")
                        if comment.get('reply_count', 0) > 0:
                            print(f"💬 Respuestas: {comment['reply_count']}")
                        print(f"📅 Fecha: {comment['published_at']}")
                        print("-"*80)
                        print(f"{comment['text']}")
                        print()
                else:
                    print("  No se encontraron comentarios.")
            
            # Modo: Exportar comentarios
            elif args.export_comments:
                print("\n" + "="*60)
                print("EXPORTAR COMENTARIOS")
                print("="*60 + "\n")
                
                # Extraer ID del video si es una URL
                video_id = extract_video_id(args.export_comments)
                if not video_id:
                    print(f"✗ No se pudo extraer el ID del video de: {args.export_comments}")
                    print("   Asegúrate de usar una URL válida de YouTube o un ID de video.")
                    sys.exit(1)
                
                # Obtener información del video primero
                stats = youtube_client.get_video_stats(video_id)
                video_title = stats['title'] if stats else None
                
                print(f"📥 Obteniendo comentarios del video: {video_id}")
                if video_title:
                    print(f"📹 Título: {video_title}")
                
                # Obtener todos los comentarios
                comments = youtube_client.get_comments(video_id, max_results=args.max_comments)
                
                if comments:
                    print(f"✓ Obtenidos {len(comments)} comentarios")
                    
                    # Exportar según formato solicitado
                    exporter = CommentExporter()
                    
                    if args.grep_format:
                        filepath = exporter.export_to_grep_format(comments, video_id, video_title)
                        print(f"✓ Comentarios exportados en formato grep: {filepath}")
                    else:
                        filepath = exporter.export_to_text(comments, video_id, video_title)
                        print(f"✓ Comentarios exportados: {filepath}")
                    
                    # Mostrar tamaño del archivo
                    file_size = os.path.getsize(filepath)
                    if file_size < 1024:
                        size_str = f"{file_size} bytes"
                    elif file_size < 1024 * 1024:
                        size_str = f"{file_size / 1024:.2f} KB"
                    else:
                        size_str = f"{file_size / (1024 * 1024):.2f} MB"
                    
                    print(f"📦 Tamaño del archivo: {size_str}")
                else:
                    print("✗ No se encontraron comentarios para exportar.")
                    sys.exit(1)
        
        # Modos que requieren autenticación OAuth2 (comentarios y gestión de comentarios)
        # Solo se autentica cuando realmente se necesita
        elif any([args.comment, args.delete_comment, args.my_comments, args.reply, 
                  args.update_comment, args.comment_replies, args.comment_info, args.monitor]) or \
             (args.video_id and args.comment) or (args.get_comments and args.video_id):
            # Verificar si existe archivo .env
            if not os.path.exists('.env'):
                print("\n" + "="*70)
                print("⚠ CONFIGURACIÓN REQUERIDA")
                print("="*70)
                print("\nPara usar funciones de comentarios necesitas configurar credenciales OAuth2.")
                print("\nOpciones:")
                print("1. Ejecuta el script de configuración interactiva:")
                print("   py setup.py")
                print("\n2. O copia y edita manualmente:")
                print("   copy env.example .env")
                print("   # Luego edita .env con tus credenciales")
                print("\n📖 Guía completa: Lee QUICK_START.md")
                print("\n" + "="*70 + "\n")
                sys.exit(1)
            
            # Importar módulos de YouTube API solo cuando se necesiten
            from youtube_client import YouTubeClient
            from moderator import Moderator
            
            # Mostrar información de seguridad solo cuando se necesita autenticación
            print("\n" + "="*60)
            print("BOT DE YOUTUBE - AUTENTICACIÓN")
            print("="*60)
            print("📝 Usarás tu propia cuenta de Google para comentar")
            print("✓ Solo se solicita acceso a YouTube API")
            print("✓ NO se solicita acceso a email/Gmail")
            print("✓ Los tokens solo permiten acciones en YouTube")
            print("="*60 + "\n")
            # Validar credenciales antes de inicializar cliente
            try:
                config.validate_credentials()
            except ValueError as e:
                print(e)
                sys.exit(1)
            
            # Inicializar cliente de YouTube (la autenticación se hará automáticamente si es necesaria)
            youtube_client = YouTubeClient()
            
            # Modo: Publicar comentario
            if args.video_id and args.comment:
                # Extraer ID del video si es una URL
                video_id = extract_video_id(args.video_id)
                if not video_id:
                    print(f"✗ No se pudo extraer el ID del video de: {args.video_id}")
                    print("   Asegúrate de usar una URL válida de YouTube o un ID de video.")
                    sys.exit(1)
                
                print(f"\n📝 Publicando comentario en video: {video_id}")
                result = youtube_client.comment_video(video_id, args.comment)
                
                if result.get('success'):
                    print("\n✓ Comentario publicado exitosamente!")
                    
                    # Activar moderación si se solicita
                    if args.moderate and config.MODERATION_ENABLED:
                        print("\n🔍 Activando moderación automática...")
                        moderator = Moderator(youtube_client)
                        moderator.monitor_video_comments(video_id)
                else:
                    print(f"\n✗ Error: {result.get('error', 'Error desconocido')}")
                    sys.exit(1)
            
            # Modo: Obtener comentarios
            # Modo: Obtener comentarios (requiere autenticación)
            elif args.video_id and args.get_comments:
                # Extraer ID del video si es una URL
                video_id = extract_video_id(args.video_id)
                if not video_id:
                    print(f"✗ No se pudo extraer el ID del video de: {args.video_id}")
                    print("   Asegúrate de usar una URL válida de YouTube o un ID de video.")
                    sys.exit(1)
                
                print("\n" + "="*60)
                print("COMENTARIOS DEL VIDEO")
                print("="*60 + "\n")
                print(f"📹 Video ID: {video_id}")
                print(f"📋 Obteniendo comentarios...")
                
                # Obtener comentarios con límite configurado
                max_comments = args.max_comments if hasattr(args, 'max_comments') and args.max_comments else 50
                comments = youtube_client.get_comments(video_id, max_results=max_comments)
                
                if comments:
                    print(f"\n✓ Encontrados {len(comments)} comentarios:\n")
                    for i, comment in enumerate(comments, 1):
                        print(f"[{i}] " + "-"*76)
                        print(f"🆔 ID del Comentario: {comment['id']}")
                        print(f"👤 Autor: {comment['author']}")
                        print(f"👍 Likes: {comment['like_count']}")
                        if comment.get('reply_count', 0) > 0:
                            print(f"💬 Respuestas: {comment['reply_count']}")
                        print(f"📅 Fecha: {comment['published_at']}")
                        if comment.get('author_channel_id'):
                            print(f"📺 Canal ID: {comment['author_channel_id']}")
                        print("-"*80)
                        print(f"{comment['text']}")
                        print()
                    
                    print(f"\n💡 Tip: Usa el ID del comentario para responder o eliminarlo:")
                    print(f"   Responder: py main.py --reply {comments[0]['id']} --reply-text 'Tu respuesta'")
                    print(f"   Ver respuestas: py main.py --comment-replies {comments[0]['id']}")
                    print(f"   Ver info: py main.py --comment-info {comments[0]['id']}")
                else:
                    print("  No se encontraron comentarios.")
            
            # Modo: Eliminar comentario
            elif args.delete_comment:
                print("\n" + "="*60)
                print("ELIMINAR COMENTARIO")
                print("="*60 + "\n")
                
                print(f"🗑️  Eliminando comentario: {args.delete_comment}")
                confirm = input("¿Estás seguro? (s/n): ").strip().lower()
                
                if confirm == 's':
                    success = youtube_client.delete_comment(args.delete_comment)
                    if success:
                        print("\n✓ Comentario eliminado exitosamente.")
                    else:
                        print("\n✗ Error eliminando comentario.")
                        sys.exit(1)
                else:
                    print("✗ Operación cancelada.")
            
            # Modo: Listar mis comentarios
            elif args.my_comments:
                print("\n" + "="*60)
                print("MIS COMENTARIOS")
                print("="*60 + "\n")
                
                if args.my_comments == 'all':
                    print("📝 Obteniendo todos tus comentarios...")
                    comments = youtube_client.get_my_comments()
                else:
                    # Extraer ID del video si es una URL
                    video_id = extract_video_id(args.my_comments)
                    if not video_id:
                        print(f"✗ No se pudo extraer el ID del video de: {args.my_comments}")
                        sys.exit(1)
                    
                    print(f"📝 Obteniendo tus comentarios en el video: {video_id}")
                    comments = youtube_client.get_my_comments(video_id)
                
                if comments:
                    print(f"\n✓ Encontrados {len(comments)} de tus comentarios:\n")
                    for i, comment in enumerate(comments, 1):
                        print(f"[{i}] " + "-"*76)
                        print(f"📹 Video ID: {comment.get('video_id', 'N/A')}")
                        print(f"💬 Comentario ID: {comment['id']}")
                        print(f"👍 Likes: {comment['like_count']}")
                        if comment.get('reply_count', 0) > 0:
                            print(f"💬 Respuestas: {comment['reply_count']}")
                        print(f"📅 Fecha: {comment['published_at']}")
                        print("-"*80)
                        print(f"{comment['text']}")
                        print()
                else:
                    print("  No se encontraron comentarios tuyos.")
            
            # Modo: Responder a comentario
            elif args.reply:
                if not args.reply_text:
                    print("✗ Error: --reply-text es requerido cuando usas --reply")
                    print("   Ejemplo: py main.py --reply COMMENT_ID --reply-text 'Tu respuesta'")
                    sys.exit(1)
                
                print("\n" + "="*60)
                print("RESPONDER A COMENTARIO")
                print("="*60 + "\n")
                
                print(f"💬 Respondiendo al comentario: {args.reply}")
                print(f"📝 Texto: {args.reply_text}")
                
                result = youtube_client.reply_to_comment(args.reply, args.reply_text)
                
                if result.get('success'):
                    print("\n✓ Respuesta publicada exitosamente!")
                else:
                    print(f"\n✗ Error: {result.get('error', 'Error desconocido')}")
                    sys.exit(1)
            
            # Modo: Actualizar comentario
            elif args.update_comment:
                if not args.new_text:
                    print("✗ Error: --new-text es requerido cuando usas --update-comment")
                    print("   Ejemplo: py main.py --update-comment COMMENT_ID --new-text 'Nuevo texto'")
                    sys.exit(1)
                
                print("\n" + "="*60)
                print("ACTUALIZAR COMENTARIO")
                print("="*60 + "\n")
                
                print(f"✏️  Actualizando comentario: {args.update_comment}")
                print(f"📝 Nuevo texto: {args.new_text}")
                
                result = youtube_client.update_comment(args.update_comment, args.new_text)
                
                if result.get('success'):
                    print("\n✓ Comentario actualizado exitosamente!")
                else:
                    print(f"\n✗ Error: {result.get('error', 'Error desconocido')}")
                    sys.exit(1)
            
            # Modo: Obtener respuestas de un comentario
            elif args.comment_replies:
                print("\n" + "="*60)
                print("RESPUESTAS DEL COMENTARIO")
                print("="*60 + "\n")
                
                print(f"💬 Obteniendo respuestas del comentario: {args.comment_replies}")
                replies = youtube_client.get_comment_replies(args.comment_replies)
                
                if replies:
                    print(f"\n✓ Encontradas {len(replies)} respuestas:\n")
                    for i, reply in enumerate(replies, 1):
                        print(f"[{i}] " + "-"*76)
                        print(f"👤 Autor: {reply['author']}")
                        print(f"👍 Likes: {reply['like_count']}")
                        print(f"📅 Fecha: {reply['published_at']}")
                        print(f"🆔 ID: {reply['id']}")
                        print("-"*80)
                        print(f"{reply['text']}")
                        print()
                else:
                    print("  No se encontraron respuestas.")
            
            # Modo: Información de comentario
            elif args.comment_info:
                print("\n" + "="*60)
                print("INFORMACIÓN DEL COMENTARIO")
                print("="*60 + "\n")
                
                print(f"📋 Obteniendo información del comentario: {args.comment_info}")
                info = youtube_client.get_comment_info(args.comment_info)
                
                if info:
                    print(f"\n📝 Texto: {info['text']}")
                    print(f"👤 Autor: {info['author']}")
                    print(f"🆔 ID: {info['id']}")
                    print(f"👍 Likes: {info['like_count']}")
                    print(f"📅 Publicado: {info['published_at']}")
                    if info.get('updated_at'):
                        print(f"✏️  Actualizado: {info['updated_at']}")
                    if info.get('author_channel_id'):
                        print(f"📺 Canal del autor: {info['author_channel_id']}")
                else:
                    print("✗ No se pudo obtener información del comentario.")
                    sys.exit(1)
            
            # Modo: Monitoreo continuo
            elif args.monitor and args.video_id:
                # Extraer ID del video si es una URL
                video_id = extract_video_id(args.video_id)
                if not video_id:
                    print(f"✗ No se pudo extraer el ID del video de: {args.video_id}")
                    print("   Asegúrate de usar una URL válida de YouTube o un ID de video.")
                    sys.exit(1)
                
                if not config.MODERATION_ENABLED:
                    print("⚠ Moderación deshabilitada en configuración.")
                    sys.exit(1)
                
                moderator = Moderator(youtube_client)
                moderator.start_monitoring([video_id])
            
            # Modo interactivo (solo si no se proporcionó ningún argumento)
            elif not any([getattr(args, 'video_id', None), getattr(args, 'comment', None), 
                          getattr(args, 'moderate', None), getattr(args, 'monitor', None), 
                          getattr(args, 'get_comments', None), getattr(args, 'delete_comment', None),
                          getattr(args, 'my_comments', None), getattr(args, 'reply', None),
                          getattr(args, 'update_comment', None), getattr(args, 'comment_replies', None),
                          getattr(args, 'comment_info', None), getattr(args, 'stats', None),
                          getattr(args, 'top_comments', None), getattr(args, 'export_comments', None),
                          getattr(args, 'search', None), getattr(args, 'download_metadata', None)]):
                print("\n" + "="*60)
                print("MODO INTERACTIVO")
                print("="*60)
                print("\nOpciones disponibles:")
                print("1. Comentar en un video")
                print("2. Descargar video MP4")
                print("3. Descargar audio MP3")
                print("4. Ver información de un video")
                print("5. Descargar metadatos de un video")
                print("6. Obtener comentarios de un video")
                print("7. Ver estadísticas de un video")
                print("8. Ver comentarios destacados")
                print("9. Exportar comentarios")
                print("10. Listar mis comentarios")
                print("11. Eliminar un comentario")
                print("12. Responder a un comentario")
                print("13. Actualizar un comentario")
                print("14. View comment replies")
                print("15. View comment information")
                print("16. Login / Authenticate")
                print("17. Logout")
                print("18. Check authentication status")
                print("19. Search YouTube videos")
                print("20. Exit")
                
                option = input("\nSelect an option (1-20): ").strip()
                
                if option == '1':
                    video_id = input("\nIngresa el ID del video: ").strip()
                    if not video_id:
                        print("✗ ID de video requerido.")
                        sys.exit(1)
                    
                    comment_text = input("Ingresa el texto del comentario: ").strip()
                    if not comment_text:
                        print("✗ Texto del comentario requerido.")
                        sys.exit(1)
                    
                    print(f"\n📝 Publicando comentario...")
                    result = youtube_client.comment_video(video_id, comment_text)
                    
                    if result.get('success'):
                        print("\n✓ Comentario publicado exitosamente!")
                        
                        if config.MODERATION_ENABLED:
                            moderate = input("\n¿Activar moderación automática? (s/n): ").strip().lower()
                            if moderate == 's':
                                moderator = Moderator(youtube_client)
                                moderator.monitor_video_comments(video_id)
                    else:
                        print(f"\n✗ Error: {result.get('error', 'Error desconocido')}")
                        sys.exit(1)
                
                elif option == '2':
                    url = input("\nIngresa la URL del video: ").strip()
                    if not url:
                        print("✗ URL requerida.")
                        sys.exit(1)
                    
                    print("\n⚠ ADVERTENCIA: Descargar videos puede violar términos de servicio.")
                    downloader = YouTubeDownloader()
                    result = downloader.download_video(url)
                    if result:
                        print(f"\n✓ Video descargado: {result}")
                
                elif option == '3':
                    url = input("\nIngresa la URL del video: ").strip()
                    if not url:
                        print("✗ URL requerida.")
                        sys.exit(1)
                    
                    print("\n⚠ ADVERTENCIA: Descargar audio puede violar términos de servicio.")
                    downloader = YouTubeDownloader()
                    result = downloader.download_audio(url)
                    if result:
                        print(f"\n✓ Audio descargado: {result}")
                
                elif option == '4':
                    url = input("\nIngresa la URL del video: ").strip()
                    if not url:
                        print("✗ URL requerida.")
                        sys.exit(1)
                    
                    downloader = YouTubeDownloader()
                    info = downloader.get_video_info(url)
                    if info:
                        print(f"\n📹 Título: {info['title']}")
                        print(f"👤 Canal: {info['uploader']}")
                        print(f"⏱️  Duración: {info['duration']} segundos")
                        print(f"👁️  Vistas: {info['view_count']:,}")
                
                elif option == '5':
                    video_id_or_url = input("\nIngresa el ID o URL del video: ").strip()
                    video_id = extract_video_id(video_id_or_url)
                    if not video_id:
                        print("✗ ID de video requerido o URL inválida.")
                        sys.exit(1)
                    
                    max_comments_str = input("Número máximo de comentarios a mostrar (default 50): ").strip()
                    max_comments = int(max_comments_str) if max_comments_str.isdigit() else 50
                    
                    print("\n" + "="*60)
                    print("COMENTARIOS DEL VIDEO")
                    print("="*60 + "\n")
                    print(f"📹 Video ID: {video_id}")
                    print(f"📋 Obteniendo comentarios...")
                    
                    comments = youtube_client.get_comments(video_id, max_results=max_comments)
                    if comments:
                        print(f"\n✓ Encontrados {len(comments)} comentarios:\n")
                        for i, comment in enumerate(comments, 1):
                            print(f"[{i}] " + "-"*76)
                            print(f"🆔 ID del Comentario: {comment['id']}")
                            print(f"👤 Autor: {comment['author']}")
                            print(f"👍 Likes: {comment['like_count']}")
                            if comment.get('reply_count', 0) > 0:
                                print(f"💬 Respuestas: {comment['reply_count']}")
                            print(f"📅 Fecha: {comment['published_at']}")
                            if comment.get('author_channel_id'):
                                print(f"📺 Canal ID: {comment['author_channel_id']}")
                            print("-"*80)
                            print(f"{comment['text']}")
                            print()
                        
                        print(f"\n💡 Tip: Usa el ID del comentario para:")
                        print(f"   Responder: py main.py --reply {comments[0]['id']} --reply-text 'Tu respuesta'")
                        print(f"   Ver respuestas: py main.py --comment-replies {comments[0]['id']}")
                        print(f"   Ver info: py main.py --comment-info {comments[0]['id']}")
                    else:
                        print("  No se encontraron comentarios.")
                
                elif option == '6':
                    video_id_or_url = input("\nIngresa el ID o URL del video: ").strip()
                    video_id = extract_video_id(video_id_or_url)
                    if not video_id:
                        print("✗ ID de video requerido o URL inválida.")
                        sys.exit(1)
                    
                    max_comments_str = input("Número máximo de comentarios a mostrar (default 50): ").strip()
                    max_comments = int(max_comments_str) if max_comments_str.isdigit() else 50
                    
                    print("\n" + "="*60)
                    print("COMENTARIOS DEL VIDEO")
                    print("="*60 + "\n")
                    print(f"📹 Video ID: {video_id}")
                    print(f"📋 Obteniendo comentarios...")
                    
                    comments = youtube_client.get_comments(video_id, max_results=max_comments)
                    if comments:
                        print(f"\n✓ Encontrados {len(comments)} comentarios:\n")
                        for i, comment in enumerate(comments, 1):
                            print(f"[{i}] " + "-"*76)
                            print(f"🆔 ID del Comentario: {comment['id']}")
                            print(f"👤 Autor: {comment['author']}")
                            print(f"👍 Likes: {comment['like_count']}")
                            if comment.get('reply_count', 0) > 0:
                                print(f"💬 Respuestas: {comment['reply_count']}")
                            print(f"📅 Fecha: {comment['published_at']}")
                            if comment.get('author_channel_id'):
                                print(f"📺 Canal ID: {comment['author_channel_id']}")
                            print("-"*80)
                            print(f"{comment['text']}")
                            print()
                        
                        print(f"\n💡 Tip: Usa el ID del comentario para:")
                        print(f"   Responder: py main.py --reply {comments[0]['id']} --reply-text 'Tu respuesta'")
                        print(f"   Ver respuestas: py main.py --comment-replies {comments[0]['id']}")
                        print(f"   Ver info: py main.py --comment-info {comments[0]['id']}")
                    else:
                        print("  No se encontraron comentarios.")
                
                elif option == '7':
                    video_id_or_url = input("\nIngresa el ID o URL del video: ").strip()
                    video_id = extract_video_id(video_id_or_url)
                    if not video_id:
                        print("✗ ID de video requerido o URL inválida.")
                        sys.exit(1)
                    
                    stats = youtube_client.get_video_stats(video_id)
                    if stats:
                        print(f"\n📹 Título: {stats['title']}")
                        print(f"👤 Canal: {stats['channel_title']}")
                        print(f"📅 Publicado: {stats['published_at']}")
                        print(f"⏱️  Duración: {stats['duration_formatted']}")
                        print(f"👁️  Vistas: {stats['view_count']:,}")
                        print(f"👍 Likes: {stats['like_count']:,}")
                        print(f"💬 Comentarios: {stats['comment_count']:,}")
                        if stats['view_count'] > 0:
                            engagement = ((stats['like_count'] + stats['comment_count']) / stats['view_count']) * 100
                            print(f"\n📊 Engagement Rate: {engagement:.2f}%")
                    else:
                        print("✗ Error obteniendo estadísticas del video.")
                
                elif option == '8':
                    video_id_or_url = input("\nIngresa el ID o URL del video: ").strip()
                    video_id = extract_video_id(video_id_or_url)
                    if not video_id:
                        print("✗ ID de video requerido o URL inválida.")
                        sys.exit(1)
                    
                    max_comments_str = input("Número máximo de comentarios (default 10): ").strip()
                    max_comments = int(max_comments_str) if max_comments_str.isdigit() else 10
                    top_comments = youtube_client.get_top_comments(video_id, max_comments=max_comments)
                    if top_comments:
                        print(f"✓ Encontrados {len(top_comments)} comentarios destacados:\n")
                        for i, comment in enumerate(top_comments, 1):
                            print(f"[{i}] " + "-"*76)
                            print(f"👤 Autor: {comment['author']}")
                            print(f"👍 Likes: {comment['like_count']}")
                            print(f"🆔 ID: {comment['id']}")
                            print("-"*80)
                            print(f"{comment['text']}")
                            print()
                    else:
                        print("  No se encontraron comentarios.")
                
                elif option == '8':
                    video_id_or_url = input("\nIngresa el ID o URL del video: ").strip()
                    video_id = extract_video_id(video_id_or_url)
                    if not video_id:
                        print("✗ ID de video requerido o URL inválida.")
                        sys.exit(1)
                    
                    max_comments_str = input("Número máximo de comentarios (default 1000): ").strip()
                    max_comments = int(max_comments_str) if max_comments_str.isdigit() else 1000
                    grep_format_str = input("¿Exportar en formato grep? (s/n): ").strip().lower()
                    grep_format = (grep_format_str == 's')

                    stats = youtube_client.get_video_stats(video_id)
                    video_title = stats['title'] if stats else None
                    
                    comments = youtube_client.get_comments(video_id, max_results=max_comments)
                    
                    if comments:
                        print(f"✓ Obtenidos {len(comments)} comentarios")
                        exporter = CommentExporter()
                        file_path = exporter.export_comments_to_file(
                            video_id=video_id,
                            video_title=video_title,
                            comments=comments,
                            grep_format=grep_format
                        )
                        if file_path:
                            print(f"\n✓ Comentarios exportados exitosamente a: {file_path}")
                        else:
                            print("✗ Error exportando comentarios.")
                    else:
                        print("  No se encontraron comentarios para exportar.")
                
                elif option == '9':
                    video_id_or_url = input("\nIngresa el ID o URL del video: ").strip()
                    video_id = extract_video_id(video_id_or_url)
                    if not video_id:
                        print("✗ ID de video requerido o URL inválida.")
                        sys.exit(1)
                    
                    max_comments_str = input("Número máximo de comentarios (default 1000): ").strip()
                    max_comments = int(max_comments_str) if max_comments_str.isdigit() else 1000
                    grep_format_str = input("¿Exportar en formato grep? (s/n): ").strip().lower()
                    grep_format = (grep_format_str == 's')

                    stats = youtube_client.get_video_stats(video_id)
                    video_title = stats['title'] if stats else None
                    
                    comments = youtube_client.get_comments(video_id, max_results=max_comments)
                    
                    if comments:
                        print(f"✓ Obtenidos {len(comments)} comentarios")
                        exporter = CommentExporter()
                        file_path = exporter.export_comments_to_file(
                            video_id=video_id,
                            video_title=video_title,
                            comments=comments,
                            grep_format=grep_format
                        )
                        if file_path:
                            print(f"\n✓ Comentarios exportados exitosamente a: {file_path}")
                        else:
                            print("✗ Error exportando comentarios.")
                    else:
                        print("  No se encontraron comentarios para exportar.")
                
                elif option == '10':
                    video_id_or_url = input("\nIngresa el ID o URL del video (o Enter para todos): ").strip()
                    if video_id_or_url:
                        video_id = extract_video_id(video_id_or_url)
                        if not video_id:
                            print("✗ URL inválida.")
                            sys.exit(1)
                        comments = youtube_client.get_my_comments(video_id)
                        print(f"\n📝 Tus comentarios en el video {video_id}:")
                    else:
                        comments = youtube_client.get_my_comments()
                        print(f"\n📝 Todos tus comentarios:")
                    
                    if comments:
                        print(f"\n✓ Encontrados {len(comments)} comentarios:\n")
                        for i, comment in enumerate(comments, 1):
                            print(f"[{i}] " + "-"*76)
                            print(f"📹 Video ID: {comment.get('video_id', 'N/A')}")
                            print(f"💬 Comentario ID: {comment['id']}")
                            print(f"👍 Likes: {comment['like_count']}")
                            print(f"📅 Fecha: {comment['published_at']}")
                            print("-"*80)
                            print(f"{comment['text']}")
                            print()
                    else:
                        print("  No se encontraron comentarios tuyos.")
                
                elif option == '11':
                    comment_id = input("\nIngresa el ID del comentario a eliminar: ").strip()
                    if not comment_id:
                        print("✗ ID de comentario requerido.")
                        sys.exit(1)
                    
                    confirm = input("¿Estás seguro de eliminar este comentario? (s/n): ").strip().lower()
                    if confirm == 's':
                        success = youtube_client.delete_comment(comment_id)
                        if success:
                            print("\n✓ Comentario eliminado exitosamente.")
                        else:
                            print("\n✗ Error eliminando comentario.")
                    else:
                        print("✗ Operación cancelada.")
                
                elif option == '11':
                    comment_id = input("\nIngresa el ID del comentario al que responder: ").strip()
                    if not comment_id:
                        print("✗ ID de comentario requerido.")
                        sys.exit(1)
                    
                    reply_text = input("Ingresa el texto de la respuesta: ").strip()
                    if not reply_text:
                        print("✗ Texto de respuesta requerido.")
                        sys.exit(1)
                    
                    result = youtube_client.reply_to_comment(comment_id, reply_text)
                    if result.get('success'):
                        print("\n✓ Respuesta publicada exitosamente!")
                    else:
                        print(f"\n✗ Error: {result.get('error', 'Error desconocido')}")
                
                elif option == '12':
                    comment_id = input("\nIngresa el ID del comentario a actualizar: ").strip()
                    if not comment_id:
                        print("✗ ID de comentario requerido.")
                        sys.exit(1)
                    
                    new_text = input("Ingresa el nuevo texto del comentario: ").strip()
                    if not new_text:
                        print("✗ Nuevo texto requerido.")
                        sys.exit(1)
                    
                    result = youtube_client.update_comment(comment_id, new_text)
                    if result.get('success'):
                        print("\n✓ Comentario actualizado exitosamente!")
                    else:
                        print(f"\n✗ Error: {result.get('error', 'Error desconocido')}")
                
                elif option == '13':
                    comment_id = input("\nIngresa el ID del comentario: ").strip()
                    if not comment_id:
                        print("✗ ID de comentario requerido.")
                        sys.exit(1)
                    
                    replies = youtube_client.get_comment_replies(comment_id)
                    if replies:
                        print(f"\n✓ Encontradas {len(replies)} respuestas:\n")
                        for i, reply in enumerate(replies, 1):
                            print(f"[{i}] " + "-"*76)
                            print(f"👤 Autor: {reply['author']}")
                            print(f"👍 Likes: {reply['like_count']}")
                            print(f"🆔 ID: {reply['id']}")
                            print("-"*80)
                            print(f"{reply['text']}")
                            print()
                    else:
                        print("  No se encontraron respuestas.")
                
                elif option == '14':
                    comment_id = input("\nIngresa el ID del comentario: ").strip()
                    if not comment_id:
                        print("✗ ID de comentario requerido.")
                        sys.exit(1)
                    
                    info = youtube_client.get_comment_info(comment_id)
                    if info:
                        print(f"\n📝 Texto: {info['text']}")
                        print(f"👤 Autor: {info['author']}")
                        print(f"🆔 ID: {info['id']}")
                        print(f"👍 Likes: {info['like_count']}")
                        print(f"📅 Publicado: {info['published_at']}")
                        if info.get('updated_at'):
                            print(f"✏️  Actualizado: {info['updated_at']}")
                    else:
                        print("✗ No se pudo obtener información del comentario.")
                
                elif option == '15':
                    comment_id = input("\nEnter comment ID: ").strip()
                    if not comment_id:
                        print("✗ Comment ID required.")
                        sys.exit(1)
                    
                    info = youtube_client.get_comment_info(comment_id)
                    if info:
                        print(f"\n📝 Text: {info['text']}")
                        print(f"👤 Author: {info['author']}")
                        print(f"🆔 ID: {info['id']}")
                        print(f"👍 Likes: {info['like_count']}")
                        print(f"📅 Published: {info['published_at']}")
                        if info.get('updated_at'):
                            print(f"✏️  Updated: {info['updated_at']}")
                    else:
                        print("✗ Could not get comment information.")
                
                elif option == '16':
                    # Verificar si existe archivo .env
                    if not os.path.exists('.env'):
                        print("\n⚠ OAuth2 credentials not configured.")
                        print("   Run: python setup.py")
                        sys.exit(1)
                    
                    try:
                        config.validate_credentials()
                    except ValueError as e:
                        print(f"\n⚠ Configuration error: {e}")
                        print("   Run: python setup.py")
                        sys.exit(1)
                    
                    print("\n" + "="*60)
                    print("LOGIN / AUTHENTICATION")
                    print("="*60)
                    print("\n📝 You will use your personal Google account")
                    print("✓ Only YouTube API access will be requested")
                    print("="*60 + "\n")
                    
                    print("Initializing YouTube client...")
                    youtube_client = YouTubeClient()
                    
                    auth_info = youtube_client.get_auth_info()
                    if auth_info['authenticated']:
                        print("\n✓ Login successful!")
                        print("You can now use all YouTube features.")
                    else:
                        print("\n⚠ Authentication completed.")
                
                elif option == '17':
                    token_exists = os.path.exists(config.TOKEN_FILE)
                    
                    if not token_exists:
                        print("\nℹ No active session found.")
                        print("You are already logged out.")
                        sys.exit(0)
                    
                    confirm = input("\nAre you sure you want to logout? (y/n): ").strip().lower()
                    
                    if confirm not in ['y', 'yes']:
                        print("✗ Logout cancelled.")
                        sys.exit(0)
                    
                    try:
                        config.validate_credentials()
                        youtube_client = YouTubeClient()
                        success = youtube_client.logout()
                        
                        if success:
                            print("\n✓ Logout successful!")
                        else:
                            print("\n⚠ Logout completed with warnings.")
                    except Exception as e:
                        if os.path.exists(config.TOKEN_FILE):
                            os.remove(config.TOKEN_FILE)
                            print(f"\n✓ Token file deleted.")
                        else:
                            print(f"\n✗ Error: {str(e)}")
                
                elif option == '18':
                    print("\n" + "="*60)
                    print("AUTHENTICATION STATUS")
                    print("="*60 + "\n")
                    
                    config_exists = os.path.exists('.env')
                    token_exists = os.path.exists(config.TOKEN_FILE)
                    
                    print(f"Configuration file (.env): {'✓ Found' if config_exists else '✗ Not found'}")
                    print(f"Token file: {'✓ Found' if token_exists else '✗ Not found'}")
                    
                    if not config_exists:
                        print("\n⚠ OAuth2 credentials not configured.")
                        print("   Run: python setup.py")
                        sys.exit(0)
                    
                    if not token_exists:
                        print("\nℹ No active session.")
                        print("   Select option 16 to login.")
                        sys.exit(0)
                    
                    try:
                        config.validate_credentials()
                        youtube_client = YouTubeClient()
                        auth_info = youtube_client.get_auth_info()
                        
                        print(f"\nAuthentication Status:")
                        print(f"  Authenticated: {'✓ Yes' if auth_info['authenticated'] else '✗ No'}")
                        print(f"  Token valid: {'✓ Yes' if auth_info['token_valid'] else '✗ No'}")
                        print(f"  Token expired: {'⚠ Yes' if auth_info['token_expired'] else '✓ No'}")
                        print(f"  Refresh token: {'✓ Available' if auth_info['has_refresh_token'] else '✗ Not available'}")
                        
                        if auth_info['authenticated'] and auth_info['token_valid']:
                            print("\n✓ You are logged in and ready to use YouTube features.")
                        elif auth_info['authenticated'] and auth_info.get('can_refresh'):
                            print("\n⚠ Token expired but can be refreshed automatically.")
                        else:
                            print("\n⚠ Session may need re-authentication.")
                            print("   Select option 16 to login.")
                    except Exception as e:
                        print(f"\n✗ Error checking authentication: {str(e)}")
                        print("   Select option 16 to login.")
                
                elif option == '19':
                    print("Exiting...")
                    sys.exit(0)
                
                else:
                    print("✗ Invalid option.")
                    sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n✓ Operación cancelada por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
