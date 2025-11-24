"""
Модуль инициализации BingX API для проверки ключей, баланса и количества монет
"""
import time
import hmac
import hashlib
from urllib.parse import urlencode
import requests


class BingXInitializer:
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://open-api.bingx.com"
        
    def _generate_signature(self, params_str):
        """Генерация подписи для запроса"""
        if not self.secret_key:
            raise ValueError("Secret key is required for signing requests")
        
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            params_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def _make_request(self, method, endpoint, params=None, sign=False):
        """Выполнение HTTP-запроса к API"""
        url = f"{self.base_url}{endpoint}"
        
        if sign:
            params = params or {}
            params['timestamp'] = str(int(time.time() * 1000))
            query_string = urlencode(params)
            signature = self._generate_signature(query_string)
            params['signature'] = signature
        
        headers = {
            'X-BX-APIKEY': self.api_key
        }
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, params=params, headers=headers)
            elif method.upper() == 'POST':
                response = requests.post(url, data=params, headers=headers)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, params=params, headers=headers)
            
            # Проверяем статус код
            if response.status_code != 200:
                raise Exception(f"HTTP Error {response.status_code}: {response.text}")
                
            result = response.json()
            
            # Проверяем код ошибки от API
            if isinstance(result, dict) and 'code' in result and result['code'] != 0:
                raise Exception(f"API Error {result['code']}: {result.get('msg', 'Unknown error')}")
            
            return result
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
        except ValueError as e:  # Ошибка при парсинге JSON
            raise Exception(f"Invalid JSON response: {str(e)}, Raw response: {response.text}")

    def validate_credentials(self):
        """Проверка валидности API-ключей"""
        try:
            result = self._make_request('GET', '/openApi/swap/v3/user/balance', sign=True)
            return result.get('code') == 0
        except Exception as e:
            print(f"Ошибка при проверке валидности API-ключей: {e}")
            return False

    def get_balance(self):
        """Получить баланс аккаунта"""
        return self._make_request('GET', '/openApi/swap/v3/user/balance', sign=True)

    def get_positions(self):
        """Получить открытые позиции"""
        return self._make_request('GET', '/openApi/swap/v2/user/positions', sign=True)

    def get_account_info(self):
        """Получить информацию о счёте"""
        return self._make_request('GET', '/openApi/swap/v2/user/account', sign=True)

    def get_contracts_info(self):
        """Получить информацию о контрактах"""
        return self._make_request('GET', '/openApi/swap/v2/quote/contracts', sign=False)

    def initialize_and_check_criteria(self):
        """
        Инициализация и проверка критериев для торговли
        Возвращает словарь с результатами проверки
        """
        try:
            print("Начинаем инициализацию и проверку критериев...")
            
            # Проверяем баланс
            print("Проверяем баланс...")
            balance_data = self.get_balance()
            if 'data' not in balance_data or 'balances' not in balance_data['data']:
                print("Ошибка: Не удалось получить баланс")
                return {
                    'success': False,
                    'error': 'Не удалось получить баланс'
                }
            
            # Выводим информацию о балансе
            print("Данные о балансе:")
            usdt_balance = 0
            total_coins = 0
            for balance in balance_data['data']['balances']:
                asset = balance['asset']
                wallet_balance = float(balance['walletBalance'])
                print(f"  {asset}: {wallet_balance}")
                if asset == 'USDT':
                    usdt_balance = wallet_balance
                if wallet_balance > 0:
                    total_coins += 1
            
            print(f"Всего монет с балансом > 0: {total_coins}")
            
            if usdt_balance <= 0:
                print(f"Ошибка: Недостаточно средств. Баланс: {usdt_balance} USDT")
                return {
                    'success': False,
                    'error': f'Недостаточно средств. Баланс: {usdt_balance} USDT'
                }
            
            # Проверяем другие критерии (например, минимальный баланс для торговли)
            if usdt_balance < 10:  # Минимальный порог для торговли
                print(f"Ошибка: Баланс слишком мал для торговли. Требуется минимум 10 USDT, текущий: {usdt_balance}")
                return {
                    'success': False,
                    'error': f'Баланс слишком мал для торговли. Требуется минимум 10 USDT, текущий: {usdt_balance}'
                }
            
            # Проверяем открытые позиции
            print("Проверяем открытые позиции...")
            positions_data = self.get_positions()
            if 'data' in positions_data:
                open_positions = [pos for pos in positions_data['data'] if float(pos.get('positionAmt', 0)) != 0]
                print(f"Открытые позиции: {len(open_positions)}")
                for pos in open_positions:
                    print(f"  {pos['symbol']}: {pos['positionAmt']} по цене {pos['entryPrice']}")
            
            # Проверяем информацию о счёте
            print("Проверяем информацию о счёте...")
            account_info = self.get_account_info()
            if 'data' in account_info:
                print(f"Можно торговать: {account_info['data'].get('canTrade', False)}")
                print(f"Можно депозит: {account_info['data'].get('canDeposit', False)}")
                print(f"Можно вывод: {account_info['data'].get('canWithdraw', False)}")
            
            # Получаем информацию о доступных контрактах
            print("Получаем информацию о доступных контрактах...")
            contracts_data = self.get_contracts_info()
            if 'data' in contracts_data:
                active_contracts = [contract for contract in contracts_data['data'] if contract.get('status') == 'TRADING']
                print(f"Активные контракты: {len(active_contracts)}")
            
            print(f"Инициализация успешна. Баланс: {usdt_balance} USDT, монет с балансом > 0: {total_coins}")
            return {
                'success': True,
                'balance': usdt_balance,
                'total_coins_with_balance': total_coins,
                'open_positions': len(open_positions) if 'open_positions' in locals() else 0,
                'active_contracts': len(active_contracts) if 'active_contracts' in locals() else 0
            }
            
        except Exception as e:
            print(f"Ошибка при инициализации: {e}")
            return {
                'success': False,
                'error': str(e)
            }


def initialize_bingx_connection(api_key, secret_key):
    """
    Функция для инициализации подключения к BingX с проверкой баланса и количества монет
    
    Args:
        api_key (str): API ключ
        secret_key (str): Секретный ключ
    
    Returns:
        dict: Результат инициализации
    """
    initializer = BingXInitializer(api_key, secret_key)
    
    # Проверяем валидность ключей
    print("Проверяем валидность API-ключей...")
    if not initializer.validate_credentials():
        return {
            'success': False,
            'error': 'Неверные API-ключи'
        }
    
    print("Ключи валидны. Выполняем инициализацию...")
    return initializer.initialize_and_check_criteria()


if __name__ == "__main__":
    # Пример использования
    api_key = input("Введите ваш API Key: ")
    secret_key = input("Введите ваш Secret Key: ")
    
    result = initialize_bingx_connection(api_key, secret_key)
    
    if result['success']:
        print("\n=== Результат инициализации ===")
        print(f"Баланс: {result['balance']} USDT")
        print(f"Монет с балансом > 0: {result['total_coins_with_balance']}")
        print(f"Открытых позиций: {result['open_positions']}")
        print(f"Активных контрактов: {result['active_contracts']}")
        print("Инициализация прошла успешно!")
    else:
        print(f"\nОшибка инициализации: {result['error']}")