"""
Analizador de contenido para detectar violaciones de reglas éticas.
"""
import re
import json
import os
from typing import Dict, List, Tuple


class ContentAnalyzer:
    """
    Analiza contenido de comentarios contra reglas éticas definidas.
    """
    
    def __init__(self, rules_file: str = 'ethics_rules.json'):
        """
        Inicializa el analizador con reglas desde archivo JSON.
        
        Args:
            rules_file: Ruta al archivo de reglas éticas
        """
        self.rules_file = rules_file
        self.rules = self._load_rules()
    
    def _load_rules(self) -> Dict:
        """
        Carga reglas desde archivo JSON.
        
        Returns:
            dict: Reglas de ética cargadas
        """
        # Si no existe el archivo, usar reglas por defecto
        if not os.path.exists(self.rules_file):
            print(f"⚠ Archivo {self.rules_file} no encontrado. Usando reglas por defecto.")
            return self._get_default_rules()
        
        try:
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                rules_data = json.load(f)
                return rules_data.get('ethics_rules', self._get_default_rules())
        except json.JSONDecodeError as e:
            print(f"✗ Error leyendo {self.rules_file}: {e}. Usando reglas por defecto.")
            return self._get_default_rules()
        except Exception as e:
            print(f"✗ Error cargando reglas: {e}. Usando reglas por defecto.")
            return self._get_default_rules()
    
    def _get_default_rules(self) -> Dict:
        """
        Retorna reglas por defecto si no se encuentra archivo de configuración.
        
        Returns:
            dict: Reglas por defecto
        """
        return {
            "banned_words": [],
            "banned_patterns": [],
            "max_length": 1000,
            "min_length": 1,
            "require_moderation": False,
            "auto_delete": True,
            "notification_on_delete": True,
            "case_sensitive": False
        }
    
    def analyze(self, comment_text: str) -> Tuple[bool, List[str]]:
        """
        Analiza un comentario contra las reglas éticas.
        
        Args:
            comment_text: Texto del comentario a analizar
            
        Returns:
            tuple: (viola_reglas: bool, razones: List[str])
        """
        violations = []
        text_to_check = comment_text
        
        # Convertir a minúsculas si no es case sensitive
        if not self.rules.get('case_sensitive', False):
            text_to_check = comment_text.lower()
        
        # Verificar longitud mínima
        if len(comment_text) < self.rules.get('min_length', 1):
            violations.append(f"Comentario muy corto (mínimo {self.rules.get('min_length')} caracteres)")
        
        # Verificar longitud máxima
        if len(comment_text) > self.rules.get('max_length', 1000):
            violations.append(f"Comentario muy largo (máximo {self.rules.get('max_length')} caracteres)")
        
        # Verificar palabras prohibidas
        banned_words = self.rules.get('banned_words', [])
        for word in banned_words:
            word_to_check = word.lower() if not self.rules.get('case_sensitive', False) else word
            if word_to_check in text_to_check:
                violations.append(f"Contiene palabra prohibida: '{word}'")
        
        # Verificar patrones prohibidos
        banned_patterns = self.rules.get('banned_patterns', [])
        for pattern in banned_patterns:
            try:
                flags = 0 if self.rules.get('case_sensitive', False) else re.IGNORECASE
                if re.search(pattern, comment_text, flags):
                    violations.append(f"Coincide con patrón prohibido: '{pattern}'")
            except re.error as e:
                print(f"⚠ Patrón regex inválido '{pattern}': {e}")
        
        return len(violations) > 0, violations
    
    def is_valid(self, comment_text: str) -> bool:
        """
        Verifica si un comentario es válido según las reglas.
        
        Args:
            comment_text: Texto del comentario
            
        Returns:
            bool: True si es válido, False si viola reglas
        """
        violates, _ = self.analyze(comment_text)
        return not violates
