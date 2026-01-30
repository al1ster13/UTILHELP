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
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QPixmap, QIcon, QGuiApplication
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


class SettingsTab(QWidget):
    """Вкладка настроек с боковой панелью - сделал для удобства навигации"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 3, 0, 3)
        main_layout.setSpacing(0)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 10px;
            }
        """)
        
        self.snow_enabled = False
        self.theme_light = False
        self.snow_toggle = None
        self.theme_toggle = None
        
        self.theme_development_dialog = None
        
        self.create_sidebar(main_layout)
        self.create_content_area(main_layout)
        self.show_interface_settings()

    def load_icon_pixmap(self, icon_name, size=None):
        """Загрузить иконку с правильным путем для exe"""
        icon_path = get_icon_path(icon_name)
        
        if icon_path:
            pixmap = QPixmap(icon_path)
            
            if not pixmap.isNull() and size:
                scaled = pixmap.scaled(size[0], size[1], Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                return scaled
            return pixmap
        
        return QPixmap()  

    def create_icon_label(self, icon_name, size=(24, 24), fallback_text="•"):
        """Создать QLabel с иконкой и fallback текстом"""
        icon_label = QLabel()
        pixmap = self.load_icon_pixmap(icon_name, size)
        if not pixmap.isNull():
            icon_label.setPixmap(pixmap)
        else:
            icon_label.setText(fallback_text)
            icon_label.setStyleSheet(f"font-size: {size[0]}px; color: #ffffff;")
        
        icon_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        icon_label.setContentsMargins(0, 2, 0, 0)
        return icon_label

    def create_sidebar(self, main_layout):
        """Создание боковой панели с кнопками"""
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-top-left-radius: 10px;
                border-bottom-left-radius: 10px;
            }
        """)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 15, 0, 15)
        sidebar_layout.setSpacing(5)
        
        # Заголовок настроек
        title_label = QLabel("НАСТРОЙКИ")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0px 0px 15px 0px;
                letter-spacing: 1px;
            }
        """)
        sidebar_layout.addWidget(title_label)
        
        # Кнопки меню
        self.interface_btn = self.create_menu_button("interface.png", "Интерфейс", True)
        self.interface_btn.clicked.connect(self.show_interface_settings)
        sidebar_layout.addWidget(self.interface_btn)
        
        self.temp_files_btn = self.create_menu_button("tempfile.png", "Файлы", False)
        self.temp_files_btn.clicked.connect(self.show_temp_files_settings)
        sidebar_layout.addWidget(self.temp_files_btn)
        
        self.updates_btn = self.create_menu_button("updatetab.png", "Обновления", False)
        self.updates_btn.clicked.connect(self.show_updates_settings)
        sidebar_layout.addWidget(self.updates_btn)
        
        self.about_btn = self.create_menu_button("info.png", "О программе", False)
        self.about_btn.clicked.connect(self.show_about_settings)
        sidebar_layout.addWidget(self.about_btn)
        
        self.contacts_btn = self.create_menu_button("contacts.png", "Контакты", False)
        self.contacts_btn.clicked.connect(self.show_contacts_settings)
        sidebar_layout.addWidget(self.contacts_btn)
        
        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)

    def create_menu_button(self, icon_name, text, active=False):
        """Создание кнопки меню"""
        btn = QPushButton()
        
        try:
            icon_path = get_icon_path(icon_name)
            if icon_path:
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    icon = QIcon(pixmap)
                    btn.setIcon(icon)
                    btn.setIconSize(pixmap.size().boundedTo(QPixmap(16, 16).size()))
                    btn.setText(f"  {text}")
                else:
                    btn.setText("•  " + text)
            else:
                btn.setText("•  " + text)
        except:
            btn.setText("•  " + text)
        
        btn.setFixedHeight(50)
        
        if active:
            btn.setStyleSheet(self.get_active_button_style())
        else:
            btn.setStyleSheet(self.get_inactive_button_style())
        
        return btn

    def get_active_button_style(self):
        """Стиль активной кнопки"""
        return """
            QPushButton {
                background-color: #404040;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: normal;
                font-family: 'Segoe UI', Arial, sans-serif;
                text-align: left;
                padding-left: 20px;
                margin: 2px 10px;
                outline: none;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:focus {
                outline: none;
                border: none;
            }
        """

    def get_inactive_button_style(self):
        """Стиль неактивной кнопки"""
        return """
            QPushButton {
                background-color: transparent;
                color: #cccccc;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: normal;
                font-family: 'Segoe UI', Arial, sans-serif;
                text-align: left;
                padding-left: 20px;
                margin: 2px 10px;
                outline: none;
            }
            QPushButton:hover {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QPushButton:focus {
                outline: none;
                border: none;
            }
        """
    def create_content_area(self, main_layout):
        """Создание области содержимого"""
        self.content_area = QWidget()
        self.content_area.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
            }
        """)
        
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(40, 30, 40, 30)
        self.content_layout.setSpacing(25)
        
        main_layout.addWidget(self.content_area)

    def clear_content(self):
        """Очистка содержимого"""
        if hasattr(self, 'cleanup_message'):
            self.cleanup_message = None
            
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def show_interface_settings(self):
        """Показать настройки интерфейса"""
        self.interface_btn.setStyleSheet(self.get_active_button_style())
        self.temp_files_btn.setStyleSheet(self.get_inactive_button_style())
        self.updates_btn.setStyleSheet(self.get_inactive_button_style())
        self.about_btn.setStyleSheet(self.get_inactive_button_style())
        self.contacts_btn.setStyleSheet(self.get_inactive_button_style())
        
        self.clear_content()
        
        self.content_layout.setContentsMargins(40, 30, 40, 30)
        
        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)
        title_layout.setContentsMargins(0, 0, 0, 20)
        
        icon_label = self.create_icon_label("interface.png", (24, 24))
        
        icon_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        icon_label.setContentsMargins(0, 4, 0, 0)
        title_layout.addWidget(icon_label)
        
        title_text = QLabel("Настройки интерфейса")
        title_text.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        title_text.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        
        title_container = QWidget()
        title_container.setLayout(title_layout)
        self.content_layout.addWidget(title_container)
        
        self.snow_toggle = ToggleSwitch()
        self.snow_toggle.setChecked(self.snow_enabled)
        if self.parent_window:
            self.snow_toggle.toggled.connect(self.parent_window.toggle_snow)
            self.snow_toggle.toggled.connect(self.save_snow_state)
        
        snow_setting = self.create_setting_item(
            "snowflake.png", 
            "Снегопад", 
            "Анимированные снежинки на фоне приложения для создания праздничной атмосферы",
            self.snow_toggle
        )
        self.content_layout.addWidget(snow_setting)
        
        self.theme_toggle = DisabledToggleSwitch()
        self.theme_toggle.setChecked(self.theme_light)  # Всегда False
        self.theme_toggle.toggled.connect(self.handle_theme_toggle)
        
        theme_setting = self.create_setting_item(
            "whitetheme.png", 
            "Светлая тема", 
            "Переключение между темной и светлой темой интерфейса",
            self.theme_toggle
        )
        self.content_layout.addWidget(theme_setting)
        

        
        self.content_layout.addStretch()

    def show_updates_settings(self):
        """Показать настройки обновлений"""
        
        self.interface_btn.setStyleSheet(self.get_inactive_button_style())
        self.temp_files_btn.setStyleSheet(self.get_inactive_button_style())
        self.updates_btn.setStyleSheet(self.get_active_button_style())
        self.about_btn.setStyleSheet(self.get_inactive_button_style())
        self.contacts_btn.setStyleSheet(self.get_inactive_button_style())
        
        self.clear_content()
        
        self.content_layout.setContentsMargins(40, 30, 40, 30)
        
        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)
        title_layout.setContentsMargins(0, 0, 0, 20)
        
        icon_label = self.create_icon_label("updatetab.png", (24, 24))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        icon_label.setContentsMargins(0, 2, 0, 0)
        title_layout.addWidget(icon_label)
        
        title_text = QLabel("Обновления")
        title_text.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        title_text.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        
        title_container = QWidget()
        title_container.setLayout(title_layout)
        self.content_layout.addWidget(title_container)
        
        # Виджет обновлений (как настройка)
        update_widget = self.create_simple_update_widget()
        self.content_layout.addWidget(update_widget)
        
        self.content_layout.addStretch()

    def show_about_settings(self):
        """Показать информацию о программе"""
        self.interface_btn.setStyleSheet(self.get_inactive_button_style())
        self.temp_files_btn.setStyleSheet(self.get_inactive_button_style())
        self.updates_btn.setStyleSheet(self.get_inactive_button_style())
        self.about_btn.setStyleSheet(self.get_active_button_style())
        self.contacts_btn.setStyleSheet(self.get_inactive_button_style())
        
        self.clear_content()
        
        self.content_layout.setContentsMargins(40, 30, 40, 30)
        
        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)
        title_layout.setContentsMargins(0, 0, 0, 20)
        
        icon_label = self.create_icon_label("info.png", (24, 24))
        
        icon_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        icon_label.setContentsMargins(0, 2, 0, 0)
        title_layout.addWidget(icon_label)
        
        title_text = QLabel("О программе")
        title_text.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        title_text.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        
        title_container = QWidget()
        title_container.setLayout(title_layout)
        self.content_layout.addWidget(title_container)
        
        info_widget = self.create_info_widget()
        self.content_layout.addWidget(info_widget)
        
        self.content_layout.addStretch()

    def show_contacts_settings(self):
        """Показать контактную информацию"""
        self.interface_btn.setStyleSheet(self.get_inactive_button_style())
        self.temp_files_btn.setStyleSheet(self.get_inactive_button_style())
        self.updates_btn.setStyleSheet(self.get_inactive_button_style())
        self.about_btn.setStyleSheet(self.get_inactive_button_style())
        self.contacts_btn.setStyleSheet(self.get_active_button_style())
        
        self.clear_content()
        
        self.content_layout.setContentsMargins(40, 30, 40, 30)
        
        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)
        title_layout.setContentsMargins(0, 0, 0, 20)
        
        icon_label = self.create_icon_label("contacts.png", (24, 24))
        
        icon_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        icon_label.setContentsMargins(0, 2, 0, 0)
        title_layout.addWidget(icon_label)
        
        title_text = QLabel("Контакты")
        title_text.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        title_text.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        
        title_container = QWidget()
        title_container.setLayout(title_layout)
        self.content_layout.addWidget(title_container)
        
        contacts_widget = self.create_contacts_widget()
        self.content_layout.addWidget(contacts_widget)
        
        self.content_layout.addStretch()

    def show_temp_files_settings(self):
        """Показать настройки временных файлов"""
        self.interface_btn.setStyleSheet(self.get_inactive_button_style())
        self.temp_files_btn.setStyleSheet(self.get_active_button_style())
        self.updates_btn.setStyleSheet(self.get_inactive_button_style())
        self.about_btn.setStyleSheet(self.get_inactive_button_style())
        self.contacts_btn.setStyleSheet(self.get_inactive_button_style())
        
        self.clear_content()
        
        self.content_layout.setContentsMargins(40, 30, 40, 30)
        
        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)
        title_layout.setContentsMargins(0, 0, 0, 20)
        
        icon_label = self.create_icon_label("tempfile.png", (24, 24))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        icon_label.setContentsMargins(0, 2, 0, 0)
        title_layout.addWidget(icon_label)
        
        title_text = QLabel("Файлы")
        title_text.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        title_text.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        
        title_container = QWidget()
        title_container.setLayout(title_layout)
        self.content_layout.addWidget(title_container)
        
        temp_info_widget = self.create_temp_files_widget()
        self.content_layout.addWidget(temp_info_widget)
        
        update_container = QWidget()
        update_container_layout = QHBoxLayout(update_container)
        update_container_layout.setContentsMargins(8, 0, 8, 0)  
        update_container_layout.setSpacing(0)
        
        update_button = self.create_update_data_button()
        update_container_layout.addWidget(update_button)
        
        self.content_layout.addWidget(update_container)
        
        self.content_layout.addStretch()

    def create_temp_files_widget(self):
        """Создание виджета с информацией о временных файлах"""
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        temp_manager = get_temp_manager()
        
        info_text = QLabel(f"Папка временных файлов:\n{temp_manager.get_temp_dir()}")
        info_text.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 14px;
                background-color: #2d2d2d;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #404040;
            }
        """)
        layout.addWidget(info_text)
        
        files_count = len(temp_manager.list_temp_files())
        total_size = temp_manager.get_temp_size()
        formatted_size = temp_manager.format_size(total_size)
        
        self.stats_text = QLabel(f"Файлов: {files_count}\nОбщий размер: {formatted_size}")
        self.stats_text.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 16px;
                background-color: #252525;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #404040;
            }
        """)
        layout.addWidget(self.stats_text)
        
        clear_btn = QPushButton("Очистить временные файлы")
        clear_btn.clicked.connect(self.clear_temp_files)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(244, 67, 54, 0.1);
                color: #f44336;
                border: 1px solid rgba(244, 67, 54, 0.3);
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(244, 67, 54, 0.2);
                border: 1px solid rgba(244, 67, 54, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(244, 67, 54, 0.3);
                border: 1px solid #f44336;
            }
            QPushButton:focus {
                outline: none;
                border: 1px solid rgba(244, 67, 54, 0.5);
            }
        """)
        layout.addWidget(clear_btn)
        
        self.cleanup_message = QLabel("")
        self.cleanup_message.setStyleSheet("""
            QLabel {
                color: #27ae60;
                font-size: 14px;
                background-color: #1e3a2e;
                border-radius: 8px;
                padding: 12px 15px;
                border: 1px solid #27ae60;
                margin-top: 10px;
            }
        """)
        self.cleanup_message.hide()
        
        layout.addWidget(self.cleanup_message)
        
        return widget
    
    def update_temp_files_stats(self):
        """Обновить статистику временных файлов без пересоздания всего интерфейса"""
        try:
            temp_manager = get_temp_manager()
            
            files_count = len(temp_manager.list_temp_files())
            total_size = temp_manager.get_temp_size()
            formatted_size = temp_manager.format_size(total_size)
            
            if hasattr(self, 'stats_text') and self.stats_text is not None:
                self.stats_text.setText(f"Файлов: {files_count}\nОбщий размер: {formatted_size}")
            
            try:
                from temp_manager import debug_log
                debug_log(f"Stats updated: {files_count} files, {formatted_size}")
            except:
                pass
                
        except Exception as e:
            try:
                from temp_manager import debug_log
                debug_log(f"Error updating stats: {e}")
            except:
                pass
    
    def clear_temp_files(self):
        """Очистить временные файлы"""
        
        try:
            temp_manager = get_temp_manager()
            
            cleaned_files = temp_manager.manual_cleanup()
            
            if not hasattr(self, 'cleanup_message') or self.cleanup_message is None:
                return  
            
            if cleaned_files:
                if len(cleaned_files) == 1:
                    message = f"✓ Удален 1 элемент: {cleaned_files[0]}"
                else:
                    message = f"✓ Удалено элементов: {len(cleaned_files)}"
                
                self.cleanup_message.setStyleSheet("""
                    QLabel {
                        color: #27ae60;
                        font-size: 14px;
                        background-color: #1e3a2e;
                        border-radius: 8px;
                        padding: 12px 15px;
                        border: 1px solid #27ae60;
                        margin-top: 10px;
                    }
                """)
            else:
                message = "Временные файлы не найдены или уже удалены"
                self.cleanup_message.setStyleSheet("""
                    QLabel {
                        color: #3498db;
                        font-size: 14px;
                        background-color: #1e2a3a;
                        border-radius: 8px;
                        padding: 12px 15px;
                        border: 1px solid #3498db;
                        margin-top: 10px;
                    }
                """)
            
            self.cleanup_message.setText(message)
            self.cleanup_message.show()
            
            self.update_temp_files_stats()
            
            QTimer.singleShot(5000, lambda: self.cleanup_message.hide() if hasattr(self, 'cleanup_message') and self.cleanup_message else None)
            
        except Exception as e:
            if hasattr(self, 'cleanup_message') and self.cleanup_message is not None:
                error_message = f"✗ Ошибка очистки: {str(e)}"
                self.cleanup_message.setText(error_message)
                self.cleanup_message.setStyleSheet("""
                    QLabel {
                        color: #e74c3c;
                        font-size: 14px;
                        background-color: #3a1e1e;
                        border-radius: 8px;
                        padding: 12px 15px;
                        border: 1px solid #e74c3c;
                        margin-top: 10px;
                    }
                """)
                self.cleanup_message.show()
                
                QTimer.singleShot(7000, lambda: self.cleanup_message.hide() if hasattr(self, 'cleanup_message') and self.cleanup_message else None)

    def create_setting_item(self, icon, title, description, control_widget):
        """Создание элемента настройки"""
        item = QWidget()
        item.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-radius: 15px;
                border: 1px solid #404040;
                padding: 5px;
            }
            QWidget:hover {
                border: 1px solid #555555;
            }
        """)
        
        item_layout = QHBoxLayout(item)
        item_layout.setContentsMargins(25, 20, 25, 20)
        item_layout.setSpacing(20)
        
        icon_label = QLabel()
        if icon.endswith('.png'):
            try:
                icon_path = get_icon_path(icon)
                if icon_path:
                    pixmap = QPixmap(icon_path)
                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        icon_label.setPixmap(scaled_pixmap)
                        icon_label.setStyleSheet("""
                            QLabel {
                                background: transparent;
                                border: none;
                                min-width: 40px;
                                max-width: 40px;
                            }
                        """)
                    else:
                        icon_label.setText("*")
                        icon_label.setStyleSheet("""
                            QLabel {
                                font-size: 28px;
                                background: transparent;
                                border: none;
                                min-width: 40px;
                                max-width: 40px;
                            }
                        """)
                else:
                    icon_label.setText("*")
                    icon_label.setStyleSheet("""
                        QLabel {
                            font-size: 28px;
                            background: transparent;
                            border: none;
                            min-width: 40px;
                            max-width: 40px;
                        }
                    """)
            except:
                icon_label.setText("*")
                icon_label.setStyleSheet("""
                    QLabel {
                        font-size: 28px;
                        background: transparent;
                        border: none;
                        min-width: 40px;
                        max-width: 40px;
                    }
                """)
        else:
            icon_label.setText(icon)
            icon_label.setStyleSheet("""
                QLabel {
                    font-size: 28px;
                    background: transparent;
                    border: none;
                    min-width: 40px;
                    max-width: 40px;
                }
            """)
        
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        item_layout.addWidget(icon_label)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(8)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                margin-left: 0px;
                padding-left: 0px;
            }
        """)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                line-height: 1.4;
                margin-left: 0px;
                padding-left: 0px;
            }
        """)
        desc_label.setWordWrap(True)
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(desc_label)
        
        item_layout.addLayout(text_layout)
        item_layout.addStretch()
        item_layout.addWidget(control_widget)
        
        return item

    def create_info_widget(self):
        """Создание виджета с информацией о программе"""
        info_widget = QWidget()
        info_widget.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-radius: 15px;
                border: 1px solid #404040;
                padding: 10px;
            }
        """)
        
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(30, 25, 30, 25)
        info_layout.setSpacing(20)
        
        header_layout = QHBoxLayout()
        
        logo_label = QLabel()
        pixmap = self.load_icon_pixmap("infologo.png", (48, 48))
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap)
            logo_label.setStyleSheet("""
                QLabel {
                    background: transparent;
                    border: none;
                }
            """)
        else:
            logo_label.setText("•")
            logo_label.setStyleSheet("""
                QLabel {
                    font-size: 48px;
                    background: transparent;
                    border: none;
                }
            """)
        
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setMinimumSize(48, 48)
        
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        
        app_title = QLabel("UTILHELP")
        app_title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 28px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                margin-left: -5px;
            }
        """)
        
        version_label = QLabel(f"Версия {self.get_app_version()}")
        version_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 16px;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
            }
        """)
        
        title_layout.addWidget(app_title)
        title_layout.addWidget(version_label)
        
        header_layout.addWidget(logo_label)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        info_layout.addLayout(header_layout)
        
        description = QLabel("Универсальный помощник для Windows\n\nПрограмма предназначена для быстрого доступа к программам, утилитам и драйверам без лишнего серфинга по интернету. Все необходимое программное обеспечение собрано в одном месте для удобства пользователей.\n\nПервая версия программы была выпущена 9 февраля 2025 года.\n\nВажно: Все ссылки на скачивание ведут на прямое скачивание файлов с официальных сайтов разработчиков или перенаправляют на официальные сайты. UTILHELP не хранит и не распространяет файлы программ и драйверов.\n\nРазработано с заботой о пользователях для экономии времени и упрощения работы с компьютером.")
        description.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                line-height: 1.6;
            }
        """)
        description.setWordWrap(True)
        
        info_layout.addWidget(description)
        
        copyright_label = QLabel('© 2025-2026 UTILHELP. Icons by <a href="https://icons8.com" style="color: #888888; text-decoration: underline;">Icons8</a>')
        copyright_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                margin-top: 10px;
            }
        """)
        copyright_label.setOpenExternalLinks(True)  
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        info_layout.addWidget(copyright_label)
        
        return info_widget

    def create_update_data_button(self):
        """Создание кнопки обновления данных с GitHub"""
        
        update_widget = QWidget()
        update_widget.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-radius: 12px;
                border: 1px solid #404040;
            }
        """)
        
        update_layout = QHBoxLayout(update_widget)
        update_layout.setContentsMargins(20, 20, 20, 20)
        update_layout.setSpacing(15)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        
        title_label = QLabel("Обновление данных")
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
            }
        """)
        text_layout.addWidget(title_label)
        
        desc_label = QLabel("Автоматическое обновление списков программ и драйверов с GitHub")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            QLabel {
                color: #aaaaaa;
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                line-height: 1.4;
            }
        """)
        text_layout.addWidget(desc_label)
        
        update_layout.addLayout(text_layout)
        update_layout.addStretch()
        
        update_btn = QPushButton("Проверить")
        update_btn.setFixedSize(120, 36)
        update_btn.clicked.connect(self.force_data_update)
        
        from resource_path import get_icon_path
        from PyQt6.QtGui import QIcon
        from PyQt6.QtCore import QSize
        
        update_icon_path = get_icon_path("update.png")
        if update_icon_path:
            update_icon = QIcon(update_icon_path)
            update_btn.setIcon(update_icon)
            update_btn.setIconSize(QSize(16, 16))
        
        update_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #666666, stop:1 #555555);
                color: white;
                border: 1px solid #777777;
                border-radius: 8px;
                font-size: 12px;
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
            QPushButton:disabled {
                background: #3a3a3a;
                color: #666666;
                border: 1px solid #444444;
            }
        """)
        
        update_layout.addWidget(update_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        
        bottom_layout = QVBoxLayout()
        bottom_layout.setContentsMargins(0, 12, 0, 0)
        
        self.last_update_label = QLabel()
        self.update_last_update_time()
        self.last_update_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 11px;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                padding-top: 5px;
                margin-left: -2px;
            }
        """)
        bottom_layout.addWidget(self.last_update_label)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addLayout(update_layout)
        main_layout.addLayout(bottom_layout)
        
        update_widget.setLayout(main_layout)
        
        return update_widget
    
    def create_program_update_button(self):
        """Создание кнопки проверки обновлений программы"""
        
        update_widget = QWidget()
        update_widget.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-radius: 12px;
                border: 1px solid #404040;
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        update_layout = QHBoxLayout()
        update_layout.setContentsMargins(20, 15, 20, 10)  
        update_layout.setSpacing(15)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        
        title_label = QLabel("Обновление программы")
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
            }
        """)
        text_layout.addWidget(title_label)
        
        desc_label = QLabel("Проверка новых версий UTILHELP на GitHub")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            QLabel {
                color: #aaaaaa;
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                line-height: 1.4;
            }
        """)
        text_layout.addWidget(desc_label)
        
        update_layout.addLayout(text_layout)
        update_layout.addStretch()
        
        button_container = QWidget()
        button_container.setFixedHeight(60)  
        button_container_layout = QVBoxLayout(button_container)
        button_container_layout.setContentsMargins(0, 0, 0, 0)
        button_container_layout.setSpacing(0)
        
        check_update_btn = QPushButton("Проверить")
        check_update_btn.setFixedSize(120, 36)
        check_update_btn.clicked.connect(self.check_program_updates)
        
        from resource_path import get_icon_path
        from PyQt6.QtGui import QIcon
        from PyQt6.QtCore import QSize
        
        update_icon_path = get_icon_path("update.png")
        if update_icon_path:
            update_icon = QIcon(update_icon_path)
            check_update_btn.setIcon(update_icon)
            check_update_btn.setIconSize(QSize(16, 16))
        
        check_update_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: 1px solid #4CAF50;
                border-radius: 8px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5CBF60, stop:1 #4CAF50);
                border: 1px solid #5CBF60;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #45a049, stop:1 #3d8b40);
            }
            QPushButton:disabled {
                background: #3a3a3a;
                color: #666666;
                border: 1px solid #444444;
            }
        """)
        
        button_container_layout.addStretch()
        button_container_layout.addWidget(check_update_btn, 0, Qt.AlignmentFlag.AlignCenter)
        button_container_layout.addStretch()
        
        update_layout.addWidget(button_container)
        
        main_layout.addLayout(update_layout)
        
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #404040; margin: 0px 20px;")
        main_layout.addWidget(separator)
        
        info_title = QLabel("Информация об обновлениях")
        info_title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 10px 20px 5px 20px;
                background: transparent;
                border: none;
            }
        """)
        main_layout.addWidget(info_title)
        
        info_text = QLabel("""• Автоматическая проверка обновлений при запуске программы
• Уведомления о доступных новых версиях
• Безопасная загрузка обновлений с GitHub
• Автоматическая установка и обновление программы
• Сохранение пользовательских настроек при обновлении""")
        info_text.setWordWrap(True)
        info_text.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                line-height: 1.5;
                margin: 5px 20px 5px 20px;
                background: transparent;
                border: none;
            }
        """)
        main_layout.addWidget(info_text)
        
        release_info = QLabel("Все обновления загружаются с официального репозитория GitHub и проходят проверку безопасности.")
        release_info.setWordWrap(True)
        release_info.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 11px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-style: italic;
                margin: 5px 20px 15px 20px;
                background: transparent;
                border: none;
            }
        """)
        main_layout.addWidget(release_info)
        
        update_widget.setLayout(main_layout)
        
        return update_widget
    
    def create_simple_update_widget(self):
        """Создание простого виджета обновлений"""
        update_widget = QWidget()
        update_widget.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-radius: 15px;
                border: 1px solid #404040;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(update_widget)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)
        
        top_layout = QHBoxLayout()
        top_layout.setSpacing(20)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        
        title_label = QLabel("Обновление программы")
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                margin-left: -2px;
            }
        """)
        text_layout.addWidget(title_label)
        
        desc_label = QLabel("Проверка новых версий UTILHELP на GitHub")
        desc_label.setStyleSheet("""
            QLabel {
                color: #aaaaaa;
                font-size: 13px;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                margin-left: 1px;
            }
        """)
        text_layout.addWidget(desc_label)
        
        top_layout.addLayout(text_layout)
        top_layout.addStretch()
        
        button_container = QWidget()
        button_container.setFixedHeight(60)
        button_container.setStyleSheet("""
            QWidget {
                background: transparent;
                border: none;
            }
        """)
        button_container_layout = QVBoxLayout(button_container)
        button_container_layout.setContentsMargins(0, 0, 0, 0)
        
        check_button = QPushButton("Проверить")
        check_button.setFixedSize(120, 36)
        check_button.clicked.connect(self.check_program_updates)
        
        update_icon_path = get_icon_path("update.png")
        if update_icon_path:
            update_icon = QIcon(update_icon_path)
            check_button.setIcon(update_icon)
            check_button.setIconSize(QSize(16, 16))
        
        check_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #666666, stop:1 #555555);
                color: white;
                border: 1px solid #666666;
                border-radius: 8px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #777777, stop:1 #666666);
                border: 1px solid #777777;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #555555, stop:1 #444444);
            }
        """)
        
        button_container_layout.addStretch()
        button_container_layout.addWidget(check_button, 0, Qt.AlignmentFlag.AlignCenter)
        button_container_layout.addStretch()
        
        top_layout.addWidget(button_container)
        layout.addLayout(top_layout)
        
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #404040;")
        layout.addWidget(separator)
        
        info_title = QLabel("Информация об обновлениях")
        info_title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(info_title)
        
        info_text = QLabel("""• Автоматическая проверка обновлений при запуске программы
• Уведомления о доступных новых версиях
• Безопасная загрузка обновлений с GitHub
• Автоматическая установка и обновление программы
• Сохранение пользовательских настроек при обновлении""")
        info_text.setWordWrap(True)
        info_text.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                line-height: 1.5;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(info_text)
        
        security_info = QLabel("Все обновления загружаются с официального репозитория GitHub и проходят проверку безопасности.")
        security_info.setWordWrap(True)
        security_info.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 11px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-style: italic;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(security_info)
        
        return update_widget
    
    def check_program_updates(self):
        """Проверить обновления программы"""
        try:
            from update_checker import get_update_manager
            
            update_manager = get_update_manager(self.parent_window if hasattr(self, 'parent_window') else self)
            
            update_manager.check_for_updates_interactive()
            
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self.parent_window if hasattr(self, 'parent_window') else self,
                "Ошибка",
                f"Не удалось проверить обновления:\n{str(e)}"
            )
    
    def update_last_update_time(self):
        """Обновляет текст с временем последнего обновления"""
        
        cache_time_file = os.path.join("data", "cache_time.txt")
        
        if os.path.exists(cache_time_file):
            try:
                with open(cache_time_file, 'r') as f:
                    cache_time = datetime.fromisoformat(f.read().strip())
                    time_str = cache_time.strftime("%d.%m.%Y %H:%M")
                    self.last_update_label.setText(f"Последнее обновление: {time_str}")
            except:
                self.last_update_label.setText("Обновления еще не проверялись")
        else:
            self.last_update_label.setText("Обновления еще не проверялись")
    
    def force_data_update(self):
        """Принудительное обновление данных"""
        
        try:
            sender = self.sender()
            if sender:
                sender.setEnabled(False)
                sender.setText("Обновление...")
                sender.setIcon(QIcon())
            
            if hasattr(self, 'last_update_label'):
                self.last_update_label.setText("Проверка обновлений...")
            
            manager = get_json_manager()
            
            main_window = self.parent_window if hasattr(self, 'parent_window') else self.parent()
            
            def on_complete(data):
                try:
                    if hasattr(main_window, 'update_last_update_time'):
                        main_window.update_last_update_time()
                    
                    if hasattr(main_window, 'programs_tab'):
                        main_window.programs_tab.set_data(data.get('programs', []))
                    if hasattr(main_window, 'drivers_tab'):
                        main_window.drivers_tab.set_data(data.get('drivers', []))
                    if hasattr(main_window, 'news_tab'):
                        main_window.news_tab.set_data(data.get('news', []))
                    
                    if sender:
                        sender.setText("Успех")
                        sender.setIcon(QIcon()) 
                        sender.setStyleSheet("""
                            QPushButton {
                                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 #27ae60, stop:1 #229954);
                                color: white;
                                border: 1px solid #2ecc71;
                                border-radius: 8px;
                                font-size: 12px;
                                font-weight: bold;
                            }
                            QPushButton:hover {
                                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 #2ecc71, stop:1 #27ae60);
                                border: 1px solid #2ecc71;
                            }
                        """)
                        
                        QTimer.singleShot(3000, lambda: self.reset_update_button(sender))
                    
                except Exception as e:
                    print(f"Ошибка в on_complete: {e}")
                    import traceback
                    traceback.print_exc()
                    from PyQt6.QtWidgets import QMessageBox
                    msg_box = QMessageBox(main_window)
                    msg_box.setWindowTitle("Ошибка")
                    msg_box.setText(f"Ошибка обновления интерфейса:\n{e}")
                    msg_box.setIcon(QMessageBox.Icon.Critical)
                    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                    msg_box.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
                    msg_box.exec()
            
            def on_failed(error):
                try:
                    if sender:
                        sender.setEnabled(True)
                        sender.setText("Проверить")
                        from resource_path import get_icon_path
                        from PyQt6.QtGui import QIcon
                        from PyQt6.QtCore import QSize
                        
                        update_icon_path = get_icon_path("update.png")
                        if update_icon_path:
                            update_icon = QIcon(update_icon_path)
                            sender.setIcon(update_icon)
                            sender.setIconSize(QSize(16, 16))
                        
                        sender.setStyleSheet("""
                            QPushButton {
                                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 #666666, stop:1 #555555);
                                color: white;
                                border: 1px solid #777777;
                                border-radius: 8px;
                                font-size: 12px;
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
                            QPushButton:disabled {
                                background: #3a3a3a;
                                color: #666666;
                                border: 1px solid #444444;
                            }
                        """)
                    
                    if hasattr(self, 'last_update_label'):
                        self.last_update_label.setText("Ошибка при проверке обновлений")
                    
                    from PyQt6.QtWidgets import QMessageBox
                    msg_box = QMessageBox(main_window)
                    msg_box.setWindowTitle("Ошибка")
                    msg_box.setText(f"Не удалось обновить данные:\n{error}")
                    msg_box.setIcon(QMessageBox.Icon.Warning)
                    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                    msg_box.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
                    msg_box.exec()
                    
                except Exception as e:
                    print(f"Ошибка в on_failed: {e}")
                    import traceback
                    traceback.print_exc()
            
            manager.load_data(on_complete=on_complete, on_failed=on_failed)
            
        except Exception as e:
            print(f"Ошибка в force_data_update: {e}")
            import traceback
            traceback.print_exc()
            from PyQt6.QtWidgets import QMessageBox
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Критическая ошибка")
            msg_box.setText(f"Ошибка обновления данных:\n{e}")
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
            msg_box.exec()
    
    def reset_update_button(self, button):
        """Возвращает кнопку обновления в исходное состояние"""
        if button:
            button.setEnabled(True)
            button.setText("Проверить")
            
            from resource_path import get_icon_path
            from PyQt6.QtGui import QIcon
            from PyQt6.QtCore import QSize
            
            update_icon_path = get_icon_path("update.png")
            if update_icon_path:
                update_icon = QIcon(update_icon_path)
                button.setIcon(update_icon)
                button.setIconSize(QSize(16, 16))
            
            button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #666666, stop:1 #555555);
                    color: white;
                    border: 1px solid #777777;
                    border-radius: 8px;
                    font-size: 12px;
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
                QPushButton:disabled {
                    background: #3a3a3a;
                    color: #666666;
                    border: 1px solid #444444;
                }
            """)
    
    def create_contacts_widget(self):
        """Создание виджета с контактной информацией"""
        contacts_widget = QWidget()
        contacts_widget.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-radius: 15px;
                border: 1px solid #404040;
                padding: 10px;
            }
        """)
        
        contacts_layout = QVBoxLayout(contacts_widget)
        contacts_layout.setContentsMargins(20, 15, 20, 15)
        contacts_layout.setSpacing(10)
        
        header_label = QLabel("Связаться с разработчиком")
        header_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                margin-bottom: 5px;
            }
        """)
        contacts_layout.addWidget(header_label)
        
        github_layout = QHBoxLayout()
        github_layout.setSpacing(8)
        github_icon = QLabel()
        pixmap = self.load_icon_pixmap("github.png", (16, 16))
        if not pixmap.isNull():
            github_icon.setPixmap(pixmap)
        else:
            github_icon.setText("•")
        github_icon.setStyleSheet("background: transparent; border: none; margin-top: 1px;")
        github_label = QLabel("GitHub:")
        github_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 13px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                min-width: 80px;
            }
        """)
        github_link = QLabel('<a href="https://github.com/al1ster13/UTILHELP" style="color: #3498db; text-decoration: none;">https://github.com/al1ster13/UTILHELP</a>')
        github_link.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-size: 13px;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
            }
        """)
        github_link.setOpenExternalLinks(True)
        github_layout.addWidget(github_icon)
        github_layout.addWidget(github_label)
        github_layout.addWidget(github_link)
        github_layout.addStretch()
        contacts_layout.addLayout(github_layout)
        
        email_layout = QHBoxLayout()
        email_layout.setSpacing(8)
        email_icon = QLabel()
        pixmap = self.load_icon_pixmap("email.png", (16, 16))
        if not pixmap.isNull():
            email_icon.setPixmap(pixmap)
        else:
            email_icon.setText("•")
        email_icon.setStyleSheet("background: transparent; border: none; margin-top: 1px;")
        email_label = QLabel("Email:")
        email_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 13px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                min-width: 80px;
            }
        """)
        email_link = QLabel('utilhelp@yandex.com')
        email_link.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-size: 13px;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
            }
            QLabel:hover {
                color: #5dade2;
                text-decoration: underline;
            }
        """)
        email_link.mousePressEvent = lambda event: self.copy_email_to_clipboard()
        
        self.copied_label = QLabel("Скопировано!")
        self.copied_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                margin-left: 10px;
            }
        """)
        self.copied_label.setVisible(False)
        
        self.copied_opacity_effect = QGraphicsOpacityEffect()
        self.copied_opacity_effect.setOpacity(0.0)
        self.copied_label.setGraphicsEffect(self.copied_opacity_effect)
        
        self.copied_fade_animation = QPropertyAnimation(self.copied_opacity_effect, b"opacity")
        self.copied_fade_animation.setDuration(300)
        self.copied_fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.copy_timer = QTimer()
        self.copy_timer.timeout.connect(self.hide_copied_label)
        self.copy_timer.setSingleShot(True)
        email_layout.addWidget(email_icon)
        email_layout.addWidget(email_label)
        email_layout.addWidget(email_link)
        email_layout.addWidget(self.copied_label)
        email_layout.addStretch()
        contacts_layout.addLayout(email_layout)
        
        telegram_layout = QHBoxLayout()
        telegram_layout.setSpacing(8)
        telegram_icon = QLabel()
        pixmap = self.load_icon_pixmap("telegram.png", (16, 16))
        if not pixmap.isNull():
            telegram_icon.setPixmap(pixmap)
        else:
            telegram_icon.setText("•")
        telegram_icon.setStyleSheet("background: transparent; border: none; margin-top: 1px;")
        telegram_label = QLabel("Telegram:")
        telegram_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 13px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                min-width: 80px;
            }
        """)
        telegram_link = QLabel('<a href="https://t.me/UTILHELP" style="color: #3498db; text-decoration: none;">https://t.me/UTILHELP</a>')
        telegram_link.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-size: 13px;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
            }
        """)
        telegram_link.setOpenExternalLinks(True)
        telegram_layout.addWidget(telegram_icon)
        telegram_layout.addWidget(telegram_label)
        telegram_layout.addWidget(telegram_link)
        telegram_layout.addStretch()
        contacts_layout.addLayout(telegram_layout)
        
        info_text = QLabel("""Мы всегда рады обратной связи от пользователей!

• Сообщения об ошибках и предложения по улучшению
• Идеи для новых функций и возможностей  
• Вопросы по использованию программы
• Предложения о сотрудничестве

Подписывайтесь на наш Telegram канал для получения новостей и обновлений. Ваше мнение помогает делать UTILHELP лучше!

Обычно мы отвечаем в течение 24 часов.""")
        info_text.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                line-height: 1.4;
            }
        """)
        info_text.setWordWrap(True)
        contacts_layout.addWidget(info_text)
        
        return contacts_widget

    def get_app_version(self):
        """Получение версии приложения"""
        try:
            with open('version.txt', 'r', encoding='utf-8') as f:
                return f'v{f.read().strip()}'
        except:
            return 'v1.0'

    def set_parent_window(self, parent_window):
        """Установка ссылки на главное окно"""
        self.parent_window = parent_window

    def show_theme_development_message(self, checked):
        """Показать сообщение о том, что функция в стадии разработки"""
        if (self.theme_development_dialog is None or 
            not self.theme_development_dialog.isVisible()):
            from custom_dialogs import CustomMessageDialog
            if self.theme_development_dialog is not None:
                self.theme_development_dialog.deleteLater()
            
            self.theme_development_dialog = CustomMessageDialog(
                "В стадии разработки",
                "Функция переключения тем находится в стадии разработки и будет доступна в следующих обновлениях.",
                "logo64x64.png",
                self.parent_window
            )
        
        self.theme_development_dialog.exec()

    def handle_theme_toggle(self, checked):
        """Обработка переключения темы"""
        self.show_theme_development_message(checked)

    def save_snow_state(self, enabled):
        """Сохранение состояния снегопада"""
        self.snow_enabled = enabled

    def copy_email_to_clipboard(self):
        """Копирование email в буфер обмена с уведомлением"""
        
        clipboard = QApplication.clipboard()
        clipboard.setText("utilhelp@yandex.com")
        
        if hasattr(self, 'copied_fade_animation'):
            self.copied_fade_animation.stop()
        if hasattr(self, 'copy_timer'):
            self.copy_timer.stop()
        
        self.copied_label.setVisible(True)
        self.copied_fade_animation.setStartValue(0.0)
        self.copied_fade_animation.setEndValue(1.0)
        
        try:
            self.copied_fade_animation.finished.disconnect()
        except:
            pass
        
        self.copied_fade_animation.start()
        
        self.copy_timer.start(5000)

    def hide_copied_label(self):
        """Скрытие метки 'Скопировано!' с анимацией исчезновения"""
        if not self.copied_label.isVisible():
            return
            
        if hasattr(self, 'copied_fade_animation'):
            self.copied_fade_animation.stop()
        
        try:
            self.copied_fade_animation.finished.disconnect()
        except:
            pass
        
        self.copied_fade_animation.finished.connect(lambda: self.copied_label.setVisible(False))
        
        self.copied_fade_animation.setStartValue(1.0)
        self.copied_fade_animation.setEndValue(0.0)
        self.copied_fade_animation.start()


class ToggleSwitch(QWidget):
    """Переключатель"""
    toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 20)
        self.checked = False  
        self._position = 4    
        
        self.animation = QPropertyAnimation(self, b"position")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def setChecked(self, checked):
        if self.checked != checked:
            self.checked = checked
            self._position = 24 if self.checked else 4
            self.update()  
    def isChecked(self):
        return self.checked

    def animate_toggle(self):
        if self.animation.state() == QPropertyAnimation.State.Running:
            self.animation.stop()
        
        end_pos = 24 if self.checked else 4
        self.animation.setStartValue(self._position)
        self.animation.setEndValue(end_pos)
        self.animation.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.checked = not self.checked
            self.animate_toggle()
            self.toggled.emit(self.checked)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        bg_color = QColor(102, 102, 102) if self.checked else QColor(64, 64, 64)
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, 40, 20, 10, 10)
        
        slider_color = QColor(255, 255, 255)
        painter.setBrush(QBrush(slider_color))
        painter.setPen(Qt.PenStyle.NoPen)
        shadow_color = QColor(0, 0, 0, 30)
        painter.setBrush(QBrush(shadow_color))
        painter.drawEllipse(int(self._position) + 1, 5, 12, 12)
        painter.setBrush(QBrush(slider_color))
        painter.drawEllipse(int(self._position), 4, 12, 12)

    @pyqtProperty(float)
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value
        self.update()


class DisabledToggleSwitch(ToggleSwitch):
    """Переключатель который не меняет состояние при клике - для функций в разработке"""
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggled.emit(self.checked)  

class SnowWidget(QWidget):
    """Виджет снегопада"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setStyleSheet("background: transparent;")
        
        self.snowflakes = []
        self.init_snowflakes()
        
        self.snow_timer = QTimer()
        self.snow_timer.timeout.connect(self.update_snowflakes)
        self.snow_timer.start(50)  # 20 FPS

    def init_snowflakes(self):
        """Инициализация снежинок"""
        for _ in range(30):  
            x = random.randint(0, max(1280, self.parent().width() if self.parent() else 1280))
            y = random.randint(-720, 0)
            size = random.randint(3, 8)
            speed = random.uniform(1, 2.5)
            self.snowflakes.append(Snowflake(x, y, size, speed))

    def reinit_snowflakes_for_size(self, new_width, new_height):
        """Пересоздать снежинки для нового размера окна"""
        target_count = max(30, min(80, (new_width * new_height) // 25000))
        
        while len(self.snowflakes) < target_count:
            x = random.randint(0, new_width)
            y = random.randint(-new_height, new_height)
            size = random.randint(3, 8)
            speed = random.uniform(1, 2.5)
            self.snowflakes.append(Snowflake(x, y, size, speed))
        
        while len(self.snowflakes) > target_count:
            self.snowflakes.pop()
        
        for snowflake in self.snowflakes:
            if snowflake.x > new_width:
                snowflake.x = random.randint(0, new_width)
            if snowflake.y > new_height:
                snowflake.y = random.randint(-new_height, 0)

    def update_snowflakes(self):
        """Обновление позиций снежинок"""
        window_width = self.parent().width() if self.parent() else self.width()
        window_height = self.parent().height() if self.parent() else self.height()
        
        for snowflake in self.snowflakes:
            snowflake.y += snowflake.speed
            snowflake.x += snowflake.drift
            
            if snowflake.y > window_height:
                snowflake.y = random.randint(-50, -10)
                snowflake.x = random.randint(0, window_width)
                snowflake.size = random.randint(3, 8)
                snowflake.speed = random.uniform(1, 2.5)
                snowflake.drift = random.uniform(-0.8, 0.8)
                snowflake.opacity = random.uniform(0.4, 0.9)
            
            if snowflake.x < -20:
                snowflake.x = window_width + 10
            elif snowflake.x > window_width + 20:
                snowflake.x = -10
        
        self.update()

    def paintEvent(self, event):
        """Отрисовка снежинок"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        for snowflake in self.snowflakes:
            color = QColor(255, 255, 255, int(snowflake.opacity * 128))
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color, 1))
            
            x, y, size = int(snowflake.x), int(snowflake.y), snowflake.size
            
            painter.drawEllipse(x - size//2, y - size//2, size, size)
            
            painter.setPen(QPen(color, 2))
            painter.drawLine(x - size, y, x + size, y)  
            painter.drawLine(x, y - size, x, y + size)  
            painter.drawLine(x - size//2, y - size//2, x + size//2, y + size//2)  
            painter.drawLine(x - size//2, y + size//2, x + size//2, y - size//2)  


class Snowflake:
    """Класс снежинки"""
    def __init__(self, x, y, size, speed):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.drift = random.uniform(-0.5, 0.5)  
        self.opacity = random.uniform(0.3, 0.8)  

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
        
        # Инициализация менеджера настроек и миграция из старой базы
        from settings_manager import settings_manager
        settings_manager.migrate_from_db()
        
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.central_widget = QWidget()  
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet("""
            background-color: #1a1a1a;
            border-radius: 12px;
        """)
        
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(3, 3, 3, 3)
        main_layout.setSpacing(0)
        
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
        self.settings_button.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                border: none;
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                border-radius: 4px;
                margin: 2px;
                text-align: center;
                padding: 0px;
                line-height: 26px;
                outline: none;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #555555;
            }
            QPushButton:focus {
                outline: none;
                border: none;
            }
        """)
        right_layout.addWidget(self.settings_button)
        
        title_bar_layout.addWidget(right_container)
        
        minimize_button = QPushButton()
        minimize_button.setFixedSize(30, 25)  
        minimize_button.clicked.connect(self.showMinimized)
        
        from resource_path import get_icon_path
        minimize_icon_path = get_icon_path("minimizemenu.png")
        if minimize_icon_path:
            minimize_button.setIcon(QIcon(minimize_icon_path))
            minimize_button.setIconSize(QSize(16, 16))
            minimize_button.setFlat(True)  
        else:
            minimize_button.setText("—")  
        minimize_button.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                border: none;
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                border-radius: 4px;
                margin: 2px;
                text-align: center;
                padding: 0px;
                line-height: 26px;
                outline: none;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #555555;
            }
            QPushButton:focus {
                outline: none;
                border: none;
            }
        """)
        right_layout.addWidget(minimize_button)
        
        self.maximize_button = QPushButton()
        self.maximize_button.setFixedSize(30, 25)  
        self.maximize_button.clicked.connect(self.toggle_maximize)
        
        unwrap_icon_path = get_icon_path("unwrapmenu.png")
        if unwrap_icon_path:
            self.maximize_button.setIcon(QIcon(unwrap_icon_path))
            self.maximize_button.setIconSize(QSize(16, 16))
            self.maximize_button.setFlat(True)  
        else:
            self.maximize_button.setText("☐")  
        self.maximize_button.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                border: none;
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                border-radius: 4px;
                margin: 2px;
                text-align: center;
                padding: 0px;
                line-height: 26px;
                outline: none;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #555555;
            }
            QPushButton:focus {
                outline: none;
                border: none;
            }
        """)
        right_layout.addWidget(self.maximize_button)
        
        close_button = QPushButton()
        close_button.setFixedSize(30, 25)  
        close_button.clicked.connect(self.close)
        
        # Загружаем иконку закрытия
        close_icon_path = get_icon_path("closemenu.png")
        if close_icon_path:
            close_button.setIcon(QIcon(close_icon_path))
            close_button.setFlat(True)  
        else:
            close_button.setText("✕")  
        
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                border: none;
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                border-radius: 4px;
                margin: 2px;
                text-align: center;
                padding: 0px;
                line-height: 26px;
                outline: none;
                qproperty-flat: true;
            }
            QPushButton:hover {
                background-color: #e74c3c;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #c0392b;
            }
            QPushButton:focus {
                outline: none;
                border: none;
        """)
        right_layout.addWidget(close_button)
        
        main_layout.addWidget(self.title_bar)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #1a1a1a;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
            QTabBar {
                margin-left: -2px;
            }
            QTabBar::tab:first {
                margin-left: 0px;
            }
            QTabBar::tab {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #404040, stop: 1 #2d2d2d);
                color: #cccccc;
                padding: 15px 30px;
                margin: 3px 2px 3px 2px;
                border-radius: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
                border: 2px solid #555555;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #555555, stop: 1 #404040);
                color: #ffffff;
                border: 2px solid #666666;
            }
            QTabBar::tab:hover:!selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #4a4a4a, stop: 1 #353535);
                color: #ffffff;
                border: 2px solid #5a5a5a;
            }
            QTabBar::tab:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #353535, stop: 1 #2a2a2a);
            }
        """)
        
        self.news_tab = NewsTab()
        self.tab_widget.addTab(self.news_tab, "НОВОСТИ")
        
        self.programs_tab = ProgramsTab()
        self.tab_widget.addTab(self.programs_tab, "ПРОГРАММЫ")
        
        self.drivers_tab = DriversTab()
        self.tab_widget.addTab(self.drivers_tab, "ДРАЙВЕРЫ")
        
        self.data_loaded = False
        self.loading_widget = None
        
        self.downloads_tab = DownloadsTab()
        self.tab_widget.addTab(self.downloads_tab, "БИБЛИОТЕКА")
        
        self.settings_tab = SettingsTab(self)
        self.settings_tab_index = self.tab_widget.addTab(self.settings_tab, "НАСТРОЙКИ")
        self.tab_widget.tabBar().setTabVisible(self.settings_tab_index, False)
        

        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        self.tab_widget.mousePressEvent = self.tab_widget_mouse_press_event
        
        main_layout.addWidget(self.tab_widget)
        
        self.status_bar = QFrame()
        self.status_bar.setFixedHeight(25) 
        self.status_bar.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
            }
        """)
        
        status_layout = QHBoxLayout(self.status_bar)
        status_layout.setContentsMargins(15, 0, 8, 0)
        
        version_text = self.get_app_version()
        version_label = QLabel(f"Версия UTILHELP: {version_text}")
        version_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 10px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        status_layout.addWidget(version_label)
        status_layout.addStretch()
        
        self.downloads_button = QPushButton()
        pixmap = self.load_icon_pixmap("button download.png")
        if pixmap and not pixmap.isNull():
            icon = QIcon(pixmap)
            self.downloads_button.setIcon(icon)
            self.downloads_button.setIconSize(QSize(16, 16))
            self.downloads_button.setText(" Загрузки")  
        else:
            self.downloads_button.setText("↓ Загрузки")
        
        self.downloads_button.setFixedHeight(20)  
        self.downloads_button.clicked.connect(self.toggle_downloads_panel)
        self.downloads_button.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                font-size: 12px;
                font-weight: normal;
                padding: 2px 8px;
                margin-right: 0px;
                margin-top: 1px;
                outline: none;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #353535;
            }
            QPushButton:focus {
                outline: none;
                border: none;
            }
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
        
        QTimer.singleShot(3000, self.check_for_updates_on_startup)
    
    def check_for_updates_on_startup(self):
        """Автоматическая проверка обновлений при запуске программы"""
        try:
            from update_checker import get_update_manager
            
            update_manager = get_update_manager(self)
            
            update_info = update_manager.check_for_updates_silent()
            
            if 'error' in update_info:
                try:
                    from temp_manager import debug_log
                    debug_log(f"Auto-update check error: {update_info['error']}")
                except:
                    pass
                return
            
            if update_info.get('update_available'):
                update_manager.show_update_dialog(update_info)
                
        except Exception as e:
            try:
                from temp_manager import debug_log
                debug_log(f"Auto-update check failed: {e}")
            except:
                pass

    def load_icon_pixmap(self, icon_name, size=None):
        """Загрузить иконку с правильным путем для exe"""
        icon_path = get_icon_path(icon_name)
        
        if icon_path:
            pixmap = QPixmap(icon_path)
            
            if not pixmap.isNull() and size:
                scaled = pixmap.scaled(size[0], size[1], Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                return scaled
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
        unwrap_icon_path = get_icon_path("unwrapmenu.png")
        if unwrap_icon_path:
            self.maximize_button.setIcon(QIcon(unwrap_icon_path))
        else:
            self.maximize_button.setText("☐")
        self.is_maximized = True
        self.maximize_button.setEnabled(True)
        self.update_window_style(True)  
        self.update_snow_widget_size()

    def on_normal_animation_finished(self):
        """Завершение анимации сворачивания"""
        self.setFixedSize(self.normal_size[0], self.normal_size[1])
        unwrap_icon_path = get_icon_path("unwrapmenu.png")
        if unwrap_icon_path:
            self.maximize_button.setIcon(QIcon(unwrap_icon_path))
        else:
            self.maximize_button.setText("☐")
        self.is_maximized = False
        self.maximize_button.setEnabled(True)
        self.update_window_style(False)  
        self.update_snow_widget_size()

    def update_window_style(self, is_maximized):
        """Обновить стиль окна"""
        if is_maximized:
            self.central_widget.setStyleSheet("""
                background-color: #1a1a1a;
                border-radius: 0px;
            """)
            self.title_bar.setStyleSheet("""
                QFrame {
                    background-color: #2d2d2d;
                    border-radius: 10px;
                }
            """)
            self.status_bar.setStyleSheet("""
                QFrame {
                    background-color: #2d2d2d;
                    border-radius: 10px;
                }
            """)
        else:
            self.central_widget.setStyleSheet("""
                background-color: #1a1a1a;
                border-radius: 12px;
            """)
            self.title_bar.setStyleSheet("""
                QFrame {
                    background-color: #2d2d2d;
                    border-radius: 10px;
                }
            """)
            self.status_bar.setStyleSheet("""
                QFrame {
                    background-color: #2d2d2d;
                    border-radius: 10px;
                }
            """)

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
        self.show_opacity_animation.setDuration(400)
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
        self.hide_opacity_animation.setDuration(400)
        self.hide_opacity_animation.setStartValue(1.0)
        self.hide_opacity_animation.setEndValue(0.0)
        self.hide_opacity_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.hide_opacity_animation.finished.connect(self.downloads_panel.hide)
        self.hide_opacity_animation.start()

    def create_downloads_panel(self):
        """Создание панели загрузок"""
        self.downloads_panel = QWidget(self)
        self.downloads_panel.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border: 2px solid #555555;
                border-radius: 15px;
            }
        """)
        
        layout = QVBoxLayout(self.downloads_panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Загрузки")
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        clear_btn = QPushButton("Очистить")
        clear_btn.setFixedSize(80, 25)
        clear_btn.clicked.connect(self.clear_downloads_history)
        
        from resource_path import get_icon_path
        from PyQt6.QtGui import QIcon
        from PyQt6.QtCore import QSize
        
        delete_icon_path = get_icon_path("delete.png")
        if delete_icon_path:
            delete_icon = QIcon(delete_icon_path)
            clear_btn.setIcon(delete_icon)
            clear_btn.setIconSize(QSize(12, 12))
        
        clear_btn.setStyleSheet("""
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
        header_layout.addWidget(clear_btn)
        
        layout.addLayout(header_layout)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        configure_scroll_area(scroll_area)
        
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 16px;
                margin: 0px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 8px;
                min-height: 30px;
                margin: 2px;
                border: none;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666666;
            }
            QScrollBar::handle:vertical:pressed {
                background-color: #777777;
            }
            QScrollBar::add-line:vertical {
                height: 0px;
                width: 0px;
                border: none;
                background: transparent;
            }
            QScrollBar::sub-line:vertical {
                height: 0px;
                width: 0px;
                border: none;
                background: transparent;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                width: 0px;
                height: 0px;
                background: transparent;
            }
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
            return 'v1.0'

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
        
        print(f"✓ Данные переданы в интерфейс")
        
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
        
        print(f"✗ Ошибка загрузки данных: {error}")
    
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
            print("Запуск автоматического сканирования системы...")
            
            programs_data = getattr(self.programs_tab, 'all_programs', [])
            drivers_data = getattr(self.drivers_tab, 'all_drivers', [])
            
            if programs_data or drivers_data:
                from system_scanner import BackgroundScanner
                self.background_scanner = BackgroundScanner(programs_data, drivers_data)
                self.background_scanner.scan_completed.connect(self.on_background_scan_completed)
                self.background_scanner.start()
    
    def on_background_scan_completed(self, programs_status, drivers_status, summary):
        """Обработка завершения фонового сканирования"""
        print(f"Автосканирование завершено: программ {summary['programs_found']}, драйверов {summary['drivers_found']}")
        
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
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #353535, stop: 1 #2a2a2a);
                border: none;
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
            print(f"Ошибка в start_download: {e}")
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
            print(f"RuntimeError в update_progress: {e}")

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