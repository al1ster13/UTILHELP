"""
Упрощенное главное окно UTILHELP
"""
from typing import Optional, Any
from PyQt6.QtWidgets import (QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, 
                             QHBoxLayout, QTabWidget, QFrame, QApplication)
from PyQt6.QtGui import QIcon, QPainter, QPen, QBrush, QColor
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from ui.base.base_widget import BaseWidget
from ui.settings.settings_tab import SettingsTab
from ui.effects.snow_widget import SnowWidget
from news_tab import NewsTab
from programs_tab import ProgramsTab
from drivers_tab import DriversTab
from downloads_tab import DownloadsTab
from resource_path import get_icon_path
from notification_manager import get_notification_manager
from logger import log_info, log_error, log_warning, log_debug


class MainWindow(QMainWindow, BaseWidget):
    """Главное окно программы - упрощенная версия"""
    
    # Сигналы
    data_loading_started = pyqtSignal()
    data_loading_completed = pyqtSignal(dict, dict, dict)
    data_loading_failed = pyqtSignal(str)
    
    def __init__(self):
        QMainWindow.__init__(self)
        BaseWidget.__init__(self)
        
        self.setWindowTitle("UTILHELP")
        self.resize(1280, 720)
        self.setMinimumSize(800, 600)
        
        # Состояние
        self.dragging = False
        self.drag_position = None
        self.snow_enabled = False
        self.snow_widget: Optional[SnowWidget] = None
        
        # Компоненты
        self.notification_manager = get_notification_manager(self)
        self.settings_tab: Optional[SettingsTab] = None
        self.tab_widget: Optional[QTabWidget] = None
        
        # Вкладки
        self.news_tab: Optional[NewsTab] = None
        self.programs_tab: Optional[ProgramsTab] = None
        self.drivers_tab: Optional[DriversTab] = None
        self.downloads_tab: Optional[DownloadsTab] = None
        
        self._setup_window()
        self._setup_ui()
        self._setup_connections()
        
        self.log_info("MainWindow initialized")
    
    def _setup_window(self) -> None:
        """Настройка окна"""
        try:
            icon_path = get_icon_path("utilhelp.ico")
            if icon_path:
                app_icon = QIcon(icon_path)
                self.setWindowIcon(app_icon)
        except Exception as e:
            self.log_error(f"Failed to load window icon: {e}")
        
        # Настройки окна
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Уведомления
        self.notification_manager.show_tray_icon()
        
        # Миграция настроек
        from settings_manager import settings_manager
        settings_manager.migrate_from_db()
    
    def _setup_ui(self) -> None:
        """Настройка интерфейса"""
        # Центральный виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet("""
            background-color: #1a1a1a;
            border-radius: 12px;
        """)
        
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(3, 3, 3, 3)
        main_layout.setSpacing(0)
        
        self._create_title_bar(main_layout)
        
        # Основной контент
        self._create_main_content(main_layout)
        
        # Снегопад 
        self._create_snow_widget()
    
    def _create_title_bar(self, main_layout: QVBoxLayout) -> None:
        """Создание заголовка окна"""
        self.title_bar = QFrame()
        self.title_bar.setFixedHeight(35)
        self.title_bar.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
            }
        """)
        
        title_bar_layout = QHBoxLayout(self.title_bar)
        title_bar_layout.setContentsMargins(5, 0, 5, 0)
        title_bar_layout.setSpacing(0)
        
        self._create_title_left_section(title_bar_layout)
        
        self.title_label = QLabel("UTILHELP")
        self.title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                letter-spacing: 2px;
            }
        """)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_bar_layout.addWidget(self.title_label)
        
        self._create_window_controls(title_bar_layout)
        
        main_layout.addWidget(self.title_bar)
    
    def _create_title_left_section(self, title_bar_layout: QHBoxLayout) -> None:
        """Создание левой части заголовка"""
        left_container = QWidget()
        left_container.setFixedWidth(120)
        left_container.setStyleSheet("background: transparent;")
        
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(1, 0, 0, 0)
        left_layout.setSpacing(5)
        
        logo_label = QLabel()
        pixmap = self.load_icon_pixmap("utilhelplogo24.png")
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap)
        else:
            logo_label.setText("•")
            logo_label.setStyleSheet("font-size: 16px;")
        
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setFixedSize(24, 24)
        left_layout.addWidget(logo_label)
        left_layout.addStretch()
        
        title_bar_layout.addWidget(left_container)
    
    def _create_window_controls(self, title_bar_layout: QHBoxLayout) -> None:
        """Создание кнопок управления окном"""
        controls_container = QWidget()
        controls_container.setFixedWidth(120)
        controls_container.setStyleSheet("background: transparent;")
        
        controls_layout = QHBoxLayout(controls_container)
        controls_layout.setContentsMargins(0, 0, 1, 0)
        controls_layout.setSpacing(2)
        controls_layout.addStretch()
        
        settings_btn = self._create_control_button("settings.png", "Настройки")
        settings_btn.clicked.connect(self.show_settings)
        controls_layout.addWidget(settings_btn)
        
        minimize_btn = self._create_control_button("minimizemenu.png", "Свернуть")
        minimize_btn.clicked.connect(self.showMinimized)
        controls_layout.addWidget(minimize_btn)
        
        close_btn = self._create_control_button("closemenu.png", "Закрыть")
        close_btn.clicked.connect(self.close)
        controls_layout.addWidget(close_btn)
        
        title_bar_layout.addWidget(controls_container)
    
    def _create_control_button(self, icon_name: str, tooltip: str) -> QPushButton:
        """Создание кнопки управления"""
        btn = QPushButton()
        btn.setFixedSize(24, 24)
        btn.setToolTip(tooltip)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            QPushButton:pressed {
                background-color: #4d4d4d;
            }
        """)
        
        pixmap = self.load_icon_pixmap(icon_name, (16, 16))
        if not pixmap.isNull():
            btn.setIcon(QIcon(pixmap))
        
        return btn
    
    def _create_main_content(self, main_layout: QVBoxLayout) -> None:
        """Создание основного контента"""
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #1a1a1a;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #cccccc;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background-color: #3d3d3d;
                color: #ffffff;
            }
            QTabBar::tab:hover {
                background-color: #333333;
            }
        """)
        
        self._create_tabs()
        
        main_layout.addWidget(self.tab_widget)
    
    def _create_tabs(self) -> None:
        """Создание вкладок"""
        # Новости
        self.news_tab = NewsTab()
        self.tab_widget.addTab(self.news_tab, "Новости")
        
        # Программы
        self.programs_tab = ProgramsTab()
        self.tab_widget.addTab(self.programs_tab, "Программы")
        
        # Драйверы
        self.drivers_tab = DriversTab()
        self.tab_widget.addTab(self.drivers_tab, "Драйверы")
        
        # Загрузки
        self.downloads_tab = DownloadsTab()
        self.tab_widget.addTab(self.downloads_tab, "Загрузки")
    
    def _create_snow_widget(self) -> None:
        """Создание виджета снегопада"""
        self.snow_widget = SnowWidget(self)
        self.snow_widget.hide()  
    
    def _setup_connections(self) -> None:
        """Настройка соединений сигналов"""
        self.data_loading_completed.connect(self.on_data_loaded)
        self.data_loading_failed.connect(self.on_data_failed)
    
    def show_settings(self) -> None:
        """Показать настройки"""
        if not self.settings_tab:
            self.settings_tab = SettingsTab(self)
            self.settings_tab.set_parent_window(self)
        
        settings_index = -1
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == "Настройки":
                settings_index = i
                break
        
        if settings_index == -1:
            settings_index = self.tab_widget.addTab(self.settings_tab, "Настройки")
        
        self.tab_widget.setCurrentIndex(settings_index)
        self.log_info("Settings tab opened")
    
    def toggle_snow(self, enabled: bool) -> None:
        """Переключение снегопада"""
        self.snow_enabled = enabled
        
        if enabled and self.snow_widget:
            self.snow_widget.show()
            self.snow_widget.raise_()
            self.log_info("Snow effect enabled")
        elif self.snow_widget:
            self.snow_widget.hide()
            self.log_info("Snow effect disabled")
    
    def on_data_loaded(self, news_data: dict, programs_data: dict, drivers_data: dict) -> None:
        """Обработка загруженных данных"""
        try:
            if self.news_tab:
                self.news_tab.set_news_data(news_data)
            
            if self.programs_tab:
                self.programs_tab.set_programs_data(programs_data)
            
            if self.drivers_tab:
                self.drivers_tab.set_drivers_data(drivers_data)
            
            self.log_info("Data loaded successfully")
            
        except Exception as e:
            self.log_error(f"Error processing loaded data: {e}")
    
    def on_data_failed(self, error: str) -> None:
        """Обработка ошибки загрузки данных"""
        self.log_error(f"Data loading failed: {error}")
        # TODO: Показать сообщение об ошибке пользователю
    
    def resizeEvent(self, event) -> None:
        """Обработка изменения размера окна"""
        super().resizeEvent(event)
        
        if self.snow_widget:
            self.snow_widget.resize(self.size())
            self.snow_widget.reinit_snowflakes_for_size(self.width(), self.height())
    
    def mousePressEvent(self, event) -> None:
        """Обработка нажатия мыши для перетаскивания окна"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.title_bar.geometry().contains(event.position().toPoint()):
                self.dragging = True
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event) -> None:
        """Обработка перемещения мыши для перетаскивания окна"""
        if self.dragging and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)
    
    def mouseReleaseEvent(self, event) -> None:
        """Обработка отпускания мыши"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.drag_position = None
    
    def closeEvent(self, event) -> None:
        """Обработка закрытия окна"""
        try:
            # Очищаем ресурсы
            if self.snow_widget:
                self.snow_widget.cleanup()
            
            if self.settings_tab:
                self.settings_tab.cleanup()
            
            # Очищаем вкладки
            for tab in [self.news_tab, self.programs_tab, self.drivers_tab, self.downloads_tab]:
                if tab and hasattr(tab, 'cleanup'):
                    tab.cleanup()
            
            self.cleanup()
            self.log_info("MainWindow closed")
            
        except Exception as e:
            self.log_error(f"Error during window close: {e}")
        
        super().closeEvent(event)