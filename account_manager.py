"""
Gestor de múltiples cuentas colectivas de Google.
Maneja autenticación y acceso a múltiples cuentas.
"""
import os
import json
from typing import List, Dict, Optional
from multi_account_client import MultiAccountYouTubeClient
import config


class AccountManager:
    """
    Gestiona múltiples cuentas colectivas de Google.
    """
    
    def __init__(self, config_file: str = 'multi_account_config.json'):
        """
        Inicializa el gestor de cuentas.
        
        Args:
            config_file: Archivo de configuración multi-cuenta
        """
        self.config_file = config_file
        self.accounts_config = self._load_config()
        self.clients = {}  # Cache de clientes autenticados
    
    def _load_config(self) -> Dict:
        """
        Carga la configuración de múltiples cuentas.
        
        Returns:
            dict: Configuración de cuentas
        """
        if not os.path.exists(self.config_file):
            return {
                'accounts': [],
                'load_balancing': {
                    'strategy': 'round_robin',
                    'failover_enabled': True
                }
            }
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠ Error cargando configuración multi-cuenta: {e}")
            return {
                'accounts': [],
                'load_balancing': {
                    'strategy': 'round_robin',
                    'failover_enabled': True
                }
            }
    
    def get_account(self, account_id: str) -> Optional[MultiAccountYouTubeClient]:
        """
        Obtiene un cliente de YouTube para una cuenta específica.
        
        Args:
            account_id: ID de la cuenta
            
        Returns:
            MultiAccountYouTubeClient: Cliente autenticado o None
        """
        # Verificar si ya está en cache
        if account_id in self.clients:
            return self.clients[account_id]
        
        # Buscar cuenta en configuración
        account_config = None
        for account in self.accounts_config.get('accounts', []):
            if account.get('id') == account_id:
                account_config = account
                break
        
        if not account_config:
            print(f"✗ Cuenta {account_id} no encontrada en configuración")
            return None
        
        # Crear cliente con credenciales de esta cuenta
        try:
            client = MultiAccountYouTubeClient(
                client_id=account_config.get('client_id'),
                client_secret=account_config.get('client_secret'),
                token_file=account_config.get('token_file', f"token_{account_id}.json")
            )
            
            # Guardar en cache
            self.clients[account_id] = client
            
            return client
        
        except Exception as e:
            print(f"✗ Error inicializando cuenta {account_id}: {e}")
            return None
    
    def get_all_accounts(self) -> List[Dict]:
        """
        Obtiene información de todas las cuentas configuradas.
        
        Returns:
            list: Lista de configuraciones de cuentas
        """
        return self.accounts_config.get('accounts', [])
    
    def get_available_accounts(self) -> List[str]:
        """
        Obtiene IDs de todas las cuentas disponibles.
        
        Returns:
            list: Lista de IDs de cuentas
        """
        return [acc.get('id') for acc in self.accounts_config.get('accounts', [])]
    
    def get_account_info(self, account_id: str) -> Optional[Dict]:
        """
        Obtiene información de configuración de una cuenta.
        
        Args:
            account_id: ID de la cuenta
            
        Returns:
            dict: Información de la cuenta o None
        """
        for account in self.accounts_config.get('accounts', []):
            if account.get('id') == account_id:
                return account
        return None
