"""
Модуль управления конфигурацией и безопасным хранением API-ключей
"""
import os
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class Config:
    def __init__(self):
        self.config_dir = os.path.join(os.path.expanduser("~"), ".futures_scout")
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.credentials_file = os.path.join(self.config_dir, "credentials.enc")
        
        # Создаем директорию конфига если не существует
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Генерируем ключ шифрования
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _get_or_create_key(self):
        """Получение или создание ключа шифрования"""
        key_file = os.path.join(self.config_dir, "key.key")
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def save_credentials(self, api_key, secret_key):
        """Сохранение зашифрованных API-ключей"""
        credentials = {
            "api_key": api_key,
            "secret_key": secret_key
        }
        
        encrypted_data = self.cipher.encrypt(json.dumps(credentials).encode())
        
        with open(self.credentials_file, 'wb') as f:
            f.write(encrypted_data)
    
    def get_saved_credentials(self):
        """Получение сохраненных API-ключей"""
        if not os.path.exists(self.credentials_file):
            return None, None
        
        with open(self.credentials_file, 'rb') as f:
            encrypted_data = f.read()
        
        try:
            decrypted_data = self.cipher.decrypt(encrypted_data)
            credentials = json.loads(decrypted_data.decode())
            return credentials["api_key"], credentials["secret_key"]
        except:
            return None, None
    
    def has_saved_credentials(self):
        """Проверка наличия сохраненных API-ключей"""
        api_key, secret_key = self.get_saved_credentials()
        return api_key is not None and secret_key is not None
    
    def clear_credentials(self):
        """Очистка сохраненных API-ключей"""
        if os.path.exists(self.credentials_file):
            os.remove(self.credentials_file)