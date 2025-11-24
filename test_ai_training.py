"""
Тестирование функциональности обучения ИИ из JSON датасета
"""
import os
import sys
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from api.bingx_api import BingXAPI
from models.ai_agent import AIAgent


def test_json_training():
    """Тестирование обучения из JSON датасета"""
    print("=== Тестирование обучения ИИ из JSON датасета ===")
    
    # Создаем API в демо-режиме
    api = BingXAPI(demo_mode=True)
    
    # Создаем ИИ-агента
    ai_agent = AIAgent(api, demo_mode=True)
    
    # Проверяем, что датасет существует
    dataset_path = 'datasets/training_dataset.json'
    if not os.path.exists(dataset_path):
        print(f"Датасет {dataset_path} не найден. Создаем датасет...")
        import subprocess
        result = subprocess.run([sys.executable, 'generate_dataset.py'])
        if result.returncode != 0:
            print("Ошибка при генерации датасета")
            return False
    
    # Обучаем модель из JSON датасета
    success = ai_agent.train_from_json_dataset(dataset_path)
    
    if success:
        print("✓ Обучение из JSON датасета прошло успешно!")
        
        # Проверяем статистику
        stats = ai_agent.get_performance_stats()
        print(f"Статистика: {stats}")
        
        return True
    else:
        print("✗ Обучение из JSON датасета не удалось!")
        return False


def main():
    """Основная функция тестирования"""
    print("Запуск тестирования функциональности ИИ-обучения...")
    
    success = test_json_training()
    
    if success:
        print("\n✓ Все тесты пройдены успешно!")
        print("Функциональность загрузки JSON датасетов для обучения ИИ работает корректно.")
        print("Эта функциональность будет доступна в exe файле.")
    else:
        print("\n✗ Один или несколько тестов не прошли.")
        sys.exit(1)


if __name__ == "__main__":
    main()