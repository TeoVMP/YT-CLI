#!/usr/bin/env python3
"""
Configuración simplificada - Solo verifica que las dependencias estén instaladas.
Las credenciales OAuth2 son compartidas y están pre-configuradas.
"""
import os
import sys

def check_dependencies():
    """Verifica que todas las dependencias estén instaladas."""
    missing = []
    
    try:
        import google.auth
    except ImportError:
        missing.append("google-auth (instalar: pip install google-api-python-client)")
    
    try:
        import yt_dlp
    except ImportError:
        missing.append("yt-dlp (instalar: pip install yt-dlp)")
    
    try:
        import mutagen
    except ImportError:
        missing.append("mutagen (instalar: pip install mutagen)")
    
    try:
        import dotenv
    except ImportError:
        missing.append("python-dotenv (instalar: pip install python-dotenv)")
    
    if missing:
        print("\n" + "="*70)
        print("⚠ DEPENDENCIAS FALTANTES")
        print("="*70)
        print("\nFaltan las siguientes dependencias:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nPara instalar todas las dependencias:")
        print("  pip install -r requirements.txt")
        print("\nO en Termux:")
        print("  ./install-termux.sh")
        print("="*70 + "\n")
        return False
    
    print("\n✓ Todas las dependencias están instaladas.")
    return True

def check_credentials():
    """Verifica si hay credenciales configuradas."""
    has_env = os.path.exists('.env')
    has_shared = os.path.exists('shared_credentials.json')
    
    if has_env or has_shared:
        print("✓ Credenciales encontradas.")
        return True
    
    print("\n" + "="*70)
    print("ℹ INFORMACIÓN SOBRE CREDENCIALES")
    print("="*70)
    print("\nEste proyecto usa credenciales OAuth2 compartidas.")
    print("No necesitas configurar tus propias credenciales.")
    print("\nSi el login no funciona, puede ser que:")
    print("  1. La aplicación no esté publicada en Google Cloud Console")
    print("  2. Necesites esperar unos minutos después de la publicación")
    print("\nPara usar tus propias credenciales (opcional):")
    print("  python setup.py")
    print("="*70 + "\n")
    return False

def main():
    print("\n" + "="*70)
    print("CONFIGURACIÓN SIMPLIFICADA")
    print("="*70)
    print("\nEste script verifica que todo esté listo para usar.")
    print("Las credenciales OAuth2 son compartidas - no necesitas configurarlas.\n")
    
    # Verificar dependencias
    if not check_dependencies():
        sys.exit(1)
    
    # Verificar credenciales (opcional)
    check_credentials()
    
    print("\n" + "="*70)
    print("✓ CONFIGURACIÓN COMPLETA")
    print("="*70)
    print("\nPuedes empezar a usar el bot:")
    print("  python main.py --login")
    print("  python main.py --search 'python tutorial'")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
