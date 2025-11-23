"""
Окно аутентификации для ввода API-ключей
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class AuthWindow(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Futures Scout - Вход')
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout()
        
        # Заголовок
        title_label = QLabel('Futures Scout')
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Предупреждение о рисках
        warning_text = QTextEdit()
        warning_text.setHtml(
            "<div style='color: orange; text-align: center;'>"
            "<b>ВАЖНОЕ ПРЕДУПРЕЖДЕНИЕ:</b><br>"
            "Фьючерсная торговля сопряжена с высоким риском потери капитала. "
            "Этот инструмент не гарантирует прибыль. Используйте на свой риск."
            "</div>"
        )
        warning_text.setMaximumHeight(80)
        warning_text.setReadOnly(True)
        layout.addWidget(warning_text)
        
        # Поля для API-ключей
        api_key_label = QLabel('BingX API Key:')
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText('Введите ваш API Key')
        layout.addWidget(api_key_label)
        layout.addWidget(self.api_key_input)
        
        secret_key_label = QLabel('BingX Secret Key:')
        self.secret_key_input = QLineEdit()
        self.secret_key_input.setPlaceholderText('Введите ваш Secret Key')
        self.secret_key_input.setEchoMode(QLineEdit.EchoMode.Password)  # Маскируем ввод
        layout.addWidget(secret_key_label)
        layout.addWidget(self.secret_key_input)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        self.connect_button = QPushButton('Подключиться')
        self.connect_button.clicked.connect(self.on_connect_clicked)
        button_layout.addWidget(self.connect_button)
        
        self.demo_button = QPushButton('Попробовать демо')
        self.demo_button.clicked.connect(self.on_demo_clicked)
        button_layout.addWidget(self.demo_button)
        
        layout.addLayout(button_layout)
        
        # Статус
        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # Центрируем окно
        self.center_window()
    
    def center_window(self):
        """Центрирование окна на экране"""
        screen_geometry = self.screen().availableGeometry()
        window_geometry = self.geometry()
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        self.move(x, y)
    
    def on_connect_clicked(self):
        """Обработка нажатия кнопки подключения"""
        api_key = self.api_key_input.text().strip()
        secret_key = self.secret_key_input.text().strip()
        
        if not api_key or not secret_key:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, введите оба ключа')
            return
        
        self.status_label.setText('Проверка ключей...')
        self.status_label.repaint()  # Обновляем интерфейс
        
        try:
            success = self.main_app.connect_with_credentials(api_key, secret_key)
            if success:
                self.status_label.setText('Успешное подключение!')
                self.status_label.setStyleSheet('color: green;')
            else:
                QMessageBox.critical(self, 'Ошибка', 
                    'Неверные ключи или нет доступа к фьючерсам. Пожалуйста, проверьте ключи и права доступа.')
                self.status_label.setText('Ошибка подключения')
                self.status_label.setStyleSheet('color: red;')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка подключения: {str(e)}')
            self.status_label.setText('Ошибка подключения')
            self.status_label.setStyleSheet('color: red;')
    
    def on_demo_clicked(self):
        """Обработка нажатия кнопки демо-режима"""
        self.main_app.start_demo_mode()
        self.close()