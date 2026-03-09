from typing import Optional, Any, List
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer
from logger import log_info, log_error, log_warning, log_debug
from .icon_mixin import IconMixin
from core.utils import StyleSheets


class BaseWidget(QWidget, IconMixin):
    """Базовый класс для всех виджетов UTILHELP"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.parent_window = parent
        self._cleanup_timers: List[QTimer] = []
        self._setup_logging()
        self._apply_base_style()
    
    def _setup_logging(self) -> None:
        """Настройка логирования для виджета"""
        self.log_info = log_info
        self.log_error = log_error
        self.log_warning = log_warning
        self.log_debug = log_debug
    
    def _apply_base_style(self) -> None:
        """Применить базовый стиль"""
        self.setStyleSheet(StyleSheets.get_base_widget_style())
    
    def set_parent_window(self, parent_window: Any) -> None:
        """Установка ссылки на главное окно"""
        self.parent_window = parent_window
    
    def add_cleanup_timer(self, timer: QTimer) -> None:
        """Добавить таймер для очистки при закрытии виджета"""
        self._cleanup_timers.append(timer)
    
    def cleanup(self) -> None:
        """Очистка ресурсов виджета"""
        try:
            # Останавливаем все таймеры
            for timer in self._cleanup_timers:
                if timer and timer.isActive():
                    timer.stop()
            self._cleanup_timers.clear()
            
            self.log_debug(f"Cleanup completed for {self.__class__.__name__}")
            
        except Exception as e:
            self.log_error(f"Ошибка при очистке {self.__class__.__name__}: {e}")
    
    def closeEvent(self, event) -> None:
        """Обработка закрытия виджета"""
        self.cleanup()
        super().closeEvent(event)
    
    def __del__(self):
        """Деструктор"""
        try:
            self.cleanup()
        except:
            pass