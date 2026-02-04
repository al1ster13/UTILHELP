from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QPushButton, QWidget, QGraphicsOpacityEffect
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QSize
from resource_path import get_icon_path
from scroll_helper import configure_scroll_area


class CustomMessageDialog(QDialog):
    def __init__(self, title, message, icon_path=None, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle(title)
        self.setFixedSize(400, 250)  
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(250)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.is_closing = False
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        background = QWidget()
        background.setStyleSheet("""
            background-color: #2d2d2d;
            border-radius: 15px;
            border: 1px solid #404040;
        """)
        
        bg_layout = QVBoxLayout(background)
        bg_layout.setContentsMargins(20, 20, 20, 20)
        bg_layout.setSpacing(20)
        
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }
        """)
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        close_button = QPushButton()
        close_button.setFixedSize(28, 28)  
        close_button.clicked.connect(self.fade_close)
        

        close_icon_path = get_icon_path("closemenu.png")
        if close_icon_path:
            icon = QIcon(close_icon_path)
            close_button.setIcon(icon)
            close_button.setIconSize(QSize(16, 16))  
            close_button.setFlat(True)  
            close_button.setStyleSheet("""
                QPushButton {
                    background-color: #666666;
                    border: none;
                    color: #ffffff;
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 12px;
                    padding: 0px;
                    margin: 0px;
                    text-align: center;
                    line-height: 21px;
                    outline: none;
                }
                QPushButton:hover {
                    background-color: #777777;
                }
                QPushButton:pressed {
                    background-color: #555555;
                }
                QPushButton:focus {
                    outline: none;
                    border: none;
                }
            """)
        else:
            close_button.setText("✕")  
            close_button.setStyleSheet("""
                QPushButton {
                    background-color: #666666;
                    border: none;
                    color: #ffffff;
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 12px;
                    padding: 0px;
                    margin: 0px;
                    text-align: center;
                    line-height: 21px;
                    outline: none;
                }
                QPushButton:hover {
                    background-color: #777777;
                }
                QPushButton:pressed {
                    background-color: #555555;
                }
                QPushButton:focus {
                    outline: none;
                    border: none;
                }
            """)

        title_layout.addWidget(close_button)
        
        bg_layout.addLayout(title_layout)
        
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        
        if icon_path:
            icon_label = QLabel()
            try:
                full_icon_path = get_icon_path(icon_path)
                if full_icon_path:
                    pixmap = QPixmap(full_icon_path)
                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        icon_label.setPixmap(scaled_pixmap)
                    else:
                        icon_label.setText("ℹ")
                        icon_label.setStyleSheet("font-size: 48px; color: #3498db; background: transparent; border: none;")
                else:
                    icon_label.setText("ℹ")
                    icon_label.setStyleSheet("font-size: 48px; color: #3498db; background: transparent; border: none;")
            except:
                icon_label.setText("ℹ")
                icon_label.setStyleSheet("font-size: 48px; color: #3498db; background: transparent; border: none;")
            
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            icon_label.setStyleSheet("background: transparent; border: none; padding: 0px; margin: 0px;")
            icon_label.setFixedSize(48, 48)
            content_layout.addWidget(icon_label)
        
        message_label = QLabel(message)
        message_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                line-height: 1.5;
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }
        """)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        content_layout.addWidget(message_label)
        
        bg_layout.addLayout(content_layout)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_button = QPushButton("OK")
        ok_button.setFixedSize(80, 35)
        ok_button.clicked.connect(self.fade_close)
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #666666;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 0px;
                margin: 0px;
            }
            QPushButton:hover {
                background-color: #777777;
            }
            QPushButton:pressed {
                background-color: #555555;
            }
        """)
        button_layout.addWidget(ok_button)
        
        bg_layout.addLayout(button_layout)
        
        main_layout.addWidget(background)
        
        QTimer.singleShot(0, self.center_on_parent)

    def center_on_parent(self):
        """Центрирование окна относительно родительского"""
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
            y = parent_rect.y() + (parent_rect.height() - self.height()) // 2
            self.move(x, y)

    def showEvent(self, event):
        """Обработка события показа окна"""
        super().showEvent(event)
        self.opacity_effect.setOpacity(0.0)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()

    def fade_close(self):
        """Закрытие с анимацией"""
        if not self.is_closing:
            self.is_closing = True
            
            try:
                self.fade_animation.finished.disconnect()
            except:
                pass
            
            self.fade_animation.finished.connect(self.accept)
            self.fade_animation.setStartValue(1.0)
            self.fade_animation.setEndValue(0.0)
            self.fade_animation.start()

    def keyPressEvent(self, event):
        """Обработка нажатий клавиш"""
        if event.key() in [Qt.Key.Key_Escape, Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            self.fade_close()
        else:
            super().keyPressEvent(event)


class CustomNewsDialog(QDialog):
    """Окно для показа новостей"""
    def __init__(self, title, content, parent=None):
        super().__init__(parent)
        
        import re
        
        date_match = re.search(r'<strong>Дата:</strong>\s*([^<]+)', content)
        date_text = date_match.group(1).strip() if date_match else "Дата не указана"
        
        description_match = re.search(r'<div[^>]*margin-top:\s*15px[^>]*>(.*?)</div>', content, re.DOTALL)
        description_text = description_match.group(1).strip() if description_match else content
        
        self.setWindowTitle(title)
        self.setFixedSize(750, 450)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(250)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.is_closing = False
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        background = QWidget()
        background.setStyleSheet("""
            background-color: #2d2d2d;
            border-radius: 15px;
        """)
        
        bg_layout = QVBoxLayout(background)
        bg_layout.setContentsMargins(20, 5, 15, 20) 
        bg_layout.setSpacing(0)
        

        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title_layout.addStretch()  
        
        close_button = QPushButton()
        close_button.setFixedSize(28, 28)  
        close_button.clicked.connect(self.fade_close)
        
        close_icon_path = get_icon_path("closemenu.png")
        if close_icon_path:
            icon = QIcon(close_icon_path)
            close_button.setIcon(icon)
            close_button.setIconSize(QSize(16, 16))  
            close_button.setFlat(True)  
            close_button.setStyleSheet("""
                QPushButton {
                    background-color: #666666;
                    border: none;
                    color: #ffffff;
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 14px;
                    margin: 0px;
                    text-align: center;
                    padding: 0px;
                    outline: none;
                }
                QPushButton:hover {
                    background-color: #777777;
                }
                QPushButton:pressed {
                    background-color: #555555;
                }
                QPushButton:focus {
                    outline: none;
                    border: none;
                }
            """)
        else:
            close_button.setText("✕")  
            close_button.setStyleSheet("""
                QPushButton {
                    background-color: #666666;
                    border: none;
                    color: #ffffff;
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 14px;
                    margin: 0px;
                    text-align: center;
                    padding: 0px;
                    outline: none;
                }
                QPushButton:hover {
                    background-color: #777777;
                }
                QPushButton:pressed {
                    background-color: #555555;
                }
                QPushButton:focus {
                    outline: none;
                    border: none;
                }
            """)

        title_layout.addWidget(close_button)
        
        bg_layout.addLayout(title_layout)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin-bottom: 10px;
                text-align: center;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bg_layout.addWidget(title_label)
        
        date_label = QLabel(f"Дата: {date_text}")
        date_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin-bottom: 15px;
                text-align: center;
            }
        """)
        date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bg_layout.addWidget(date_label)
        
        content_label = QLabel()
        content_label.setTextFormat(Qt.TextFormat.RichText)  
        
        formatted_description = f"""
        <div style="color: #ffffff; line-height: 1.6; font-size: 13px; font-family: 'Segoe UI', Arial, sans-serif;">
            {description_text}
        </div>
        """
        content_label.setText(formatted_description)
        content_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
                line-height: 1.6;
                background-color: transparent;
            }
        """)
        content_label.setWordWrap(True)
        content_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_label)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        configure_scroll_area(scroll_area)
        
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
                margin-top: 0px;
            }
            QScrollBar:vertical {
                background-color: transparent;
                width: 16px;
                border-radius: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 8px;
                min-height: 30px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666666;
            }
            QScrollBar::handle:vertical:pressed {
                background-color: #777777;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        bg_layout.addWidget(scroll_area)
        
        main_layout.addWidget(background)

    def showEvent(self, event):
        """Обработка события показа окна"""
        super().showEvent(event)
        self.opacity_effect.setOpacity(0.0)

    def start_fade_in(self):
        """Запуск анимации появления"""
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()

    def fade_close(self):
        """Закрытие с анимацией"""
        if not self.is_closing:
            self.is_closing = True
    
            try:
                self.fade_animation.finished.disconnect()
            except:
                pass
            
            self.fade_animation.finished.connect(self.accept)
            
            self.fade_animation.setStartValue(1.0)
            self.fade_animation.setEndValue(0.0)
            self.fade_animation.start()

    def keyPressEvent(self, event):
        """Обработка клавиш"""
        if event.key() == Qt.Key.Key_Escape:
            self.fade_close()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        """Обработка мыши для перетаскивания"""
        if event.button() == Qt.MouseButton.LeftButton:
            if event.position().y() < 50:  
                self.dragging = True
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        """Обработка перемещения мыши для перетаскивания"""
        if hasattr(self, 'dragging') and self.dragging and event.buttons() & Qt.MouseButton.LeftButton:
            new_pos = event.globalPosition().toPoint() - self.drag_position
            
            if self.parent():
                parent_rect = self.parent().geometry()
                min_x = parent_rect.x() + 10
                max_x = parent_rect.x() + parent_rect.width() - self.width() - 10
                min_y = parent_rect.y() + 60
                max_y = parent_rect.y() + parent_rect.height() - self.height() - 35
                
                new_x = max(min_x, min(new_pos.x(), max_x))
                new_y = max(min_y, min(new_pos.y(), max_y))
                self.move(new_x, new_y)
            else:
                self.move(new_pos)
            
            event.accept()

    def mouseReleaseEvent(self, event):
        """Обработка отпускания мыши"""
        if event.button() == Qt.MouseButton.LeftButton:
            if hasattr(self, 'dragging'):
                self.dragging = False
            event.accept()

    def showEvent(self, event):
        """Обработка события показа окна"""
        super().showEvent(event)
        self.center_on_screen()

    def center_on_screen(self):
        """Центрирование окна на экране или в родительском окне"""
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
            y = parent_rect.y() + (parent_rect.height() - self.height()) // 2
            
            min_x = parent_rect.x() + 10
            max_x = parent_rect.x() + parent_rect.width() - self.width() - 10
            min_y = parent_rect.y() + 60
            max_y = parent_rect.y() + parent_rect.height() - self.height() - 35
            
            x = max(min_x, min(x, max_x))
            y = max(min_y, min(y, max_y))
            self.move(x, y)
        else:
            screen = self.screen().geometry()
            x = (screen.width() - self.width()) // 2
            y = (screen.height() - self.height()) // 2
            self.move(x, y)


class CustomConfirmDialog(QDialog):
    """Диалог подтверждения"""
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle(title)
        self.setFixedSize(380, 220)  
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.result_value = False
        
        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(250)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.is_closing = False
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        background = QWidget()
        background.setStyleSheet("""
            background-color: #2d2d2d;
            border-radius: 15px;
            border: 1px solid #404040;
        """)
        
        bg_layout = QVBoxLayout(background)
        bg_layout.setContentsMargins(20, 20, 20, 20)
        bg_layout.setSpacing(20)
        
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        bg_layout.addLayout(title_layout)
        
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setFixedHeight(105)  
        message_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                line-height: 1.2;
                padding: 0px 15px;
                margin-top: -10px;
            }
        """)
        bg_layout.addWidget(message_label)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        yes_button = QPushButton("Да")
        yes_button.setFixedSize(80, 35)
        yes_button.clicked.connect(self.accept_dialog)
        yes_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                outline: none;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
            QPushButton:focus {
                outline: none;
                border: none;
            }
        """)
        buttons_layout.addWidget(yes_button)
        
        no_button = QPushButton("Нет")
        no_button.setFixedSize(80, 35)
        no_button.clicked.connect(self.fade_close)
        no_button.setStyleSheet("""
            QPushButton {
                background-color: #666666;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                outline: none;
                margin-left: 10px;
            }
            QPushButton:hover {
                background-color: #777777;
            }
            QPushButton:pressed {
                background-color: #555555;
            }
            QPushButton:focus {
                outline: none;
                border: none;
            }
        """)
        buttons_layout.addWidget(no_button)
        
        bg_layout.addLayout(buttons_layout)
        
        main_layout.addWidget(background)
        
        if parent:
            self.move(
                parent.x() + (parent.width() - self.width()) // 2,
                parent.y() + (parent.height() - self.height()) // 2
            )

    def accept_dialog(self):
        """Принять диалог (Да)"""
        self.result_value = True
        self.fade_close()

    def fade_close(self):
        """Закрытие с анимацией"""
        if self.is_closing:
            return
            
        self.is_closing = True
        self.fade_animation.finished.connect(self.accept)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.start()

    def keyPressEvent(self, event):
        """Обработка нажатий клавиш"""
        if event.key() == Qt.Key.Key_Escape:
            self.fade_close()
        elif event.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            self.accept_dialog()
        else:
            super().keyPressEvent(event)

    def get_result(self):
        """Результат диалога"""
        return self.result_value