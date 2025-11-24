import json
import os
from typing import Dict, List, Optional

class Config:
    def __init__(self, config_file: str = "api_config.json"):
        self.config_file = config_file
        self.config_data = self.load_config()
    
    def load_config(self) -> Dict:
        """Загружает конфигурацию из файла или создает стандартную"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Создаем стандартную конфигурацию
            default_config = {
                "apis": {
                    "openai": {
                        "endpoint": "https://api.openai.com/v1/models",
                        "headers": {
                            "Authorization": "Bearer {key}",
                            "Content-Type": "application/json"
                        },
                        "test_endpoint": True
                    },
                    "anthropic": {
                        "endpoint": "https://api.anthropic.com/v1/messages",  # Обновленный эндпоинт
                        "headers": {
                            "x-api-key": "{key}",
                            "Content-Type": "application/json",
                            "anthropic-version": "2023-06-01"
                        },
                        "test_endpoint": True
                    },
                    "google": {
                        "endpoint": "https://generativelanguage.googleapis.com/v1beta/models?key={key}",
                        "headers": {
                            "Content-Type": "application/json"
                        },
                        "test_endpoint": True
                    },
                    "cohere": {
                        "endpoint": "https://api.cohere.ai/v1/models",
                        "headers": {
                            "Authorization": "Bearer {key}",
                            "Content-Type": "application/json"
                        },
                        "test_endpoint": True
                    },
                    "huggingface": {
                        "endpoint": "https://api-inference.huggingface.co/models",
                        "headers": {
                            "Authorization": "Bearer {key}",
                            "Content-Type": "application/json"
                        },
                        "test_endpoint": True
                    }
                },
                "check_timeout": 120,  # 2 минуты на общую проверку
                "single_request_timeout": 10,  # 10 секунд на один запрос
                "log_file": "api_check.log",
                "error_log_file": "erroApi.log"
            }
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config: Dict):
        """Сохраняет конфигурацию в файл"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def get_apis_config(self) -> Dict:
        """Возвращает конфигурацию API"""
        return self.config_data.get("apis", {})
    
    def get_check_timeout(self) -> int:
        """Возвращает таймаут проверки в секундах"""
        return self.config_data.get("check_timeout", 120)
    
    def get_single_request_timeout(self) -> int:
        """Возвращает таймаут одного запроса в секундах"""
        return self.config_data.get("single_request_timeout", 10)
    
    def get_log_file(self) -> str:
        """Возвращает имя файла лога"""
        return self.config_data.get("log_file", "api_check.log")
    
    def get_error_log_file(self) -> str:
        """Возвращает имя файла с ошибками API"""
        return self.config_data.get("error_log_file", "erroApi.log")

# Глобальный экземпляр конфига
config = Config()