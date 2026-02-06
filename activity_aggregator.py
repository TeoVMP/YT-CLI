"""
Agregador de actividad para múltiples cuentas.
Consolida logs de todas las cuentas en un solo reporte.
"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict
from collections import defaultdict
from account_manager import AccountManager
import config


class ActivityAggregator:
    """
    Agrega y consolida actividad de múltiples cuentas.
    """
    
    def __init__(self, account_manager: AccountManager):
        """
        Inicializa el agregador de actividad.
        
        Args:
            account_manager: Gestor de cuentas
        """
        self.account_manager = account_manager
        self.activity_log_dir = config.DOWNLOAD_DIR
    
    def _load_account_activity(self, account_id: str) -> List[Dict]:
        """
        Carga actividad de una cuenta específica.
        
        Args:
            account_id: ID de la cuenta
            
        Returns:
            list: Lista de actividades
        """
        # Buscar archivo de log de actividad para esta cuenta
        log_file = os.path.join(self.activity_log_dir, f'activity_log_{account_id}.json')
        
        if not os.path.exists(log_file):
            # Intentar con el log general
            log_file = os.path.join(self.activity_log_dir, 'activity_log.json')
        
        if not os.path.exists(log_file):
            return []
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                activities = json.load(f)
                
                # Si es un diccionario con estructura específica, extraer actividades
                if isinstance(activities, dict):
                    if 'activities' in activities:
                        activities = activities['activities']
                    elif 'items' in activities:
                        activities = activities['items']
                
                # Agregar account_id a cada actividad
                for activity in activities:
                    activity['account_id'] = account_id
                
                return activities if isinstance(activities, list) else []
        
        except Exception as e:
            print(f"⚠ Error cargando actividad de {account_id}: {e}")
            return []
    
    def aggregate_all_activity(self, hours: int = 24) -> List[Dict]:
        """
        Agrega actividad de todas las cuentas.
        
        Args:
            hours: Número de horas hacia atrás para buscar actividad
            
        Returns:
            list: Lista consolidada de actividades
        """
        accounts = self.account_manager.get_available_accounts()
        all_activities = []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        for account_id in accounts:
            activities = self._load_account_activity(account_id)
            
            # Filtrar por tiempo
            for activity in activities:
                try:
                    activity_time = datetime.fromisoformat(activity.get('timestamp', ''))
                    if activity_time >= cutoff_time:
                        all_activities.append(activity)
                except:
                    # Si no se puede parsear la fecha, incluirla de todas formas
                    all_activities.append(activity)
        
        # Ordenar por timestamp
        all_activities.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return all_activities
    
    def get_aggregated_stats(self, hours: int = 24) -> Dict:
        """
        Obtiene estadísticas agregadas de todas las cuentas.
        
        Args:
            hours: Número de horas hacia atrás
            
        Returns:
            dict: Estadísticas agregadas
        """
        activities = self.aggregate_all_activity(hours)
        
        stats = {
            'total_activities': len(activities),
            'by_account': defaultdict(int),
            'by_type': defaultdict(int),
            'by_hour': defaultdict(int),
            'time_range': {
                'start': None,
                'end': None
            }
        }
        
        for activity in activities:
            account_id = activity.get('account_id', 'unknown')
            action_type = activity.get('action_type', 'unknown')
            timestamp = activity.get('timestamp', '')
            
            stats['by_account'][account_id] += 1
            stats['by_type'][action_type] += 1
            
            # Agrupar por hora
            try:
                activity_time = datetime.fromisoformat(timestamp)
                hour_key = activity_time.strftime('%Y-%m-%d %H:00')
                stats['by_hour'][hour_key] += 1
            except:
                pass
        
        # Obtener rango de tiempo
        if activities:
            try:
                first_time = datetime.fromisoformat(activities[-1].get('timestamp', ''))
                last_time = datetime.fromisoformat(activities[0].get('timestamp', ''))
                stats['time_range']['start'] = first_time.isoformat()
                stats['time_range']['end'] = last_time.isoformat()
            except:
                pass
        
        return stats
    
    def print_aggregated_report(self, hours: int = 24):
        """
        Imprime un reporte agregado de todas las cuentas.
        
        Args:
            hours: Número de horas hacia atrás
        """
        stats = self.get_aggregated_stats(hours)
        activities = self.aggregate_all_activity(hours)
        
        print("\n" + "="*70)
        print(f"REPORTE AGREGADO - TODAS LAS CUENTAS ({hours}h)")
        print("="*70)
        
        print(f"\n📊 Total de actividades: {stats['total_activities']}")
        
        if stats['by_account']:
            print("\n📋 Por cuenta:")
            for account_id, count in sorted(stats['by_account'].items(), key=lambda x: x[1], reverse=True):
                print(f"   {account_id}: {count} actividades")
        
        if stats['by_type']:
            print("\n🔧 Por tipo de acción:")
            for action_type, count in sorted(stats['by_type'].items(), key=lambda x: x[1], reverse=True):
                print(f"   {action_type}: {count}")
        
        if stats['by_hour']:
            print("\n⏰ Por hora:")
            for hour, count in sorted(stats['by_hour'].items()):
                print(f"   {hour}: {count} actividades")
        
        if activities:
            print("\n📝 Actividades recientes (últimas 10):")
            for i, activity in enumerate(activities[:10], 1):
                account_id = activity.get('account_id', 'unknown')
                action_type = activity.get('action_type', 'unknown')
                timestamp = activity.get('timestamp', '')
                
                # Formatear timestamp
                try:
                    dt = datetime.fromisoformat(timestamp)
                    time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    time_str = timestamp
                
                print(f"   {i}. [{account_id}] {action_type} - {time_str}")
        
        print("="*70 + "\n")
    
    def export_aggregated_log(self, output_file: str = None, hours: int = 24):
        """
        Exporta log agregado a un archivo.
        
        Args:
            output_file: Archivo de salida (opcional)
            hours: Número de horas hacia atrás
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.activity_log_dir, f'aggregated_activity_{timestamp}.json')
        
        activities = self.aggregate_all_activity(hours)
        stats = self.get_aggregated_stats(hours)
        
        export_data = {
            'exported_at': datetime.now().isoformat(),
            'time_range_hours': hours,
            'statistics': stats,
            'activities': activities
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Log agregado exportado a: {output_file}")
            return output_file
        
        except Exception as e:
            print(f"✗ Error exportando log agregado: {e}")
            return None
