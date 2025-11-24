"""
Скрипт для обучения ИИ-модели на основе JSON датасета
"""
import json
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import pickle
import os
import sys
from datetime import datetime


def load_dataset(dataset_path):
    """Загрузка датасета из JSON файла"""
    print(f"Загрузка датасета из {dataset_path}...")
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    print(f"Загружено {len(dataset)} образцов")
    return dataset


def prepare_features_and_labels(dataset):
    """Подготовка признаков и меток для обучения"""
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


def train_model(X, y, test_size=0.2, random_state=42):
    """Обучение XGBoost модели"""
    print("Разделение данных на обучающую и тестовую выборки...")
    
    # Разделяем данные
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    print(f"Размер обучающей выборки: {X_train.shape}")
    print(f"Размер тестовой выборки: {X_test.shape}")
    
    # Создаем и обучаем модель XGBoost
    print("Обучение модели XGBoost...")
    
    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=8,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=random_state,
        n_jobs=-1  # Использовать все ядра
    )
    
    model.fit(X_train, y_train)
    
    # Предсказания на тестовой выборке
    y_pred = model.predict(X_test)
    
    # Оценка модели
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Точность модели: {accuracy:.4f}")
    
    print("\nКлассификационный отчет:")
    print(classification_report(y_test, y_pred, target_names=['Неудача', 'Успех']))
    
    print("\nМатрица ошибок:")
    print(confusion_matrix(y_test, y_pred))
    
    return model, X_test, y_test, y_pred


def save_model(model, model_path):
    """Сохранение обученной модели"""
    print(f"Сохранение модели в {model_path}...")
    
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    print("Модель успешно сохранена!")


def load_and_evaluate_existing_model(model_path, X_test, y_test):
    """Загрузка и оценка существующей модели"""
    if os.path.exists(model_path):
        print(f"Загрузка существующей модели из {model_path}...")
        
        with open(model_path, 'rb') as f:
            existing_model = pickle.load(f)
        
        # Предсказания существующей модели
        y_pred_existing = existing_model.predict(X_test)
        accuracy_existing = accuracy_score(y_test, y_pred_existing)
        
        print(f"Точность существующей модели: {accuracy_existing:.4f}")
        print("\nКлассификационный отчет существующей модели:")
        print(classification_report(y_test, y_pred_existing, target_names=['Неудача', 'Успех']))
        
        return existing_model, accuracy_existing
    
    return None, 0.0


def main(dataset_path=None, model_path=None):
    """Основная функция обучения модели"""
    # Пути по умолчанию
    if dataset_path is None:
        dataset_path = 'datasets/training_dataset.json'
    
    if model_path is None:
        model_path = os.path.join(os.path.expanduser("~"), '.futures_scout', 'ai_model.pkl')
    
    print("=== Обучение ИИ-модели для Futures Scout ===")
    print(f"Датасет: {dataset_path}")
    print(f"Модель будет сохранена в: {model_path}")
    
    try:
        # Загружаем датасет
        dataset = load_dataset(dataset_path)
        
        # Подготавливаем признаки и метки
        X, y = prepare_features_and_labels(dataset)
        
        # Обучаем модель
        model, X_test, y_test, y_pred = train_model(X, y)
        
        # Загружаем и сравниваем с существующей моделью (если есть)
        existing_model, existing_accuracy = load_and_evaluate_existing_model(model_path, X_test, y_test)
        
        # Сохраняем новую модель
        save_model(model, model_path)
        
        # Выводим статистику
        print("\n=== Статистика обучения ===")
        print(f"Количество образцов: {len(dataset)}")
        print(f"Количество признаков: {X.shape[1]}")
        print(f"Точность новой модели: {accuracy_score(y_test, y_pred):.4f}")
        
        if existing_model is not None:
            print(f"Точность существующей модели: {existing_accuracy:.4f}")
            improvement = accuracy_score(y_test, y_pred) - existing_accuracy
            print(f"Улучшение: {improvement:.4f}")
        
        print(f"\nМодель успешно обучена и сохранена в {model_path}")
        
        return model
        
    except FileNotFoundError:
        print(f"Ошибка: файл датасета не найден: {dataset_path}")
        print("Создайте датасет с помощью generate_dataset.py или укажите правильный путь")
        return None
    except Exception as e:
        print(f"Ошибка при обучении модели: {e}")
        import traceback
        traceback.print_exc()
        return None


def load_json_dataset_for_training(json_file_path):
    """Функция для загрузки JSON датасета, которая может быть использована в exe файле"""
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


def train_from_json_dataset(json_file_path, model_save_path=None):
    """Обучение модели из JSON датасета"""
    if model_save_path is None:
        model_save_path = os.path.join(os.path.expanduser("~"), '.futures_scout', 'ai_model.pkl')
    
    dataset = load_json_dataset_for_training(json_file_path)
    
    if dataset is None:
        return None
    
    print("Подготовка данных для обучения...")
    X, y = prepare_features_and_labels(dataset)
    
    print("Обучение модели...")
    model, X_test, y_test, y_pred = train_model(X, y)
    
    print("Сохранение модели...")
    save_model(model, model_save_path)
    
    print(f"Модель обучена и сохранена в {model_save_path}")
    return model


if __name__ == "__main__":
    # Если передан аргумент командной строки, используем его как путь к датасету
    if len(sys.argv) > 1:
        dataset_path = sys.argv[1]
        model_path = sys.argv[2] if len(sys.argv) > 2 else None
        main(dataset_path, model_path)
    else:
        # Проверяем, существует ли датасет, если нет - создаем
        dataset_path = 'datasets/training_dataset.json'
        if not os.path.exists(dataset_path):
            print(f"Датасет {dataset_path} не найден. Создаем датасет...")
            import subprocess
            result = subprocess.run([sys.executable, 'generate_dataset.py'])
            if result.returncode != 0:
                print("Ошибка при генерации датасета")
                sys.exit(1)
        
        # Запускаем обучение
        main(dataset_path)