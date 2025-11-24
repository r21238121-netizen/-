import asyncio
import aiohttp
import logging
from typing import List, Dict, Optional
import time
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

    async def check_single_api(self, api_name: str, api_key: str, endpoint: str, headers: Optional[Dict] = None) -> bool:
        """Проверяет один API-эндпоинт на работоспособность"""
        try:
            timeout = aiohttp.ClientTimeout(total=config.get_single_request_timeout())  # Таймаут на один запрос из конфига
            async with aiohttp.ClientSession(timeout=timeout) as session:
                request_headers = headers or {}
                # Заменяем {key} в заголовках на реальный ключ
                processed_headers = {}
                for header_name, header_value in request_headers.items():
                    processed_headers[header_name] = header_value.format(key=api_key)
                
                async with session.get(endpoint, headers=processed_headers) as response:
                    if response.status == 200:
                        logging.info(f"API {api_name} is working")
                        return True
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
        start_time = time.time()
        
        tasks = []
        for api_name, config in endpoints_config.items():
            if api_name in self.api_keys:
                task = self.check_single_api(
                    api_name, 
                    self.api_keys[api_name], 
                    config['endpoint'], 
                    config.get('headers')
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

def get_api_keys():
    """Получает API-ключи от пользователя"""
    print("Введите API-ключи для проверки:")
    api_keys = {}
    
    # Пример получения ключей - в реальности это может быть настраиваемо
    apis_to_check = [
        "openai",
        "anthropic", 
        "google",
        "cohere",
        "huggingface"
    ]
    
    for api in apis_to_check:
        key = input(f"Введите API-ключ для {api}: ")
        if key.strip():
            api_keys[api] = key.strip()
    
    return api_keys

def get_endpoints_config():
    """Конфигурация эндпоинтов для проверки из файла конфигурации"""
    return config.get_apis_config()

async def main():
    print("=== API Key Initialization ===")
    
    # Получаем API-ключи от пользователя
    api_keys = get_api_keys()
    
    if not api_keys:
        print("Не введено ни одного API-ключа. Завершение.")
        return
    
    # Получаем конфигурацию эндпоинтов
    endpoints_config = get_endpoints_config()
    
    # Обновляем эндпоинты Google, так как ему нужен ключ в URL
    for api_name in endpoints_config:
        if api_name == "google" and api_name in api_keys:
            endpoints_config[api_name]["endpoint"] = endpoints_config[api_name]["endpoint"].format(key=api_keys[api_name])
    
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
        # Здесь будет основная логика работы с рабочими API
        return results['working']
    else:
        print("\nНе найдено ни одного рабочего API. Завершение работы.")
        return {}

if __name__ == "__main__":
    working_apis = asyncio.run(main())