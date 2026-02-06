"""
Configuración compartida para usar credenciales OAuth2 públicas.
Esto permite que todos los usuarios usen la misma API sin configurar credenciales propias.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Scopes OAuth2 - SOLO YouTube, SIN acceso a email/Gmail
YOUTUBE_SCOPES = [
    'https://www.googleapis.com/auth/youtube.force-ssl',
]

# Credenciales OAuth2 compartidas (pueden estar en .env o usar valores por defecto)
# Si no existen en .env, se intentarán usar valores por defecto del proyecto
CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID') or os.getenv('SHARED_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET') or os.getenv('SHARED_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:8080')

# Si no hay credenciales configuradas, intentar usar credenciales compartidas del proyecto
# Estas deben estar publicadas en Google Cloud Console para funcionar sin test users
if not CLIENT_ID or not CLIENT_SECRET:
    # Intentar cargar desde archivo de credenciales compartidas si existe
    shared_creds_file = os.path.join(os.path.dirname(__file__), 'shared_credentials.json')
    if os.path.exists(shared_creds_file):
        import json
        try:
            with open(shared_creds_file, 'r') as f:
                shared_creds = json.load(f)
                CLIENT_ID = shared_creds.get('installed', {}).get('client_id') or CLIENT_ID
                CLIENT_SECRET = shared_creds.get('installed', {}).get('client_secret') or CLIENT_SECRET
        except:
            pass

def validate_credentials():
    """Valida que las credenciales estén configuradas."""
    if not CLIENT_ID or not CLIENT_SECRET:
        raise ValueError(
            "ERROR: Credenciales OAuth2 no configuradas.\n"
            "El proyecto usa credenciales compartidas. Si no funcionan, contacta al mantenedor.\n"
            "O configura tus propias credenciales ejecutando: python setup.py"
        )

API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'

MODERATION_ENABLED = os.getenv('MODERATION_ENABLED', 'true').lower() == 'true'
MODERATION_CHECK_INTERVAL = int(os.getenv('MODERATION_CHECK_INTERVAL', '300'))

MAX_COMMENTS_PER_DAY = int(os.getenv('MAX_COMMENTS_PER_DAY', '50'))
MAX_COMMENTS_PER_HOUR = int(os.getenv('MAX_COMMENTS_PER_HOUR', '10'))

COLLECTIVE_ACCOUNT_ENABLED = os.getenv('COLLECTIVE_ACCOUNT_ENABLED', 'true').lower() == 'true'
PROTECTION_ENABLED = os.getenv('PROTECTION_ENABLED', 'true').lower() == 'true'

ETHICS_RULES_FILE = 'ethics_rules.json'
LOG_FILE = 'bot.log'
MODERATION_LOG_FILE = 'moderation_logs.json'

DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR', 'downloads')
VIDEOS_DIR = os.path.join(DOWNLOAD_DIR, 'videos')
AUDIO_DIR = os.path.join(DOWNLOAD_DIR, 'audio')
COMMENT_EXPORT_DIR = os.path.join(DOWNLOAD_DIR, 'comments')
METADATA_DIR = os.path.join(DOWNLOAD_DIR, 'metadata')

os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(COMMENT_EXPORT_DIR, exist_ok=True)
os.makedirs(METADATA_DIR, exist_ok=True)

VIDEO_QUALITY = os.getenv('VIDEO_QUALITY', 'best')
AUDIO_QUALITY = os.getenv('AUDIO_QUALITY', '192')
