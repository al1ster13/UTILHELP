"""
Кастомные уведомления
"""
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QUrl
from PyQt6.QtGui import QPixmap
from PyQt6.QtMultimedia import QSoundEffect
from resource_path import get_icon_path, get_sound_path


class ToastNotification(QWidget):
    def __init__(self, title: str, message: str, icon_name: str = "complete.png", 
                 duration: int = 5000, notification_type: str = "success", parent=None,
                 on_click=None, play_sound: bool = True):
        super().__init__(parent)
        
        self.duration = duration
        self.notification_type = notification_type
        self.on_click = on_click
        self.play_sound = play_sound
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        self.setMinimumSize(320, 70)
        self.setMaximumSize(320, 80)
        
        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.fade_in_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_animation.setDuration(250)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(0.95)
        self.fade_in_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.fade_out_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out_animation.setDuration(250)
        self.fade_out_animation.setStartValue(0.95)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.fade_out_animation.finished.connect(self.close)
        
        self.close_timer = QTimer()
        self.close_timer.setSingleShot(True)
        self.close_timer.timeout.connect(self.start_fade_out)
        
        self.sound_effect = None
        if self.play_sound:
            self._setup_sound()
        
        self._setup_ui(title, message, icon_name)
    
    def _setup_sound(self) -> None:
        """Настройка звукового эффекта"""
        try:
            if self.notification_type == "error":
                sound_file = "utilhelp-notification-error.wav"
            else:
                sound_file = "utilhelp-notification.wav"
            
            sound_path = get_sound_path(sound_file)
            if sound_path:
                self.sound_effect = QSoundEffect()
                self.sound_effect.setSource(QUrl.fromLocalFile(sound_path))
                self.sound_effect.setVolume(0.5)  # 50% громкости
        except Exception as e:
            pass
    
    def _setup_ui(self, title: str, message: str, icon_name: str) -> None:
        """Настройка интерфейса"""
        from theme_manager import theme_manager
        c = theme_manager.colors

        container = QWidget()
        container.setStyleSheet(f"""
            QWidget {{
                background-color: {c['bg_secondary']};
                border-radius: 8px;
                border: 1px solid {c['border']};
            }}
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)
        
        content_layout = QHBoxLayout(container)
        content_layout.setContentsMargins(15, 12, 15, 12)
        content_layout.setSpacing(12)
        
        icon_label = QLabel()
        icon_path = get_icon_path(icon_name)
        if icon_path:
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                from theme_manager import colorize_pixmap
                if theme_manager.is_light():
                    pixmap = colorize_pixmap(pixmap, c['text_secondary'])
                scaled_pixmap = pixmap.scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                icon_label.setPixmap(scaled_pixmap)
        icon_label.setFixedSize(24, 24)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(icon_label)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 13px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
            }}
        """)
        title_label.setWordWrap(True)
        text_layout.addWidget(title_label)
        
        message_label = QLabel(message)
        message_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_secondary']};
                font-size: 11px;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
            }}
        """)
        message_label.setWordWrap(True)
        text_layout.addWidget(message_label)
        
        text_layout.addStretch()
        content_layout.addLayout(text_layout)
        
        close_btn = QLabel("✕")
        close_btn.setFixedSize(20, 20)
        close_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        close_btn.setStyleSheet(f"""
            QLabel {{
                color: {c['text_disabled']};
                font-size: 16px;
                font-weight: bold;
                background: transparent;
                border: none;
                border-radius: 10px;
                outline: none;
            }}
            QLabel:hover {{
                color: {c['text_primary']};
                background-color: {c['bg_hover']};
            }}
        """)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        close_btn.mousePressEvent = lambda e: self.start_fade_out()
        content_layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignTop)
    
    def show_notification(self) -> None:
        """Показать уведомление"""
        screen = self.screen().geometry()
        x = screen.width() - self.width() - 20
        y = screen.height() - self.height() - 60
        self.move(x, y)
        
        self.show()
        self.fade_in_animation.start()
        
        if self.sound_effect:
            try:
                self.sound_effect.play()
            except:
                pass
        
        self.close_timer.start(self.duration)
    
    def start_fade_out(self) -> None:
        """Начать анимацию исчезновения"""
        self.close_timer.stop()
        self.fade_out_animation.start()
    
    def mousePressEvent(self, event) -> None:
        """Клик по уведомлению"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.on_click:
                self.on_click()
            self.start_fade_out()


class ToastNotificationManager:
    """Менеджер уведомлений"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.active_notifications = []
        self.max_notifications = 5
        self.spacing = 10
    
    def show_notification(self, title: str, message: str, icon_name: str = "complete.png",
                         duration: int = 5000, notification_type: str = "success",
                         on_click=None, play_sound: bool = True) -> None:
        """Показать новое уведомление"""
        if len(self.active_notifications) >= self.max_notifications:
            oldest = self.active_notifications.pop(0)
            oldest.start_fade_out()
        
        notification = ToastNotification(
            title, message, icon_name, duration, notification_type, self.parent, on_click, play_sound
        )
        
        self.active_notifications.append(notification)
        
        self._position_notification(notification)
        
        notification.show()
        notification.fade_in_animation.start()
        
        if play_sound and notification.sound_effect:
            try:
                notification.sound_effect.play()
            except:
                pass
        
        notification.close_timer.start(duration)
        
        notification.fade_out_animation.finished.connect(
            lambda: self._remove_notification(notification)
        )
    
    def _position_notification(self, notification: ToastNotification) -> None:
        """Позиционировать уведомление с учетом других"""
        screen = notification.screen().geometry()
        x = screen.width() - notification.width() - 20
        
        y = screen.height() - notification.height() - 60
        
        for existing in self.active_notifications:
            if existing != notification and existing.isVisible():
                y -= (existing.height() + self.spacing)
        
        notification.move(x, y)
    
    def _remove_notification(self, notification: ToastNotification) -> None:
        """Удалить уведомление из списка"""
        if notification in self.active_notifications:
            self.active_notifications.remove(notification)
        
        self._reposition_notifications()
    
    def _reposition_notifications(self) -> None:
        """Переместить все активные уведомления"""
        screen_height = 0
        if self.active_notifications:
            screen = self.active_notifications[0].screen().geometry()
            screen_height = screen.height()
        
        y = screen_height - 60
        for notification in reversed(self.active_notifications):
            if notification.isVisible():
                current_pos = notification.pos()
                new_y = y - notification.height()
                
                notification.move(current_pos.x(), new_y)
                y = new_y - self.spacing
    
    def show_download_notification(self, program_name: str, success: bool = True, 
                                   item_type: str = "программа") -> None:
        """Показать уведомление о завершении загрузки"""
        from localization import t
        from settings_manager import settings_manager
        
        play_sound = settings_manager.get_setting("notification_sounds", True)
        
        is_driver = item_type in ["драйвер", "driver", "drivers"]
        
        if success:
            title = t("notifications.download_complete")
            if is_driver:
                message = t("notifications.driver_downloaded", name=program_name)
            else:
                message = t("notifications.program_downloaded", name=program_name)
            icon = "completenotif.png"
            notification_type = "success"
            
            def go_to_library():
                self._open_library()
            
            self.show_notification(title, message, icon, 5000, notification_type, on_click=go_to_library, play_sound=play_sound)
        else:
            title = t("notifications.download_failed")
            if is_driver:
                message = t("notifications.driver_download_failed", name=program_name)
            else:
                message = t("notifications.program_download_failed", name=program_name)
            icon = "errornotif.png"
            notification_type = "error"
            
            self.show_notification(title, message, icon, 5000, notification_type, play_sound=play_sound)
    
    def show_installation_notification(self, program_name: str, success: bool = True) -> None:
        """Показать уведомление о завершении установки"""
        from localization import t
        from settings_manager import settings_manager
        
        play_sound = settings_manager.get_setting("notification_sounds", True)
        
        if success:
            title = t("notifications.installation_complete")
            message = t("notifications.program_installed", name=program_name)
            icon = "completenotif.png"
            notification_type = "success"
        else:
            title = t("notifications.installation_failed")
            message = t("notifications.program_install_failed", name=program_name)
            icon = "errornotif.png"
            notification_type = "error"
        
        self.show_notification(title, message, icon, 5000, notification_type, play_sound=play_sound)
    
    def show_update_notification(self, version: str) -> None:
        """Показать уведомление о доступном обновлении"""
        from localization import t
        from settings_manager import settings_manager
        
        play_sound = settings_manager.get_setting("notification_sounds", True)
        
        title = t("notifications.update_available")
        message = t("notifications.new_version", version=version)
        icon = "updatenotif.png"
        notification_type = "info"
        
        self.show_notification(title, message, icon, 8000, notification_type, play_sound=play_sound)
    
    def clear_all(self) -> None:
        """Закрыть все уведомления"""
        for notification in self.active_notifications[:]:
            notification.start_fade_out()
        self.active_notifications.clear()
    
    def _open_library(self) -> None:
        """Открыть библиотеку в главном окне"""
        try:
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
            
            if app:
                for widget in app.topLevelWidgets():
                    if widget.__class__.__name__ == 'MainWindow':
                        if widget.isMinimized():
                            widget.showNormal()
                        
                        widget.raise_()
                        widget.activateWindow()
                        
                        if hasattr(widget, 'tab_widget'):
                            for i in range(widget.tab_widget.count()):
                                tab_text = widget.tab_widget.tabText(i)
                                if 'БИБЛИОТЕКА' in tab_text or 'LIBRARY' in tab_text:
                                    widget.tab_widget.setCurrentIndex(i)
                                    break
                        break
        except Exception as e:
            from logger import log_error
            log_error(f"Ошибка открытия библиотеки: {e}")


_toast_manager = None


def get_toast_manager(parent=None):
    """Получить глобальный экземпляр менеджера уведомлений"""
    global _toast_manager
    if _toast_manager is None:
        _toast_manager = ToastNotificationManager(parent)
    return _toast_manager
