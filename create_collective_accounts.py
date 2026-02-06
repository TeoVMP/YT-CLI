"""
Script guiado para crear cuentas colectivas de Google/YouTube con datos ofuscados.
Permite navegar hacia atrás y se usa solo una vez.
"""
import sys
import json
import os
from datetime import datetime
from obfuscator import DataObfuscator, AccountNameGenerator


class CollectiveAccountCreator:
    """
    Creador guiado de cuentas colectivas.
    """
    
    def __init__(self):
        """
        Inicializa el creador de cuentas.
        """
        self.obfuscator = DataObfuscator()
        self.generator = AccountNameGenerator()
        self.accounts = []  # Lista de cuentas creadas
        self.current_step = 0
        self.steps = []
        self.config_file = 'multi_account_config.json'
    
    def clear_screen(self):
        """
        Limpia la pantalla (compatible con Windows y Unix).
        """
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title: str):
        """
        Imprime un encabezado formateado.
        
        Args:
            title: Título del encabezado
        """
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70)
    
    def wait_for_enter(self, message: str = "\nPresiona Enter para continuar..."):
        """
        Espera a que el usuario presione Enter.
        
        Args:
            message: Mensaje a mostrar
        """
        input(message)
    
    def show_menu(self, options: list, allow_back: bool = True, allow_exit: bool = True) -> str:
        """
        Muestra un menú y retorna la opción seleccionada.
        
        Args:
            options: Lista de opciones [(número, texto, función)]
            allow_back: Si permite volver atrás
            allow_exit: Si permite salir
            
        Returns:
            str: Opción seleccionada
        """
        print("\n" + "-"*70)
        for num, text, _ in options:
            print(f"  {num}. {text}")
        
        if allow_back:
            print(f"  b. Volver atrás")
        if allow_exit:
            print(f"  q. Salir sin guardar")
        
        print("-"*70)
        
        while True:
            choice = input("\nSelecciona una opción: ").strip().lower()
            
            # Verificar opciones válidas
            valid_numbers = [str(num) for num, _, _ in options]
            if choice in valid_numbers:
                return choice
            elif choice == 'b' and allow_back:
                return 'back'
            elif choice == 'q' and allow_exit:
                return 'exit'
            else:
                print("✗ Opción inválida. Intenta de nuevo.")
    
    def step_1_welcome(self):
        """
        Paso 1: Bienvenida y explicación.
        """
        self.clear_screen()
        self.print_header("CREACIÓN DE CUENTAS COLECTIVAS DE GOOGLE/YOUTUBE")
        
        print("\nEste script te guiará paso a paso para crear cuentas colectivas")
        print("de Google/YouTube con datos personales ofuscados.")
        print("\n📋 Lo que necesitarás:")
        print("   • Acceso a internet")
        print("   • Un número de teléfono para verificación (puede ser el mismo para todas)")
        print("   • Tiempo: ~5-10 minutos por cuenta")
        print("\n📋 Lo que hará este script:")
        print("   • Generar datos ofuscados para cada cuenta")
        print("   • Guiarte paso a paso en la creación")
        print("   • Configurar automáticamente multi_account_config.json")
        print("\n⚠️  IMPORTANTE:")
        print("   • Usa nombres genéricos (no información personal)")
        print("   • Considera usar ProtonMail para mayor privacidad")
        print("   • Guarda las credenciales en un lugar seguro")
        
        self.wait_for_enter()
        return 'next'
    
    def step_2_number_of_accounts(self):
        """
        Paso 2: Determinar cuántas cuentas crear.
        """
        self.clear_screen()
        self.print_header("PASO 2: NÚMERO DE CUENTAS")
        
        print("\n¿Cuántas cuentas colectivas quieres crear?")
        print("\n💡 Recomendaciones:")
        print("   • 1 cuenta: Uso básico (50 comentarios/día)")
        print("   • 2-3 cuentas: Uso medio (100-150 comentarios/día)")
        print("   • 5-10 cuentas: Uso intensivo (200+ comentarios/día)")
        
        while True:
            try:
                num = input("\nNúmero de cuentas (1-10): ").strip()
                if num.lower() == 'b':
                    return 'back'
                elif num.lower() == 'q':
                    return 'exit'
                
                num = int(num)
                if 1 <= num <= 10:
                    self.num_accounts = num
                    return 'next'
                else:
                    print("✗ Por favor ingresa un número entre 1 y 10.")
            except ValueError:
                print("✗ Por favor ingresa un número válido.")
    
    def step_3_generate_account_data(self):
        """
        Paso 3: Generar datos ofuscados para las cuentas.
        """
        self.clear_screen()
        self.print_header("PASO 3: GENERANDO DATOS OFUSCADOS")
        
        print("\n📝 Generando datos genéricos para las cuentas...")
        
        self.accounts = []
        for i in range(1, self.num_accounts + 1):
            account_data = self.obfuscator.generate_safe_account_name()
            youtube_data = self.generator.generate_youtube_account_name()
            project_data = self.generator.generate_project_name()
            
            account_info = {
                'number': i,
                'account_name': account_data['account_name'],
                'suggested_email': account_data['suggested_email'],
                'display_name': account_data['display_name'],
                'youtube_channel_name': youtube_data['youtube_channel_name'],
                'project_name': project_data,
                'description': f"Cuenta colectiva #{i}",
                'created': False,
                'client_id': None,
                'client_secret': None,
                'token_file': f"token_account_{i}.json"
            }
            
            self.accounts.append(account_info)
        
        print(f"\n✓ Generados datos para {len(self.accounts)} cuenta(s)\n")
        
        # Mostrar resumen
        for acc in self.accounts:
            print(f"\n📧 Cuenta #{acc['number']}:")
            print(f"   Email sugerido: {acc['suggested_email']}")
            print(f"   Nombre de cuenta: {acc['account_name']}")
            print(f"   Canal YouTube: {acc['youtube_channel_name']}")
            print(f"   Proyecto Cloud: {acc['project_name']}")
        
        print("\n" + "="*70)
        print("⚠️  IMPORTANTE: Guarda esta información en un lugar seguro")
        print("="*70)
        
        # Guardar datos generados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f'accounts_backup_{timestamp}.json'
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(self.accounts, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Datos guardados en: {backup_file}")
        
        self.wait_for_enter()
        return 'next'
    
    def step_4_create_accounts_guide(self):
        """
        Paso 4: Guía para crear las cuentas en Google.
        """
        self.clear_screen()
        self.print_header("PASO 4: CREAR CUENTAS EN GOOGLE")
        
        print("\n📋 INSTRUCCIONES PARA CREAR CADA CUENTA:\n")
        print("="*70)
        print("PARA CADA CUENTA:")
        print("="*70)
        print("\n1. Ve a: https://accounts.google.com/signup")
        print("2. Usa el EMAIL SUGERIDO de la lista anterior")
        print("3. Usa el NOMBRE DE CUENTA sugerido")
        print("4. Crea una contraseña fuerte y segura")
        print("5. Verifica con tu número de teléfono")
        print("6. Completa la verificación de seguridad")
        print("\n💡 TIP: Puedes usar el mismo número de teléfono para todas")
        print("💡 TIP: Considera usar ProtonMail para crear el email primero")
        
        print("\n" + "="*70)
        print("¿Ya creaste todas las cuentas en Google?")
        print("="*70)
        
        options = [
            ('1', 'Sí, ya creé todas las cuentas', None),
            ('2', 'No, necesito más tiempo', None),
        ]
        
        choice = self.show_menu(options, allow_back=True, allow_exit=True)
        
        if choice == 'back':
            return 'back'
        elif choice == 'exit':
            return 'exit'
        elif choice == '1':
            return 'next'
        else:
            print("\n⏸️  Pausa. Cuando termines de crear las cuentas, ejecuta este script de nuevo.")
            print("   Los datos generados están guardados en el archivo de backup.")
            sys.exit(0)
    
    def step_5_google_cloud_setup(self):
        """
        Paso 5: Guía para configurar Google Cloud Console.
        """
        self.clear_screen()
        self.print_header("PASO 5: CONFIGURAR GOOGLE CLOUD CONSOLE")
        
        print("\n📋 Para cada cuenta, necesitas crear un proyecto en Google Cloud Console:\n")
        print("="*70)
        print("PARA CADA CUENTA:")
        print("="*70)
        print("\n1. Ve a: https://console.cloud.google.com/")
        print("2. Inicia sesión con la cuenta que acabas de crear")
        print("3. Crea un proyecto nuevo:")
        print("   - Click en el selector de proyectos (arriba)")
        print("   - Click 'NEW PROJECT' o 'NUEVO PROYECTO'")
        print("   - Nombre: Usa el 'PROYECTO CLOUD' de la lista")
        print("   - Click 'CREATE' o 'CREAR'")
        print("   - Espera a que se cree y selecciónalo")
        print("\n4. Habilita YouTube Data API v3:")
        print("   - Ve a 'APIs & Services' → 'Library' (o 'APIs y servicios' → 'Biblioteca')")
        print("   - Busca 'YouTube Data API v3'")
        print("   - Click en el resultado")
        print("   - Click 'ENABLE' o 'HABILITAR'")
        print("\n5. Configura OAuth Consent Screen (Pantalla de consentimiento):")
        print("   - Ve a 'APIs & Services' → 'OAuth consent screen'")
        print("   - O desde el menú lateral: 'Google Auth Platform' → 'OAuth consent screen'")
        print("   - Tipo de usuario: 'External' (Externo)")
        print("   - Click 'CREATE' o 'CREAR'")
        print("   - App information (Información de la app):")
        print("     • App name: 'YouTube Bot'")
        print("     • User support email: Tu email de la cuenta")
        print("     • Developer contact: Tu email de la cuenta")
        print("   - Click 'SAVE AND CONTINUE' o 'GUARDAR Y CONTINUAR'")
        print("   - Scopes (Alcances):")
        print("     • Click 'ADD OR REMOVE SCOPES'")
        print("     • Busca y selecciona: 'youtube.force-ssl'")
        print("     • IMPORTANTE: NO selecciones nada de Gmail o email")
        print("     • Click 'UPDATE' → 'SAVE AND CONTINUE'")
        print("   - Test users (Usuarios de prueba):")
        print("     • Agrega el email de la cuenta colectiva")
        print("     • Click 'SAVE AND CONTINUE'")
        print("   - Summary: Click 'BACK TO DASHBOARD'")
        print("\n6. Crea credenciales OAuth2:")
        print("   - Ve a 'APIs & Services' → 'Credentials' (o 'Credenciales')")
        print("   - O desde el menú: 'Google Auth Platform' → 'Clients'")
        print("   - Click 'CREATE CREDENTIALS' → 'OAuth client ID'")
        print("   - En el dropdown 'Application type':")
        print("     • Selecciona 'Desktop app' (Aplicación de escritorio)")
        print("     • NO selecciones 'Web application' u otros tipos")
        print("   - Name: 'YouTube Bot Desktop'")
        print("   - Click 'CREATE' o 'CREAR'")
        print("   - Se mostrará una ventana con:")
        print("     • Your Client ID (tu Client ID)")
        print("     • Your Client Secret (tu Client Secret)")
        print("\n7. Copia el Client ID y Client Secret")
        print("   ⚠️  IMPORTANTE: Guárdalos en un lugar seguro")
        print("\n💡 NOTA: 'User Type: External' se configura en OAuth Consent Screen")
        print("   (paso anterior). Si no lo hiciste, vuelve al paso 5.")
        
        print("\n" + "="*70)
        print("¿Ya configuraste Google Cloud Console para todas las cuentas?")
        print("="*70)
        
        options = [
            ('1', 'Sí, ya configuré todas', None),
            ('2', 'No, necesito más tiempo', None),
        ]
        
        choice = self.show_menu(options, allow_back=True, allow_exit=True)
        
        if choice == 'back':
            return 'back'
        elif choice == 'exit':
            return 'exit'
        elif choice == '1':
            return 'next'
        else:
            print("\n⏸️  Pausa. Cuando termines, ejecuta este script de nuevo.")
            sys.exit(0)
    
    def step_6_enter_credentials(self):
        """
        Paso 6: Ingresar credenciales de cada cuenta.
        """
        self.clear_screen()
        self.print_header("PASO 6: INGRESAR CREDENCIALES")
        
        print("\n📝 Ahora necesitas ingresar las credenciales OAuth2 de cada cuenta.\n")
        
        for i, account in enumerate(self.accounts):
            print("\n" + "="*70)
            print(f"CUENTA #{account['number']}: {account['account_name']}")
            print("="*70)
            print(f"Email: {account['suggested_email']}")
            print(f"Proyecto: {account['project_name']}")
            print("-"*70)
            
            while True:
                client_id = input(f"\nClient ID de la cuenta #{account['number']}: ").strip()
                if client_id.lower() == 'b':
                    return 'back'
                elif client_id.lower() == 'q':
                    return 'exit'
                
                if client_id:
                    account['client_id'] = client_id
                    break
                else:
                    print("✗ Client ID es requerido.")
            
            while True:
                client_secret = input(f"Client Secret de la cuenta #{account['number']}: ").strip()
                if client_secret.lower() == 'b':
                    return 'back'
                elif client_secret.lower() == 'q':
                    return 'exit'
                
                if client_secret:
                    account['client_secret'] = client_secret
                    account['created'] = True
                    break
                else:
                    print("✗ Client Secret es requerido.")
            
            print(f"\n✓ Credenciales de cuenta #{account['number']} guardadas.")
        
        self.wait_for_enter()
        return 'next'
    
    def step_7_create_config(self):
        """
        Paso 7: Crear archivo de configuración multi-cuenta.
        """
        self.clear_screen()
        self.print_header("PASO 7: CREAR CONFIGURACIÓN")
        
        print("\n📝 Creando archivo de configuración multi-cuenta...\n")
        
        # Preparar configuración
        config_data = {
            'accounts': [],
            'load_balancing': {
                'strategy': 'round_robin',
                'failover_enabled': True,
                'quota_threshold_warning': 1000,
                'quota_threshold_critical': 500
            },
            'description': 'Configuración de cuentas colectivas creada automáticamente',
            'created_at': datetime.now().isoformat()
        }
        
        # Agregar cada cuenta
        for account in self.accounts:
            if account['created']:
                account_config = {
                    'id': f"account_{account['number']}",
                    'client_id': account['client_id'],
                    'client_secret': account['client_secret'],
                    'token_file': account['token_file'],
                    'max_comments_per_day': 50,
                    'max_comments_per_hour': 10,
                    'priority': account['number'],
                    'description': account['description'],
                    'email': account['suggested_email'],
                    'project_name': account['project_name']
                }
                config_data['accounts'].append(account_config)
        
        # Guardar configuración
        try:
            if os.path.exists(self.config_file):
                backup_name = f"{self.config_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(self.config_file, backup_name)
                print(f"⚠ Archivo existente respaldado como: {backup_name}")
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Configuración guardada en: {self.config_file}")
            print(f"✓ {len(config_data['accounts'])} cuenta(s) configurada(s)")
            
        except Exception as e:
            print(f"✗ Error guardando configuración: {e}")
            return 'back'
        
        self.wait_for_enter()
        return 'next'
    
    def step_8_finalize(self):
        """
        Paso 8: Finalización y próximos pasos.
        """
        self.clear_screen()
        self.print_header("✓ CONFIGURACIÓN COMPLETADA")
        
        print("\n🎉 ¡Todas las cuentas colectivas han sido configuradas!\n")
        
        print("="*70)
        print("PRÓXIMOS PASOS:")
        print("="*70)
        print("\n1. Autorizar cada cuenta (primera vez):")
        print("   py main.py --stats VIDEO_ID")
        print("   (Se abrirá el navegador - inicia sesión con cada cuenta)")
        print("\n2. Usar las cuentas:")
        print("   py main.py --video-id VIDEO_ID --comment 'Texto'")
        print("\n3. Ver reporte de cuota:")
        print("   py main.py --activity-report")
        print("\n4. Ver documentación completa:")
        print("   Lee MULTI_ACCOUNT.md")
        
        print("\n" + "="*70)
        print("ARCHIVOS CREADOS:")
        print("="*70)
        print(f"   • {self.config_file} - Configuración de cuentas")
        print(f"   • accounts_backup_*.json - Backup de datos generados")
        
        print("\n" + "="*70)
        print("⚠️  IMPORTANTE:")
        print("="*70)
        print("   • Mantén estos archivos seguros y privados")
        print("   • NO subas credenciales a GitHub")
        print("   • Los tokens se crearán automáticamente al autorizar")
        
        print("\n✓ Script completado exitosamente.\n")
        
        self.wait_for_enter()
        return 'done'
    
    def run(self):
        """
        Ejecuta el flujo completo del script.
        """
        # Definir pasos
        steps = [
            ('Bienvenida', self.step_1_welcome),
            ('Número de cuentas', self.step_2_number_of_accounts),
            ('Generar datos', self.step_3_generate_account_data),
            ('Crear cuentas', self.step_4_create_accounts_guide),
            ('Google Cloud', self.step_5_google_cloud_setup),
            ('Credenciales', self.step_6_enter_credentials),
            ('Configuración', self.step_7_create_config),
            ('Finalización', self.step_8_finalize),
        ]
        
        current_index = 0
        
        while current_index < len(steps):
            step_name, step_func = steps[current_index]
            
            try:
                result = step_func()
                
                if result == 'next':
                    current_index += 1
                elif result == 'back':
                    if current_index > 0:
                        current_index -= 1
                    else:
                        print("\n⚠ Ya estás en el primer paso.")
                        self.wait_for_enter()
                elif result == 'exit':
                    print("\n⚠ Script cancelado. Los datos generados están guardados.")
                    sys.exit(0)
                elif result == 'done':
                    break
                else:
                    current_index += 1
            
            except KeyboardInterrupt:
                print("\n\n⚠ Script interrumpido por el usuario.")
                print("Los datos generados están guardados en los archivos de backup.")
                sys.exit(0)
            except Exception as e:
                print(f"\n✗ Error en paso '{step_name}': {e}")
                print("\nOpciones:")
                print("  - Presiona Enter para continuar")
                print("  - Escribe 'b' y Enter para volver atrás")
                print("  - Escribe 'q' y Enter para salir")
                
                choice = input("\nTu elección: ").strip().lower()
                if choice == 'b' and current_index > 0:
                    current_index -= 1
                elif choice == 'q':
                    sys.exit(0)


def main():
    """
    Función principal.
    """
    try:
        creator = CollectiveAccountCreator()
        creator.run()
    except KeyboardInterrupt:
        print("\n\n✓ Script cancelado por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error fatal: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
