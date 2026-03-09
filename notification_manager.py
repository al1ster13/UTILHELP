import os
import sys
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QBrush, QColor
from PyQt6.QtCore import QTimer
from resource_path import get_icon_path
from logger import log_info, log_error, log_warning, log_debug


class NotificationManager:
    """Менеджер уведомлений (системные и кастомные)"""
    
    def __init__(self, main_window=None):
        self.main_window = main_window
        self.tray_icon = None
        self.toast_manager = None
        self.setup_tray_icon()
    
    def _get_toast_manager(self):
        """Получить менеджер toast-уведомлений"""
        if self.toast_manager is None:
            try:
                from ui.components.toast_notification import get_toast_manager
                self.toast_manager = get_toast_manager(self.main_window)
            except Exception as e:
                log_error(f"Ошибка загрузки toast manager: {e}")
        return self.toast_manager
    
    def _should_use_custom_notifications(self):
        """Проверить, нужно ли использовать кастомные уведомления"""
        try:
            from settings_manager import settings_manager
            
            notifications_enabled = settings_manager.get_setting("notifications_enabled", True)
            if not notifications_enabled:
                log_info("Notifications disabled in settings")
                return False
            
            style = settings_manager.get_setting("notification_style", "custom")
            log_info(f"Notification style: {style}")
            return style == "custom"
        except Exception as e:
            log_error(f"Ошибка проверки настроек уведомлений: {e}")
            # По умолчанию используем кастомные
            return True
    
    def setup_tray_icon(self):
        """Настройка системного трея"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        
        try:
            from PyQt6.QtCore import QFile
            icon_path = get_icon_path("utilhelp14x14.png")
            
            if icon_path and (icon_path.startswith(":/") or os.path.exists(icon_path)):
                icon = QIcon(icon_path)
            else:
                icon = self.create_default_icon()
            
            self.tray_icon = QSystemTrayIcon(icon)
            self.tray_icon.setToolTip("UTILHELP")
            
            menu = QMenu()
            show_action = menu.addAction("Показать UTILHELP")
            show_action.triggered.connect(self.show_main_window)
            menu.addSeparator()
            exit_action = menu.addAction("Выход")
            exit_action.triggered.connect(QApplication.quit)
            
            self.tray_icon.setContextMenu(menu)
            self.tray_icon.activated.connect(self.on_tray_activated)
            
        except Exception as e:
            log_error(f"Ошибка настройки трея: {e}")
    
    def create_default_icon(self):
        """Создание иконки по умолчанию"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(0, 0, 0, 0))
        
        painter = QPainter(pixmap)
        painter.setBrush(QBrush(QColor(70, 130, 180)))
        painter.drawEllipse(2, 2, 12, 12)
        painter.end()
        
        return QIcon(pixmap)
    
    def show_tray_icon(self):
        """Показать иконку в трее"""
        if self.tray_icon:
            self.tray_icon.show()
    
    def hide_tray_icon(self):
        """Скрыть иконку из трея"""
        if self.tray_icon:
            self.tray_icon.hide()
    
    def on_tray_activated(self, reason):
        """Обработка клика по иконке в трее"""
        try:
            if reason == 2:  # DoubleClick
                self.show_main_window()
        except Exception as e:
            log_error(f"Ошибка обработки клика по трею: {e}")
    
    def show_main_window(self):
        """Показать главное окно"""
        try:
            if self.main_window:
                self.main_window.show()
                self.main_window.raise_()
                self.main_window.activateWindow()
                if self.main_window.isMinimized():
                    self.main_window.showNormal()
            else:
                app = QApplication.instance()
                if app:
                    for widget in app.topLevelWidgets():
                        if widget.__class__.__name__ == 'MainWindow':
                            widget.show()
                            widget.raise_()
                            widget.activateWindow()
                            if widget.isMinimized():
                                widget.showNormal()
                            break
        except Exception as e:
            log_error(f"Ошибка показа главного окна: {e}")
    
    def show_download_notification(self, program_name, success=True, item_type="программа"):
        """Показать уведомление о завершении загрузки"""
        try:
            from settings_manager import settings_manager
            if not settings_manager.get_setting("notifications_enabled", True):
                log_info("Notifications disabled, skipping download notification")
                return
        except Exception as e:
            log_error(f"Ошибка проверки настроек: {e}")
        
        if self._should_use_custom_notifications():
            toast_manager = self._get_toast_manager()
            if toast_manager:
                toast_manager.show_download_notification(program_name, success, item_type)
                return
        
        # Используем системные уведомления
        if not self.tray_icon:
            return
            
        if not QSystemTrayIcon.supportsMessages():
            return
        
        try:
            if success:
                title = "Загрузка завершена"
                if item_type == "driver":
                    message = f"Драйвер '{program_name}' успешно загружен"
                else:
                    message = f"Программа '{program_name}' успешно загружена"
                icon = QSystemTrayIcon.MessageIcon.Information
            else:
                title = "Ошибка загрузки"
                if item_type == "driver":
                    message = f"Не удалось загрузить драйвер '{program_name}'"
                else:
                    message = f"Не удалось загрузить программу '{program_name}'"
                icon = QSystemTrayIcon.MessageIcon.Critical
            
            self.tray_icon.showMessage(title, message, icon, 5000)
            
        except Exception as e:
            log_error(f"Ошибка показа уведомления загрузки: {e}")
    
    def show_installation_notification(self, program_name, success=True):
        """Показать уведомление о завершении установки"""
        try:
            from settings_manager import settings_manager
            if not settings_manager.get_setting("notifications_enabled", True):
                log_info("Notifications disabled, skipping installation notification")
                return
        except Exception as e:
            log_error(f"Ошибка проверки настроек: {e}")
        
        if self._should_use_custom_notifications():
            toast_manager = self._get_toast_manager()
            if toast_manager:
                toast_manager.show_installation_notification(program_name, success)
                return
        
        # Используем системные уведомления
        if not self.tray_icon or not QSystemTrayIcon.supportsMessages():
            return
        
        try:
            if success:
                title = "Установка завершена"
                message = f"'{program_name}' успешно установлен"
                icon = QSystemTrayIcon.MessageIcon.Information
            else:
                title = "Ошибка установки"
                message = f"Не удалось установить '{program_name}'"
                icon = QSystemTrayIcon.MessageIcon.Warning
            
            self.tray_icon.showMessage(title, message, icon, 5000)
            
        except Exception as e:
            log_error(f"Ошибка показа уведомления установки: {e}")
    
    def show_update_notification(self, version):
        """Показать уведомление о доступном обновлении"""
        try:
            from settings_manager import settings_manager
            if not settings_manager.get_setting("notifications_enabled", True):
                log_info("Notifications disabled, skipping update notification")
                return
        except Exception as e:
            log_error(f"Ошибка проверки настроек: {e}")
        
        if self._should_use_custom_notifications():
            toast_manager = self._get_toast_manager()
            if toast_manager:
                toast_manager.show_update_notification(version)
                return
        
        # Используем системные уведомления
        if not self.tray_icon or not QSystemTrayIcon.supportsMessages():
            return
        
        try:
            title = "Доступно обновление"
            message = f"Доступна новая версия UTILHELP {version}"
            icon = QSystemTrayIcon.MessageIcon.Information
            
            self.tray_icon.showMessage(title, message, icon, 8000)
            
        except Exception as e:
            log_error(f"Ошибка показа уведомления обновления: {e}")
    
    def show_custom_notification(self, title, message, success=True):
        """Показать пользовательское уведомление"""
        if not self.tray_icon or not QSystemTrayIcon.supportsMessages():
            return
        
        try:
            icon = QSystemTrayIcon.MessageIcon.Information if success else QSystemTrayIcon.MessageIcon.Warning
            self.tray_icon.showMessage(title, message, icon, 5000)
            
        except Exception as e:
            log_error(f"Ошибка показа пользовательского уведомления: {e}")


_notification_manager = None

def get_notification_manager(main_window=None):
    """Получить глобальный экземпляр менеджера уведомлений"""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager(main_window)
    elif main_window and not _notification_manager.main_window:
        _notification_manager.main_window = main_window
    return _notification_manager