"""
Balanceador de carga para múltiples cuentas colectivas.
Distribuye acciones entre cuentas según estrategia configurada.
"""
import random
from typing import List, Dict, Optional
from account_manager import AccountManager
from quota_monitor import QuotaMonitor
from multi_account_client import MultiAccountYouTubeClient


class LoadBalancer:
    """
    Balanceador de carga para distribuir acciones entre múltiples cuentas.
    """
    
    def __init__(self, account_manager: AccountManager, quota_monitor: QuotaMonitor):
        """
        Inicializa el balanceador de carga.
        
        Args:
            account_manager: Gestor de cuentas
            quota_monitor: Monitor de cuota
        """
        self.account_manager = account_manager
        self.quota_monitor = quota_monitor
        self.current_index = {}  # Para round-robin
        self.usage_count = {}  # Para least-used
    
    def _get_strategy(self) -> str:
        """
        Obtiene la estrategia de balanceo configurada.
        
        Returns:
            str: Estrategia ('round_robin', 'least_used', 'random')
        """
        config = self.account_manager.accounts_config
        return config.get('load_balancing', {}).get('strategy', 'round_robin')
    
    def _get_operation_cost(self, operation: str) -> int:
        """
        Obtiene el costo en unidades de cuota de una operación.
        
        Args:
            operation: Tipo de operación
            
        Returns:
            int: Unidades de cuota requeridas
        """
        costs = {
            'comment': 50,
            'delete_comment': 50,
            'stats': 1,
            'list_comments': 1,
            'export_comments': 1,
            'top_comments': 1
        }
        return costs.get(operation, 1)
    
    def select_account(self, operation: str, exclude_accounts: List[str] = None) -> Optional[str]:
        """
        Selecciona una cuenta para realizar una operación.
        
        Args:
            operation: Tipo de operación a realizar
            exclude_accounts: Lista de IDs de cuentas a excluir
            
        Returns:
            str: ID de cuenta seleccionada o None
        """
        if exclude_accounts is None:
            exclude_accounts = []
        
        required_units = self._get_operation_cost(operation)
        strategy = self._get_strategy()
        
        # Filtrar cuentas disponibles
        all_accounts = self.account_manager.get_available_accounts()
        available_accounts = [
            acc_id for acc_id in all_accounts 
            if acc_id not in exclude_accounts
        ]
        
        if not available_accounts:
            return None
        
        # Verificar cuota disponible
        accounts_with_quota = []
        for acc_id in available_accounts:
            has_quota, _ = self.quota_monitor.is_quota_available(acc_id, required_units)
            if has_quota:
                accounts_with_quota.append(acc_id)
        
        if not accounts_with_quota:
            return None
        
        # Aplicar estrategia de selección
        if strategy == 'round_robin':
            return self._round_robin_select(accounts_with_quota, operation)
        elif strategy == 'least_used':
            return self._least_used_select(accounts_with_quota, operation)
        elif strategy == 'random':
            return random.choice(accounts_with_quota)
        else:
            # Default: round_robin
            return self._round_robin_select(accounts_with_quota, operation)
    
    def _round_robin_select(self, accounts: List[str], operation: str) -> str:
        """
        Selecciona cuenta usando estrategia round-robin.
        
        Args:
            accounts: Lista de cuentas disponibles
            operation: Tipo de operación
            
        Returns:
            str: ID de cuenta seleccionada
        """
        if operation not in self.current_index:
            self.current_index[operation] = 0
        
        selected = accounts[self.current_index[operation] % len(accounts)]
        self.current_index[operation] = (self.current_index[operation] + 1) % len(accounts)
        
        return selected
    
    def _least_used_select(self, accounts: List[str], operation: str) -> str:
        """
        Selecciona la cuenta menos usada.
        
        Args:
            accounts: Lista de cuentas disponibles
            operation: Tipo de operación
            
        Returns:
            str: ID de cuenta seleccionada
        """
        # Inicializar contadores si no existen
        if operation not in self.usage_count:
            self.usage_count[operation] = {acc: 0 for acc in accounts}
        
        # Encontrar cuenta con menos uso
        min_usage = min(self.usage_count[operation][acc] for acc in accounts)
        least_used = [acc for acc in accounts if self.usage_count[operation][acc] == min_usage]
        
        # Si hay empate, usar round-robin entre las menos usadas
        selected = least_used[0] if len(least_used) == 1 else random.choice(least_used)
        
        # Incrementar contador
        self.usage_count[operation][selected] += 1
        
        return selected
    
    def get_client_for_operation(self, operation: str) -> Optional[MultiAccountYouTubeClient]:
        """
        Obtiene un cliente de YouTube para realizar una operación.
        Selecciona automáticamente la mejor cuenta disponible.
        
        Args:
            operation: Tipo de operación
            
        Returns:
            YouTubeClient: Cliente autenticado o None
        """
        account_id = self.select_account(operation)
        
        if not account_id:
            print("✗ No hay cuentas disponibles con cuota suficiente")
            return None
        
        client = self.account_manager.get_account(account_id)
        
        if client:
            # Registrar uso de cuota
            units = self._get_operation_cost(operation)
            self.quota_monitor.record_quota_usage(account_id, operation, units)
            
            # Actualizar contador de uso para least-used
            if operation in self.usage_count and account_id in self.usage_count[operation]:
                self.usage_count[operation][account_id] += 1
        
        return client
    
    def get_account_status(self) -> Dict:
        """
        Obtiene el estado de todas las cuentas.
        
        Returns:
            dict: Estado de cuentas
        """
        accounts = self.account_manager.get_available_accounts()
        status = {}
        
        for acc_id in accounts:
            quota_info = self.quota_monitor.get_quota_usage_today(acc_id)
            account_info = self.account_manager.get_account_info(acc_id)
            
            status[acc_id] = {
                'available': quota_info['remaining_units'] > 0,
                'quota_used': quota_info['total_units'],
                'quota_remaining': quota_info['remaining_units'],
                'percentage_used': quota_info['percentage_used'],
                'priority': account_info.get('priority', 999) if account_info else 999
            }
        
        return status
