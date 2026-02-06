"""
Sistema de protección para cuenta colectiva.
Implementa medidas de seguridad y validación.
"""
import os
import hashlib
from datetime import datetime
from typing import Optional, Dict, Tuple
from activity_monitor import ActivityMonitor
import config


class AccountProtection:
    """
    Sistema de protección para la cuenta colectiva.
    """
    
    def __init__(self):
        """
        Inicializa el sistema de protección.
        """
        self.monitor = ActivityMonitor()
        self.allowed_ips_file = os.path.join(config.DOWNLOAD_DIR, 'allowed_ips.json')
        self._ensure_allowed_ips_file()
    
    def _ensure_allowed_ips_file(self):
        """
        Asegura que el archivo de IPs permitidas existe.
        """
        if not os.path.exists(self.allowed_ips_file):
            with open(self.allowed_ips_file, 'w', encoding='utf-8') as f:
                import json
                json.dump([], f)
    
    def validate_action(self, action_type: str, details: Dict) -> Tuple[bool, Optional[str]]:
        """
        Valida si una acción está permitida antes de ejecutarla.
        
        Args:
            action_type: Tipo de acción
            details: Detalles de la acción
            
        Returns:
            tuple: (permitido: bool, mensaje: str o None)
        """
        # 1. Verificar rate limits
        allowed, message = self.monitor.check_rate_limits(action_type)
        if not allowed:
            return False, message
        
        # 2. Verificar actividad sospechosa
        suspicious = self.monitor.detect_suspicious_activity()
        if suspicious and len(suspicious) > 2:  # Más de 2 alertas
            return False, "Actividad sospechosa detectada. Acción bloqueada por seguridad."
        
        # 3. Validaciones específicas por tipo de acción
        if action_type == 'comment':
            # Validar contenido del comentario
            comment_text = details.get('text', '')
            if len(comment_text) < 1:
                return False, "Comentario vacío no permitido"
            if len(comment_text) > 5000:
                return False, "Comentario demasiado largo (máximo 5000 caracteres)"
        
        return True, None
    
    def log_and_protect(self, action_type: str, details: Dict) -> bool:
        """
        Registra una acción y aplica protección.
        
        Args:
            action_type: Tipo de acción
            details: Detalles de la acción
            
        Returns:
            bool: True si la acción fue registrada exitosamente
        """
        # Validar antes de registrar
        allowed, message = self.validate_action(action_type, details)
        
        if not allowed:
            print(f"✗ Acción bloqueada: {message}")
            # Registrar intento bloqueado
            self.monitor.log_action(f'{action_type}_blocked', {
                **details,
                'reason': message,
                'timestamp': datetime.now().isoformat()
            })
            return False
        
        # Registrar acción permitida
        self.monitor.log_action(action_type, details)
        return True
    
    def get_protection_status(self) -> Dict:
        """
        Obtiene el estado actual de protección.
        
        Returns:
            dict: Estado de protección
        """
        report = self.monitor.generate_report()
        suspicious = self.monitor.detect_suspicious_activity()
        
        return {
            'status': 'protected' if len(suspicious) == 0 else 'warning',
            'suspicious_count': len(suspicious),
            'recent_activity': report['total_actions_1h'],
            'rate_limits': report['rate_limit_status']
        }
