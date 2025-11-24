import asyncio
from api_initializer import main as api_init_main

def run_main_app(working_apis):
    """Основная функция запуска приложения после проверки API"""
    print("Запуск основного приложения...")
    
    # Здесь будет основная логика приложения, которая использует проверенные API
    print(f"Приложение работает с {len(working_apis)} рабочими API: {list(working_apis.keys())}")
    
def main():
    print("=== Система инициализации API ===")
    
    # Запускаем инициализацию API
    working_apis = api_init_main()
    
    if working_apis:
        print("\nВсе проверки пройдены. Запуск основного приложения...")
        run_main_app(working_apis)
    else:
        print("\nНе удалось подключиться к каким-либо API. Приложение не может быть запущено.")

if __name__ == "__main__":
    main()