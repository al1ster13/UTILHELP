from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap


class LoadingWidget(QWidget):
    """Виджет для показа состояния загрузки"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.animation = None
    
    def setup_ui(self):
        """Настройка интерфейса"""
        from theme_manager import theme_manager
        c = theme_manager.colors
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {c['bg_main']};
                border-radius: 10px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setFixedSize(64, 64)
        self.icon_label.setStyleSheet("""
            QLabel {
                color: #4a9eff;
                font-size: 48px;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(self.icon_label)
        
        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
                border: none;
                margin: 10px 0px;
            }
        """)
        layout.addWidget(self.title_label)
        
        self.description_label = QLabel()
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 14px;
                background: transparent;
                border: none;
                line-height: 1.5;
            }
        """)
        layout.addWidget(self.description_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #333333;
                text-align: center;
            }
            QProgressBar::chunk {
                border-radius: 4px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a9eff, stop:1 #3a7ed8);
            }
        """)
        layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel()
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 12px;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(self.progress_label)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.retry_button = QPushButton("🔄 Повторить")
        self.retry_button.setFixedHeight(35)
        self.retry_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #666666, stop:1 #555555);
                color: white;
                border: 1px solid #777777;
                padding: 8px 20px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #777777, stop:1 #666666);
                border: 1px solid #888888;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #555555, stop:1 #444444);
            }
        """)
        self.retry_button.hide()
        
        button_layout.addWidget(self.retry_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
    
    def show_loading(self):
        """Показать состояние загрузки"""
        self.icon_label.setText("⏳")
        self.title_label.setText("Загрузка данных")
        self.description_label.setText("Подключение к серверу...")
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.progress_label.setText("0%")
        self.progress_label.show()
        self.retry_button.hide()
        
        self.start_loading_animation()
    
    def show_error(self, error_message, on_retry=None):
        """Показать ошибку"""
        self.stop_loading_animation()
        
        self.icon_label.setText("❌")
        self.title_label.setText("Нет подключения к интернету")
        
        if "подключения к интернету" in error_message.lower():
            self.description_label.setText("Проверьте подключение к интернету и попробуйте снова.\nДля работы программы требуется доступ в интернет.")
        else:
            self.description_label.setText(f"Ошибка загрузки данных:\n{error_message}")
        
        self.progress_bar.hide()
        self.progress_label.hide()
        
        if on_retry:
            self.retry_button.clicked.disconnect()
            self.retry_button.clicked.connect(on_retry)
            self.retry_button.show()
    
    def update_progress(self, message, percent):
        """Обновить прогресс"""
        self.description_label.setText(message)
        self.progress_bar.setValue(percent)
        self.progress_label.setText(f"{percent}%")
    
    def show_success(self):
        """Показать успешную загрузку"""
        self.stop_loading_animation()
        
        self.icon_label.setText("✅")
        self.title_label.setText("Данные загружены")
        self.description_label.setText("Все данные успешно загружены с сервера")
        self.progress_bar.setValue(100)
        self.progress_label.setText("100%")
        self.retry_button.hide()
        
        QTimer.singleShot(1000, self.hide)
    
    def start_loading_animation(self):
        """Запуск анимации загрузки"""
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_loading)
        self.animation_timer.start(500)  
        self.animation_step = 0
    
    def animate_loading(self):
        """Анимация иконки загрузки"""
        icons = ["⏳", "⌛"]
        self.icon_label.setText(icons[self.animation_step % len(icons)])
        self.animation_step += 1
    
    def stop_loading_animation(self):
        """Остановка анимации"""
        if hasattr(self, 'animation_timer'):
            self.animation_timer.stop()


class NoInternetWidget(QWidget):
    """Виджет для показа отсутствия интернета"""
    def __init__(self, parent=None, on_retry=None):
        super().__init__(parent)
        self.on_retry = on_retry
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        from theme_manager import theme_manager
        c = theme_manager.colors
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {c['bg_main']};
                border-radius: 10px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(25)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_label = QLabel("🌐")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 72px;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(icon_label)
        
        title_label = QLabel("Нет подключения к интернету")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 28px;
                font-weight: bold;
                background: transparent;
                border: none;
                margin: 10px 0px;
            }
        """)
        layout.addWidget(title_label)
        
        description_label = QLabel("Для работы программы требуется подключение к интернету.\nПроверьте соединение и попробуйте снова.")
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description_label.setWordWrap(True)
        description_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 16px;
                background: transparent;
                border: none;
                line-height: 1.6;
            }
        """)
        layout.addWidget(description_label)
        
        if self.on_retry:
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            
            retry_button = QPushButton("🔄 Повторить попытку")
            retry_button.setFixedHeight(45)
            retry_button.clicked.connect(self.on_retry)
            retry_button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #4a9eff, stop:1 #3a7ed8);
                    color: white;
                    border: none;
                    padding: 12px 30px;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #5aafff, stop:1 #4a8ee8);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #3a7ed8, stop:1 #2a6ec8);
                }
            """)
            
            button_layout.addWidget(retry_button)
            button_layout.addStretch()
            
            layout.addLayout(button_layout)