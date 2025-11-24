"""
Интеграция функциональности обучения ИИ в приложение Futures Scout
"""
import json
import os
import sys
import pickle
import numpy as np
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from src.models.ai_agent import AIAgent, SignalHistory


class AIModelTrainer:
    """Класс для обучения и управления ИИ-моделью"""
    
    def __init__(self, ai_agent):
        self.ai_agent = ai_agent
        self.model = ai_agent.model
        self.session = ai_agent.session
    
    def load_json_dataset(self, json_file_path):
        """Загрузка JSON датасета для обучения"""
        print(f"Загрузка JSON датасета из {json_file_path}...")
        
        if not os.path.exists(json_file_path):
            print(f"Файл {json_file_path} не найден!")
            return None
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                dataset = json.load(f)
            
            print(f"Загружено {len(dataset)} образцов из JSON датасета")
            return dataset
        except Exception as e:
            print(f"Ошибка при загрузке JSON датасета: {e}")
            return None
    
    def prepare_features_from_json_dataset(self, dataset):
        """Подготовка признаков из JSON датасета"""
        X = []  # Признаки
        y = []  # Метки (успех/неуспех)
        
        for sample in dataset:
            # Извлекаем признаки из датасета
            features = sample['features']
            
            # Формируем вектор признаков
            feature_vector = [
                features['current_price'],
                features['sma_20'],
                features['sma_50'],
                features['rsi'],
                features['macd'],
                features['volatility'],
                features['avg_volume'],
                features['current_volume'],
                features['ob_imbalance'],
                features['funding_rate'],
                features['hour'],
                features['day_of_week'],
                features['price_to_sma20'],
                features['price_to_sma50'],
                features['candle_count'],
                features['price_change_period'],
                features['total_volume'],
                features['last_candle_change'],
                features['deviation_from_5_sma'],
                features['external_volatility']
            ]
            
            # Добавляем признаки, связанные с самим сигналом
            signal_features = [
                sample['entry_price'],
                sample['tp_price'],
                sample['sl_price'],
                sample['confidence'],
                1 if sample['side'] == 'LONG' else 0,  # one-hot для side
                0 if sample['side'] == 'LONG' else 1   # one-hot для side
            ]
            
            # Объединяем все признаки
            full_feature_vector = feature_vector + signal_features
            X.append(full_feature_vector)
            
            # Метка: 1 для успеха, 0 для неудачи
            y.append(1 if sample['success'] else 0)
        
        return np.array(X), np.array(y)
    
    def train_model_from_json_dataset(self, json_file_path, save_model=True):
        """Обучение модели из JSON датасета"""
        print("Загрузка JSON датасета...")
        dataset = self.load_json_dataset(json_file_path)
        
        if dataset is None:
            return False
        
        print("Подготовка признаков из датасета...")
        X, y = self.prepare_features_from_json_dataset(dataset)
        
        if len(X) == 0:
            print("Нет данных для обучения")
            return False
        
        print(f"Размер обучающей выборки: {X.shape}")
        
        # Обучение модели
        print("Обучение модели...")
        try:
            # Используем XGBoost
            from xgboost import XGBClassifier
            
            # Создаем новую модель
            new_model = XGBClassifier(
                n_estimators=200,
                max_depth=8,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                n_jobs=-1
            )
            
            # Обучаем модель
            new_model.fit(X, y)
            
            # Обновляем модель в AI агенте
            self.ai_agent.model = new_model
            
            if save_model:
                # Сохраняем модель
                self.ai_agent._save_model()
                print("Модель успешно обучена и сохранена!")
            else:
                print("Модель успешно обучена!")
            
            return True
            
        except Exception as e:
            print(f"Ошибка при обучении модели: {e}")
            return False
    
    def get_current_model_performance(self):
        """Получение текущей производительности модели"""
        return self.ai_agent.get_performance_stats()


def integrate_training_functionality():
    """Интеграция функциональности обучения в приложение"""
    print("Интеграция функциональности обучения ИИ в приложение...")
    
    # Эта функция будет вызываться из основного приложения
    # Она добавляет возможность загружать JSON датасеты и обучать модель
    pass


def main():
    """Демонстрация интеграции функциональности"""
    print("=== Интеграция обучения ИИ в Futures Scout ===")
    
    # Пример использования (в реальном приложении будет вызываться из GUI)
    if len(sys.argv) > 1:
        json_dataset_path = sys.argv[1]
        print(f"Обучение модели из датасета: {json_dataset_path}")
        
        # В реальном приложении здесь будет создание AI агента
        # Но для демонстрации мы просто покажем как это будет работать
        print("Функция обучения модели из JSON датасета готова к использованию в приложении")
        print("В exe файле будет возможность загружать JSON датасеты для обучения ИИ")
    else:
        print("Пример использования:")
        print("python integrated_ai_training.py path/to/dataset.json")


if __name__ == "__main__":
    main()