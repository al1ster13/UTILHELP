"""
Полная версия SettingsTab - точная копия оригинала
"""
from typing import Optional, Any
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QFrame, QMessageBox, QApplication, QScrollArea, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QClipboard, QPixmap
from resource_path import get_icon_path
from temp_manager import get_temp_manager
from logger import log_info, log_error
from ui.base.base_widget import BaseWidget
from .toggle_switch import ToggleSwitch, DisabledToggleSwitch
from localization import t


class SettingsTab(BaseWidget):
    """Вкладка настроек с боковой панелью - точная копия оригинала"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.parent_window = parent
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 3, 0, 3)
        main_layout.setSpacing(0)

        from theme_manager import theme_manager
        c = theme_manager.colors
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {c['bg_main']};
                border-radius: 10px;
            }}
        """)

        from settings_manager import settings_manager
        self.snow_enabled = settings_manager.get_setting("snow_enabled", False)
        self.theme_light = theme_manager.is_light()
        self.snow_toggle = None
        self.theme_toggle = None

        self.create_sidebar(main_layout)
        self.create_content_area(main_layout)
        self.show_interface_settings()

    def load_icon_pixmap(self, icon_name: str, size=None) -> QPixmap:
        """Загрузить иконку с правильным путем для exe"""
        from theme_manager import theme_manager, colorize_pixmap

        icon_path = get_icon_path(icon_name)

        if icon_path:
            pixmap = QPixmap(icon_path)

            if not pixmap.isNull() and size:
                pixmap = pixmap.scaled(size[0], size[1], Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

            if not pixmap.isNull() and theme_manager.is_light():
                pixmap = colorize_pixmap(pixmap, theme_manager.colors['text_secondary'])

            return pixmap

        return QPixmap()

    def create_icon_label(self, icon_name: str, size=(24, 24), fallback_text="•") -> QLabel:
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

    def create_sidebar(self, main_layout: QHBoxLayout) -> None:
        """Создание боковой панели с кнопками"""
        from theme_manager import theme_manager
        c = theme_manager.colors

        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet(f"""
            QWidget {{
                background-color: {c['bg_sidebar']};
                border-top-left-radius: 10px;
                border-bottom-left-radius: 10px;
            }}
        """)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 15, 0, 15)
        sidebar_layout.setSpacing(5)

        self.title_label = QLabel(t("settings.title"))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0px 0px 15px 0px;
                letter-spacing: 1px;
            }}
        """)
        sidebar_layout.addWidget(self.title_label)
        
        self.interface_btn = self.create_menu_button("interface.png", t("settings.interface"), True)
        self.interface_btn.clicked.connect(self.show_interface_settings)
        sidebar_layout.addWidget(self.interface_btn)
        
        self.temp_files_btn = self.create_menu_button("tempfile.png", t("settings.files"))
        self.temp_files_btn.clicked.connect(self.show_temp_files_settings)
        sidebar_layout.addWidget(self.temp_files_btn)
        
        self.updates_btn = self.create_menu_button("updatetab.png", t("settings.updates"))
        self.updates_btn.clicked.connect(self.show_updates_settings)
        sidebar_layout.addWidget(self.updates_btn)
        
        self.about_btn = self.create_menu_button("info.png", t("settings.about"))
        self.about_btn.clicked.connect(self.show_about_settings)
        sidebar_layout.addWidget(self.about_btn)
        
        self.contacts_btn = self.create_menu_button("contacts.png", t("settings.contacts"))
        self.contacts_btn.clicked.connect(self.show_contacts_settings)
        sidebar_layout.addWidget(self.contacts_btn)
        
        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)

    def create_menu_button(self, icon_name: str, text: str, active: bool = False) -> QPushButton:
        """Создание кнопки меню"""
        btn = QPushButton()
        btn.setProperty("icon_name", icon_name)  # Сохраняем имя иконки для перезагрузки
        
        pixmap = self.load_icon_pixmap(icon_name)
        if pixmap and not pixmap.isNull():
            from PyQt6.QtGui import QIcon
            from PyQt6.QtCore import QSize
            icon = QIcon(pixmap)
            btn.setIcon(icon)
            btn.setIconSize(QSize(16, 16))
            btn.setText(f"  {text}")
        else:
            btn.setText("•  " + text)
        
        btn.setFixedHeight(50)
        
        if active:
            btn.setStyleSheet(self.get_active_button_style())
        else:
            btn.setStyleSheet(self.get_inactive_button_style())
        
        return btn

    def get_active_button_style(self) -> str:
        """Стиль активной кнопки"""
        from theme_manager import theme_manager
        c = theme_manager.colors
        return f"""
            QPushButton {{
                background-color: {c['bg_input']};
                color: {c['text_primary']};
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: normal;
                font-family: 'Segoe UI', Arial, sans-serif;
                text-align: left;
                padding-left: 20px;
                margin: 2px 10px;
                outline: none;
            }}
            QPushButton:hover {{
                background-color: {c['bg_hover']};
            }}
            QPushButton:focus {{
                outline: none;
                border: none;
            }}
        """

    def get_inactive_button_style(self) -> str:
        """Стиль неактивной кнопки"""
        from theme_manager import theme_manager
        c = theme_manager.colors
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {c['text_secondary']};
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: normal;
                font-family: 'Segoe UI', Arial, sans-serif;
                text-align: left;
                padding-left: 20px;
                margin: 2px 10px;
                outline: none;
            }}
            QPushButton:hover {{
                background-color: {c['bg_hover']};
                color: {c['text_primary']};
            }}
            QPushButton:focus {{
                outline: none;
                border: none;
            }}
        """

    def create_content_area(self, main_layout: QHBoxLayout) -> None:
        """Создание области содержимого с прокруткой"""
    def create_content_area(self, main_layout: QHBoxLayout) -> None:
        """Создание области содержимого с прокруткой"""
        from theme_manager import theme_manager
        c = theme_manager.colors

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {c['bg_main']};
                border: none;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
            }}
            QScrollBar:vertical {{
                background-color: {c['scrollbar_bg']};
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {c['scrollbar_handle']};
                border-radius: 6px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {c['scrollbar_hover']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)

        self.content_area = QWidget()
        self.content_area.setStyleSheet(f"""
            QWidget {{
                background-color: {c['bg_main']};
                border: none;
            }}
        """)
        
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(40, 30, 40, 30)
        self.content_layout.setSpacing(25)
        
        self.scroll_area.setWidget(self.content_area)
        
        main_layout.addWidget(self.scroll_area)

    def clear_content(self) -> None:
        """Очистка содержимого"""
        if hasattr(self, 'cleanup_message'):
            self.cleanup_message = None
            
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def show_interface_settings(self) -> None:
        """Показать настройки интерфейса"""
        self.interface_btn.setStyleSheet(self.get_active_button_style())
        self.temp_files_btn.setStyleSheet(self.get_inactive_button_style())
        self.updates_btn.setStyleSheet(self.get_inactive_button_style())
        self.about_btn.setStyleSheet(self.get_inactive_button_style())
        self.contacts_btn.setStyleSheet(self.get_inactive_button_style())

        self.clear_content()
        self.content_layout.setContentsMargins(40, 30, 40, 30)

        from theme_manager import theme_manager
        c = theme_manager.colors

        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)
        title_layout.setContentsMargins(0, 0, 0, 20)

        icon_label = self.create_icon_label("interface.png", (24, 24))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        icon_label.setContentsMargins(0, 4, 0, 0)
        title_layout.addWidget(icon_label)

        title_text = QLabel(t("settings.interface"))
        title_text.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 24px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
        """)
        title_text.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        title_layout.addWidget(title_text)
        title_layout.addStretch()

        title_container = QWidget()
        title_container.setLayout(title_layout)
        self.content_layout.addWidget(title_container)

        from localization import get_localization
        from ui.components.catalog_combo_box import CatalogComboBox
        from settings_manager import settings_manager
        from logger import log_info

        localization = get_localization()

        self.language_combo = CatalogComboBox()
        self.language_combo.setFixedHeight(40)
        
        # Уменьшаем ширину dropdown для языков  
        self.language_combo.dropdown.setFixedWidth(199)
        # Отключаем скроллбар
        self.language_combo.dropdown.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Добавляем языки в явном порядке
        available_langs = localization.get_available_languages()
        log_info(f"Available languages: {available_langs}")
        
        # Сначала русский, потом английский
        for lang_code in ["ru", "en"]:
            if lang_code in available_langs:
                lang_name = available_langs[lang_code]
                self.language_combo.addItem(lang_name, lang_code)
                log_info(f"Added language: {lang_name} ({lang_code})")
        
        log_info(f"Total items in combo: {len(self.language_combo.items)}")
        log_info(f"Items: {self.language_combo.items}")
        log_info(f"Dropdown item count: {self.language_combo.dropdown.count()}")
        
        # Проверяем каждый элемент в dropdown
        for i in range(self.language_combo.dropdown.count()):
            item = self.language_combo.dropdown.item(i)
            log_info(f"Dropdown item {i}: {item.text() if item else 'None'}")
        
        # Принудительно обновляем dropdown
        self.language_combo.dropdown.update()
        self.language_combo.dropdown.repaint()
        # Прокручиваем к началу списка
        self.language_combo.dropdown.scrollToTop()
        
        # Подключаемся к сигналу нажатия кнопки для изменения высоты dropdown
        def fix_dropdown_height():
            from PyQt6.QtCore import QTimer
            # Увеличиваем высоту чуть больше для комфортного отображения
            # padding 8px*2 + текст ~20px = ~36px на элемент
            # 36px * 2 + padding списка 8px + запас 10px = 90px
            QTimer.singleShot(10, lambda: self.language_combo.dropdown.setFixedHeight(90))
        
        self.language_combo.button.clicked.connect(fix_dropdown_height)
        
        current_lang = settings_manager.get_setting("language", "ru")
        log_info(f"Current language setting: {current_lang}")
        
        for i in range(len(self.language_combo.items)):
            if self.language_combo.items[i][1] == current_lang:
                self.language_combo.setCurrentIndex(i)
                log_info(f"Set current index to: {i}")
                break
        
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        
        language_setting = self.create_setting_item(
            "language.png",
            t("settings.language"),
            t("settings.language_hint"),
            self.language_combo
        )
        self.content_layout.addWidget(language_setting)
        
        # Снегопад
        self.snow_toggle = ToggleSwitch()
        self.snow_toggle.setChecked(self.snow_enabled)
        if self.parent_window:
            self.snow_toggle.toggled.connect(self.parent_window.toggle_snow)
            self.snow_toggle.toggled.connect(self.save_snow_state)
        
        snow_setting = self.create_setting_item(
            "snowflake.png", 
            t("settings.snowfall"), 
            t("settings.snowfall_hint"),
            self.snow_toggle
        )
        self.content_layout.addWidget(snow_setting)
        
        notifications_enabled = settings_manager.get_setting("notifications_enabled", True)
        
        self.notifications_toggle = ToggleSwitch()
        self.notifications_toggle.setChecked(notifications_enabled)
        self.notifications_toggle.toggled.connect(self.save_notifications_state)
        self.notifications_toggle.toggled.connect(self.toggle_notification_sounds_availability)
        
        notifications_setting = self.create_setting_item(
            "notification.png",
            t("notifications.notifications_setting"),
            t("notifications.notifications_hint"),
            self.notifications_toggle
        )
        self.content_layout.addWidget(notifications_setting)
        
        notification_sounds = settings_manager.get_setting("notification_sounds", True)
        
        self.notification_sounds_toggle = ToggleSwitch()
        self.notification_sounds_toggle.setChecked(notification_sounds)
        self.notification_sounds_toggle.toggled.connect(self.save_notification_sounds)
        
        self.sounds_setting = self.create_setting_item(
            "notificationsound.png",
            t("notifications.notification_sounds"),
            t("notifications.notification_sounds_hint"),
            self.notification_sounds_toggle
        )
        self.content_layout.addWidget(self.sounds_setting)
        
        self.toggle_notification_sounds_availability(notifications_enabled)

        # Тема — теперь полностью рабочая
        from theme_manager import theme_manager
        self.theme_light = theme_manager.is_light()

        self.theme_toggle = ToggleSwitch()
        self.theme_toggle.setChecked(self.theme_light)
        self.theme_toggle.toggled.connect(self.save_theme_state)

        self.theme_setting = self.create_setting_item(
            "whitetheme.png",
            t("settings.theme"),
            t("settings.theme_light"),
            self.theme_toggle
        )
        self.content_layout.addWidget(self.theme_setting)

        self.content_layout.addStretch()

    def create_setting_item(self, icon: str, title: str, description: str, control_widget: QWidget) -> QWidget:
        """Создание элемента настройки"""
        from theme_manager import theme_manager
        c = theme_manager.colors

        item = QWidget()
        item.setMinimumHeight(100)
        item.setStyleSheet(f"""
            QWidget {{
                background-color: {c['bg_card']};
                border-radius: 15px;
                border: 1px solid {c['card_border']};
            }}
            QWidget:hover {{
                border: 1px solid {c['border_hover']};
            }}
        """)
        
        item_layout = QHBoxLayout(item)
        item_layout.setContentsMargins(25, 25, 25, 25)  # Увеличены отступы
        item_layout.setSpacing(20)
        
        icon_label = QLabel()
        if icon.endswith('.png'):
            try:
                pixmap = self.load_icon_pixmap(icon, (28, 28))
                if not pixmap.isNull():
                    icon_label.setPixmap(pixmap)
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
        item_layout.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignVCenter)  # Выравнивание по вертикали
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)  # Уменьшен отступ между заголовком и описанием
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                margin-left: 0px;
                padding-left: 0px;
            }}
        """)
        title_label.setTextFormat(Qt.TextFormat.PlainText)

        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_secondary']};
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                line-height: 1.4;
                margin-left: 0px;
                padding-left: 0px;
            }}
        """)
        desc_label.setWordWrap(False)  # Однострочное описание
        desc_label.setTextFormat(Qt.TextFormat.PlainText)
        
        from PyQt6.QtWidgets import QSizePolicy
        title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        desc_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(desc_label)
        
        item_layout.addLayout(text_layout, 1)  # Stretch factor 1 для текста
        item_layout.addStretch()
        item_layout.addWidget(control_widget, 0, Qt.AlignmentFlag.AlignVCenter)  # Выравнивание переключателя
        
        return item

    def show_updates_settings(self) -> None:
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
        
        from theme_manager import theme_manager
        c = theme_manager.colors
        title_text = QLabel(t("settings.updates"))
        title_text.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 24px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
        """)
        title_text.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        
        title_container = QWidget()
        title_container.setLayout(title_layout)
        self.content_layout.addWidget(title_container)
        
        update_widget = self.create_simple_update_widget()
        self.content_layout.addWidget(update_widget)
        
        self.content_layout.addStretch()

    def show_about_settings(self) -> None:
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
        
        from theme_manager import theme_manager
        c = theme_manager.colors
        title_text = QLabel(t("settings.about"))
        title_text.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 24px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
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

    def show_contacts_settings(self) -> None:
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
        
        from theme_manager import theme_manager
        c = theme_manager.colors
        title_text = QLabel(t("settings.contacts"))
        title_text.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 24px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
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

    def show_temp_files_settings(self) -> None:
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
        
        from theme_manager import theme_manager
        c = theme_manager.colors
        title_text = QLabel(t("settings.files"))
        title_text.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 24px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
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

    def create_temp_files_widget(self) -> QWidget:
        """Создание виджета с информацией о временных файлах"""
        from theme_manager import theme_manager
        c = theme_manager.colors

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        temp_manager = get_temp_manager()
        
        info_text = QLabel(f"{t('settings.temp_folder')}\n{temp_manager.get_temp_dir()}")
        info_text.setStyleSheet(f"""
            QLabel {{
                color: {c['text_secondary']};
                font-size: 14px;
                background-color: {c['bg_card']};
                border-radius: 8px;
                padding: 15px;
                border: 1px solid {c['card_border']};
            }}
        """)
        layout.addWidget(info_text)
        
        files_count = len(temp_manager.list_temp_files())
        total_size = temp_manager.get_temp_size()
        formatted_size = temp_manager.format_size(total_size)
        
        self.stats_text = QLabel(t("settings.files_stats", count=files_count, size=formatted_size))
        self.stats_text.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 16px;
                background-color: {c['bg_tertiary']};
                border-radius: 8px;
                padding: 15px;
                border: 1px solid {c['card_border']};
            }}
        """)
        layout.addWidget(self.stats_text)
        
        clear_btn = QPushButton(t("settings.clean_temp"))
        clear_btn.clicked.connect(self.clear_temp_files)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(244, 67, 54, 0.1);
                color: {c['error']};
                border: 1px solid rgba(244, 67, 54, 0.3);
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: rgba(244, 67, 54, 0.2);
                border: 1px solid rgba(244, 67, 54, 0.5);
            }}
            QPushButton:pressed {{
                background-color: rgba(244, 67, 54, 0.3);
                border: 1px solid {c['error']};
            }}
            QPushButton:focus {{
                outline: none;
                border: 1px solid rgba(244, 67, 54, 0.5);
            }}
        """)
        layout.addWidget(clear_btn)
        
        self.cleanup_message = QLabel("")
        self.cleanup_message.setStyleSheet(f"""
            QLabel {{
                color: {c['success']};
                font-size: 14px;
                background-color: {c['bg_card']};
                border-radius: 8px;
                padding: 12px 15px;
                border: 1px solid {c['success']};
                margin-top: 10px;
            }}
        """)
        self.cleanup_message.hide()
        
        layout.addWidget(self.cleanup_message)
        
        return widget
    
    def update_temp_files_stats(self) -> None:
        """Обновить статистику временных файлов без пересоздания всего интерфейса"""
        try:
            temp_manager = get_temp_manager()
            
            files_count = len(temp_manager.list_temp_files())
            total_size = temp_manager.get_temp_size()
            formatted_size = temp_manager.format_size(total_size)
            
            if hasattr(self, 'stats_text') and self.stats_text is not None:
                self.stats_text.setText(t("settings.files_stats", count=files_count, size=formatted_size))
            
            try:
                log_info(f"Stats updated: {files_count} files, {formatted_size}")
            except:
                pass
                
        except Exception as e:
            try:
                log_error(f"Error updating stats: {e}")
            except:
                pass
    
    def clear_temp_files(self) -> None:
        """Очистить временные файлы"""
        from theme_manager import theme_manager
        c = theme_manager.colors
        
        try:
            temp_manager = get_temp_manager()
            cleaned_files = temp_manager.manual_cleanup()
            
            if not hasattr(self, 'cleanup_message') or self.cleanup_message is None:
                return
            
            if cleaned_files:
                if len(cleaned_files) == 1:
                    message = t("settings.temp_deleted_one", name=cleaned_files[0])
                else:
                    message = t("settings.temp_deleted_many", count=len(cleaned_files))
                self.cleanup_message.setStyleSheet(f"""
                    QLabel {{
                        color: {c['success']};
                        font-size: 14px;
                        background-color: {c['bg_card']};
                        border-radius: 8px;
                        padding: 12px 15px;
                        border: 1px solid {c['success']};
                        margin-top: 10px;
                    }}
                """)
            else:
                message = t("settings.temp_not_found")
                self.cleanup_message.setStyleSheet(f"""
                    QLabel {{
                        color: {c['accent']};
                        font-size: 14px;
                        background-color: {c['bg_card']};
                        border-radius: 8px;
                        padding: 12px 15px;
                        border: 1px solid {c['accent']};
                        margin-top: 10px;
                    }}
                """)
            
            self.cleanup_message.setText(message)
            self.cleanup_message.show()
            self.update_temp_files_stats()
            QTimer.singleShot(5000, lambda: self.cleanup_message.hide() if hasattr(self, 'cleanup_message') and self.cleanup_message else None)
            
        except Exception as e:
            if hasattr(self, 'cleanup_message') and self.cleanup_message is not None:
                error_message = t("settings.error_cleanup", error=str(e))
                self.cleanup_message.setText(error_message)
                self.cleanup_message.setStyleSheet(f"""
                    QLabel {{
                        color: {c['error']};
                        font-size: 14px;
                        background-color: {c['bg_card']};
                        border-radius: 8px;
                        padding: 12px 15px;
                        border: 1px solid {c['error']};
                        margin-top: 10px;
                    }}
                """)
                self.cleanup_message.show()
                QTimer.singleShot(7000, lambda: self.cleanup_message.hide() if hasattr(self, 'cleanup_message') and self.cleanup_message else None)

    def save_snow_state(self, enabled: bool) -> None:
        """Сохранение состояния снегопада"""
        self.snow_enabled = enabled
        log_info(f"Snow effect {'enabled' if enabled else 'disabled'}")

    def save_theme_state(self, light_enabled: bool) -> None:
        """Сохранение и применение темы"""
        from theme_manager import theme_manager
        from settings_manager import settings_manager

        theme = "light" if light_enabled else "dark"
        settings_manager.set_setting("theme", theme)
        theme_manager.apply(theme)
        self.theme_light = light_enabled
        log_info(f"Theme changed to: {theme}")

        # Обновляем главное окно
        if self.parent_window and hasattr(self.parent_window, 'apply_theme'):
            self.parent_window.apply_theme()
    
    def on_language_changed(self, index: int) -> None:
        """Обработка смены языка"""
        from localization import get_localization
        from PyQt6.QtWidgets import QMessageBox
        from settings_manager import settings_manager
        
        # Получаем код языка из кастомного комбобокса
        if index < len(self.language_combo.items):
            lang_code = self.language_combo.items[index][1]  # (text, data)
        else:
            return
            
        localization = get_localization()
        
        settings_manager.set_setting("language", lang_code)
        localization.set_language(lang_code)
        
        main_window = self.parent_window or self.window()
        
        try:
            update_method = getattr(main_window, 'update_translations', None)
            
            if update_method and callable(update_method):
                update_method()
            else:
                self._manual_update_translations(main_window, lang_code)
                
        except Exception as e:
            log_error(f"Error updating translations: {e}")
            if lang_code == "ru":
                QMessageBox.information(
                    self,
                    "Язык изменен",
                    "Перезапустите программу для применения изменений."
                )
            else:
                QMessageBox.information(
                    self,
                    "Language Changed",
                    "Please restart the application to apply changes."
                )
    
    def _manual_update_translations(self, main_window, lang_code):
        """Ручное обновление переводов если метод update_translations не найден"""
        try:
            if hasattr(main_window, 'tab_widget'):
                main_window.tab_widget.setTabText(0, t("tabs.news"))
                main_window.tab_widget.setTabText(1, t("tabs.programs"))
                main_window.tab_widget.setTabText(2, t("tabs.drivers"))
                main_window.tab_widget.setTabText(3, t("tabs.library"))
                main_window.tab_widget.setTabText(4, t("tabs.settings"))
            
            if hasattr(self, 'title_label'):
                self.title_label.setText(t("settings.title"))
            
            if hasattr(self, 'interface_btn'):
                # Получаем иконку из кнопки и обновляем текст
                icon = self.interface_btn.icon()
                if not icon.isNull():
                    self.interface_btn.setText(f"  {t('settings.interface')}")
                else:
                    self.interface_btn.setText("•  " + t("settings.interface"))
            
            if hasattr(self, 'temp_files_btn'):
                icon = self.temp_files_btn.icon()
                if not icon.isNull():
                    self.temp_files_btn.setText(f"  {t('settings.files')}")
                else:
                    self.temp_files_btn.setText("•  " + t("settings.files"))
            
            if hasattr(self, 'updates_btn'):
                icon = self.updates_btn.icon()
                if not icon.isNull():
                    self.updates_btn.setText(f"  {t('settings.updates')}")
                else:
                    self.updates_btn.setText("•  " + t("settings.updates"))
            
            if hasattr(self, 'about_btn'):
                icon = self.about_btn.icon()
                if not icon.isNull():
                    self.about_btn.setText(f"  {t('settings.about')}")
                else:
                    self.about_btn.setText("•  " + t("settings.about"))
            
            if hasattr(self, 'contacts_btn'):
                icon = self.contacts_btn.icon()
                if not icon.isNull():
                    self.contacts_btn.setText(f"  {t('settings.contacts')}")
                else:
                    self.contacts_btn.setText("•  " + t("settings.contacts"))
            
            if hasattr(main_window, 'downloads_button'):
                main_window.downloads_button.setText(t("main_window.downloads_button"))
            
            if hasattr(main_window, 'version_label'):
                try:
                    from resource_path import resource_path
                    with open(resource_path('version.txt'), 'r', encoding='utf-8') as f:
                        version = f.read().strip()
                    main_window.version_label.setText(t("app.version", version=version))
                except:
                    pass
            
            # Перезагружаем вкладки с обновлением переводов
            if hasattr(main_window, 'news_tab') and main_window.news_tab:
                if hasattr(main_window.news_tab, 'update_translations'):
                    main_window.news_tab.update_translations()
                else:
                    main_window.news_tab.load_news_from_data()
            
            if hasattr(main_window, 'programs_tab') and main_window.programs_tab:
                if hasattr(main_window.programs_tab, 'update_translations'):
                    main_window.programs_tab.update_translations()
                else:
                    main_window.programs_tab.display_programs()
            
            if hasattr(main_window, 'drivers_tab') and main_window.drivers_tab:
                if hasattr(main_window.drivers_tab, 'update_translations'):
                    main_window.drivers_tab.update_translations()
                else:
                    main_window.drivers_tab.display_drivers()
            
            if hasattr(main_window, 'downloads_tab') and main_window.downloads_tab:
                if hasattr(main_window.downloads_tab, 'update_translations'):
                    main_window.downloads_tab.update_translations()
                else:
                    main_window.downloads_tab.load_downloads()
            
            # Перезагружаем текущий раздел настроек
            self.show_interface_settings()
            
            log_info("Translations updated manually")
            
        except Exception as e:
            log_error(f"Error in manual update: {e}")
            import traceback
            traceback.print_exc()
            raise

    def save_notifications_state(self, enabled: bool) -> None:
        """Сохранение состояния уведомлений"""
        from settings_manager import settings_manager
        
        settings_manager.set_setting("notifications_enabled", enabled)
        log_info(f"Notifications {'enabled' if enabled else 'disabled'}")
    
    def save_notification_sounds(self, enabled: bool) -> None:
        """Сохранение настройки звуков уведомлений"""
        from settings_manager import settings_manager
        
        settings_manager.set_setting("notification_sounds", enabled)
        
        log_info(f"Notification sounds {'enabled' if enabled else 'disabled'}")
    
    def toggle_notification_sounds_availability(self, notifications_enabled: bool) -> None:
        """Включение/отключение доступности настройки звуков уведомлений"""
        from theme_manager import theme_manager
        c = theme_manager.colors

        if hasattr(self, 'notification_sounds_toggle') and hasattr(self, 'sounds_setting'):
            self.notification_sounds_toggle.setEnabled(notifications_enabled)
            
            if notifications_enabled:
                self.sounds_setting.setStyleSheet(f"""
                    QWidget {{
                        background-color: {c['bg_card']};
                        border-radius: 15px;
                        border: 1px solid {c['card_border']};
                    }}
                    QWidget:hover {{
                        border: 1px solid {c['border_hover']};
                    }}
                """)
                self.sounds_setting.setGraphicsEffect(None)
            else:
                self.sounds_setting.setStyleSheet(f"""
                    QWidget {{
                        background-color: {c['bg_tertiary']};
                        border-radius: 15px;
                        border: 1px solid {c['border_light']};
                    }}
                """)
                from PyQt6.QtWidgets import QGraphicsOpacityEffect
                opacity_effect = QGraphicsOpacityEffect()
                opacity_effect.setOpacity(0.4)
                self.sounds_setting.setGraphicsEffect(opacity_effect)
            
            log_info(f"Notification sounds setting {'enabled' if notifications_enabled else 'disabled'}")

    def set_parent_window(self, parent_window: Any) -> None:
        """Установка ссылки на главное окно"""
        self.parent_window = parent_window

    def copy_email_to_clipboard(self) -> None:
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

    def hide_copied_label(self) -> None:
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
    def create_info_widget(self) -> QWidget:
        """Создание виджета с информацией о программе"""
        from theme_manager import theme_manager
        c = theme_manager.colors

        info_widget = QWidget()
        info_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {c['bg_card']};
                border-radius: 15px;
                border: 1px solid {c['card_border']};
                padding: 10px;
            }}
        """)
        
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(30, 25, 30, 25)
        info_layout.setSpacing(20)
        
        header_layout = QHBoxLayout()
        
        logo_label = QLabel()
        pixmap = self.load_icon_pixmap("infologo.png", (48, 48))
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap)
            logo_label.setStyleSheet("QLabel { background: transparent; }")
        else:
            logo_label.setText("•")
            logo_label.setStyleSheet("QLabel { font-size: 48px; background: transparent; }")
        
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setMinimumSize(48, 48)
        
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        
        app_title = QLabel("UTILHELP")
        app_title.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 28px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                margin-left: -5px;
            }}
        """)
        
        version_label = QLabel(t("settings.version_label", version=self.get_app_version()))
        version_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_secondary']};
                font-size: 16px;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
            }}
        """)
        
        title_layout.addWidget(app_title)
        title_layout.addWidget(version_label)
        
        header_layout.addWidget(logo_label)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        info_layout.addLayout(header_layout)
        
        description = QLabel(t("settings.description_full"))
        description.setStyleSheet(f"""
            QLabel {{
                color: {c['text_secondary']};
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                line-height: 1.6;
            }}
        """)
        description.setWordWrap(True)
        info_layout.addWidget(description)
        
        copyright_label = QLabel('© 2025-2026 UTILHELP. Icons by <a href="https://icons8.com" style="color: #888888; text-decoration: underline;">Icons8</a>')
        copyright_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_disabled']};
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                margin-top: 10px;
            }}
        """)
        copyright_label.setOpenExternalLinks(True)
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        info_layout.addWidget(copyright_label)
        
        return info_widget

    def create_update_data_button(self) -> QWidget:
        """Создание кнопки обновления данных с GitHub"""
        from theme_manager import theme_manager
        c = theme_manager.colors

        update_widget = QWidget()
        update_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {c['bg_card']};
                border-radius: 12px;
                border: 1px solid {c['card_border']};
            }}
        """)
        
        update_layout = QHBoxLayout(update_widget)
        update_layout.setContentsMargins(20, 20, 20, 20)
        update_layout.setSpacing(15)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        
        title_label = QLabel(t("settings.update_data"))
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 16px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
            }}
        """)
        text_layout.addWidget(title_label)
        
        desc_label = QLabel(t("settings.update_data_desc"))
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_hint']};
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                line-height: 1.4;
            }}
        """)
        text_layout.addWidget(desc_label)
        
        update_layout.addLayout(text_layout)
        update_layout.addStretch()
        
        update_btn = QPushButton(t("settings.check_button"))
        update_btn.setFixedSize(120, 36)
        update_btn.clicked.connect(self.force_data_update)
        
        update_icon_path = get_icon_path("update.png")
        if update_icon_path:
            from PyQt6.QtGui import QIcon
            from PyQt6.QtCore import QSize
            update_icon = QIcon(update_icon_path)
            update_btn.setIcon(update_icon)
            update_btn.setIconSize(QSize(16, 16))
        
        update_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['bg_button']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {c['bg_hover']};
                border: 1px solid {c['border_hover']};
            }}
            QPushButton:pressed {{
                background-color: {c['bg_pressed']};
            }}
            QPushButton:disabled {{
                background-color: {c['bg_tertiary']};
                color: {c['text_disabled']};
                border: 1px solid {c['border_light']};
            }}
        """)
        
        update_layout.addWidget(update_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        
        bottom_layout = QVBoxLayout()
        bottom_layout.setContentsMargins(0, 12, 0, 0)
        
        self.last_update_label = QLabel()
        self.update_last_update_time()
        self.last_update_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_hint']};
                font-size: 11px;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                padding-top: 5px;
                margin-left: -2px;
            }}
        """)
        bottom_layout.addWidget(self.last_update_label)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addLayout(update_layout)
        main_layout.addLayout(bottom_layout)
        
        update_widget.setLayout(main_layout)
        
        return update_widget

    def create_simple_update_widget(self) -> QWidget:
        """Создание простого виджета обновлений"""
        from theme_manager import theme_manager
        c = theme_manager.colors

        update_widget = QWidget()
        update_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {c['bg_card']};
                border-radius: 15px;
                border: 1px solid {c['card_border']};
                padding: 10px;
            }}
        """)
        
        layout = QVBoxLayout(update_widget)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)
        
        top_layout = QHBoxLayout()
        top_layout.setSpacing(20)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        
        title_label = QLabel(t("settings.update_program"))
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                margin-left: -2px;
            }}
        """)
        text_layout.addWidget(title_label)
        
        desc_label = QLabel(t("settings.update_program_desc"))
        desc_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_hint']};
                font-size: 13px;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                margin-left: 1px;
            }}
        """)
        text_layout.addWidget(desc_label)
        
        top_layout.addLayout(text_layout)
        top_layout.addStretch()
        
        button_container = QWidget()
        button_container.setFixedHeight(60)
        button_container.setStyleSheet("QWidget { background: transparent; }")
        button_container_layout = QVBoxLayout(button_container)
        button_container_layout.setContentsMargins(0, 0, 0, 0)
        
        check_button = QPushButton(t("settings.check_button"))
        check_button.setFixedSize(120, 36)
        check_button.clicked.connect(self.check_program_updates)
        
        update_icon_path = get_icon_path("update.png")
        if update_icon_path:
            from PyQt6.QtGui import QIcon
            from PyQt6.QtCore import QSize
            update_icon = QIcon(update_icon_path)
            check_button.setIcon(update_icon)
            check_button.setIconSize(QSize(16, 16))
        
        check_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['bg_button']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {c['bg_hover']};
                border: 1px solid {c['border_hover']};
            }}
            QPushButton:pressed {{
                background-color: {c['bg_pressed']};
            }}
        """)
        
        button_container_layout.addStretch()
        button_container_layout.addWidget(check_button, 0, Qt.AlignmentFlag.AlignCenter)
        button_container_layout.addStretch()
        
        top_layout.addWidget(button_container)
        layout.addLayout(top_layout)
        
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"background-color: {c['border']};")
        layout.addWidget(separator)
        
        info_title = QLabel(t("settings.update_info_title"))
        info_title.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(info_title)
        
        info_text = QLabel(t("settings.update_info_text"))
        info_text.setWordWrap(True)
        info_text.setStyleSheet(f"""
            QLabel {{
                color: {c['text_secondary']};
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                line-height: 1.5;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(info_text)
        
        security_info = QLabel(t("settings.update_security"))
        security_info.setWordWrap(True)
        security_info.setStyleSheet(f"""
            QLabel {{
                color: {c['text_hint']};
                font-size: 11px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-style: italic;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(security_info)
        
        return update_widget

    def create_contacts_widget(self) -> QWidget:
        """Создание виджета с контактной информацией"""
        from theme_manager import theme_manager
        c = theme_manager.colors

        contacts_widget = QWidget()
        contacts_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {c['bg_card']};
                border-radius: 15px;
                border: 1px solid {c['card_border']};
                padding: 10px;
            }}
        """)
        
        contacts_layout = QVBoxLayout(contacts_widget)
        contacts_layout.setContentsMargins(20, 15, 20, 15)
        contacts_layout.setSpacing(10)
        
        header_label = QLabel(t("settings.contact_developer"))
        header_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                margin-bottom: 5px;
            }}
        """)
        contacts_layout.addWidget(header_label)
        
        link_label_style = f"""
            QLabel {{
                color: {c['accent']};
                font-size: 13px;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
            }}
        """
        caption_style = f"""
            QLabel {{
                color: {c['text_secondary']};
                font-size: 13px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                min-width: 80px;
            }}
        """
        icon_style = "background: transparent; border: none; margin-top: 1px;"

        # GitHub
        github_layout = QHBoxLayout()
        github_layout.setSpacing(8)
        github_icon = QLabel()
        pixmap = self.load_icon_pixmap("github.png", (16, 16))
        if not pixmap.isNull():
            github_icon.setPixmap(pixmap)
        else:
            github_icon.setText("•")
        github_icon.setStyleSheet(icon_style)
        github_label = QLabel("GitHub:")
        github_label.setStyleSheet(caption_style)
        github_link = QLabel('<a href="https://github.com/al1ster13/UTILHELP" style="color: ' + c['accent'] + '; text-decoration: none;">https://github.com/al1ster13/UTILHELP</a>')
        github_link.setStyleSheet(link_label_style)
        github_link.setOpenExternalLinks(True)
        github_layout.addWidget(github_icon)
        github_layout.addWidget(github_label)
        github_layout.addWidget(github_link)
        github_layout.addStretch()
        contacts_layout.addLayout(github_layout)
        
        # Email
        email_layout = QHBoxLayout()
        email_layout.setSpacing(8)
        email_icon = QLabel()
        pixmap = self.load_icon_pixmap("email.png", (16, 16))
        if not pixmap.isNull():
            email_icon.setPixmap(pixmap)
        else:
            email_icon.setText("•")
        email_icon.setStyleSheet(icon_style)
        email_label = QLabel("Email:")
        email_label.setStyleSheet(caption_style)
        email_link = QLabel('utilhelp@yandex.com')
        email_link.setStyleSheet(f"""
            QLabel {{
                color: {c['accent']};
                font-size: 13px;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
            }}
            QLabel:hover {{ text-decoration: underline; }}
        """)
        email_link.mousePressEvent = lambda event: self.copy_email_to_clipboard()
        
        self.copied_label = QLabel("Скопировано!")
        self.copied_label.setStyleSheet(f"""
            QLabel {{
                color: {c['success']};
                font-size: 12px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                margin-left: 10px;
            }}
        """)
        self.copied_label.setVisible(False)
        
        self.copied_opacity_effect = QGraphicsOpacityEffect()
        self.copied_opacity_effect.setOpacity(0.0)
        self.copied_label.setGraphicsEffect(self.copied_opacity_effect)
        
        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QTimer
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
        
        # Telegram
        telegram_layout = QHBoxLayout()
        telegram_layout.setSpacing(8)
        telegram_icon = QLabel()
        pixmap = self.load_icon_pixmap("telegram.png", (16, 16))
        if not pixmap.isNull():
            telegram_icon.setPixmap(pixmap)
        else:
            telegram_icon.setText("•")
        telegram_icon.setStyleSheet(icon_style)
        telegram_label = QLabel("Telegram:")
        telegram_label.setStyleSheet(caption_style)
        telegram_link = QLabel('<a href="https://t.me/UTILHELP" style="color: ' + c['accent'] + '; text-decoration: none;">https://t.me/UTILHELP</a>')
        telegram_link.setStyleSheet(link_label_style)
        telegram_link.setOpenExternalLinks(True)
        telegram_layout.addWidget(telegram_icon)
        telegram_layout.addWidget(telegram_label)
        telegram_layout.addWidget(telegram_link)
        telegram_layout.addStretch()
        contacts_layout.addLayout(telegram_layout)
        
        info_text = QLabel(t("settings.contact_info"))
        info_text.setStyleSheet(f"""
            QLabel {{
                color: {c['text_secondary']};
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                line-height: 1.4;
            }}
        """)
        info_text.setWordWrap(True)
        contacts_layout.addWidget(info_text)
        
        return contacts_widget

    def get_app_version(self) -> str:
        """Получение версии приложения"""
        try:
            with open('version.txt', 'r', encoding='utf-8') as f:
                return f'v{f.read().strip()}'
        except:
            return 'v1.0.1'

    def check_program_updates(self) -> None:
        """Проверить обновления программы"""
        try:
            from update_checker import get_update_manager
            
            update_manager = get_update_manager(self.parent_window if hasattr(self, 'parent_window') else self)
            
            update_manager.check_for_updates_interactive()
            
        except Exception as e:
            QMessageBox.critical(
                self.parent_window if hasattr(self, 'parent_window') else self,
                t("settings.error_title"),
                t("settings.error_check_updates", error=str(e))
            )
    
    def update_last_update_time(self) -> None:
        """Обновляет текст с временем последнего обновления"""
        import os
        from datetime import datetime
        
        cache_time_file = os.path.join("data", "cache_time.txt")
        
        if os.path.exists(cache_time_file):
            try:
                with open(cache_time_file, 'r') as f:
                    cache_time = datetime.fromisoformat(f.read().strip())
                    time_str = cache_time.strftime("%d.%m.%Y %H:%M")
                    self.last_update_label.setText(t("settings.last_update", time=time_str))
            except:
                self.last_update_label.setText(t("settings.never_updated"))
        else:
            self.last_update_label.setText(t("settings.never_updated"))
    
    def force_data_update(self) -> None:
        """Принудительное обновление данных"""
        
        try:
            from json_data_manager import get_json_manager
            from PyQt6.QtCore import QTimer
            from PyQt6.QtGui import QIcon
            
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
                    log_error(f"Ошибка в on_complete: {e}")
                    import traceback
                    traceback.print_exc()
                    QMessageBox.critical(main_window, t("settings.error_title"), t("settings.error_update_ui", error=e))
            
            def on_failed(error):
                try:
                    if sender:
                        sender.setEnabled(True)
                        sender.setText(t("settings.check_button"))
                        
                        update_icon_path = get_icon_path("update.png")
                        if update_icon_path:
                            from PyQt6.QtGui import QIcon
                            from PyQt6.QtCore import QSize
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
                    
                    QMessageBox.warning(main_window, "Ошибка", f"Не удалось обновить данные:\n{error}")
                    
                except Exception as e:
                    log_error(f"Ошибка в on_failed: {e}")
                    import traceback
                    traceback.print_exc()
            
            manager.load_data(on_complete=on_complete, on_failed=on_failed)
            
        except Exception as e:
            log_error(f"Ошибка в force_data_update: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, t("settings.critical_error"), t("settings.error_update_data", error=e))
    
    def reset_update_button(self, button) -> None:
        """Возвращает кнопку обновления в исходное состояние"""
        if button:
            button.setEnabled(True)
            button.setText(t("settings.check_button"))
            
            update_icon_path = get_icon_path("update.png")
            if update_icon_path:
                from PyQt6.QtGui import QIcon
                from PyQt6.QtCore import QSize
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
            """)

    def apply_theme(self):
        """Применить тему ко всем элементам настроек"""
        from theme_manager import theme_manager
        c = theme_manager.colors
        
        # Обновляем основной стиль
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {c['bg_main']};
                border-radius: 10px;
            }}
        """)
        
        # Обновляем стиль боковой панели
        if hasattr(self, 'title_label'):
            sidebar = self.title_label.parent()
            if sidebar:
                sidebar.setStyleSheet(f"""
                    QWidget {{
                        background-color: {c['bg_sidebar']};
                        border-top-left-radius: 10px;
                        border-bottom-left-radius: 10px;
                    }}
                """)
            
            self.title_label.setStyleSheet(f"""
                QLabel {{
                    color: {c['text_primary']};
                    font-size: 18px;
                    font-weight: bold;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    margin: 0px 0px 15px 0px;
                    letter-spacing: 1px;
                }}
            """)
        
        # Обновляем стиль scroll_area
        if hasattr(self, 'scroll_area'):
            self.scroll_area.setStyleSheet(f"""
                QScrollArea {{
                    background-color: {c['bg_main']};
                    border: none;
                    border-top-right-radius: 10px;
                    border-bottom-right-radius: 10px;
                }}
                QScrollBar:vertical {{
                    background-color: {c['scrollbar_bg']};
                    width: 12px;
                    border-radius: 6px;
                    margin: 0px;
                }}
                QScrollBar::handle:vertical {{
                    background-color: {c['scrollbar_handle']};
                    border-radius: 6px;
                    min-height: 30px;
                }}
                QScrollBar::handle:vertical:hover {{
                    background-color: {c['scrollbar_hover']};
                }}
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                    height: 0px;
                }}
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                    background: none;
                }}
            """)
        
        # Обновляем стиль content_area
        if hasattr(self, 'content_area'):
            self.content_area.setStyleSheet(f"""
                QWidget {{
                    background-color: {c['bg_main']};
                    border: none;
                }}
            """)
        
        # Перезагружаем иконки кнопок меню
        for btn in [self.interface_btn, self.temp_files_btn, self.updates_btn, 
                    self.about_btn, self.contacts_btn]:
            if btn and hasattr(btn, 'property'):
                icon_name = btn.property("icon_name")
                if icon_name:
                    pixmap = self.load_icon_pixmap(icon_name)
                    if pixmap and not pixmap.isNull():
                        from PyQt6.QtGui import QIcon
                        from PyQt6.QtCore import QSize
                        btn.setIcon(QIcon(pixmap))
                        btn.setIconSize(QSize(16, 16))
        
        # Обновляем стили кнопок меню
        if hasattr(self, 'interface_btn'):
            # Определяем какая кнопка активна
            active_btn = None
            for btn in [self.interface_btn, self.temp_files_btn, self.updates_btn, 
                       self.about_btn, self.contacts_btn]:
                if btn and 'bg_input' in btn.styleSheet():
                    active_btn = btn
                    break
            
            # Обновляем стили всех кнопок
            for btn in [self.interface_btn, self.temp_files_btn, self.updates_btn, 
                       self.about_btn, self.contacts_btn]:
                if btn:
                    if btn == active_btn:
                        btn.setStyleSheet(self.get_active_button_style())
                    else:
                        btn.setStyleSheet(self.get_inactive_button_style())
        
        # Перерисовываем текущую страницу настроек
        self.show_interface_settings()
