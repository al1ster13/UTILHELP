import sys
import random
import math
import os
import time
import traceback
from datetime import datetime
from urllib.parse import urlparse
from PyQt6.QtWidgets import (QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, 
                             QHBoxLayout, QTabWidget, QFrame, QScrollArea, QProgressBar, 
                             QGraphicsOpacityEffect, QApplication, QMessageBox)
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QPixmap, QIcon, QGuiApplication, QKeySequence, QShortcut
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QTimer, pyqtSignal, pyqtProperty, QSize
from news_tab import NewsTab
from programs_tab import ProgramsTab
from drivers_tab import DriversTab
from downloads_tab import DownloadsTab
from resource_path import resource_path, get_icon_path, get_db_path
from temp_manager import get_temp_manager
from json_data_manager import get_json_manager
from loading_widget import LoadingWidget, NoInternetWidget
from scroll_helper import configure_scroll_area
from notification_manager import get_notification_manager
from logger import log_info, log_error, log_warning, log_debug
from ui.settings.toggle_switch import ToggleSwitch
from ui.effects.snow_widget import SnowWidget
from ui.settings.settings_tab_full import SettingsTab
from localization import t

class MainWindow(QMainWindow):
    """Главное окно программы"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UTILHELP")
        self.resize(1280, 720)
        self.setMinimumSize(800, 600)

        try:
            icon_path = get_icon_path("utilhelp.ico")
            if icon_path:
                app_icon = QIcon(icon_path)
                self.setWindowIcon(app_icon)
        except:
            pass 
        
        self.dragging = False
        self.drag_position = None
        self.settings_dialog = None
        
        self.snow_enabled = False  
        
        self.notification_manager = get_notification_manager(self)
        self.notification_manager.show_tray_icon()
        
        from settings_manager import settings_manager
        settings_manager.migrate_from_db()
        
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        from theme_manager import theme_manager
        c = theme_manager.colors

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet(f"""
            background-color: {c['bg_main']};
            border-radius: 12px;
        """)
        
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(3, 3, 3, 3)
        main_layout.setSpacing(0)
        
        self.title_bar = QFrame()
        self.title_bar.setFixedHeight(35)
        self.title_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {c['bg_titlebar']};
                border-radius: 10px;
            }}
        """)
        
        title_bar_layout = QHBoxLayout(self.title_bar)
        title_bar_layout.setContentsMargins(5, 0, 5, 0)  
        title_bar_layout.setSpacing(0)  
        
        left_container = QWidget()
        left_container.setFixedWidth(120)  
        left_container.setStyleSheet("background: transparent;")  
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(1, 0, 0, 0)  
        left_layout.setSpacing(5)
        
        logo_label = QLabel()
        self.logo_label = logo_label  # Сохраняем ссылку
        pixmap = self.load_icon_pixmap("utilhelplogo24.png")
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap)
        else:
            logo_label.setText("•")
            logo_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                }
            """)
        
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setFixedSize(24, 24)  
        left_layout.addWidget(logo_label)
        
        left_layout.addStretch()
        
        title_bar_layout.addWidget(left_container)
        
        self.title_label = QLabel("UTILHELP")
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 16px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                letter-spacing: 2px;
            }}
        """)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  
        title_bar_layout.addWidget(self.title_label)
        
        right_container = QWidget()
        right_container.setFixedWidth(120)  
        right_container.setStyleSheet("background: transparent;")  
        right_layout = QHBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 5, 0)
        right_layout.setSpacing(5)
        
        right_layout.addStretch()
        
        self.settings_button = QPushButton()
        pixmap = self.load_icon_pixmap("settings.png")
        if pixmap and not pixmap.isNull():
            icon = QIcon(pixmap)
            self.settings_button.setIcon(icon)
            self.settings_button.setIconSize(QSize(16, 16))
        else:
            self.settings_button.setText("⚙")
        
        self.settings_button.setFixedSize(30, 25)
        self.settings_button.clicked.connect(self.show_settings)
        self.settings_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['bg_button']};
                border: none;
                color: {c['text_primary']};
                font-size: 16px;
                font-weight: bold;
                border-radius: 4px;
                margin: 2px;
                text-align: center;
                padding: 0px;
                line-height: 26px;
                outline: none;
            }}
            QPushButton:hover {{
                background-color: {c['bg_hover']};
            }}
            QPushButton:pressed {{
                background-color: {c['bg_pressed']};
            }}
            QPushButton:focus {{
                outline: none;
                border: none;
            }}
        """)
        right_layout.addWidget(self.settings_button)
        
        title_bar_layout.addWidget(right_container)
        
        minimize_button = QPushButton()
        minimize_button.setFixedSize(30, 25)  
        minimize_button.clicked.connect(self.showMinimized)
        self.minimize_button = minimize_button  # Сохраняем ссылку
        
        minimize_pixmap = self.load_icon_pixmap("minimizemenu.png")
        if minimize_pixmap and not minimize_pixmap.isNull():
            minimize_button.setIcon(QIcon(minimize_pixmap))
            minimize_button.setIconSize(QSize(16, 16))
            minimize_button.setFlat(True)  
        else:
            minimize_button.setText("—")  
        minimize_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['bg_button']};
                border: none;
                color: {c['text_primary']};
                font-size: 16px;
                font-weight: bold;
                border-radius: 4px;
                margin: 2px;
                text-align: center;
                padding: 0px;
                line-height: 26px;
                outline: none;
            }}
            QPushButton:hover {{
                background-color: {c['bg_hover']};
            }}
            QPushButton:pressed {{
                background-color: {c['bg_pressed']};
            }}
            QPushButton:focus {{
                outline: none;
                border: none;
            }}
        """)
        right_layout.addWidget(minimize_button)
        
        self.maximize_button = QPushButton()
        self.maximize_button.setFixedSize(30, 25)  
        self.maximize_button.clicked.connect(self.toggle_maximize)
        
        maximize_pixmap = self.load_icon_pixmap("unwrapmenu.png")
        if maximize_pixmap and not maximize_pixmap.isNull():
            self.maximize_button.setIcon(QIcon(maximize_pixmap))
            self.maximize_button.setIconSize(QSize(16, 16))
            self.maximize_button.setFlat(True)  
        else:
            self.maximize_button.setText("☐")  
        self.maximize_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['bg_button']};
                border: none;
                color: {c['text_primary']};
                font-size: 16px;
                font-weight: bold;
                border-radius: 4px;
                margin: 2px;
                text-align: center;
                padding: 0px;
                line-height: 26px;
                outline: none;
            }}
            QPushButton:hover {{
                background-color: {c['bg_hover']};
            }}
            QPushButton:pressed {{
                background-color: {c['bg_pressed']};
            }}
            QPushButton:focus {{
                outline: none;
                border: none;
            }}
        """)
        right_layout.addWidget(self.maximize_button)
        
        close_button = QPushButton()
        close_button.setFixedSize(30, 25)  
        close_button.clicked.connect(self.close)
        self.close_button = close_button  # Сохраняем ссылку
        
        close_pixmap = self.load_icon_pixmap("closemenu.png")
        if close_pixmap and not close_pixmap.isNull():
            close_button.setIcon(QIcon(close_pixmap))
            close_button.setIconSize(QSize(16, 16))
            close_button.setFlat(True)  
        else:
            close_button.setText("✕")  
        
        close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['bg_button']};
                border: none;
                color: {c['text_primary']};
                font-size: 16px;
                font-weight: bold;
                border-radius: 4px;
                margin: 2px;
                text-align: center;
                padding: 0px;
                line-height: 26px;
                outline: none;
                qproperty-flat: true;
            }}
            QPushButton:hover {{
                background-color: #e74c3c;
                color: #ffffff;
            }}
            QPushButton:pressed {{
                background-color: #c0392b;
            }}
            QPushButton:focus {{
                outline: none;
                border: none;
        """)
        right_layout.addWidget(close_button)
        
        main_layout.addWidget(self.title_bar)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background-color: {c['bg_main']};
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }}
            QTabBar {{
                margin-left: -2px;
            }}
            QTabBar::tab:first {{
                margin-left: 0px;
            }}
            QTabBar::tab {{
                background-color: {c['bg_button']};
                color: {c['text_secondary']};
                padding: 15px 30px;
                margin: 3px 2px 3px 2px;
                border-radius: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
                border: 2px solid {c['border']};
            }}
            QTabBar::tab:selected {{
                background-color: {c['bg_hover']};
                color: {c['text_primary']};
                border: 2px solid {c['border_hover']};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {c['bg_hover']};
                color: {c['text_primary']};
                border: 2px solid {c['border_hover']};
            }}
            QTabBar::tab:pressed {{
                background-color: {c['bg_pressed']};
            }}
        """)
        
        self.news_tab = NewsTab()
        self.tab_widget.addTab(self.news_tab, t("tabs.news"))
        
        self.programs_tab = ProgramsTab()
        self.programs_tab.main_window = self
        self.tab_widget.addTab(self.programs_tab, t("tabs.programs"))
        
        self.drivers_tab = DriversTab()
        self.drivers_tab.main_window = self
        self.tab_widget.addTab(self.drivers_tab, t("tabs.drivers"))
        
        self.data_loaded = False
        self.loading_widget = None
        
        self.downloads_tab = DownloadsTab()
        self.tab_widget.addTab(self.downloads_tab, t("tabs.library"))
        
        self.settings_tab = SettingsTab(self)
        self.settings_tab_index = self.tab_widget.addTab(self.settings_tab, t("tabs.settings"))
        self.tab_widget.tabBar().setTabVisible(self.settings_tab_index, False)
        

        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        self.tab_widget.mousePressEvent = self.tab_widget_mouse_press_event
        
        main_layout.addWidget(self.tab_widget)

        # Подписываем все вкладки на смену темы
        from theme_manager import theme_manager as _tm
        _tm.add_listener(self.apply_theme)
        
        self.status_bar = QFrame()
        self.status_bar.setFixedHeight(25)
        self.status_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {c['bg_titlebar']};
                border-radius: 10px;
            }}
        """)

        status_layout = QHBoxLayout(self.status_bar)
        status_layout.setContentsMargins(15, 0, 8, 0)

        version_text = self.get_app_version()
        self.version_label = QLabel(t("app.version", version=version_text))
        self.version_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_secondary']};
                font-size: 10px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
        """)
        status_layout.addWidget(self.version_label)
        status_layout.addStretch()
        
        self.downloads_button = QPushButton()
        pixmap = self.load_icon_pixmap("button download.png")
        if pixmap and not pixmap.isNull():
            icon = QIcon(pixmap)
            self.downloads_button.setIcon(icon)
            self.downloads_button.setIconSize(QSize(16, 16))
            self.downloads_button.setText(f" {t('main_window.downloads_button')}")  
        else:
            self.downloads_button.setText(f"↓ {t('main_window.downloads_button')}")
        
        self.downloads_button.setFixedHeight(20)
        self.downloads_button.clicked.connect(self.toggle_downloads_panel)
        self.downloads_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['bg_button']};
                color: {c['text_primary']};
                border: none;
                border-radius: 4px;
                font-size: 12px;
                font-weight: normal;
                padding: 2px 8px;
                margin-right: 0px;
                margin-top: 1px;
                outline: none;
            }}
            QPushButton:hover {{
                background-color: {c['bg_hover']};
            }}
            QPushButton:pressed {{
                background-color: {c['bg_pressed']};
            }}
            QPushButton:focus {{
                outline: none;
                border: none;
            }}
        """)
        status_layout.addWidget(self.downloads_button)
        
        main_layout.addWidget(self.status_bar)
        
        self.snow_widget = SnowWidget(self)
        self.update_snow_widget_size()
        if self.snow_enabled:
            self.snow_widget.show()
        else:
            self.snow_widget.hide()
        
        self.downloads_panel = None
        self.current_downloads = []
        
        self.downloads_count_label = None
        self.create_downloads_count_indicator()
        
        self.cleanup_message = None
        
        self.normal_size = (1280, 720)
        self.is_maximized = False
        
        self.center_window()
        
        QApplication.instance().installEventFilter(self)
        
        self.setup_shortcuts()
        
        QTimer.singleShot(3000, self.check_for_updates_on_startup)
    
    def check_for_updates_on_startup(self):
        """Автоматическая проверка обновлений при запуске программы"""
        try:
            from update_checker import get_update_manager
            
            update_manager = get_update_manager(self)
            
            update_info = update_manager.check_for_updates_silent()
            
            if 'error' in update_info:
                try:
                    from logger import log_error
                    log_error(f"Auto-update check error: {update_info['error']}")
                except:
                    pass
                return
            
            if update_info.get('update_available'):
                update_manager.show_update_dialog(update_info)
                
        except Exception as e:
            try:
                from logger import log_error
                log_error(f"Auto-update check failed: {e}")
            except:
                pass

    def setup_shortcuts(self):
        """Настройка горячих клавиш"""
        shortcut_downloads = QShortcut(QKeySequence("Ctrl+D"), self)
        shortcut_downloads.activated.connect(self.toggle_downloads_panel)
        
        shortcut_search = QShortcut(QKeySequence("Ctrl+F"), self)
        shortcut_search.activated.connect(self.focus_search)
        
        shortcut_refresh = QShortcut(QKeySequence("Ctrl+R"), self)
        shortcut_refresh.activated.connect(self.refresh_current_tab)
        
        shortcut_scan = QShortcut(QKeySequence("Ctrl+S"), self)
        shortcut_scan.activated.connect(self.scan_system)
        
        shortcut_f5 = QShortcut(QKeySequence("F5"), self)
        shortcut_f5.activated.connect(self.refresh_current_tab)
        
        log_info("Горячие клавиши настроены")
    
    def focus_search(self):
        """Установить фокус на поле поиска в текущей вкладке"""
        current_widget = self.tab_widget.currentWidget()
        
        if hasattr(current_widget, 'search_input'):
            current_widget.search_input.setFocus()
            current_widget.search_input.selectAll()
            log_info("Фокус установлен на поиск")
    
    def refresh_current_tab(self):
        """Обновить данные в текущей вкладке"""
        current_widget = self.tab_widget.currentWidget()
        current_index = self.tab_widget.currentIndex()
        
        if current_index == 0 and hasattr(current_widget, 'load_news_from_data'):
            current_widget.load_news_from_data()
            log_info("Новости обновлены")
        
        elif current_index == 1 and hasattr(current_widget, 'display_programs'):
            current_widget.display_programs()
            log_info("Программы обновлены")
        
        elif current_index == 2 and hasattr(current_widget, 'display_drivers'):
            current_widget.display_drivers()
            log_info("Драйверы обновлены")
        
        elif current_index == 3 and hasattr(current_widget, 'load_downloads'):
            current_widget.load_downloads()
            log_info("Библиотека загрузок обновлена")
    
    def scan_system(self):
        """Запустить сканирование системы"""
        current_widget = self.tab_widget.currentWidget()
        
        if hasattr(current_widget, 'start_system_scan'):
            current_widget.start_system_scan()
            log_info("Запущено сканирование системы")
        else:
            log_warning("Сканирование недоступно на текущей вкладке")

    def load_icon_pixmap(self, icon_name, size=None):
        """Загрузить иконку с правильным путем для exe"""
        from theme_manager import theme_manager, colorize_pixmap

        icon_path = get_icon_path(icon_name)

        if icon_path:
            pixmap = QPixmap(icon_path)

            if not pixmap.isNull() and size:
                pixmap = pixmap.scaled(size[0], size[1], Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

            # В светлой теме перекрашиваем белые иконки UI
            if not pixmap.isNull() and theme_manager.is_light():
                pixmap = colorize_pixmap(pixmap, theme_manager.colors['text_secondary'])

            return pixmap

        return QPixmap()  

    def update_snow_widget_size(self):
        """Обновить размер виджета снежинок под размер окна"""
        if hasattr(self, 'snow_widget'):
            QTimer.singleShot(50, lambda: self.snow_widget.setGeometry(0, 0, self.width(), self.height()))
            QTimer.singleShot(100, lambda: self.snow_widget.reinit_snowflakes_for_size(self.width(), self.height()))

    def toggle_maximize(self):
        """Переключение между обычным и полноэкранным режимом"""
        self.maximize_button.setEnabled(False)
        if self.is_maximized:
            self.animate_to_normal()
        else:
            self.animate_to_fullscreen()

    def animate_to_fullscreen(self):
        """Анимация разворачивания в полный экран"""
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        self.setMaximumSize(16777215, 16777215)
        self.setMinimumSize(0, 0)
        
        self.resize_animation = QPropertyAnimation(self, b"geometry")
        self.resize_animation.setDuration(150)
        self.resize_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        start_rect = self.geometry()
        end_rect = QRect(screen_geometry.x(), screen_geometry.y(), 
                        screen_geometry.width(), screen_geometry.height())
        
        self.resize_animation.setStartValue(start_rect)
        self.resize_animation.setEndValue(end_rect)
        self.resize_animation.finished.connect(self.on_fullscreen_animation_finished)
        self.resize_animation.start()

    def animate_to_normal(self):
        """Анимация сворачивания в обычный размер"""
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        center_x = screen_geometry.x() + (screen_geometry.width() - self.normal_size[0]) // 2
        center_y = screen_geometry.y() + (screen_geometry.height() - self.normal_size[1]) // 2
        
        self.resize_animation = QPropertyAnimation(self, b"geometry")
        self.resize_animation.setDuration(150)
        self.resize_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        start_rect = self.geometry()
        end_rect = QRect(center_x, center_y, self.normal_size[0], self.normal_size[1])
        
        self.resize_animation.setStartValue(start_rect)
        self.resize_animation.setEndValue(end_rect)
        self.resize_animation.finished.connect(self.on_normal_animation_finished)
        self.resize_animation.start()

    def on_fullscreen_animation_finished(self):
        """Завершение анимации разворачивания"""
        unwrap_pixmap = self.load_icon_pixmap("unwrapmenu.png")
        if unwrap_pixmap and not unwrap_pixmap.isNull():
            self.maximize_button.setIcon(QIcon(unwrap_pixmap))
        else:
            self.maximize_button.setText("☐")
        self.is_maximized = True
        self.maximize_button.setEnabled(True)
        self.update_window_style(True)  
        self.update_snow_widget_size()

    def on_normal_animation_finished(self):
        """Завершение анимации сворачивания"""
        self.setFixedSize(self.normal_size[0], self.normal_size[1])
        unwrap_pixmap = self.load_icon_pixmap("unwrapmenu.png")
        if unwrap_pixmap and not unwrap_pixmap.isNull():
            self.maximize_button.setIcon(QIcon(unwrap_pixmap))
        else:
            self.maximize_button.setText("☐")
        self.is_maximized = False
        self.maximize_button.setEnabled(True)
        self.update_window_style(False)  
        self.update_snow_widget_size()

    def update_window_style(self, is_maximized):
        """Обновить стиль окна"""
        from theme_manager import theme_manager
        c = theme_manager.colors
        radius = "0px" if is_maximized else "12px"
        self.central_widget.setStyleSheet(f"""
            background-color: {c['bg_main']};
            border-radius: {radius};
        """)
        self.title_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {c['bg_titlebar']};
                border-radius: 10px;
            }}
        """)
        self.status_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {c['bg_titlebar']};
                border-radius: 10px;
            }}
        """)

    def apply_theme(self):
        """Применить текущую тему ко всем элементам главного окна"""
        from theme_manager import theme_manager
        from logger import log_info
        c = theme_manager.colors
        
        log_info("MainWindow.apply_theme вызван")

        # Перезагружаем логотип
        if hasattr(self, 'logo_label'):
            logo_pixmap = self.load_icon_pixmap("utilhelplogo24.png")
            if logo_pixmap and not logo_pixmap.isNull():
                self.logo_label.setPixmap(logo_pixmap)

        # Перезагружаем иконки с учетом темы
        if hasattr(self, 'settings_button'):
            settings_pixmap = self.load_icon_pixmap("settings.png")
            if settings_pixmap and not settings_pixmap.isNull():
                self.settings_button.setIcon(QIcon(settings_pixmap))
        
        if hasattr(self, 'minimize_button'):
            minimize_pixmap = self.load_icon_pixmap("minimizemenu.png")
            if minimize_pixmap and not minimize_pixmap.isNull():
                self.minimize_button.setIcon(QIcon(minimize_pixmap))
                self.minimize_button.setIconSize(QSize(16, 16))
            self.minimize_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {c['bg_button']};
                    border: none;
                    color: {c['text_primary']};
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 4px;
                    margin: 2px;
                    text-align: center;
                    padding: 0px;
                    line-height: 26px;
                    outline: none;
                }}
                QPushButton:hover {{
                    background-color: {c['bg_hover']};
                }}
                QPushButton:pressed {{
                    background-color: {c['bg_pressed']};
                }}
                QPushButton:focus {{
                    outline: none;
                    border: none;
                }}
            """)
            self.minimize_button.update()
        
        if hasattr(self, 'maximize_button'):
            maximize_pixmap = self.load_icon_pixmap("unwrapmenu.png")
            if maximize_pixmap and not maximize_pixmap.isNull():
                self.maximize_button.setIcon(QIcon(maximize_pixmap))
                self.maximize_button.setIconSize(QSize(16, 16))
            self.maximize_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {c['bg_button']};
                    border: none;
                    color: {c['text_primary']};
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 4px;
                    margin: 2px;
                    text-align: center;
                    padding: 0px;
                    line-height: 26px;
                    outline: none;
                }}
                QPushButton:hover {{
                    background-color: {c['bg_hover']};
                }}
                QPushButton:pressed {{
                    background-color: {c['bg_pressed']};
                }}
                QPushButton:focus {{
                    outline: none;
                    border: none;
                }}
            """)
            self.maximize_button.update()
        
        if hasattr(self, 'close_button'):
            close_pixmap = self.load_icon_pixmap("closemenu.png")
            if close_pixmap and not close_pixmap.isNull():
                self.close_button.setIcon(QIcon(close_pixmap))
                self.close_button.setIconSize(QSize(16, 16))
            self.close_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {c['bg_button']};
                    border: none;
                    color: {c['text_primary']};
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 4px;
                    margin: 2px;
                    text-align: center;
                    padding: 0px;
                    line-height: 26px;
                    outline: none;
                    qproperty-flat: true;
                }}
                QPushButton:hover {{
                    background-color: #e74c3c;
                    color: #ffffff;
                }}
                QPushButton:pressed {{
                    background-color: #c0392b;
                }}
                QPushButton:focus {{
                    outline: none;
                    border: none;
                }}
            """)
            self.close_button.update()
        
        if hasattr(self, 'downloads_button'):
            downloads_pixmap = self.load_icon_pixmap("button download.png")
            if downloads_pixmap and not downloads_pixmap.isNull():
                self.downloads_button.setIcon(QIcon(downloads_pixmap))

        self.central_widget.setStyleSheet(f"""
            background-color: {c['bg_main']};
            border-radius: {'0px' if self.is_maximized else '12px'};
        """)
        self.title_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {c['bg_titlebar']};
                border-radius: 10px;
            }}
        """)
        self.status_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {c['bg_titlebar']};
                border-radius: 10px;
            }}
        """)
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 16px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                letter-spacing: 2px;
            }}
        """)
        self.version_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_secondary']};
                font-size: 10px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
        """)
        btn_style = f"""
            QPushButton {{
                background-color: {c['bg_button']};
                border: none;
                color: {c['text_primary']};
                font-size: 16px;
                font-weight: bold;
                border-radius: 4px;
                margin: 2px;
                outline: none;
            }}
            QPushButton:hover {{ background-color: {c['bg_hover']}; }}
            QPushButton:pressed {{ background-color: {c['bg_pressed']}; }}
            QPushButton:focus {{ outline: none; border: none; }}
        """
        self.settings_button.setStyleSheet(btn_style)
        self.maximize_button.setStyleSheet(btn_style)
        self.downloads_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['bg_button']};
                color: {c['text_primary']};
                border: none;
                border-radius: 4px;
                font-size: 12px;
                padding: 2px 8px;
                outline: none;
            }}
            QPushButton:hover {{ background-color: {c['bg_hover']}; }}
            QPushButton:pressed {{ background-color: {c['bg_pressed']}; }}
            QPushButton:focus {{ outline: none; border: none; }}
        """)
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background-color: {c['bg_main']};
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }}
            QTabBar {{
                margin-left: -2px;
            }}
            QTabBar::tab:first {{
                margin-left: 0px;
            }}
            QTabBar::tab {{
                background-color: {c['bg_button']};
                color: {c['text_secondary']};
                padding: 15px 30px;
                margin: 3px 2px 3px 2px;
                border-radius: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
                border: 2px solid {c['border']};
            }}
            QTabBar::tab:selected {{
                background-color: {c['bg_hover']};
                color: {c['text_primary']};
                border: 2px solid {c['border_hover']};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {c['bg_hover']};
                color: {c['text_primary']};
                border: 2px solid {c['border_hover']};
            }}
            QTabBar::tab:pressed {{
                background-color: {c['bg_pressed']};
            }}
        """)

        # Перезагружаем вкладку настроек
        if hasattr(self, 'settings_tab') and hasattr(self.settings_tab, 'apply_theme'):
            self.settings_tab.apply_theme()

        # Перерисовываем все вкладки с локальными стилями
        self._refresh_all_tabs()
        
        # Обновляем панель загрузок если она существует
        self.update_downloads_panel_theme()

    def _refresh_all_tabs(self):
        """Перерисовать все вкладки после смены темы"""
        # NewsTab
        if hasattr(self, 'news_tab') and self.news_tab:
            if hasattr(self.news_tab, 'apply_theme'):
                self.news_tab.apply_theme()
            elif hasattr(self.news_tab, 'load_news_from_data'):
                self.news_tab.load_news_from_data()

        # ProgramsTab
        if hasattr(self, 'programs_tab') and self.programs_tab:
            if hasattr(self.programs_tab, 'apply_theme'):
                self.programs_tab.apply_theme()

        # DriversTab
        if hasattr(self, 'drivers_tab') and self.drivers_tab:
            if hasattr(self.drivers_tab, 'apply_theme'):
                self.drivers_tab.apply_theme()

        # DownloadsTab
        if hasattr(self, 'downloads_tab') and self.downloads_tab:
            if hasattr(self.downloads_tab, 'apply_theme'):
                self.downloads_tab.apply_theme()
            elif hasattr(self.downloads_tab, 'load_downloads'):
                self.downloads_tab.load_downloads()

    def center_window(self):
        """Центрировать окно на экране"""
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(screen_geometry.x() + x, screen_geometry.y() + y)

    def resizeEvent(self, event):
        """Обработка изменения размера окна"""
        super().resizeEvent(event)
        if hasattr(self, 'snow_widget'):
            QTimer.singleShot(10, self.update_snow_widget_size)
        
        if hasattr(self, 'downloads_count_label') and self.downloads_count_label:
            QTimer.singleShot(10, self.position_downloads_indicator)

    def show_settings(self):
        """Показать/скрыть вкладку настроек"""
        if self.tab_widget.currentIndex() == self.settings_tab_index:
            self.tab_widget.tabBar().setTabVisible(self.settings_tab_index, False)
            self.tab_widget.setCurrentIndex(0)
            self.tab_widget.tabBar().show()
        else:
            self.tab_widget.setCurrentIndex(self.settings_tab_index)
            self.tab_widget.tabBar().hide()

    def on_tab_changed(self, index):
        """Обработка смены вкладки"""
        current_widget = self.tab_widget.widget(index)
        
        if hasattr(current_widget, 'reset_search_and_scroll'):
            current_widget.reset_search_and_scroll()

    def toggle_snow(self, enabled):
        """Включить/выключить снегопад"""
        if enabled:
            self.snow_widget.show()
        else:
            self.snow_widget.hide()

    def toggle_downloads_panel(self):
        """Переключение панели загрузок - система загрузок"""
        if self.downloads_panel and self.downloads_panel.isVisible():
            self.hide_downloads_panel()
        else:
            if hasattr(self, 'show_opacity_animation') and self.show_opacity_animation:
                self.show_opacity_animation.stop()
            if hasattr(self, 'hide_opacity_animation') and self.hide_opacity_animation:
                self.hide_opacity_animation.stop()
                
            if self.downloads_panel:
                self.downloads_panel.deleteLater()
                self.downloads_panel = None
            self.create_downloads_panel()
            self.update_downloads_panel()
            self.show_downloads_panel()

    def create_downloads_count_indicator(self):
        """Создание индикатора количества загрузок"""
        self.downloads_count_label = QLabel(self)  
        self.downloads_count_label.setFixedSize(14, 14)
        self.downloads_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        self.downloads_count_label.setStyleSheet("""
            QLabel {
                background-color: #e74c3c;
                color: white;
                border-radius: 7px;
                font-size: 8px;
                font-weight: bold;
                font-family: 'Arial';
            }
        """)
        self.downloads_count_label.hide()  
        
        self.position_downloads_indicator()

    def position_downloads_indicator(self):
        """Позиционирование индикатора загрузок"""
        if self.downloads_count_label and self.downloads_button:
            global_pos = self.downloads_button.mapToGlobal(self.downloads_button.rect().topLeft())
            local_pos = self.mapFromGlobal(global_pos)
            
            button_width = self.downloads_button.width()
            button_height = self.downloads_button.height()
            
            x = local_pos.x() + button_width - 7  
            y = local_pos.y() - 3  
            
            self.downloads_count_label.move(x, y)

    def update_downloads_count(self):
        """Обновление индикатора количества загрузок"""
        if not self.downloads_count_label:
            return
            
        count = len(self.current_downloads)
        
        if count > 0:
            self.downloads_count_label.setText(str(count))
            self.downloads_count_label.show()
            self.position_downloads_indicator()
        else:
            self.downloads_count_label.hide()

    def show_downloads_panel(self):
        """Показать панель загрузок с анимацией"""
        if not self.downloads_panel:
            return
        
        if hasattr(self, 'show_opacity_animation') and self.show_opacity_animation and self.show_opacity_animation.state() == QPropertyAnimation.State.Running:
            return
        
        if hasattr(self, 'hide_opacity_animation') and self.hide_opacity_animation:
            self.hide_opacity_animation.stop()
        
        main_window_size = self.size()
        panel_x = main_window_size.width() - 422  
        panel_y = main_window_size.height() - 391  
        
        final_geometry = QRect(panel_x, panel_y, 410, 360)  
        self.downloads_panel.setGeometry(final_geometry)
        
        self.opacity_effect = QGraphicsOpacityEffect()
        self.downloads_panel.setGraphicsEffect(self.opacity_effect)
        
        self.downloads_panel.show()
        self.downloads_panel.raise_()
        
        if hasattr(self, 'show_opacity_animation') and self.show_opacity_animation:
            try:
                self.show_opacity_animation.finished.disconnect()
            except:
                pass
        
        self.show_opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.show_opacity_animation.setDuration(200)  # Ускорена анимация с 400 до 200 мс
        self.show_opacity_animation.setStartValue(0.0)
        self.show_opacity_animation.setEndValue(1.0)
        self.show_opacity_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.show_opacity_animation.start()
    def hide_downloads_panel(self):
        """Скрыть панель загрузок с анимацией"""
        if not self.downloads_panel:
            return
        
        if hasattr(self, 'hide_opacity_animation') and self.hide_opacity_animation and self.hide_opacity_animation.state() == QPropertyAnimation.State.Running:
            return
        
        if hasattr(self, 'show_opacity_animation') and self.show_opacity_animation:
            self.show_opacity_animation.stop()
        
        opacity_effect = self.downloads_panel.graphicsEffect()
        if not opacity_effect:
            opacity_effect = QGraphicsOpacityEffect()
            self.downloads_panel.setGraphicsEffect(opacity_effect)
        
        if hasattr(self, 'hide_opacity_animation') and self.hide_opacity_animation:
            try:
                self.hide_opacity_animation.finished.disconnect()
            except:
                pass
        
        self.hide_opacity_animation = QPropertyAnimation(opacity_effect, b"opacity")
        self.hide_opacity_animation.setDuration(200)  # Ускорена анимация с 400 до 200 мс
        self.hide_opacity_animation.setStartValue(1.0)
        self.hide_opacity_animation.setEndValue(0.0)
        self.hide_opacity_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.hide_opacity_animation.finished.connect(self.downloads_panel.hide)
        self.hide_opacity_animation.start()

    def create_downloads_panel(self):
        """Создание панели загрузок"""
        from theme_manager import theme_manager
        c = theme_manager.colors
        
        self.downloads_panel = QWidget(self)
        self.downloads_panel.setStyleSheet(f"""
            QWidget {{
                background-color: {c['bg_secondary']};
                border: 2px solid {c['border']};
                border-radius: 15px;
            }}
        """)
        
        layout = QVBoxLayout(self.downloads_panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        header_layout = QHBoxLayout()
        
        self.downloads_panel_title = QLabel(t("main_window.downloads_button"))
        self.downloads_panel_title.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 16px;
                font-weight: bold;
                background: transparent;
                border: none;
            }}
        """)
        header_layout.addWidget(self.downloads_panel_title)
        header_layout.addStretch()
        
        self.downloads_clear_btn = QPushButton("Очистить")
        self.downloads_clear_btn.setFixedSize(100, 25)
        self.downloads_clear_btn.clicked.connect(self.clear_downloads_history)
        
        from resource_path import get_icon_path
        from PyQt6.QtGui import QIcon
        from PyQt6.QtCore import QSize
        
        delete_pixmap = self.load_icon_pixmap("delete.png")
        if delete_pixmap and not delete_pixmap.isNull():
            self.downloads_clear_btn.setIcon(QIcon(delete_pixmap))
            self.downloads_clear_btn.setIconSize(QSize(12, 12))
        
        self.downloads_clear_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(244, 67, 54, 0.1);
                color: #f44336;
                border: 1px solid rgba(244, 67, 54, 0.3);
                border-radius: 4px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(244, 67, 54, 0.2);
                border: 1px solid rgba(244, 67, 54, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(244, 67, 54, 0.3);
                border: 1px solid #f44336;
            }
        """)
        header_layout.addWidget(self.downloads_clear_btn)
        
        layout.addLayout(header_layout)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        configure_scroll_area(scroll_area)
        
        self.downloads_scroll_area = scroll_area
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {c['bg_secondary']};
                width: 16px;
                margin: 0px;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background-color: {c['border']};
                border-radius: 8px;
                min-height: 30px;
                margin: 2px;
                border: none;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {c['border_hover']};
            }}
            QScrollBar::handle:vertical:pressed {{
                background-color: {c['bg_pressed']};
            }}
            QScrollBar::add-line:vertical {{
                height: 0px;
                width: 0px;
                border: none;
                background: transparent;
            }}
            QScrollBar::sub-line:vertical {{
                height: 0px;
                width: 0px;
                border: none;
                background: transparent;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {{
                width: 0px;
                height: 0px;
                background: transparent;
            }}
        """)
        
        self.downloads_container = QWidget()
        self.downloads_container.setStyleSheet("background: transparent; border: none;")
        self.downloads_layout = QVBoxLayout(self.downloads_container)
        self.downloads_layout.setContentsMargins(0, 0, 20, 0)  # Увеличиваем отступ справа для скроллбара
        self.downloads_layout.setSpacing(15)
        
        if not self.current_downloads:
            no_downloads_label = QLabel("Нет активных загрузок")
            no_downloads_label.setStyleSheet("""
                QLabel {
                    color: #888888;
                    font-size: 14px;
                    padding: 30px;
                    background: transparent;
                    border: none;
                }
            """)
            no_downloads_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.downloads_layout.addWidget(no_downloads_label)
        
        self.downloads_layout.addStretch()
        scroll_area.setWidget(self.downloads_container)
        layout.addWidget(scroll_area)
    
    def update_downloads_panel_theme(self):
        """Обновить тему панели загрузок"""
        if not self.downloads_panel:
            return
        
        from theme_manager import theme_manager
        c = theme_manager.colors
        
        # Обновляем основной стиль панели
        self.downloads_panel.setStyleSheet(f"""
            QWidget {{
                background-color: {c['bg_secondary']};
                border: 2px solid {c['border']};
                border-radius: 15px;
            }}
        """)
        
        # Обновляем заголовок
        if hasattr(self, 'downloads_panel_title'):
            self.downloads_panel_title.setStyleSheet(f"""
                QLabel {{
                    color: {c['text_primary']};
                    font-size: 16px;
                    font-weight: bold;
                    background: transparent;
                    border: none;
                }}
            """)
        
        # Обновляем иконку кнопки очистки
        if hasattr(self, 'downloads_clear_btn'):
            delete_pixmap = self.load_icon_pixmap("delete.png")
            if delete_pixmap and not delete_pixmap.isNull():
                self.downloads_clear_btn.setIcon(QIcon(delete_pixmap))
        
        # Обновляем скроллбар
        if hasattr(self, 'downloads_scroll_area'):
            self.downloads_scroll_area.setStyleSheet(f"""
                QScrollArea {{
                    background: transparent;
                    border: none;
                }}
                QScrollBar:vertical {{
                    background-color: {c['bg_secondary']};
                    width: 16px;
                    margin: 0px;
                    border: none;
                }}
                QScrollBar::handle:vertical {{
                    background-color: {c['border']};
                    border-radius: 8px;
                    min-height: 30px;
                    margin: 2px;
                    border: none;
                }}
                QScrollBar::handle:vertical:hover {{
                    background-color: {c['border_hover']};
                }}
                QScrollBar::handle:vertical:pressed {{
                    background-color: {c['bg_pressed']};
                }}
                QScrollBar::add-line:vertical {{
                    height: 0px;
                    width: 0px;
                    border: none;
                    background: transparent;
                }}
                QScrollBar::sub-line:vertical {{
                    height: 0px;
                    width: 0px;
                    border: none;
                    background: transparent;
                }}
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                    background: none;
                }}
                QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {{
                    width: 0px;
                    height: 0px;
                    background: transparent;
                }}
            """)
    
    def clear_downloads_history(self):
        """Очистить историю загрузок"""
        if not self.current_downloads:
            return
        
        from custom_dialogs import CustomConfirmDialog
        dialog = CustomConfirmDialog(
            "Очистить историю", 
            "Очистить историю загрузок?\n\nФайлы останутся на диске, удалится только история.",
            self
        )
        dialog.exec()
        
        if dialog.get_result():
            self.current_downloads.clear()
            self.update_downloads_count()
            
            if self.downloads_panel:
                self.downloads_panel.deleteLater()
                self.downloads_panel = None
            
            self.hide_downloads_panel()
    
    def add_download(self, program_name, download_url, icon_path=None, file_type="program"):
        """Добавить новую загрузку"""
        if self.downloads_panel:
            self.downloads_panel.deleteLater()
            self.downloads_panel = None
        
        download_item = DownloadItem(program_name, download_url, self, icon_path, file_type)
        self.current_downloads.append(download_item)
        
        self.create_downloads_panel()
        self.update_downloads_panel()
        
        self.update_downloads_count()
        
    def remove_download(self, download_item):
        """Удалить загрузку из списка"""
        if download_item in self.current_downloads:
            self.current_downloads.remove(download_item)
            if self.downloads_panel and download_item.widget:
                self.downloads_layout.removeWidget(download_item.widget)
                download_item.widget.deleteLater()
        
        self.update_downloads_panel()
        self.update_downloads_count()
        
        if not self.current_downloads and self.downloads_panel:
            QTimer.singleShot(100, self.force_update_empty_state)

    def update_downloads_panel(self):
        """Обновить панель загрузок"""
        if not self.downloads_panel:
            return
        
        if not self.current_downloads:
            while self.downloads_layout.count() > 1:
                child = self.downloads_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            no_downloads_label = QLabel("Нет активных загрузок")
            no_downloads_label.setStyleSheet("""
                QLabel {
                    color: #888888;
                    font-size: 14px;
                    padding: 30px;
                    background: transparent;
                    border: none;
                }
            """)
            no_downloads_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.downloads_layout.insertWidget(0, no_downloads_label)
        else:
            for i in range(self.downloads_layout.count() - 1):
                item = self.downloads_layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    if isinstance(widget, QLabel) and widget.text() == "Нет активных загрузок":
                        self.downloads_layout.removeWidget(widget)
                        widget.deleteLater()
                        
            existing_widgets = []
            for i in range(self.downloads_layout.count() - 1):
                item = self.downloads_layout.itemAt(i)
                if item and item.widget():
                    existing_widgets.append(item.widget())
            
            for download in self.current_downloads:
                widget = download.get_widget()
                if widget not in existing_widgets:
                    self.downloads_layout.insertWidget(self.downloads_layout.count() - 1, widget)

    def force_update_empty_state(self):
        """Принудительно обновить состояние пустой панели"""
        if not self.current_downloads and self.downloads_panel:
            while self.downloads_layout.count() > 1:
                child = self.downloads_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            no_downloads_label = QLabel("Нет активных загрузок")
            no_downloads_label.setStyleSheet("""
                QLabel {
                    color: #888888;
                    font-size: 14px;
                    padding: 30px;
                    background: transparent;
                    border: none;
                }
            """)
            no_downloads_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.downloads_layout.insertWidget(0, no_downloads_label)

    def eventFilter(self, obj, event):
        """Фильтр событий для закрытия панели загрузок при клике вне её"""
        if event.type() == event.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                if self.downloads_panel and self.downloads_panel.isVisible():
                    global_pos = event.globalPosition().toPoint()
                    
                    local_pos = self.mapFromGlobal(global_pos)
                    
                    panel_geometry = self.downloads_panel.geometry()
                    
                    button_global_pos = self.downloads_button.mapTo(self, self.downloads_button.rect().topLeft())
                    downloads_button_geometry = QRect(button_global_pos, self.downloads_button.size())
                    
                    if not panel_geometry.contains(local_pos) and not downloads_button_geometry.contains(local_pos):
                        self.hide_downloads_panel()
                        return True  
        
        return super().eventFilter(obj, event)

    def mousePressEvent(self, event):
        """Обработка нажатия мыши для перетаскивания окна и закрытия панели загрузок"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.downloads_panel and self.downloads_panel.isVisible():
                click_pos = event.position().toPoint()
                
                panel_geometry = self.downloads_panel.geometry()
                
                button_global_pos = self.downloads_button.mapTo(self, self.downloads_button.rect().topLeft())
                downloads_button_geometry = QRect(button_global_pos, self.downloads_button.size())
                
                if not panel_geometry.contains(click_pos) and not downloads_button_geometry.contains(click_pos):
                    self.hide_downloads_panel()
                    event.accept()
                    return
            
            if not self.is_maximized and event.position().y() < 50: 
                self.dragging = True
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        """Обработка перемещения мыши для перетаскивания окна"""
        if self.dragging and not self.is_maximized and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Обработка отпускания мыши"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            event.accept()

    def tab_widget_mouse_press_event(self, event):
        """Обработка кликов по области вкладок для закрытия панели загрузок"""
        if self.downloads_panel and self.downloads_panel.isVisible():
            self.hide_downloads_panel()
        
        QTabWidget.mousePressEvent(self.tab_widget, event)

    def keyPressEvent(self, event):
        """Обработка нажатий клавиш"""
        if event.key() == Qt.Key.Key_Escape:
            if hasattr(self, 'settings_tab_index') and self.tab_widget.currentIndex() == self.settings_tab_index:
                self.show_settings()  
                event.accept()
                return
            elif self.downloads_panel and self.downloads_panel.isVisible():
                self.hide_downloads_panel()
                event.accept()
                return
        
        super().keyPressEvent(event)

    def get_app_version(self):
        """Получение версии приложения"""
        try:
            with open('version.txt', 'r', encoding='utf-8') as f:
                return f'v{f.read().strip()}'
        except:
            return 'v1.0.1'

    def on_data_loaded(self, data):
        """Обработка успешной загрузки данных"""
        
        self.data_loaded = True
        
        if hasattr(self, 'programs_tab'):
            self.programs_tab.set_data(data.get('programs', []))
        
        if hasattr(self, 'drivers_tab'):
            self.drivers_tab.set_data(data.get('drivers', []))
        
        if hasattr(self, 'news_tab'):
            self.news_tab.set_data(data.get('news', []))
        
        if self.loading_widget:
            self.loading_widget.hide()
            self.loading_widget = None
        
        log_info("✓ Данные переданы в интерфейс")
        
        self.start_auto_scan_if_needed()
    
    def on_data_failed(self, error):
        """Обработка ошибки загрузки данных"""
        
        self.data_loaded = False
        
        self.loading_widget = NoInternetWidget(self, self.retry_data_loading)
        
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.loading_widget)
        
        old_central = self.centralWidget()
        self.setCentralWidget(central_widget)
        
        self.old_central_widget = old_central
        
        log_error(f"✗ Ошибка загрузки данных: {error}")
    
    def retry_data_loading(self):
        """Повторная попытка загрузки данных"""
        
        if self.loading_widget:
            self.loading_widget.hide()
        
        if hasattr(self, 'old_central_widget') and self.old_central_widget:
            self.setCentralWidget(self.old_central_widget)
            delattr(self, 'old_central_widget')
        
        self.loading_widget = LoadingWidget(self)
        
        overlay_layout = QVBoxLayout()
        overlay_layout.addWidget(self.loading_widget)
        
        overlay_widget = QWidget(self)
        overlay_widget.setLayout(overlay_layout)
        overlay_widget.setGeometry(self.rect())
        overlay_widget.show()
        
        self.loading_widget.show_loading()
        
        json_manager = get_json_manager()
        json_manager.force_reload(
            on_complete=lambda data: self.on_retry_success(data, overlay_widget),
            on_failed=lambda error: self.on_retry_failed(error, overlay_widget),
            on_progress=self.loading_widget.update_progress
        )
    
    def on_retry_success(self, data, overlay_widget):
        """Успешная повторная загрузка"""
        self.loading_widget.show_success()
        QTimer.singleShot(1000, lambda: overlay_widget.hide())
        self.on_data_loaded(data)
    
    def on_retry_failed(self, error, overlay_widget):
        """Ошибка повторной загрузки"""
        overlay_widget.hide()
        
        self.on_data_failed(error)
    
    def start_auto_scan_if_needed(self):
        """Запуск автоматического сканирования если необходимо"""
        from settings_manager import settings_manager
        
        if settings_manager.should_auto_scan():
            log_info("Запуск автоматического сканирования системы...")
            
            programs_data = getattr(self.programs_tab, 'all_programs', [])
            drivers_data = getattr(self.drivers_tab, 'all_drivers', [])
            
            if programs_data or drivers_data:
                from system_scanner import BackgroundScanner
                self.background_scanner = BackgroundScanner(programs_data, drivers_data)
                self.background_scanner.scan_completed.connect(self.on_background_scan_completed)
                self.background_scanner.start()
    
    def on_background_scan_completed(self, programs_status, drivers_status, summary):
        """Обработка завершения фонового сканирования"""
        log_info(f"Автосканирование завершено: программ {summary['programs_found']}, драйверов {summary['drivers_found']}")
        
        if hasattr(self, 'programs_tab') and hasattr(self.programs_tab, 'status_manager'):
            self.programs_tab.status_manager.refresh_cache()
        
        if hasattr(self, 'drivers_tab') and hasattr(self.drivers_tab, 'status_manager'):
            self.drivers_tab.status_manager.refresh_cache()
        
        if hasattr(self, 'programs_tab'):
            self.programs_tab.display_programs()
            self.programs_tab.update()  
        
        if hasattr(self, 'drivers_tab'):
            self.drivers_tab.display_drivers()
            self.drivers_tab.update()  


class DownloadItem:
    """Элемент загрузки - каждый файл имеет свой прогресс и управление"""

    def __init__(self, program_name, download_url, parent_window, icon_path=None, file_type="program"):
        self.program_name = program_name
        self.download_url = download_url
        self.parent_window = parent_window
        self.icon_path = icon_path
        self.file_type = file_type
        self.download_thread = None
        self.widget = None
        self.progress_bar = None
        self.info_label = None
        self.cancel_button = None
        self.open_button = None
        self.size_label = None
        self.start_time = None
        self.downloaded_file_path = None
        self.notification_manager = get_notification_manager()
        
        self.create_widget()
        self.start_download()

    def create_widget(self):
        """Создание виджета элемента загрузки"""
        self.widget = QWidget()
        self.widget.setFixedHeight(160)
        self.widget.setStyleSheet("""
            QWidget {
                background-color: #353535;
                border: 1px solid #4a4a4a;
                border-radius: 15px;
            }
        """)
        
        layout = QVBoxLayout(self.widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        header_layout = QHBoxLayout()
        
        title_label = QLabel(self.program_name)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: bold;
                color: #ffffff;
                background: transparent;
                border: none;
                min-height: 20px;
            }
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        self.open_button = QPushButton()
        self.open_button.setFixedSize(80, 24)
        self.open_button.clicked.connect(self.open_file)
        
        icon_path = get_icon_path("opensize.png")
        if icon_path:
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                icon = QIcon(pixmap)
                self.open_button.setIcon(icon)
                self.open_button.setIconSize(pixmap.size().boundedTo(QPixmap(11, 11).size()))
                self.open_button.setText("Открыть")
            else:
                self.open_button.setText("Открыть")
        else:
            self.open_button.setText("Открыть")
        
        self.open_button.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                padding: 2px 6px;
                border-radius: 12px;
                background-color: #4a4a4a;
                color: #ffffff;
                border: none;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        self.open_button.hide()
        header_layout.addWidget(self.open_button)
        
        self.cancel_button = QPushButton()
        self.cancel_button.setFixedSize(24, 24)
        self.cancel_button.clicked.connect(self.cancel_download)
        
        icon_path = get_icon_path("closemenu.png")
        if icon_path:
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                icon = QIcon(pixmap)
                self.cancel_button.setIcon(icon)
            else:
                self.cancel_button.setText("×")
        else:
            self.cancel_button.setText("×")
        
        self.cancel_button.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                padding: 0px;
                border-radius: 12px;
                background-color: #666666;
                color: #ffffff;
                border: none;
                margin-left: 5px;
                min-width: 24px;
                max-width: 24px;
                min-height: 24px;
                max-height: 24px;
            }
            QPushButton:hover {
                background-color: #777777;
            }
        """)
        header_layout.addWidget(self.cancel_button)
        
        layout.addLayout(header_layout)
        
        parsed_url = urlparse(self.download_url)
        filename = os.path.basename(parsed_url.path)
        if not filename or '.' not in filename:
            filename = f"{self.program_name.replace(' ', '_')}_installer.exe"
        
        self.file_label = QLabel()
        file_layout = QHBoxLayout()
        file_layout.setContentsMargins(0, 0, 0, 0)
        file_layout.setSpacing(5)
        
        file_icon = QLabel()
        icon_path = get_icon_path("file.png")
        if icon_path:
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(12, 12, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                file_icon.setPixmap(scaled_pixmap)
            else:
                file_icon.setText("•")
        else:
            file_icon.setText("•")
        
        file_icon.setStyleSheet("background: transparent; border: none;")
        file_icon.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        file_layout.addWidget(file_icon)
        
        file_text = QLabel(self.program_name)
        file_text.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #cccccc;
                background: transparent;
                border: none;
                min-height: 18px;
            }
        """)
        file_text.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        file_layout.addWidget(file_text)
        file_layout.addStretch()
        
        file_container = QWidget()
        file_container.setLayout(file_layout)
        file_container.setStyleSheet("background: transparent; border: none;")
        file_container.setFixedHeight(18)
        self.file_label = file_container
        layout.addWidget(self.file_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(24)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 8px;
                background-color: #404040;
                text-align: center;
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #666666;
                border-radius: 6px;
                margin: 1px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        self.info_label = QLabel()
        self.info_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #cccccc;
                background: transparent;
                border: none;
                min-height: 18px;
            }
        """)
        self.info_label.setTextFormat(Qt.TextFormat.RichText)
        self.set_info_text("Подготовка к скачиванию...", "preparation")
        layout.addWidget(self.info_label)
        
        self.size_label = QLabel("")
        self.size_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #888888;
                background: transparent;
                border: none;
                min-height: 16px;
            }
        """)
        layout.addWidget(self.size_label)

    def set_info_text(self, text, icon_name):
        """Установить текст с иконкой для info_label"""
        icon_path = get_icon_path(f"{icon_name}.png")
        if icon_path:
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(12, 12, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                
                temp_manager = get_temp_manager()
                temp_path = temp_manager.get_temp_file_path(f"{icon_name}_temp.png")
                
                scaled_pixmap.save(temp_path)
                self.info_label.setText(f'<img src="{temp_path}" width="12" height="12" style="vertical-align: middle; margin-right: 3px;"> {text}')
            else:
                emoji_map = {
                    "preparation": "...",
                    "speed": "→", 
                    "time": "⏰",
                    "size": "□",
                    "installer": "○",
                    "complete": "✓",
                    "error": "×",
                    "delete": "×"
                }
                emoji = emoji_map.get(icon_name, "•")
                self.info_label.setText(f"{emoji} {text}")
        else:
            emoji_map = {
                "preparation": "...",
                "speed": "→", 
                "time": "⏰",
                "size": "□",
                "installer": "○",
                "complete": "✓",
                "error": "×",
                "delete": "×"
            }
            emoji = emoji_map.get(icon_name, "•")
            self.info_label.setText(f"{emoji} {text}")
    def start_download(self):
        """Запуск скачивания"""
        
        self.start_time = time.time()
        
        parsed_url = urlparse(self.download_url)
        filename = os.path.basename(parsed_url.path)
        if not filename or '.' not in filename:
            filename = f"{self.program_name.replace(' ', '_')}_installer.exe"
        
        try:
            import sys
            import importlib
            download_manager = importlib.import_module('download_manager')
            DownloadThread = download_manager.DownloadThread
            
            self.download_thread = DownloadThread(self.download_url, filename)
            self.download_thread.progress_updated.connect(self.update_progress)
            self.download_thread.download_finished.connect(self.download_completed)
            self.download_thread.download_error.connect(self.download_failed)
            self.download_thread.start()
        except Exception as e:
            log_error(f"Ошибка в start_download: {e}")
            if self.info_label:
                self.info_label.setText(f"Ошибка: {e}")

    def update_progress(self, percent, speed, size):
        """Обновление прогресса"""
        if not self.progress_bar or not self.info_label:
            return
        
        try:
            self.progress_bar.setValue(percent)
            
            if hasattr(self, 'size_label') and self.size_label and size and not self.size_label.text():
                self.size_label.setText(f"Размер: {size}")
            
            if self.start_time and percent > 0:
                elapsed = time.time() - self.start_time
                if percent < 100:
                    estimated_total = elapsed * 100 / percent
                    remaining = estimated_total - elapsed
                    remaining_str = self.format_time(remaining)
                    
                    speed_html = self.get_icon_html("speed", 12) + f" {speed}"
                    time_html = self.get_icon_html("time", 12) + f" Осталось: {remaining_str}"
                    self.info_label.setText(f"{speed_html} • {time_html}")
                else:
                    self.set_info_text("Завершено", "complete")
            else:
                self.set_info_text(speed, "speed")
        except RuntimeError as e:
            log_error(f"RuntimeError в update_progress: {e}")

    def download_completed(self, file_path):
        """Скачивание завершено"""
        if not self.progress_bar or not self.info_label or not self.cancel_button:
            return
        
        try:
            self.progress_bar.setValue(100)
            
            try:
                from downloads_manager import get_downloads_manager
                import shutil
                
                manager = get_downloads_manager()
                
                filename = os.path.basename(file_path)
                dest_path = os.path.join(manager.downloads_dir, filename)
                
                if os.path.exists(file_path):
                    os.makedirs(manager.downloads_dir, exist_ok=True)
                    
                    shutil.move(file_path, dest_path)
                    
                    manager.add_download(filename, self.program_name, self.file_type, self.icon_path)
                    
                    self.downloaded_file_path = dest_path
                    
                    self.notification_manager.show_download_notification(self.program_name, success=True, item_type=self.file_type)
                    
                    if hasattr(self.parent_window, 'downloads_tab'):
                        QTimer.singleShot(500, self.parent_window.downloads_tab.refresh_downloads)
                else:
                    self.downloaded_file_path = file_path
            except Exception as e:
                print(f"Ошибка копирования файла в UHDOWNLOAD: {e}")
                traceback.print_exc()
                self.downloaded_file_path = file_path
            
            file_extension = self.downloaded_file_path.lower().split('.')[-1]
            if file_extension in ['zip', 'rar', '7z', 'tar', 'gz', 'bz2']:
                self.set_info_text("Архив готов к использованию", "complete")
            else:
                self.set_info_text("Установщик готов к запуску", "installer")
            
            self.open_button.show()
            self.cancel_button.hide()
        except RuntimeError:
            pass

    def download_failed(self, error):
        """Ошибка скачивания"""
        if not self.info_label or not self.cancel_button:
            return
        
        try:
            short_error = error.split('\n')[0] if '\n' in error else error
            if len(short_error) > 50:
                short_error = short_error[:47] + "..."
            self.set_info_text(f"Ошибка: {short_error}", "error")
            
            filename = getattr(self, 'filename', 'файл')
            program_name = getattr(self, 'program_name', filename)
            file_type = getattr(self, 'file_type', 'program')
            self.notification_manager.show_download_notification(program_name, success=False, item_type=file_type)
            
            from download_manager import CustomMessageBox
            CustomMessageBox.critical(None, "Ошибка скачивания", error)
            
            icon_path = get_icon_path("closemenu.png")
            if icon_path:
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    icon = QIcon(pixmap)
                    self.cancel_button.setIcon(icon)
                    self.cancel_button.setText("")
                else:
                    self.cancel_button.setText("×")
            else:
                self.cancel_button.setText("×")
            
            if hasattr(self, 'size_label') and self.size_label:
                self.size_label.setText("")
            if hasattr(self, 'open_button') and self.open_button:
                self.open_button.hide()
            
            QTimer.singleShot(3000, self.remove_from_list)
        except RuntimeError:
            pass

    def run_as_admin_file(self, file_path):
        """Запустить файл с правами администратора"""
        try:
            import ctypes
            import sys
            
            if sys.platform == "win32":
                result = ctypes.windll.shell32.ShellExecuteW(
                    None,
                    "runas",
                    file_path,
                    None,
                    None,
                    1
                )
                return result > 32
            else:
                import subprocess
                subprocess.Popen(['sudo', file_path])
                return True
        except Exception as e:
            print(f"Ошибка запуска с правами администратора: {e}")
            return False

    def open_file(self):
        """Открыть скачанный файл"""
        if not self.downloaded_file_path:
            return
            
        try:
            import subprocess
            
            file_extension = self.downloaded_file_path.lower().split('.')[-1]
            
            if file_extension in ['zip', 'rar', '7z', 'tar', 'gz', 'bz2']:
                os.startfile(self.downloaded_file_path)
                self.set_info_text("Архив открыт", "complete")
            else:
                success = False
                if self.downloaded_file_path.lower().endswith('.msi'):
                    success = self.run_as_admin_file('msiexec')
                    if not success:
                        try:
                            subprocess.Popen(['msiexec', '/i', self.downloaded_file_path])
                            success = True
                        except:
                            pass
                elif self.downloaded_file_path.lower().endswith('.exe'):
                    success = self.run_as_admin_file(self.downloaded_file_path)
                    if not success:
                        try:
                            subprocess.Popen([self.downloaded_file_path])
                            success = True
                        except:
                            pass
                else:
                    os.startfile(self.downloaded_file_path)
                    success = True
                
                if success:
                    self.set_info_text("Установщик запущен", "installer")
                else:
                    self.set_info_text("Ошибка запуска установщика", "error")
            
            self.open_button.hide()
            
            icon_path = get_icon_path("delete.png")
            if icon_path:
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    icon = QIcon(pixmap)
                    self.cancel_button.setIcon(icon)
                    self.cancel_button.setIconSize(QSize(16, 16))
                    self.cancel_button.setText("")
                else:
                    self.cancel_button.setText("×")
            else:
                self.cancel_button.setText("×")
            self.cancel_button.setStyleSheet("""
                QPushButton {
                    font-size: 12px;
                    padding: 0px;
                    border-radius: 12px;
                    background-color: #f44336;
                    color: #ffffff;
                    border: none;
                    margin-left: 5px;
                    min-width: 24px;
                    max-width: 24px;
                    min-height: 24px;
                    max-height: 24px;
                }
                QPushButton:hover {
                    background-color: #da190b;
                }
            """)
            self.cancel_button.show()
            
            self.cancel_button.clicked.disconnect()
            self.cancel_button.clicked.connect(self.remove_from_history)
            
        except Exception as e:
            self.set_info_text(f"Ошибка: {str(e)}", "error")

    def delete_and_remove(self):
        """Удалить файл и убрать из списка"""
        if self.downloaded_file_path:
            try:
                if os.path.exists(self.downloaded_file_path):
                    try:
                        from downloads_manager import get_downloads_manager
                        manager = get_downloads_manager()
                        filename = os.path.basename(self.downloaded_file_path)
                        manager.delete_download(filename)
                        
                        if hasattr(self.parent_window, 'downloads_tab'):
                            self.parent_window.downloads_tab.refresh_downloads()
                    except Exception as e:
                        print(f"Ошибка удаления из менеджера: {e}")
                    
                    os.remove(self.downloaded_file_path)
                    self.set_info_text("Файл удален", "delete")
            except Exception as e:
                self.set_info_text(f"Ошибка удаления: {str(e)}", "error")
        
        QTimer.singleShot(1000, self.remove_from_list)

    def remove_from_history(self):
        """Убрать из истории загрузок (не удаляя файл)"""
        if self.downloaded_file_path:
            try:
                try:
                    from downloads_manager import get_downloads_manager
                    manager = get_downloads_manager()
                    filename = os.path.basename(self.downloaded_file_path)
                    manager.delete_download(filename)
                    
                    if hasattr(self.parent_window, 'downloads_tab'):
                        self.parent_window.downloads_tab.refresh_downloads()
                        
                    self.set_info_text("Убрано из истории", "delete")
                except Exception as e:
                    print(f"Ошибка удаления из истории: {e}")
                    self.set_info_text(f"Ошибка: {str(e)}", "error")
            except Exception as e:
                self.set_info_text(f"Ошибка: {str(e)}", "error")
        
        QTimer.singleShot(1000, self.remove_from_list)

    def cancel_download(self):
        """Отмена загрузки"""
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.terminate()
            self.download_thread.wait()
        
        self.remove_from_list()

    def remove_from_list(self):
        """Удаление из списка загрузок"""
        if self.parent_window:
            self.parent_window.remove_download(self)

    def get_widget(self):
        """Получить виджет элемента"""
        return self.widget

    def format_time(self, seconds):
        """Форматирование времени"""
        if seconds < 60:
            return f"{int(seconds)}с"
        elif seconds < 3600:
            return f"{int(seconds // 60)}м {int(seconds % 60)}с"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}ч {minutes}м"

    def get_icon_html(self, icon_name, size):
        """Получить HTML код для иконки"""
        icon_path = get_icon_path(f"{icon_name}.png")
        if icon_path:
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                
                temp_manager = get_temp_manager()
                temp_path = temp_manager.get_temp_file_path(f"{icon_name}_{size}_temp.png")
                
                scaled_pixmap.save(temp_path)
                return f'<img src="{temp_path}" width="{size}" height="{size}" style="vertical-align: middle; margin-right: 3px;">'
            else:
                emoji_map = {
                    "preparation": "...",
                    "speed": "→", 
                    "time": "⏰",
                    "size": "□",
                    "installer": "○",
                    "complete": "✓",
                    "error": "×",
                    "delete": "×"
                }
                return emoji_map.get(icon_name, "•")
        else:
            emoji_map = {
                "preparation": "...",
                "speed": "→", 
                "time": "⏰",
                "size": "□",
                "installer": "○",
                "complete": "✓",
                "error": "×",
                "delete": "×"
            }
            return emoji_map.get(icon_name, "•")
    
    def update_translations(self):
        """Обновление всех переводов в интерфейсе без перезапуска"""
        try:
            print("=== UPDATE TRANSLATIONS CALLED ===")
            log_info("Starting translations update")
            
            self.tab_widget.setTabText(0, t("tabs.news"))
            self.tab_widget.setTabText(1, t("tabs.programs"))
            self.tab_widget.setTabText(2, t("tabs.drivers"))
            self.tab_widget.setTabText(3, t("tabs.library"))
            self.tab_widget.setTabText(4, t("tabs.settings"))
            print("Tab names updated")
            
            if hasattr(self, 'downloads_button'):
                self.downloads_button.setText(t("main_window.downloads_button"))
                print("Downloads button updated")
            
            if hasattr(self, 'version_label'):
                try:
                    with open(resource_path('version.txt'), 'r', encoding='utf-8') as f:
                        version = f.read().strip()
                    self.version_label.setText(t("app.version", version=version))
                    print("Version label updated")
                except:
                    pass
            
            # Перезагружаем текущую вкладку для обновления её содержимого
            current_index = self.tab_widget.currentIndex()
            print(f"Current tab index: {current_index}")
            
            if hasattr(self, 'news_tab') and self.news_tab:
                self.news_tab.load_news_from_data()
                print("News tab updated")
            
            if hasattr(self, 'programs_tab') and self.programs_tab:
                self.programs_tab.load_programs()
                print("Programs tab updated")
            
            if hasattr(self, 'drivers_tab') and self.drivers_tab:
                self.drivers_tab.load_drivers()
                print("Drivers tab updated")
            
            if hasattr(self, 'downloads_tab') and self.downloads_tab:
                self.downloads_tab.load_downloads()
                print("Downloads tab updated")
            
            if hasattr(self, 'settings_tab') and self.settings_tab:
                # Просто перезагружаем раздел интерфейса
                self.settings_tab.show_interface_settings()
                print("Settings tab updated")
            
            log_info("Translations updated successfully")
            print("=== UPDATE TRANSLATIONS COMPLETED ===")
            
        except Exception as e:
            log_error(f"Error updating translations: {e}")
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    def closeEvent(self, event):
        """Обработка закрытия приложения"""
        try:
            # Очищаем менеджер логотипов
            from logo_manager import cleanup_logo_manager
            cleanup_logo_manager()
            
            # Очищаем все вкладки
            if hasattr(self, 'programs_tab') and self.programs_tab:
                self.programs_tab.cleanup()
            
            if hasattr(self, 'drivers_tab') and self.drivers_tab:
                self.drivers_tab.cleanup()
            
            if hasattr(self, 'downloads_tab') and self.downloads_tab:
                if hasattr(self.downloads_tab, 'cleanup'):
                    self.downloads_tab.cleanup()
            
            # Останавливаем все анимации
            if hasattr(self, 'snow_timer') and self.snow_timer:
                self.snow_timer.stop()
            
            # Очищаем уведомления
            notification_manager = get_notification_manager()
            if notification_manager:
                notification_manager.cleanup()
                
        except Exception as e:
            print(f"Ошибка при закрытии приложения: {e}")
        
        event.accept()