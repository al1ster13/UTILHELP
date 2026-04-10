from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QPushButton, QWidget, QGraphicsOpacityEffect
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QSize
from resource_path import get_icon_path
from scroll_helper import configure_scroll_area


def _close_btn_style(c: dict, radius: int = 12) -> str:
    return f"""
        QPushButton {{
            background-color: {c['bg_pressed']};
            border: none;
            color: {c['text_primary']};
            font-size: 14px;
            font-weight: bold;
            border-radius: {radius}px;
            padding: 0px;
            margin: 0px;
            text-align: center;
            outline: none;
        }}
        QPushButton:hover {{ background-color: {c['bg_hover']}; }}
        QPushButton:pressed {{ background-color: {c['border_hover']}; }}
        QPushButton:focus {{ outline: none; border: none; }}
    """


def _action_btn_style(c: dict, bg: str, hover: str, pressed: str) -> str:
    return f"""
        QPushButton {{
            background-color: {bg};
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial, sans-serif;
            outline: none;
        }}
        QPushButton:hover {{ background-color: {hover}; }}
        QPushButton:pressed {{ background-color: {pressed}; }}
        QPushButton:focus {{ outline: none; border: none; }}
    """


class CustomMessageDialog(QDialog):
    def __init__(self, title, message, icon_path=None, parent=None):
        super().__init__(parent)

        from theme_manager import theme_manager
        c = theme_manager.colors

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
        background.setStyleSheet(f"""
            background-color: {c['bg_secondary']};
            border-radius: 15px;
            border: 1px solid {c['border']};
        """)

        bg_layout = QVBoxLayout(background)
        bg_layout.setContentsMargins(20, 20, 20, 20)
        bg_layout.setSpacing(20)

        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
            }}
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        close_button = QPushButton()
        close_button.setFixedSize(28, 28)
        close_button.clicked.connect(self.fade_close)
        close_icon_path = get_icon_path("closemenu.png")
        if close_icon_path:
            close_button.setIcon(QIcon(close_icon_path))
            close_button.setIconSize(QSize(16, 16))
            close_button.setFlat(True)
        else:
            close_button.setText("✕")
        close_button.setStyleSheet(_close_btn_style(c))
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
                        icon_label.setPixmap(pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                    else:
                        icon_label.setText("ℹ")
                else:
                    icon_label.setText("ℹ")
            except:
                icon_label.setText("ℹ")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            icon_label.setStyleSheet("background: transparent; border: none;")
            icon_label.setFixedSize(48, 48)
            content_layout.addWidget(icon_label)

        message_label = QLabel(message)
        message_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                background: transparent;
                border: none;
            }}
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
        ok_button.setStyleSheet(_action_btn_style(c, c['bg_pressed'], c['bg_hover'], c['border_hover']))
        button_layout.addWidget(ok_button)

        bg_layout.addLayout(button_layout)
        main_layout.addWidget(background)

        QTimer.singleShot(0, self.center_on_parent)

    def center_on_parent(self):
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
            y = parent_rect.y() + (parent_rect.height() - self.height()) // 2
            self.move(x, y)

    def showEvent(self, event):
        super().showEvent(event)
        self.opacity_effect.setOpacity(0.0)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()

    def fade_close(self):
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
        if event.key() in [Qt.Key.Key_Escape, Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            self.fade_close()
        else:
            super().keyPressEvent(event)


class CustomNewsDialog(QDialog):
    """Окно для показа новостей"""
    def __init__(self, title, content, parent=None):
        super().__init__(parent)

        import re
        from localization import t
        from theme_manager import theme_manager
        c = theme_manager.colors

        self.setWindowTitle(title)
        self.setFixedSize(750, 450)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(False)  # Не блокируем родительское окно

        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self.opacity_effect)

        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(250)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.is_closing = False
        
        # Устанавливаем event filter на родительское окно для отслеживания кликов вне диалога
        if parent:
            parent.installEventFilter(self)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        background = QWidget()
        background.setStyleSheet(f"""
            background-color: {c['bg_secondary']};
            border-radius: 15px;
            border: 1px solid {c['border']};
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
            close_button.setIcon(QIcon(close_icon_path))
            close_button.setIconSize(QSize(16, 16))
            close_button.setFlat(True)
        else:
            close_button.setText("✕")
        close_button.setStyleSheet(_close_btn_style(c, radius=14))
        title_layout.addWidget(close_button)

        bg_layout.addLayout(title_layout)

        content_label = QLabel()
        content_label.setTextFormat(Qt.TextFormat.RichText)
        content_label.setText(content)
        content_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
                background-color: transparent;
                border: none;
            }}
        """)
        content_label.setWordWrap(True)
        content_label.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_label)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        configure_scroll_area(scroll_area)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{ border: none; background-color: transparent; }}
            QScrollBar:vertical {{
                background-color: transparent;
                width: 16px; border-radius: 8px; margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {c['scrollbar_handle']};
                border-radius: 8px; min-height: 30px; margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{ background-color: {c['scrollbar_hover']}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none; background: none; height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
        """)

        bg_layout.addWidget(scroll_area)
        main_layout.addWidget(background)

    def showEvent(self, event):
        super().showEvent(event)
        self.center_on_screen()
        self.opacity_effect.setOpacity(0.0)

    def start_fade_in(self):
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()

    def fade_close(self):
        if not self.is_closing:
            self.is_closing = True
            # Удаляем event filter
            if self.parent():
                self.parent().removeEventFilter(self)
            try:
                self.fade_animation.finished.disconnect()
            except:
                pass
            self.fade_animation.finished.connect(self.accept)
            self.fade_animation.setStartValue(1.0)
            self.fade_animation.setEndValue(0.0)
            self.fade_animation.start()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.fade_close()
        else:
            super().keyPressEvent(event)
    
    def eventFilter(self, obj, event):
        """Обработка событий для закрытия окна при клике вне его"""
        if event.type() == event.Type.MouseButtonPress:
            # Проверяем, что клик был вне диалога
            if not self.geometry().contains(self.mapFromGlobal(event.globalPosition().toPoint())):
                self.fade_close()
                return True
        return super().eventFilter(obj, event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if event.position().y() < 50:
                self.dragging = True
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'dragging') and self.dragging and event.buttons() & Qt.MouseButton.LeftButton:
            new_pos = event.globalPosition().toPoint() - self.drag_position
            if self.parent():
                parent_rect = self.parent().geometry()
                new_x = max(parent_rect.x() + 10, min(new_pos.x(), parent_rect.x() + parent_rect.width() - self.width() - 10))
                new_y = max(parent_rect.y() + 60, min(new_pos.y(), parent_rect.y() + parent_rect.height() - self.height() - 35))
                self.move(new_x, new_y)
            else:
                self.move(new_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if hasattr(self, 'dragging'):
                self.dragging = False
            event.accept()

    def center_on_screen(self):
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
            y = parent_rect.y() + (parent_rect.height() - self.height()) // 2
            x = max(parent_rect.x() + 10, min(x, parent_rect.x() + parent_rect.width() - self.width() - 10))
            y = max(parent_rect.y() + 60, min(y, parent_rect.y() + parent_rect.height() - self.height() - 35))
            self.move(x, y)
        else:
            screen = self.screen().geometry()
            self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)


class CustomConfirmDialog(QDialog):
    """Диалог подтверждения"""
    def __init__(self, title, message, parent=None):
        super().__init__(parent)

        from theme_manager import theme_manager
        c = theme_manager.colors

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
        background.setStyleSheet(f"""
            background-color: {c['bg_secondary']};
            border-radius: 15px;
            border: 1px solid {c['border']};
        """)

        bg_layout = QVBoxLayout(background)
        bg_layout.setContentsMargins(20, 20, 20, 20)
        bg_layout.setSpacing(20)

        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
            }}
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        bg_layout.addLayout(title_layout)

        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setFixedHeight(105)
        message_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                padding: 0px 15px;
                margin-top: -10px;
            }}
        """)
        bg_layout.addWidget(message_label)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        yes_button = QPushButton("Да")
        yes_button.setFixedSize(80, 35)
        yes_button.clicked.connect(self.accept_dialog)
        yes_button.setStyleSheet(_action_btn_style(c, c['error'], "#c0392b", "#a93226"))
        buttons_layout.addWidget(yes_button)

        no_button = QPushButton("Нет")
        no_button.setFixedSize(80, 35)
        no_button.clicked.connect(self.fade_close)
        no_button.setStyleSheet(_action_btn_style(c, c['bg_pressed'], c['bg_hover'], c['border_hover']))
        buttons_layout.addWidget(no_button)

        bg_layout.addLayout(buttons_layout)
        main_layout.addWidget(background)

        if parent:
            self.move(
                parent.x() + (parent.width() - self.width()) // 2,
                parent.y() + (parent.height() - self.height()) // 2
            )

    def accept_dialog(self):
        self.result_value = True
        self.fade_close()

    def fade_close(self):
        if self.is_closing:
            return
        self.is_closing = True
        self.fade_animation.finished.connect(self.accept)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.start()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.fade_close()
        elif event.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            self.accept_dialog()
        else:
            super().keyPressEvent(event)

    def get_result(self):
        return self.result_value
