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
  # Comentar
  python main.py --video-id dQw4w9WgXcQ --comment "¡Excelente video!"
  
  # Descargar video MP4
  python main.py --download-video "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  
  # Descargar audio MP3
  python main.py --download-audio "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  
  # Ver información del video
  python main.py --info "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
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
    
    args = parser.parse_args()
    
    # Modo: Generar nombres de cuenta
    if args.generate_account:
        from generate_account import main as generate_main
        generate_main()
        sys.exit(0)
    
    # Verificar si necesita configuración
    if not os.path.exists('.env'):
        print("\n" + "="*70)
        print("⚠ CONFIGURACIÓN REQUERIDA")
        print("="*70)
        print("\nPara usar funciones de comentarios/estadísticas necesitas configurar credenciales.")
        print("\nOpciones:")
        print("1. Ejecuta el script de configuración interactiva:")
        print("   py setup.py")
        print("\n2. O copia y edita manualmente:")
        print("   copy env.example .env")
        print("   # Luego edita .env con tus credenciales")
        print("\n3. O usa solo funciones de descarga (no requieren configuración):")
        print("   py main.py --download-video URL")
        print("   py main.py --info URL")
        print("\n" + "="*70 + "\n")
        
        # Si solo está usando funciones que no requieren auth, continuar
        if not any([args.stats, args.top_comments, args.export_comments, 
                   args.video_id, args.comment, args.monitor, args.get_comments]):
            sys.exit(0)
        else:
            sys.exit(1)
    
    try:
        # Modo: Reporte de actividad
        if args.activity_report:
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
        
        # Modos que requieren autenticación OAuth2 (comentarios)
        else:
            # Mostrar información de seguridad solo cuando se necesita autenticación
            print("\n" + "="*60)
            print("BOT DE YOUTUBE - PROTECCIÓN DE CUENTA")
            print("="*60)
            print("✓ Solo se solicita acceso a YouTube API")
            print("✓ NO se solicita acceso a email/Gmail")
            print("✓ Los tokens solo permiten acciones en YouTube")
            print("="*60 + "\n")
            # Inicializar cliente de YouTube
            print("Inicializando cliente de YouTube...")
            youtube_client = YouTubeClient()
            
            # Modo: Publicar comentario
        if args.video_id and args.comment:
            print(f"\n📝 Publicando comentario en video: {args.video_id}")
            result = youtube_client.comment_video(args.video_id, args.comment)
            
            if result.get('success'):
                print("\n✓ Comentario publicado exitosamente!")
                
                # Activar moderación si se solicita
                if args.moderate and config.MODERATION_ENABLED:
                    print("\n🔍 Activando moderación automática...")
                    moderator = Moderator(youtube_client)
                    moderator.monitor_video_comments(args.video_id)
            else:
                print(f"\n✗ Error: {result.get('error', 'Error desconocido')}")
                sys.exit(1)
        
        # Modo: Obtener comentarios
        elif args.video_id and args.get_comments:
            print(f"\n📋 Obteniendo comentarios del video: {args.video_id}")
            comments = youtube_client.get_comments(args.video_id)
            
            if comments:
                print(f"\n✓ Encontrados {len(comments)} comentarios:")
                for i, comment in enumerate(comments[:10], 1):  # Mostrar primeros 10
                    print(f"\n{i}. {comment['text'][:50]}...")
                    print(f"   Autor: {comment['author']}")
                    print(f"   Likes: {comment['like_count']}")
            else:
                print("  No se encontraron comentarios.")
        
        # Modo: Monitoreo continuo
        elif args.monitor and args.video_id:
            if not config.MODERATION_ENABLED:
                print("⚠ Moderación deshabilitada en configuración.")
                sys.exit(1)
            
            moderator = Moderator(youtube_client)
            moderator.start_monitoring([args.video_id])
        
        # Modo interactivo (solo si no se proporcionó ningún argumento)
        elif not any([args.video_id, args.comment, args.moderate, args.monitor, args.get_comments]):
            print("\n" + "="*60)
            print("MODO INTERACTIVO")
            print("="*60)
            print("\nOpciones disponibles:")
            print("1. Comentar en un video")
            print("2. Descargar video MP4")
            print("3. Descargar audio MP3")
            print("4. Ver información de un video")
            print("5. Obtener comentarios de un video")
            
            option = input("\nSelecciona una opción (1-5): ").strip()
            
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
                video_id = input("\nIngresa el ID del video: ").strip()
                if not video_id:
                    print("✗ ID de video requerido.")
                    sys.exit(1)
                
                from youtube_client import YouTubeClient
                config.validate_credentials()
                youtube_client = YouTubeClient()
                
                stats = youtube_client.get_video_stats(video_id)
                if stats:
                    print(f"\n📹 Título: {stats['title']}")
                    print(f"👁️  Vistas: {stats['view_count']:,}")
                    print(f"👍 Likes: {stats['like_count']:,}")
                    print(f"💬 Comentarios: {stats['comment_count']:,}")
            
            elif option == '6':
                video_id = input("\nIngresa el ID del video: ").strip()
                if not video_id:
                    print("✗ ID de video requerido.")
                    sys.exit(1)
                
                from youtube_client import YouTubeClient
                config.validate_credentials()
                youtube_client = YouTubeClient()
                
                top_comments = youtube_client.get_top_comments(video_id, max_results=10)
                if top_comments:
                    print(f"\n✓ Top {len(top_comments)} comentarios destacados:")
                    for i, comment in enumerate(top_comments, 1):
                        print(f"\n[{i}] {comment['author']} ({comment['like_count']} likes)")
                        print(f"    {comment['text'][:100]}...")
            
            elif option == '7':
                video_id = input("\nIngresa el ID del video: ").strip()
                if not video_id:
                    print("✗ ID de video requerido.")
                    sys.exit(1)
                
                from youtube_client import YouTubeClient
                from comment_exporter import CommentExporter
                config.validate_credentials()
                youtube_client = YouTubeClient()
                
                max_comments = input("Número máximo de comentarios (default: 1000): ").strip()
                max_comments = int(max_comments) if max_comments.isdigit() else 1000
                
                grep_format = input("¿Usar formato grep? (s/n, default: n): ").strip().lower() == 's'
                
                stats = youtube_client.get_video_stats(video_id)
                video_title = stats['title'] if stats else None
                
                comments = youtube_client.get_comments(video_id, max_results=max_comments)
                if comments:
                    exporter = CommentExporter()
                    if grep_format:
                        filepath = exporter.export_to_grep_format(comments, video_id, video_title)
                    else:
                        filepath = exporter.export_to_text(comments, video_id, video_title)
                    print(f"\n✓ Comentarios exportados: {filepath}")
            
            elif option == '8':
                video_id = input("\nIngresa el ID del video: ").strip()
                if not video_id:
                    print("✗ ID de video requerido.")
                    sys.exit(1)
                
                from youtube_client import YouTubeClient
                config.validate_credentials()
                youtube_client = YouTubeClient()
                
                comments = youtube_client.get_comments(video_id)
                if comments:
                    print(f"\n✓ Encontrados {len(comments)} comentarios:")
                    for i, comment in enumerate(comments[:10], 1):
                        print(f"\n{i}. {comment['text'][:50]}...")
                        print(f"   Autor: {comment['author']}")
                        print(f"   Likes: {comment['like_count']}")
                else:
                    print("  No se encontraron comentarios.")
            
            else:
                print("✗ Opción inválida.")
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n✓ Operación cancelada por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
