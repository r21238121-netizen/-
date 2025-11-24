import asyncio
import aiohttp
import logging
import json
import os
from typing import Dict
from config import config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.get_log_file()),
        logging.StreamHandler()
    ]
)

class ApiChecker:
    def __init__(self, api_keys: Dict[str, str]):
        self.api_keys = api_keys
        self.working_apis = {}
        self.failed_apis = {}
        self.timeout = config.get_check_timeout()  # Таймаут из конфига

    async def check_single_api(self, api_name: str, api_key: str, endpoint: str, headers: Dict) -> bool:
        """Проверяет один API-эндпоинт на работоспособность"""
        try:
            timeout = aiohttp.ClientTimeout(total=config.get_single_request_timeout())  # Таймаут на один запрос из конфига
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # Заменяем {key} в заголовках и URL на реальный ключ
                processed_endpoint = endpoint.format(key=api_key)
                processed_headers = {}
                for header_name, header_value in headers.items():
                    processed_headers[header_name] = header_value.format(key=api_key)
                
                async with session.get(processed_endpoint, headers=processed_headers) as response:
                    if response.status in [200, 401, 403]:  # 401 и 403 означают, что API доступен, но ключ невалиден
                        if response.status == 200:
                            logging.info(f"API {api_name} is working correctly")
                            return True
                        else:
                            logging.info(f"API {api_name} is reachable but returned status {response.status} (possibly invalid key)")
                            return True  # Считаем API рабочим, если он доступен, даже если ключ невалиден
                    else:
                        logging.warning(f"API {api_name} returned status {response.status}")
                        return False
        except asyncio.TimeoutError:
            logging.error(f"API {api_name} timed out")
            return False
        except Exception as e:
            logging.error(f"API {api_name} failed with error: {str(e)}")
            return False

    async def check_all_apis(self, endpoints_config: Dict[str, Dict]) -> Dict[str, Dict]:
        """Проверяет все API-эндпоинты"""
        tasks = []
        for api_name, config_item in endpoints_config.items():
            if api_name in self.api_keys and config_item.get('test_endpoint', True):
                task = self.check_single_api(
                    api_name,
                    self.api_keys[api_name], 
                    config_item['endpoint'], 
                    config_item.get('headers', {})
                )
                tasks.append((api_name, task))
        
        # Ограничиваем время выполнения проверки
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*[task for _, task in tasks], return_exceptions=True),
                timeout=self.timeout
            )
        except asyncio.TimeoutError:
            logging.error("API checking timed out after 2 minutes")
            # Возвращаем частичные результаты
            for api_name, _ in tasks:
                if api_name not in self.working_apis and api_name not in self.failed_apis:
                    self.failed_apis[api_name] = {
                        'key': self.api_keys[api_name],
                        'reason': 'Timeout during checking'
                    }
            return {'working': self.working_apis, 'failed': self.failed_apis}
        
        # Обрабатываем результаты
        for i, (api_name, _) in enumerate(tasks):
            if i < len(results) and isinstance(results[i], bool):
                if results[i]:
                    self.working_apis[api_name] = self.api_keys[api_name]
                else:
                    self.failed_apis[api_name] = {
                        'key': self.api_keys[api_name],
                        'reason': 'Failed during checking'
                    }
            elif i < len(results) and isinstance(results[i], Exception):
                self.failed_apis[api_name] = {
                    'key': self.api_keys[api_name],
                    'reason': str(results[i])
                }
        
        return {'working': self.working_apis, 'failed': self.failed_apis}

    def save_failed_apis(self):
        """Сохраняет неработающие API в файл erroApi.log"""
        error_log_file = config.get_error_log_file()
        with open(error_log_file, 'w') as f:
            for api_name, info in self.failed_apis.items():
                f.write(f"{api_name}: {info['reason']}\n")

def get_api_keys_from_user():
    """Получает API-ключи от пользователя"""
    print("Введите API-ключи для проверки:")
    api_keys = {}
    
    # Получаем список API из конфигурации
    apis_config = config.get_apis_config()
    apis_to_check = list(apis_config.keys())
    
    for api in apis_to_check:
        key = input(f"Введите API-ключ для {api} (или нажмите Enter для пропуска): ")
        if key.strip():
            api_keys[api] = key.strip()
        else:
            print(f"Пропускаем API {api}")
    
    return api_keys

def get_api_keys_from_config():
    """Получает API-ключи из файла конфигурации"""
    api_keys_file = "api_keys.json"
    if os.path.exists(api_keys_file):
        with open(api_keys_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print(f"Файл {api_keys_file} не найден. Введите API-ключи вручную или создайте файл с ключами.")
        return {}

def get_endpoints_config():
    """Конфигурация эндпоинтов для проверки из файла конфигурации"""
    return config.get_apis_config()

async def initialize_apis(use_config_file=False):
    """
    Основная функция инициализации API
    
    Args:
        use_config_file (bool): Если True, использует ключи из файла api_keys.json,
                               иначе запрашивает ввод у пользователя
    """
    print("=== API Key Initialization ===")
    
    # Получаем API-ключи
    if use_config_file:
        api_keys = get_api_keys_from_config()
    else:
        api_keys = get_api_keys_from_user()
    
    if not api_keys:
        print("Не введено ни одного API-ключа. Завершение.")
        return None
    
    # Получаем конфигурацию эндпоинтов
    endpoints_config = get_endpoints_config()
    
    # Создаем экземпляр проверяльщика API
    checker = ApiChecker(api_keys)
    
    print("Начинаем проверку API-эндпоинтов... (максимум 2 минуты)")
    
    # Выполняем проверку всех API
    results = await checker.check_all_apis(endpoints_config)
    
    # Выводим результаты
    print(f"\nРаботающие API: {list(results['working'].keys())}")
    print(f"Неработающие API: {list(results['failed'].keys())}")
    
    # Сохраняем неработающие API в файл
    checker.save_failed_apis()
    
    if results['working']:
        print("\nИнициализация завершена успешно. Начинаем работу с рабочими API...")
        return results['working']
    else:
        print("\nНе найдено ни одного рабочего API. Завершение работы.")
        return None

def main():
    """Основная функция - точка входа в систему инициализации API"""
    print("Система инициализации API")
    print("Выберите режим работы:")
    print("1. Ввод API-ключей вручную")
    print("2. Использование ключей из файла api_keys.json")
    
    choice = input("Введите номер режима (1 или 2): ").strip()
    
    if choice == "2":
        use_config = True
        print("Используем API-ключи из файла api_keys.json")
    else:
        use_config = False
        print("Будете вводить API-ключи вручную")
    
    # Запускаем инициализацию API
    working_apis = asyncio.run(initialize_apis(use_config_file=use_config))
    
    if working_apis:
        print("Система готова к работе с рабочими API")
        # Здесь можно продолжить выполнение основной логики приложения
        return working_apis
    else:
        print("Система не может продолжить работу без рабочих API")
        return None

if __name__ == "__main__":
    main()