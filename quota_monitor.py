"""
Monitor de cuota para múltiples cuentas.
Rastrea el uso de cuota de cada cuenta y alerta cuando se acerca al límite.
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
from account_manager import AccountManager
import config


class QuotaMonitor:
    """
    Monitorea el uso de cuota de cada cuenta.
    """
    
    def __init__(self, account_manager: AccountManager):
        """
        Inicializa el monitor de cuota.
        
        Args:
            account_manager: Gestor de cuentas
        """
        self.account_manager = account_manager
        self.quota_log_file = os.path.join(config.DOWNLOAD_DIR, 'quota_usage.json')
        self._ensure_quota_log()
    
    def _ensure_quota_log(self):
        """
        Asegura que el archivo de log de cuota existe.
        """
        if not os.path.exists(self.quota_log_file):
            with open(self.quota_log_file, 'w', encoding='utf-8') as f:
                json.dump({}, f)
    
    def _load_quota_log(self) -> Dict:
        """
        Carga el log de uso de cuota.
        
        Returns:
            dict: Log de cuota
        """
        try:
            with open(self.quota_log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_quota_log(self, quota_log: Dict):
        """
        Guarda el log de uso de cuota.
        
        Args:
            quota_log: Log de cuota a guardar
        """
        try:
            with open(self.quota_log_file, 'w', encoding='utf-8') as f:
                json.dump(quota_log, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠ Error guardando log de cuota: {e}")
    
    def record_quota_usage(self, account_id: str, operation: str, units: int):
        """
        Registra el uso de cuota de una operación.
        
        Args:
            account_id: ID de la cuenta
            operation: Tipo de operación ('comment', 'stats', 'list_comments')
            units: Unidades de cuota usadas
        """
        quota_log = self._load_quota_log()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        if account_id not in quota_log:
            quota_log[account_id] = {}
        
        if today not in quota_log[account_id]:
            quota_log[account_id][today] = {
                'total_units': 0,
                'operations': defaultdict(int),
                'last_updated': datetime.now().isoformat()
            }
        
        quota_log[account_id][today]['total_units'] += units
        quota_log[account_id][today]['operations'][operation] += units
        quota_log[account_id][today]['last_updated'] = datetime.now().isoformat()
        
        self._save_quota_log(quota_log)
    
    def get_quota_usage_today(self, account_id: str) -> Dict:
        """
        Obtiene el uso de cuota de hoy para una cuenta.
        
        Args:
            account_id: ID de la cuenta
            
        Returns:
            dict: Uso de cuota de hoy
        """
        quota_log = self._load_quota_log()
        today = datetime.now().strftime('%Y-%m-%d')
        
        account_data = quota_log.get(account_id, {})
        today_data = account_data.get(today, {
            'total_units': 0,
            'operations': {}
        })
        
        return {
            'account_id': account_id,
            'date': today,
            'total_units': today_data.get('total_units', 0),
            'operations': dict(today_data.get('operations', {})),
            'remaining_units': 10000 - today_data.get('total_units', 0),
            'percentage_used': (today_data.get('total_units', 0) / 10000) * 100
        }
    
    def get_all_accounts_quota(self) -> List[Dict]:
        """
        Obtiene el uso de cuota de todas las cuentas hoy.
        
        Returns:
            list: Lista de uso de cuota por cuenta
        """
        accounts = self.account_manager.get_available_accounts()
        return [self.get_quota_usage_today(acc_id) for acc_id in accounts]
    
    def is_quota_available(self, account_id: str, required_units: int) -> tuple[bool, Optional[str]]:
        """
        Verifica si hay cuota disponible para una operación.
        
        Args:
            account_id: ID de la cuenta
            required_units: Unidades requeridas
            
        Returns:
            tuple: (disponible: bool, mensaje: str o None)
        """
        usage = self.get_quota_usage_today(account_id)
        remaining = usage['remaining_units']
        
        if remaining < required_units:
            return False, f"Cuota insuficiente: {remaining}/{required_units} unidades disponibles"
        
        # Alerta si queda menos del 10%
        if remaining < 1000:
            return True, f"⚠ Cuota baja: {remaining} unidades restantes"
        
        return True, None
    
    def find_account_with_quota(self, required_units: int, exclude_accounts: List[str] = None) -> Optional[str]:
        """
        Encuentra una cuenta con cuota disponible.
        
        Args:
            required_units: Unidades requeridas
            exclude_accounts: Lista de IDs de cuentas a excluir
            
        Returns:
            str: ID de cuenta disponible o None
        """
        if exclude_accounts is None:
            exclude_accounts = []
        
        accounts = self.account_manager.get_available_accounts()
        
        for account_id in accounts:
            if account_id in exclude_accounts:
                continue
            
            available, _ = self.is_quota_available(account_id, required_units)
            if available:
                return account_id
        
        return None
    
    def print_quota_report(self):
        """
        Imprime un reporte de cuota de todas las cuentas.
        """
        all_quota = self.get_all_accounts_quota()
        
        print("\n" + "="*70)
        print("REPORTE DE CUOTA - MÚLTIPLES CUENTAS")
        print("="*70)
        
        if not all_quota:
            print("\n⚠ No hay cuentas configuradas.")
            return
        
        total_used = 0
        total_remaining = 0
        
        for quota in all_quota:
            print(f"\n📊 Cuenta: {quota['account_id']}")
            print(f"   Unidades usadas hoy: {quota['total_units']:,} / 10,000")
            print(f"   Unidades restantes: {quota['remaining_units']:,}")
            print(f"   Porcentaje usado: {quota['percentage_used']:.1f}%")
            
            if quota['operations']:
                print(f"   Operaciones:")
                for op, units in quota['operations'].items():
                    print(f"     - {op}: {units} unidades")
            
            # Estado
            if quota['remaining_units'] < 1000:
                print(f"   ⚠️  ESTADO: Cuota baja")
            elif quota['remaining_units'] < 5000:
                print(f"   ⚠️  ESTADO: Cuota media")
            else:
                print(f"   ✅ ESTADO: Cuota disponible")
            
            total_used += quota['total_units']
            total_remaining += quota['remaining_units']
        
        print("\n" + "-"*70)
        print(f"📈 TOTAL:")
        print(f"   Unidades usadas: {total_used:,}")
        print(f"   Unidades restantes: {total_remaining:,}")
        print(f"   Total disponible: {len(all_quota) * 10000:,}")
        print("="*70 + "\n")
