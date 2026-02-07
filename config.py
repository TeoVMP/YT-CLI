"""
Configuración del bot de YouTube.
Maneja credenciales y configuración de forma segura.
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Scopes OAuth2 - SOLO YouTube, SIN acceso a email/Gmail
# Esto protege la cuenta: solo permite acceso a YouTube API
YOUTUBE_SCOPES = [
    'https://www.googleapis.com/auth/youtube.force-ssl',  # Comentar y gestionar comentarios
]

# NO incluir estos scopes (protección del email):
# 'https://www.googleapis.com/auth/gmail.readonly'
# 'https://mail.google.com/'
# 'https://www.googleapis.com/auth/gmail.modify'

# Credenciales OAuth2
# Limpiar Client ID si viene con https:// o http://
raw_client_id = os.getenv('GOOGLE_CLIENT_ID', '')
if raw_client_id:
    # Remover https:// o http:// si están presentes
    if raw_client_id.startswith('https://'):
        raw_client_id = raw_client_id.replace('https://', '', 1)
    elif raw_client_id.startswith('http://'):
        raw_client_id = raw_client_id.replace('http://', '', 1)
CLIENT_ID = raw_client_id if raw_client_id else None
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:8080')

# API Key (opcional, para funciones de solo lectura como búsqueda)
API_KEY = os.getenv('YOUTUBE_API_KEY')

# Credenciales de Spotify (opcional, para reproducir playlists de Spotify)
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:8080')
# Token de acceso temporal (opcional, para uso rápido sin configurar credenciales)
SPOTIFY_ACCESS_TOKEN = os.getenv('SPOTIFY_ACCESS_TOKEN')

# Validar que las credenciales estén configuradas (solo si se necesitan)
# Las funciones de descarga NO requieren credenciales OAuth2
def validate_credentials():
    """Valida que las credenciales estén configuradas. Solo se llama cuando se necesitan."""
    if not CLIENT_ID or not CLIENT_SECRET:
        raise ValueError(
            "\n" + "="*70 + "\n"
            "⚠️  CREDENCIALES OAuth2 NO CONFIGURADAS\n"
            "="*70 + "\n\n"
            "Para usar funciones que requieren autenticación (comentar, estadísticas, etc.),\n"
            "necesitas configurar credenciales OAuth2.\n\n"
            "Opciones:\n"
            "1. Configuración rápida (recomendado):\n"
            "   python setup_simple.py\n\n"
            "2. Configuración completa con tus propias credenciales:\n"
            "   python setup.py\n\n"
            "3. Usar credenciales compartidas:\n"
            "   Crea un archivo .env con GOOGLE_CLIENT_ID y GOOGLE_CLIENT_SECRET\n\n"
            "NOTA: Las funciones de descarga NO requieren estas credenciales.\n"
            "="*70 + "\n"
        )

# Configuración de la API
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

# Archivos de tokens
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'

# Configuración de moderación
MODERATION_ENABLED = os.getenv('MODERATION_ENABLED', 'true').lower() == 'true'
MODERATION_CHECK_INTERVAL = int(os.getenv('MODERATION_CHECK_INTERVAL', '300'))  # 5 minutos por defecto

# Configuración de rate limiting (para cuenta colectiva)
MAX_COMMENTS_PER_DAY = int(os.getenv('MAX_COMMENTS_PER_DAY', '50'))
MAX_COMMENTS_PER_HOUR = int(os.getenv('MAX_COMMENTS_PER_HOUR', '10'))

# Configuración de protección de cuenta colectiva
COLLECTIVE_ACCOUNT_ENABLED = os.getenv('COLLECTIVE_ACCOUNT_ENABLED', 'true').lower() == 'true'
PROTECTION_ENABLED = os.getenv('PROTECTION_ENABLED', 'true').lower() == 'true'

# Archivo de reglas éticas
ETHICS_RULES_FILE = 'ethics_rules.json'

# Logging
LOG_FILE = 'bot.log'
MODERATION_LOG_FILE = 'moderation_logs.json'

# Configuración de descargas
DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR', 'downloads')
VIDEOS_DIR = os.path.join(DOWNLOAD_DIR, 'videos')
AUDIO_DIR = os.path.join(DOWNLOAD_DIR, 'audio')

# Crear directorios si no existen
os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

# Calidad de descarga
VIDEO_QUALITY = os.getenv('VIDEO_QUALITY', 'best')  # best, worst, o formato específico
AUDIO_QUALITY = os.getenv('AUDIO_QUALITY', '192')  # Calidad de audio en kbps
