#!/usr/bin/env python3
"""
Анализ кода BingX API на наличие потенциальных ошибок
"""
import ast
import sys
import os
sys.path.insert(0, 'src')

def analyze_bingx_api_file():
    """Анализ файла bingx_api.py на наличие потенциальных ошибок"""
    print("Анализ файла bingx_api.py на наличие потенциальных ошибок...")
    
    file_path = 'src/api/bingx_api.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse the file to analyze the code structure
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        print(f"Синтаксическая ошибка: {e}")
        return False
    
    # Check for potential issues
    issues = []
    
    # Find all function definitions
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            
            # Check for functions that might have issues
            if func_name == '_make_request':
                # Check if the function properly handles both real and demo modes
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.If):
                        # Check for demo mode handling
                        if isinstance(subnode.test, ast.Attribute) and hasattr(subnode.test, 'attr'):
                            if subnode.test.attr == 'demo_mode':
                                print(f"  ✓ {func_name}: Обработка демо-режима найдена")
            
            elif func_name == '_get_demo_data':
                # Check if all required endpoints are handled in demo mode
                demo_endpoints = []
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.If):
                        if isinstance(subnode.test, ast.Compare):
                            for comparator in subnode.test.comparators:
                                if isinstance(comparator, ast.Constant) and isinstance(comparator.value, str):
                                    endpoint = comparator.value
                                    if '/user/' in endpoint or '/trade/' in endpoint:
                                        demo_endpoints.append(endpoint)
                
                print(f"  ✓ {func_name}: Обрабатываются {len(demo_endpoints)} эндпоинтов в демо-режиме")
                for ep in demo_endpoints:
                    print(f"    - {ep}")
    
    # Look for potential issues in the code
    lines = content.split('\n')
    
    print("\nАнализ потенциальных проблем:")
    
    # Check for common issues
    for i, line in enumerate(lines, 1):
        line_lower = line.lower()
        
        # Check for potential security issues
        if 'print(' in line and ('api_key' in line_lower or 'secret' in line_lower):
            issues.append(f"  ⚠️  Строка {i}: Потенциальная утечка API-ключей в выводе: {line.strip()}")
        
        # Check for error handling
        if 'except:' in line or 'except Exception:' in line:
            # Check if it's followed by pass or minimal handling
            if i < len(lines) - 1:
                next_line = lines[i]
                if 'pass' in next_line or ('return' in next_line and 'False' in next_line):
                    issues.append(f"  ⚠️  Строка {i}: Общее исключение без надлежащей обработки: {line.strip()}")
        
        # Check for hardcoded values that should be configurable
        if 'https://open-api.bingx.com' in line:
            # This is OK as it's the official API endpoint
            pass
        
        # Check for potential type conversion issues
        if 'float(' in line and 'get(' in line:
            # Look for patterns like float(data.get('key'))
            if 'price' in line_lower or 'balance' in line_lower or 'amount' in line_lower:
                # These are typically OK for financial data
                pass
    
    # Check the validate_credentials method specifically
    if 'return result.get(\'code\') == 0' in content:
        print("  ✓ validate_credentials: Проверка кода ответа реализована")
    else:
        issues.append("  ⚠️  validate_credentials: Отсутствует надлежащая проверка кода ответа")
    
    # Check for proper signature implementation
    if 'hmac.new' in content and 'hashlib.sha256' in content:
        print("  ✓ Подписи запросов: Реализация HMAC-SHA256 найдена")
    else:
        issues.append("  ⚠️  Подписи запросов: Отсутствует реализация HMAC-SHA256")
    
    # Check for proper timestamp handling
    if 'time.time()' in content or 'int(time.time()' in content:
        print("  ✓ Временные метки: Обработка timestamp найдена")
    else:
        issues.append("  ⚠️  Временные метки: Отсутствует обработка timestamp")
    
    # Check for request signing logic
    if 'X-BX-APIKEY' in content:
        print("  ✓ Аутентификация: Заголовок API-ключа найден")
    else:
        issues.append("  ⚠️  Аутентификация: Отсутствует заголовок API-ключа")
    
    # Check for all required endpoints implementation
    required_endpoints = [
        'get_balance',
        'get_positions', 
        'get_income_history',
        'get_commission_rate',
        'get_market_price',
        'get_kline_data',
        'get_orderbook',
        'get_funding_rate',
        'get_open_interest'
    ]
    
    print(f"\nПроверка реализации обязательных методов:")
    for endpoint in required_endpoints:
        if f'def {endpoint}(' in content:
            print(f"  ✓ {endpoint}: РЕАЛИЗОВАН")
        else:
            issues.append(f"  ✗ {endpoint}: ОТСУТСТВУЕТ")
    
    print(f"\nНайдено потенциальных проблем: {len(issues)}")
    for issue in issues:
        print(issue)
    
    return len(issues) == 0

def check_error_handling():
    """Проверка обработки ошибок в ключевых методах"""
    print("\nПроверка обработки ошибок:")
    
    # Import and test the API
    from api.bingx_api import BingXAPI
    
    api = BingXAPI(demo_mode=True)
    
    # Test that demo mode returns proper data structures
    try:
        balance = api.get_balance()
        assert 'code' in balance, "Баланс должен содержать 'code'"
        assert 'data' in balance, "Баланс должен содержать 'data'"
        print("  ✓ get_balance: Возвращает правильную структуру данных")
    except Exception as e:
        print(f"  ⚠️  get_balance: Ошибка структуры данных - {e}")
    
    try:
        positions = api.get_positions()
        assert 'code' in positions, "Позиции должны содержать 'code'"
        assert 'data' in positions, "Позиции должны содержать 'data'"
        print("  ✓ get_positions: Возвращает правильную структуру данных")
    except Exception as e:
        print(f"  ⚠️  get_positions: Ошибка структуры данных - {e}")
    
    try:
        income = api.get_income_history()
        assert 'code' in income, "Доходы должны содержать 'code'"
        assert 'data' in income, "Доходы должны содержать 'data'"
        print("  ✓ get_income_history: Возвращает правильную структуру данных")
    except Exception as e:
        print(f"  ⚠️  get_income_history: Ошибка структуры данных - {e}")

def check_demo_mode_consistency():
    """Проверка консистентности данных в демо-режиме"""
    print("\nПроверка консистентности демо-данных:")
    
    from api.bingx_api import BingXAPI
    
    api = BingXAPI(demo_mode=True)
    
    # Получаем данные несколько раз
    results = []
    for i in range(3):
        balance = api.get_balance()
        positions = api.get_positions()
        income = api.get_income_history()
        
        results.append({
            'balance': balance['data']['balances'][0]['walletBalance'] if 'data' in balance and 'balances' in balance['data'] else None,
            'positions_count': len(positions['data']) if 'data' in positions else 0,
            'income_count': len(income['data']) if 'data' in income else 0
        })
    
    # Проверяем, что данные консистентны
    first_result = results[0]
    all_consistent = all(r == first_result for r in results)
    
    if all_consistent:
        print("  ✓ Демо-данные консистентны между вызовами")
        print(f"    Баланс: {first_result['balance']}, Позиции: {first_result['positions_count']}, Доходы: {first_result['income_count']}")
    else:
        print("  ⚠️  Демо-данные НЕ консистентны между вызовами")
        for i, r in enumerate(results):
            print(f"    Вызов {i+1}: Баланс={r['balance']}, Позиции={r['positions_count']}, Доходы={r['income_count']}")

def check_real_mode_readiness():
    """Проверка готовности к работе в реальном режиме"""
    print("\nПроверка готовности к реальному режиму:")
    
    from api.bingx_api import BingXAPI
    
    # Создаем API в реальном режиме (без ключей)
    api = BingXAPI(demo_mode=False)
    
    # Проверяем, что базовые URL установлены правильно
    expected_base = "https://open-api.bingx.com"
    expected_ws = "wss://open-api-ws.bingx.com"
    
    if api.base_url == expected_base:
        print("  ✓ Базовый URL корректен для реального режима")
    else:
        print(f"  ⚠️  Базовый URL некорректен: ожидал {expected_base}, получил {api.base_url}")
    
    if api.websocket_url == expected_ws:
        print("  ✓ WebSocket URL корректен для реального режима")
    else:
        print(f"  ⚠️  WebSocket URL некорректен: ожидал {expected_ws}, получил {api.websocket_url}")
    
    # Проверяем, что подпись генерируется правильно
    try:
        # Тестовая подпись
        test_string = "test=123&timestamp=1234567890"
        signature = api._generate_signature(test_string)
        assert len(signature) == 64, "Подпись должна быть 64-символьной (SHA256)"
        print("  ✓ Генерация подписей работает корректно")
    except Exception as e:
        print(f"  ⚠️  Ошибка генерации подписи: {e}")

if __name__ == "__main__":
    print("Запуск анализа кода BingX API...")
    
    success = analyze_bingx_api_file()
    check_error_handling()
    check_demo_mode_consistency()
    check_real_mode_readiness()
    
    print(f"\nАнализ завершен!")