"""
Sistema de ofuscación para proteger datos personales y privacidad.
Genera nombres aleatorios y ofusca información sensible.
"""
import random
import string
import hashlib
import json
import os
from typing import Dict, Optional
from datetime import datetime


class DataObfuscator:
    """
    Ofusca datos personales y genera identificadores aleatorios.
    """
    
    def __init__(self):
        """
        Inicializa el ofuscador.
        """
        self.mapping_file = 'obfuscation_mapping.json'
        self.mapping = self._load_mapping()
    
    def _load_mapping(self) -> Dict:
        """
        Carga el mapeo de datos ofuscados.
        
        Returns:
            dict: Mapeo de datos reales a ofuscados
        """
        if os.path.exists(self.mapping_file):
            try:
                with open(self.mapping_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_mapping(self):
        """
        Guarda el mapeo de datos ofuscados.
        """
        try:
            with open(self.mapping_file, 'w', encoding='utf-8') as f:
                json.dump(self.mapping, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠ Error guardando mapeo de ofuscación: {e}")
    
    def generate_random_name(self, prefix: str = "user") -> str:
        """
        Genera un nombre aleatorio genérico.
        
        Args:
            prefix: Prefijo para el nombre
            
        Returns:
            str: Nombre aleatorio
        """
        # Lista de adjetivos y sustantivos genéricos
        adjectives = [
            "digital", "virtual", "automated", "system", "bot", "service",
            "collective", "shared", "public", "generic", "standard", "common"
        ]
        nouns = [
            "account", "user", "profile", "entity", "instance", "node",
            "client", "agent", "service", "bot", "system", "unit"
        ]
        
        adj = random.choice(adjectives)
        noun = random.choice(nouns)
        number = random.randint(1000, 9999)
        
        return f"{adj}_{noun}_{number}"
    
    def generate_random_email_domain(self) -> str:
        """
        Genera un dominio de email genérico.
        
        Returns:
            str: Dominio aleatorio
        """
        domains = [
            "example.com", "test.com", "demo.org", "sample.net",
            "generic.com", "temp.org", "placeholder.net"
        ]
        return random.choice(domains)
    
    def generate_account_name(self) -> str:
        """
        Genera un nombre de cuenta completamente genérico.
        
        Returns:
            str: Nombre de cuenta ofuscado
        """
        return self.generate_random_name("account")
    
    def obfuscate_email(self, email: str) -> str:
        """
        Ofusca un email manteniendo el formato.
        
        Args:
            email: Email real
            
        Returns:
            str: Email ofuscado
        """
        if email in self.mapping.get('emails', {}):
            return self.mapping['emails'][email]
        
        # Generar email ofuscado
        local_part = email.split('@')[0] if '@' in email else 'user'
        domain = email.split('@')[1] if '@' in email else 'example.com'
        
        # Crear hash corto del email real
        hash_obj = hashlib.md5(email.encode())
        hash_short = hash_obj.hexdigest()[:8]
        
        # Generar email ofuscado
        obfuscated_local = f"user_{hash_short}"
        obfuscated_domain = self.generate_random_email_domain()
        obfuscated_email = f"{obfuscated_local}@{obfuscated_domain}"
        
        # Guardar mapeo
        if 'emails' not in self.mapping:
            self.mapping['emails'] = {}
        self.mapping['emails'][email] = obfuscated_email
        self._save_mapping()
        
        return obfuscated_email
    
    def obfuscate_client_id(self, client_id: str) -> str:
        """
        Ofusca un Client ID manteniendo solo parte visible.
        
        Args:
            client_id: Client ID real
            
        Returns:
            str: Client ID parcialmente ofuscado
        """
        if not client_id:
            return "***HIDDEN***"
        
        # Mostrar solo primeros y últimos caracteres
        if len(client_id) > 20:
            visible_start = client_id[:8]
            visible_end = client_id[-4:]
            return f"{visible_start}...{visible_end}"
        else:
            return "***" + "*" * (len(client_id) - 6) + "***"
    
    def obfuscate_client_secret(self, client_secret: str) -> str:
        """
        Ofusca completamente un Client Secret.
        
        Args:
            client_secret: Client Secret real
            
        Returns:
            str: Client Secret ofuscado
        """
        if not client_secret:
            return "***HIDDEN***"
        
        # Solo mostrar primeros 4 caracteres
        if len(client_secret) > 4:
            return client_secret[:4] + "*" * (len(client_secret) - 4)
        else:
            return "*" * len(client_secret)
    
    def generate_safe_account_name(self) -> Dict[str, str]:
        """
        Genera un conjunto completo de datos para una cuenta segura.
        
        Returns:
            dict: Datos de cuenta ofuscados
        """
        account_name = self.generate_account_name()
        email_local = f"{account_name}_{random.randint(100, 999)}"
        email_domain = self.generate_random_email_domain()
        email = f"{email_local}@{email_domain}"
        
        return {
            'account_name': account_name,
            'suggested_email': email,
            'display_name': f"{account_name.replace('_', ' ').title()}",
            'description': "Generic YouTube bot account"
        }
    
    def mask_sensitive_data(self, text: str, sensitive_patterns: list = None) -> str:
        """
        Enmascara datos sensibles en un texto.
        
        Args:
            text: Texto a enmascarar
            sensitive_patterns: Patrones a buscar (opcional)
            
        Returns:
            str: Texto con datos enmascarados
        """
        if sensitive_patterns is None:
            sensitive_patterns = [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Emails
                r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
                r'\b\d{10,}\b',  # Números largos (posibles IDs)
            ]
        
        import re
        masked_text = text
        
        # Enmascarar emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        masked_text = re.sub(email_pattern, lambda m: self.obfuscate_email(m.group()), masked_text)
        
        # Enmascarar Client IDs (formato típico)
        client_id_pattern = r'\b\d+-[a-zA-Z0-9_-]+\.apps\.googleusercontent\.com\b'
        masked_text = re.sub(client_id_pattern, lambda m: self.obfuscate_client_id(m.group()), masked_text)
        
        return masked_text
    
    def get_obfuscated_info(self) -> Dict:
        """
        Obtiene información sobre qué datos están ofuscados.
        
        Returns:
            dict: Información de ofuscación
        """
        return {
            'total_emails_obfuscated': len(self.mapping.get('emails', {})),
            'mapping_file': self.mapping_file,
            'obfuscation_active': True
        }


class AccountNameGenerator:
    """
    Generador de nombres de cuenta genéricos y seguros.
    """
    
    @staticmethod
    def generate_youtube_account_name() -> Dict[str, str]:
        """
        Genera un nombre de cuenta de YouTube genérico.
        
        Returns:
            dict: Información de cuenta sugerida
        """
        # Nombres genéricos que no revelan información personal
        generic_names = [
            "ContentBot", "VideoService", "MediaCollective", "StreamHelper",
            "DigitalAssistant", "AutoService", "GenericBot", "SystemAccount",
            "PublicService", "SharedAccount", "CommonBot", "StandardService"
        ]
        
        number = random.randint(100, 999)
        name = random.choice(generic_names)
        full_name = f"{name}{number}"
        
        return {
            'youtube_channel_name': full_name,
            'google_account_name': full_name,
            'display_name': full_name,
            'suggested_email_prefix': full_name.lower().replace(' ', ''),
            'description': "Generic automated service account"
        }
    
    @staticmethod
    def generate_project_name() -> str:
        """
        Genera un nombre de proyecto genérico para Google Cloud.
        
        Returns:
            str: Nombre de proyecto
        """
        prefixes = ["youtube", "video", "media", "content", "stream"]
        suffixes = ["bot", "service", "api", "client", "tool"]
        
        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)
        number = random.randint(100, 999)
        
        return f"{prefix}-{suffix}-{number}"

