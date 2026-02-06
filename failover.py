"""
Sistema de failover automático para múltiples cuentas.
Cambia automáticamente a otra cuenta cuando una se agota o falla.
"""
from typing import Optional, List
from account_manager import AccountManager
from quota_monitor import QuotaMonitor
from load_balancer import LoadBalancer
from multi_account_client import MultiAccountYouTubeClient


class FailoverSystem:
    """
    Sistema de failover automático para cambiar entre cuentas.
    """
    
    def __init__(self, account_manager: AccountManager, quota_monitor: QuotaMonitor, load_balancer: LoadBalancer):
        """
        Inicializa el sistema de failover.
        
        Args:
            account_manager: Gestor de cuentas
            quota_monitor: Monitor de cuota
            load_balancer: Balanceador de carga
        """
        self.account_manager = account_manager
        self.quota_monitor = quota_monitor
        self.load_balancer = load_balancer
        self.failed_accounts = set()  # Cuentas que han fallado
        self.failover_enabled = self._is_failover_enabled()
    
    def _is_failover_enabled(self) -> bool:
        """
        Verifica si el failover está habilitado en la configuración.
        
        Returns:
            bool: True si está habilitado
        """
        config = self.account_manager.accounts_config
        return config.get('load_balancing', {}).get('failover_enabled', True)
    
    def get_client_with_failover(self, operation: str, exclude_accounts: List[str] = None) -> Optional[MultiAccountYouTubeClient]:
        """
        Obtiene un cliente con failover automático.
        Si una cuenta falla o se agota, intenta con otra automáticamente.
        
        Args:
            operation: Tipo de operación
            exclude_accounts: Lista de IDs de cuentas a excluir
            
        Returns:
            YouTubeClient: Cliente disponible o None
        """
        if exclude_accounts is None:
            exclude_accounts = []
        
        # Agregar cuentas fallidas a la lista de exclusión
        exclude_accounts = list(set(exclude_accounts) | self.failed_accounts)
        
        max_attempts = 3
        attempts = 0
        
        while attempts < max_attempts:
            # Seleccionar cuenta
            account_id = self.load_balancer.select_account(operation, exclude_accounts)
            
            if not account_id:
                print("✗ No hay cuentas disponibles con cuota suficiente")
                return None
            
            # Verificar cuota antes de usar
            required_units = self.load_balancer._get_operation_cost(operation)
            has_quota, quota_message = self.quota_monitor.is_quota_available(account_id, required_units)
            
            if not has_quota:
                print(f"⚠ Cuenta {account_id} sin cuota suficiente: {quota_message}")
                exclude_accounts.append(account_id)
                attempts += 1
                continue
            
            # Obtener cliente
            try:
                client = self.account_manager.get_account(account_id)
                
                if client:
                    # Registrar uso de cuota
                    self.quota_monitor.record_quota_usage(account_id, operation, required_units)
                    
                    # Remover de cuentas fallidas si estaba ahí
                    self.failed_accounts.discard(account_id)
                    
                    return client
                else:
                    print(f"⚠ No se pudo obtener cliente para cuenta {account_id}")
                    exclude_accounts.append(account_id)
                    attempts += 1
                    continue
            
            except Exception as e:
                print(f"✗ Error con cuenta {account_id}: {e}")
                self.failed_accounts.add(account_id)
                exclude_accounts.append(account_id)
                attempts += 1
                continue
        
        print("✗ No se pudo obtener una cuenta válida después de múltiples intentos")
        return None
    
    def handle_quota_exhausted(self, account_id: str):
        """
        Maneja cuando una cuenta se queda sin cuota.
        
        Args:
            account_id: ID de la cuenta agotada
        """
        print(f"⚠ Cuenta {account_id} agotada. Marcando para failover.")
        self.failed_accounts.add(account_id)
        
        # Verificar si hay otras cuentas disponibles
        available = self.account_manager.get_available_accounts()
        remaining = [acc for acc in available if acc not in self.failed_accounts]
        
        if not remaining:
            print("⚠ Todas las cuentas están agotadas o fallidas")
        else:
            print(f"✓ {len(remaining)} cuenta(s) aún disponible(s)")
    
    def reset_failed_accounts(self):
        """
        Resetea la lista de cuentas fallidas.
        Útil después de un período de tiempo o cuando se refresca la cuota.
        """
        self.failed_accounts.clear()
        print("✓ Lista de cuentas fallidas reseteada")
    
    def get_failed_accounts(self) -> List[str]:
        """
        Obtiene la lista de cuentas que han fallado.
        
        Returns:
            list: Lista de IDs de cuentas fallidas
        """
        return list(self.failed_accounts)
    
    def check_and_recover_accounts(self):
        """
        Verifica cuentas fallidas y las recupera si tienen cuota disponible.
        """
        recovered = []
        
        for account_id in list(self.failed_accounts):
            # Verificar si ahora tiene cuota disponible
            quota_info = self.quota_monitor.get_quota_usage_today(account_id)
            
            if quota_info['remaining_units'] > 100:  # Al menos 100 unidades disponibles
                self.failed_accounts.discard(account_id)
                recovered.append(account_id)
        
        if recovered:
            print(f"✓ Cuentas recuperadas: {', '.join(recovered)}")
        
        return recovered
