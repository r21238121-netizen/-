import asyncio
import aiohttp
import logging
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
        for api_name, config in endpoints_config.items():
            if api_name in self.api_keys and config.get('test_endpoint', True):
                task = self.check_single_api(
                    api_name,
                    self.api_keys[api_name], 
                    config['endpoint'], 
                    config.get('headers', {})
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

def get_test_api_keys():
    """Возвращает тестовые API-ключи (фиктивные для проверки системы)"""
    print("Используем тестовые ключи для проверки системы...")
    return {
        "openai": "fake_openai_key",
        "anthropic": "fake_anthropic_key", 
        "google": "fake_google_key",
        "cohere": "fake_cohere_key",
        "huggingface": "fake_huggingface_key"
    }

def get_endpoints_config():
    """Конфигурация эндпоинтов для проверки из файла конфигурации"""
    return config.get_apis_config()

async def main():
    print("=== API Key Initialization (Test Mode) ===")
    
    # Получаем тестовые API-ключи
    api_keys = get_test_api_keys()
    
    if not api_keys:
        print("Не введено ни одного API-ключа. Завершение.")
        return
    
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
        return {}

if __name__ == "__main__":
    working_apis = asyncio.run(main())