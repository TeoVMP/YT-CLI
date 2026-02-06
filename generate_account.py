"""
Script para generar nombres de cuenta genéricos y ofuscados.
Ayuda a crear cuentas sin revelar información personal.
"""
import sys
from datetime import datetime
from obfuscator import DataObfuscator, AccountNameGenerator


def main():
    """
    Genera sugerencias de nombres de cuenta ofuscados.
    """
    print("\n" + "="*70)
    print("GENERADOR DE NOMBRES DE CUENTA OFUSCADOS")
    print("="*70)
    print("\nEste script genera nombres genéricos para proteger tu privacidad.\n")
    
    obfuscator = DataObfuscator()
    generator = AccountNameGenerator()
    
    # Generar datos de cuenta
    account_data = obfuscator.generate_safe_account_name()
    youtube_data = generator.generate_youtube_account_name()
    project_name = generator.generate_project_name()
    
    print("="*70)
    print("SUGERENCIAS PARA CREAR LA CUENTA COLECTIVA")
    print("="*70)
    
    print("\n📧 EMAIL SUGERIDO (para crear cuenta de Google):")
    print(f"   {account_data['suggested_email']}")
    print("   (Puedes usar este formato o crear uno similar)")
    
    print("\n👤 NOMBRE DE CUENTA SUGERIDO:")
    print(f"   {account_data['account_name']}")
    print(f"   Display Name: {account_data['display_name']}")
    
    print("\n📺 NOMBRE DE CANAL DE YOUTUBE SUGERIDO:")
    print(f"   {youtube_data['youtube_channel_name']}")
    
    print("\n☁️  NOMBRE DE PROYECTO EN GOOGLE CLOUD:")
    print(f"   {project_name}")
    
    print("\n" + "="*70)
    print("RECOMENDACIONES DE SEGURIDAD")
    print("="*70)
    print("\n✅ Usa nombres genéricos que no revelen información personal")
    print("✅ No uses tu nombre real ni información identificable")
    print("✅ Usa números aleatorios en los nombres")
    print("✅ Considera usar un email de ProtonMail para más privacidad")
    print("✅ No compartas estos nombres públicamente")
    
    print("\n" + "="*70)
    print("PRÓXIMOS PASOS")
    print("="*70)
    print("\n1. Crea la cuenta de Google con el email sugerido")
    print("2. Usa el nombre de cuenta sugerido")
    print("3. Crea el proyecto en Google Cloud con el nombre sugerido")
    print("4. Configura el bot con: py setup.py")
    print("\n" + "="*70 + "\n")
    
    # Guardar sugerencias en archivo
    suggestions = {
        'account_email': account_data['suggested_email'],
        'account_name': account_data['account_name'],
        'youtube_channel_name': youtube_data['youtube_channel_name'],
        'project_name': project_name,
        'generated_at': str(datetime.now())
    }
    
    try:
        import json
        with open('account_suggestions.json', 'w', encoding='utf-8') as f:
            json.dump(suggestions, f, indent=2, ensure_ascii=False)
        print("✓ Sugerencias guardadas en: account_suggestions.json\n")
    except Exception as e:
        print(f"⚠ No se pudo guardar sugerencias: {e}\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✓ Operación cancelada.")
        sys.exit(0)
