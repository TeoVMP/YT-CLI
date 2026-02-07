"""
Script de configuración interactiva para el bot de YouTube.
Guía al usuario paso a paso para configurar las credenciales.
"""
import os
import sys


def print_header():
    """Imprime el encabezado del script."""
    print("\n" + "="*70)
    print("CONFIGURACIÓN DEL BOT DE YOUTUBE")
    print("="*70)
    print("\nEste script te ayudará a configurar las credenciales necesarias.")
    print("Sigue las instrucciones paso a paso.\n")


def check_env_exists():
    """Verifica si el archivo .env ya existe."""
    if os.path.exists('.env'):
        print("⚠ Archivo .env ya existe.")
        respuesta = input("¿Quieres sobrescribirlo? (s/n): ").strip().lower()
        if respuesta != 's':
            print("✓ Configuración cancelada. Manteniendo archivo existente.")
            return False
    return True


def get_credentials():
    """Obtiene las credenciales del usuario."""
    print("\n" + "="*70)
    print("PASO 1: Credenciales OAuth2 de Google Cloud Console")
    print("="*70)
    print("\n📖 CONFIGURACIÓN DE CREDENCIALES OAuth2")
    print("\n💡 IMPORTANTE: Usarás tu propia cuenta de Google para comentar")
    print("   Cada usuario autoriza con su cuenta personal.\n")
    print("Resumen rápido:")
    print("1. Ve a https://console.cloud.google.com/")
    print("2. Crea un proyecto (o usa uno existente)")
    print("3. Habilita SOLO 'YouTube Data API v3' (NO Gmail API)")
    print("4. Configura OAuth Consent Screen:")
    print("   - User Type: External")
    print("   - Scopes: SOLO 'youtube.force-ssl' (NO Gmail)")
    print("   - Agrega tu email como Test User")
    print("5. Crea credenciales OAuth2:")
    print("   - Application type: 'Desktop app'")
    print("   - Name: 'YouTube Bot Desktop'")
    print("6. Copia el Client ID y Client Secret\n")
    print("⚠️ IMPORTANTE:")
    print("   - Solo habilita YouTube API, NO habilites Gmail API")
    print("   - Agrega tu email como Test User en OAuth Consent Screen")
    print("   - Cada usuario autoriza con su propia cuenta de Google\n")
    print("="*70 + "\n")
    
    client_id = input("Ingresa tu GOOGLE_CLIENT_ID: ").strip()
    if not client_id:
        print("✗ Client ID es requerido.")
        return None, None
    
    # Limpiar Client ID si viene con https:// o http://
    if client_id.startswith('https://'):
        client_id = client_id.replace('https://', '', 1)
        print("ℹ Se removió 'https://' del Client ID")
    elif client_id.startswith('http://'):
        client_id = client_id.replace('http://', '', 1)
        print("ℹ Se removió 'http://' del Client ID")
    
    client_secret = input("Ingresa tu GOOGLE_CLIENT_SECRET: ").strip()
    if not client_secret:
        print("✗ Client Secret es requerido.")
        return None, None
    
    # Ofuscar credenciales en la salida (solo mostrar parcialmente)
    print("\n✓ Credenciales recibidas:")
    print(f"   Client ID: {client_id[:20]}...{client_id[-10:]}")
    print(f"   Client Secret: {client_secret[:4]}***")
    
    return client_id, client_secret


def get_optional_settings():
    """Obtiene configuraciones opcionales."""
    print("\n" + "-"*70)
    print("PASO 2: Configuraciones Opcionales")
    print("-"*70)
    
    redirect_uri = input("\nRedirect URI (presiona Enter para usar http://localhost:8080): ").strip()
    if not redirect_uri:
        redirect_uri = "http://localhost:8080"
    
    print("\nConfiguración de Rate Limiting:")
    max_comments_day = input("Máximo de comentarios por día (presiona Enter para 50): ").strip()
    if not max_comments_day or not max_comments_day.isdigit():
        max_comments_day = "50"
    
    max_comments_hour = input("Máximo de comentarios por hora (presiona Enter para 10): ").strip()
    if not max_comments_hour or not max_comments_hour.isdigit():
        max_comments_hour = "10"
    
    print("\nConfiguración de Protección:")
    protection = input("¿Activar protección de cuenta colectiva? (s/n, default: s): ").strip().lower()
    protection_enabled = "true" if (protection == 's' or protection == '') else "false"
    
    return redirect_uri, max_comments_day, max_comments_hour, protection_enabled


def create_env_file(client_id, client_secret, redirect_uri, max_comments_day, max_comments_hour, protection_enabled):
    """Crea el archivo .env con las credenciales."""
    env_content = f"""# YouTube Bot Configuration
# Configurado automáticamente por setup.py

# Credenciales OAuth2 de Google Cloud Console
GOOGLE_CLIENT_ID={client_id}
GOOGLE_CLIENT_SECRET={client_secret}

# Redirect URI (debe coincidir con la configurada en Google Cloud Console)
REDIRECT_URI={redirect_uri}

# Configuración de moderación
MODERATION_ENABLED=true
MODERATION_CHECK_INTERVAL=300

# Configuración de rate limiting
MAX_COMMENTS_PER_DAY={max_comments_day}
MAX_COMMENTS_PER_HOUR={max_comments_hour}

# Configuración de cuenta colectiva y protección
COLLECTIVE_ACCOUNT_ENABLED={protection_enabled}
PROTECTION_ENABLED={protection_enabled}

# Configuración de descargas
DOWNLOAD_DIR=downloads
VIDEO_QUALITY=best
AUDIO_QUALITY=192
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        return True
    except Exception as e:
        print(f"✗ Error creando archivo .env: {e}")
        return False


def main():
    """Función principal del script de configuración."""
    print_header()
    
    # Verificar si .env existe
    if not check_env_exists():
        sys.exit(0)
    
    # Obtener credenciales
    client_id, client_secret = get_credentials()
    if not client_id or not client_secret:
        print("\n✗ Configuración cancelada. Credenciales requeridas.")
        sys.exit(1)
    
    # Obtener configuraciones opcionales
    redirect_uri, max_comments_day, max_comments_hour, protection_enabled = get_optional_settings()
    
    # Crear archivo .env
    print("\n" + "-"*70)
    print("Creando archivo .env...")
    if create_env_file(client_id, client_secret, redirect_uri, max_comments_day, max_comments_hour, protection_enabled):
        print("✓ Archivo .env creado exitosamente!")
    else:
        print("✗ Error creando archivo .env")
        sys.exit(1)
    
    # Mensaje final
    print("\n" + "="*70)
    print("✓ CONFIGURACIÓN COMPLETADA")
    print("="*70)
    print("\nPróximos pasos:")
    print("1. Ejecuta cualquier comando que requiera autenticación:")
    print("   py main.py --stats VIDEO_ID")
    print("2. Se abrirá tu navegador para autorizar la aplicación")
    print("3. Inicia sesión con tu cuenta de Google")
    print("4. Autoriza la aplicación")
    print("5. ¡Listo! Ya puedes usar todas las funciones.\n")
    print("="*70 + "\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✓ Configuración cancelada por el usuario.")
        sys.exit(0)
