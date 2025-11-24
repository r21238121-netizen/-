"""
Скрипт для генерации обучающего датасета для ИИ-агента
"""
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os


def generate_market_features():
    """Генерация признаков для одного временного шага"""
    return {
        # Цены
        'current_price': random.uniform(30000, 70000),
        'sma_20': random.uniform(30000, 70000),
        'sma_50': random.uniform(30000, 70000),
        
        # Индикаторы
        'rsi': random.uniform(20, 80),
        'macd': random.uniform(-1000, 1000),
        'volatility': random.uniform(0.5, 5.0),
        
        # Объемы
        'avg_volume': random.uniform(1000, 10000),
        'current_volume': random.uniform(500, 5000),
        
        # Стакан
        'ob_imbalance': random.uniform(-1.0, 1.0),
        
        # Фондирование
        'funding_rate': random.uniform(-0.01, 0.01),
        
        # Временные признаки
        'hour': random.uniform(0, 23) / 24.0,
        'day_of_week': random.uniform(0, 6) / 7.0,
        
        # Отношения
        'price_to_sma20': random.uniform(0.8, 1.2),
        'price_to_sma50': random.uniform(0.8, 1.2),
        
        # Другие
        'candle_count': random.randint(10, 100),
        'price_change_period': random.uniform(-0.1, 0.1),
        'total_volume': random.uniform(50000, 500000),
        'last_candle_change': random.uniform(-1000, 1000),
        'deviation_from_5_sma': random.uniform(-500, 500),
        
        # Внешние признаки
        'external_volatility': random.uniform(0.5, 5.0)
    }


def generate_signal_data():
    """Генерация данных для одного сигнала"""
    features = generate_market_features()
    
    # Определяем направление сигнала на основе признаков
    if features['rsi'] < 30 and features['price_to_sma20'] < 0.95:
        side = 'LONG'
    elif features['rsi'] > 70 and features['price_to_sma20'] > 1.05:
        side = 'SHORT'
    else:
        side = random.choice(['LONG', 'SHORT'])
    
    # Рассчитываем TP и SL на основе волатильности
    volatility = features['volatility']
    entry_price = features['current_price']
    tp_distance = volatility * random.uniform(1.5, 3.0)
    sl_distance = volatility * random.uniform(0.8, 1.5)
    
    if side == 'LONG':
        tp_price = entry_price + tp_distance
        sl_price = entry_price - sl_distance
    else:
        tp_price = entry_price - tp_distance
        sl_price = entry_price + sl_distance
    
    # Определяем успешность сигнала на основе признаков
    # Более высокий RSI при SHORT или низкий RSI при LONG может указывать на успех
    if side == 'LONG' and features['rsi'] < 40:
        success = random.choice([True, False]) if random.random() < 0.7 else True
    elif side == 'SHORT' and features['rsi'] > 60:
        success = random.choice([True, False]) if random.random() < 0.7 else True
    else:
        success = random.choice([True, False])  # 50/50 для неочевидных сигналов
    
    return {
        'features': features,
        'side': side,
        'entry_price': entry_price,
        'tp_price': tp_price,
        'sl_price': sl_price,
        'confidence': random.uniform(0.4, 0.95),  # Уверенность модели
        'success': success,
        'timestamp': datetime.now().isoformat()
    }


def generate_dataset(num_samples=10000):
    """Генерация полного датасета"""
    print(f"Генерация датасета из {num_samples} образцов...")
    
    dataset = []
    for i in range(num_samples):
        if i % 1000 == 0:
            print(f"Сгенерировано {i}/{num_samples} образцов...")
        
        signal_data = generate_signal_data()
        dataset.append(signal_data)
    
    print(f"Датасет из {len(dataset)} образцов сгенерирован!")
    return dataset


def save_dataset(dataset, filename):
    """Сохранение датасета в JSON файл"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    print(f"Датасет сохранен в {filename}")


def main():
    # Создаем директорию для датасетов
    os.makedirs('datasets', exist_ok=True)
    
    # Генерируем датасет
    dataset = generate_dataset(10000)
    
    # Сохраняем датасет
    save_dataset(dataset, 'datasets/training_dataset.json')
    
    # Создаем небольшой тестовый датасет
    test_dataset = generate_dataset(1000)
    save_dataset(test_dataset, 'datasets/test_dataset.json')
    
    print("Генерация датасетов завершена!")


if __name__ == "__main__":
    main()