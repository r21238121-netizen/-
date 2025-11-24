"""
Диалог для загрузки JSON датасета и обучения ИИ модели
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFileDialog, QTextEdit, QProgressBar, QApplication
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import sys
import os


class TrainingThread(QThread):
    """Поток для обучения модели, чтобы не блокировать интерфейс"""
    training_finished = pyqtSignal(bool, str)
    progress_updated = pyqtSignal(int, str)
    
    def __init__(self, ai_agent, dataset_path):
        super().__init__()
        self.ai_agent = ai_agent
        self.dataset_path = dataset_path
    
    def run(self):
        """Выполнение обучения в отдельном потоке"""
        try:
            # Обновляем прогресс
            self.progress_updated.emit(10, "Загрузка датасета...")
            
            # Обучение модели
            success = self.ai_agent.train_from_json_dataset(self.dataset_path)
            
            if success:
                self.progress_updated.emit(100, "Обучение завершено успешно!")
                self.training_finished.emit(True, "Модель успешно обучена из JSON датасета!")
            else:
                self.training_finished.emit(False, "Ошибка при обучении модели")
                
        except Exception as e:
            self.training_finished.emit(False, f"Ошибка: {str(e)}")


class TrainingDialog(QDialog):
    def __init__(self, ai_agent, parent=None):
        super().__init__(parent)
        self.ai_agent = ai_agent
        self.training_thread = None
        
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Обучение ИИ модели из датасета')
        self.setModal(True)
        self.resize(500, 300)
        
        layout = QVBoxLayout()
        
        # Инструкция
        instruction = QLabel('Выберите JSON файл с датасетом для обучения ИИ модели:')
        instruction.setWordWrap(True)
        layout.addWidget(instruction)
        
        # Поле для отображения выбранного файла
        self.file_label = QLabel('Файл не выбран')
        self.file_label.setStyleSheet('padding: 10px; background-color: #2a2a5a; border-radius: 5px;')
        layout.addWidget(self.file_label)
        
        # Кнопка выбора файла
        self.select_button = QPushButton('Выбрать JSON датасет')
        self.select_button.clicked.connect(self.select_dataset_file)
        layout.addWidget(self.select_button)
        
        # Кнопка начала обучения
        self.train_button = QPushButton('Начать обучение')
        self.train_button.clicked.connect(self.start_training)
        self.train_button.setEnabled(False)  # Пока файл не выбран
        layout.addWidget(self.train_button)
        
        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Область для сообщений
        self.message_area = QTextEdit()
        self.message_area.setMaximumHeight(100)
        self.message_area.setReadOnly(True)
        layout.addWidget(self.message_area)
        
        # Кнопка закрытия
        close_button = QPushButton('Закрыть')
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
        
        self.setLayout(layout)
    
    def select_dataset_file(self):
        """Выбор файла датасета"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Выберите JSON датасет',
            '',
            'JSON Files (*.json);;All Files (*)'
        )
        
        if file_path:
            self.selected_file_path = file_path
            self.file_label.setText(f'Выбран файл: {os.path.basename(file_path)}')
            self.train_button.setEnabled(True)
            self.add_message(f'Выбран датасет: {file_path}')
    
    def start_training(self):
        """Начало процесса обучения"""
        if not hasattr(self, 'selected_file_path'):
            self.add_message('Сначала выберите файл датасета')
            return
        
        # Проверяем существование файла
        if not os.path.exists(self.selected_file_path):
            self.add_message('Файл датасета не найден')
            return
        
        # Настройка интерфейса для процесса обучения
        self.select_button.setEnabled(False)
        self.train_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Создаем и запускаем поток обучения
        self.training_thread = TrainingThread(self.ai_agent, self.selected_file_path)
        self.training_thread.training_finished.connect(self.on_training_finished)
        self.training_thread.progress_updated.connect(self.on_progress_updated)
        self.training_thread.start()
    
    def on_progress_updated(self, value, message):
        """Обновление прогресса"""
        self.progress_bar.setValue(value)
        self.add_message(message)
    
    def on_training_finished(self, success, message):
        """Обработка завершения обучения"""
        self.progress_bar.setValue(100 if success else 0)
        
        if success:
            self.add_message(f'✓ {message}')
            # Обновляем статистику в основном окне, если оно есть
            if hasattr(self.ai_agent, 'get_performance_stats'):
                stats = self.ai_agent.get_performance_stats()
                self.add_message(f'Статистика модели: {stats}')
        else:
            self.add_message(f'✗ {message}')
        
        # Восстанавливаем интерфейс
        self.select_button.setEnabled(True)
        self.train_button.setEnabled(True)
        self.progress_bar.setVisible(False)
    
    def add_message(self, message):
        """Добавление сообщения в область сообщений"""
        self.message_area.append(f'[{QApplication.instance().applicationName()}] {message}')
    
    def closeEvent(self, event):
        """Обработка закрытия диалога"""
        # Если обучение все еще идет, пытаемся завершить поток
        if self.training_thread and self.training_thread.isRunning():
            self.training_thread.terminate()
            self.training_thread.wait(3000)  # Ждем до 3 секунд
        
        event.accept()


if __name__ == "__main__":
    # Тестирование диалога (для демонстрации)
    app = QApplication(sys.argv)
    app.setApplicationName("Futures Scout")
    
    # Создаем фиктивный AI агент для тестирования
    class DummyAIAgent:
        def train_from_json_dataset(self, dataset_path):
            import time
            time.sleep(2)  # Имитация обучения
            return True
    
    dialog = TrainingDialog(DummyAIAgent())
    dialog.show()
    
    sys.exit(app.exec())