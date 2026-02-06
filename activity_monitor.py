"""
Sistema de monitoreo de actividad para cuenta colectiva.
Registra y monitorea todas las acciones realizadas con la cuenta.
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import config

# Importar ofuscador si está disponible
try:
    from obfuscator import DataObfuscator
    OBFUSCATION_AVAILABLE = True
except ImportError:
    OBFUSCATION_AVAILABLE = False
    DataObfuscator = None


class ActivityMonitor:
    """
    Monitorea y registra toda la actividad de la cuenta colectiva.
    """
    
    def __init__(self):
        """
        Inicializa el monitor de actividad.
        """
        self.log_file = os.path.join(config.DOWNLOAD_DIR, 'activity_log.json')
        self._ensure_log_file()
        
        # Inicializar ofuscador si está disponible
        if OBFUSCATION_AVAILABLE and DataObfuscator:
            self.obfuscator = DataObfuscator()
        else:
            self.obfuscator = None
    
    def _ensure_log_file(self):
        """
        Asegura que el archivo de log existe.
        """
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def log_action(self, action_type: str, details: Dict):
        """
        Registra una acción en el log de actividad.
        
        Args:
            action_type: Tipo de acción ('comment', 'download', 'stats', etc.)
            details: Diccionario con detalles de la acción
        """
        # Ofuscar datos sensibles antes de guardar
        safe_details = self._obfuscate_details(details) if self.obfuscator else details
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'details': safe_details
        }
        
        try:
            # Leer log existente
            with open(self.log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            # Agregar nueva entrada
            logs.append(log_entry)
            
            # Mantener solo últimas 10000 entradas
            if len(logs) > 10000:
                logs = logs[-10000:]
            
            # Guardar log
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            print(f"⚠ Error guardando log de actividad: {e}")
    
    def get_recent_activity(self, hours: int = 24) -> List[Dict]:
        """
        Obtiene actividad reciente de las últimas N horas.
        
        Args:
            hours: Número de horas hacia atrás
            
        Returns:
            list: Lista de actividades recientes
        """
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            recent_activities = []
            for log_entry in logs:
                log_time = datetime.fromisoformat(log_entry['timestamp'])
                if log_time >= cutoff_time:
                    recent_activities.append(log_entry)
            
            return recent_activities
        
        except Exception as e:
            print(f"⚠ Error leyendo log de actividad: {e}")
            return []
    
    def check_rate_limits(self, action_type: str) -> Tuple[bool, Optional[str]]:
        """
        Verifica si una acción excede los límites de rate limiting.
        
        Args:
            action_type: Tipo de acción a verificar
            
        Returns:
            tuple: (permitido: bool, mensaje: str o None)
        """
        recent_activities = self.get_recent_activity(hours=24)
        
        # Contar acciones por tipo en las últimas 24 horas
        actions_last_24h = defaultdict(int)
        actions_last_hour = defaultdict(int)
        
        one_hour_ago = datetime.now() - timedelta(hours=1)
        
        for activity in recent_activities:
            act_type = activity.get('action_type')
            act_time = datetime.fromisoformat(activity['timestamp'])
            
            actions_last_24h[act_type] += 1
            
            if act_time >= one_hour_ago:
                actions_last_hour[act_type] += 1
        
        # Verificar límites diarios
        daily_limit = config.MAX_COMMENTS_PER_DAY if action_type == 'comment' else 1000
        if actions_last_24h[action_type] >= daily_limit:
            return False, f"Límite diario alcanzado: {actions_last_24h[action_type]}/{daily_limit}"
        
        # Verificar límites horarios
        hourly_limit = config.MAX_COMMENTS_PER_HOUR if action_type == 'comment' else 100
        if actions_last_hour[action_type] >= hourly_limit:
            return False, f"Límite horario alcanzado: {actions_last_hour[action_type]}/{hourly_limit}"
        
        return True, None
    
    def detect_suspicious_activity(self) -> List[Dict]:
        """
        Detecta actividad sospechosa en el log.
        
        Returns:
            list: Lista de actividades sospechosas detectadas
        """
        suspicious = []
        recent_activities = self.get_recent_activity(hours=1)
        
        # Agrupar por tipo de acción
        action_counts = defaultdict(int)
        for activity in recent_activities:
            action_counts[activity['action_type']] += 1
        
        # Detectar patrones sospechosos
        # 1. Muchas acciones en poco tiempo
        total_actions = sum(action_counts.values())
        if total_actions > 50:  # Más de 50 acciones en 1 hora
            suspicious.append({
                'type': 'high_frequency',
                'message': f'Actividad muy alta: {total_actions} acciones en la última hora',
                'count': total_actions
            })
        
        # 2. Muchos comentarios en poco tiempo
        if action_counts.get('comment', 0) > 20:
            suspicious.append({
                'type': 'comment_spam',
                'message': f'Muchos comentarios: {action_counts["comment"]} en la última hora',
                'count': action_counts['comment']
            })
        
        return suspicious
    
    def generate_report(self) -> Dict:
        """
        Genera un reporte de actividad.
        
        Returns:
            dict: Reporte de actividad
        """
        recent_24h = self.get_recent_activity(hours=24)
        recent_1h = self.get_recent_activity(hours=1)
        
        # Contar acciones por tipo
        actions_24h = defaultdict(int)
        actions_1h = defaultdict(int)
        
        for activity in recent_24h:
            actions_24h[activity['action_type']] += 1
        
        for activity in recent_1h:
            actions_1h[activity['action_type']] += 1
        
        # Detectar actividad sospechosa
        suspicious = self.detect_suspicious_activity()
        
        return {
            'period': '24 horas',
            'total_actions_24h': len(recent_24h),
            'total_actions_1h': len(recent_1h),
            'actions_by_type_24h': dict(actions_24h),
            'actions_by_type_1h': dict(actions_1h),
            'suspicious_activities': suspicious,
            'rate_limit_status': {
                'comments_24h': f"{actions_24h['comment']}/{config.MAX_COMMENTS_PER_DAY}",
                'comments_1h': f"{actions_1h['comment']}/{config.MAX_COMMENTS_PER_HOUR}"
            }
        }
    
    def print_report(self):
        """
        Imprime un reporte de actividad en consola.
        """
        report = self.generate_report()
        
        print("\n" + "="*60)
        print("REPORTE DE ACTIVIDAD - CUENTA COLECTIVA")
        print("="*60)
        print(f"\n📊 Actividad últimas 24 horas: {report['total_actions_24h']} acciones")
        print(f"📊 Actividad última hora: {report['total_actions_1h']} acciones")
        
        if report['actions_by_type_24h']:
            print("\n📋 Desglose por tipo (24h):")
            for action_type, count in report['actions_by_type_24h'].items():
                print(f"   - {action_type}: {count}")
        
        if report['suspicious_activities']:
            print("\n⚠️  ACTIVIDAD SOSPECHOSA DETECTADA:")
            for suspicious in report['suspicious_activities']:
                print(f"   ⚠ {suspicious['message']}")
        else:
            print("\n✓ No se detectó actividad sospechosa")
        
        print("\n🔒 Estado de límites:")
        print(f"   Comentarios (24h): {report['rate_limit_status']['comments_24h']}")
        print(f"   Comentarios (1h): {report['rate_limit_status']['comments_1h']}")
        print("="*60 + "\n")
    
    def _obfuscate_details(self, details: Dict) -> Dict:
        """
        Ofusca datos sensibles en los detalles de una acción.
        
        Args:
            details: Detalles originales
            
        Returns:
            dict: Detalles con datos ofuscados
        """
        if not self.obfuscator:
            return details
        
        safe_details = details.copy()
        
        # Ofuscar emails si aparecen
        for key, value in safe_details.items():
            if isinstance(value, str) and '@' in value:
                safe_details[key] = self.obfuscator.obfuscate_email(value)
            elif isinstance(value, str) and 'apps.googleusercontent.com' in value:
                safe_details[key] = self.obfuscator.obfuscate_client_id(value)
        
        return safe_details
