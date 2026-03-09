"""
Вкладка настроек
"""
from typing import Optional, Any
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QFrame, QMessageBox, QApplication)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QClipboard
from ui.base.base_widget import BaseWidget
from .toggle_switch import ToggleSwitch, DisabledToggleSwitch
from core.utils import StyleSheets, WidgetFactory, LayoutUtils


class SettingsTab(BaseWidget):
    """Вкладка настроек с боковой панелью"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.snow_enabled = False
        self.theme_light = False
        self.snow_toggle: Optional[ToggleSwitch] = None
        self.theme_toggle: Optional[DisabledToggleSwitch] = None
        self.theme_development_dialog: Optional[QMessageBox] = None
        self.copied_label: Optional[QLabel] = None
        self.copy_timer: Optional[QTimer] = None
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Настройка интерфейса"""
        main_layout = LayoutUtils.create_horizontal_layout((0, 3, 0, 3), 0)
        self.setLayout(main_layout)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 10px;
            }
        """)
        
        self.create_sidebar(main_layout)
        self.create_content_area(main_layout)
        self.show_interface_settings()
    
    def create_sidebar(self, main_layout: QHBoxLayout) -> None:
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
        
        sidebar_layout = LayoutUtils.create_vertical_layout((0, 15, 0, 15), 5)
        sidebar.setLayout(sidebar_layout)
        
        title_label = QLabel("НАСТРОЙКИ")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {StyleSheets.COLORS['text_muted']};
                font-size: 12px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 10px 20px 5px 20px;
            }}
        """)
        sidebar_layout.addWidget(title_label)
        
        self.interface_btn = self.create_menu_button("interface.png", "Интерфейс", True)
        self.interface_btn.clicked.connect(self.show_interface_settings)
        sidebar_layout.addWidget(self.interface_btn)
        
        self.temp_files_btn = self.create_menu_button("tempfile.png", "Файлы")
        self.temp_files_btn.clicked.connect(self.show_temp_files_settings)
        sidebar_layout.addWidget(self.temp_files_btn)
        
        self.updates_btn = self.create_menu_button("updatetab.png", "Обновления")
        self.updates_btn.clicked.connect(self.show_updates_settings)
        sidebar_layout.addWidget(self.updates_btn)
        
        self.about_btn = self.create_menu_button("info.png", "О программе")
        self.about_btn.clicked.connect(self.show_about_settings)
        sidebar_layout.addWidget(self.about_btn)
        
        self.contacts_btn = self.create_menu_button("contacts.png", "Контакты")
        self.contacts_btn.clicked.connect(self.show_contacts_settings)
        sidebar_layout.addWidget(self.contacts_btn)
        
        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)
    
    def create_menu_button(self, icon_name: str, text: str, active: bool = False) -> QPushButton:
        """Создание кнопки меню"""
        btn = QPushButton(text)
        btn.setFixedHeight(40)
        btn.setStyleSheet(StyleSheets.get_button_style(active))
        
        icon_label = WidgetFactory.create_icon_label(icon_name, (16, 16))
        # TODO: Добавить иконку к кнопке через layout
        
        return btn
    
    def create_content_area(self, main_layout: QHBoxLayout) -> None:
        """Создание области содержимого"""
        self.content_area = QWidget()
        self.content_area.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
            }
        """)
        
        self.content_layout = LayoutUtils.create_vertical_layout((40, 30, 40, 30), 25)
        self.content_area.setLayout(self.content_layout)
        
        main_layout.addWidget(self.content_area)
    
    def clear_content(self) -> None:
        """Очистка содержимого"""
        if hasattr(self, 'cleanup_message'):
            self.cleanup_message = None
        
        LayoutUtils.clear_layout(self.content_layout)
    
    def show_interface_settings(self) -> None:
        """Показать настройки интерфейса"""
        self._update_button_styles("interface")
        self.clear_content()
        
        title_container = WidgetFactory.create_section_title("interface.png", "Настройки интерфейса")
        self.content_layout.addWidget(title_container)
        
        self.snow_toggle = ToggleSwitch()
        self.snow_toggle.setChecked(self.snow_enabled)
        if self.parent_window:
            self.snow_toggle.toggled.connect(self.parent_window.toggle_snow)
            self.snow_toggle.toggled.connect(self.save_snow_state)
        
        snow_setting = self.create_setting_item(
            "snowflake.png", 
            "Снегопад", 
            "Праздничная анимация снежинок на фоне приложения",
            self.snow_toggle
        )
        self.content_layout.addWidget(snow_setting)
        
        self.theme_toggle = DisabledToggleSwitch()
        self.theme_toggle.setChecked(self.theme_light)
        self.theme_toggle.toggled.connect(self.handle_theme_toggle)
        
        theme_setting = self.create_setting_item(
            "whitetheme.png", 
            "Светлая тема", 
            "Светлая тема интерфейса (в разработке)",
            self.theme_toggle
        )
        self.content_layout.addWidget(theme_setting)
        
        from localization import t
        from settings_manager import settings_manager
        
        notifications_enabled = settings_manager.get_setting("notifications_enabled", True)
        
        self.notifications_toggle = ToggleSwitch()
        self.notifications_toggle.setChecked(notifications_enabled)
        self.notifications_toggle.toggled.connect(self.save_notifications_state)
        
        notifications_setting = self.create_setting_item(
            "info.png",
            t("notifications.notifications_setting"),
            t("notifications.notifications_hint"),
            self.notifications_toggle
        )
        self.content_layout.addWidget(notifications_setting)
        
        notification_style = settings_manager.get_setting("notification_style", "custom")
        
        self.notification_style_toggle = ToggleSwitch()
        self.notification_style_toggle.setChecked(notification_style == "custom")
        self.notification_style_toggle.toggled.connect(self.save_notification_style)
        
        style_setting = self.create_setting_item(
            "settings.png",
            t("notifications.notification_style"),
            t("notifications.style_custom") if notification_style == "custom" else t("notifications.style_system"),
            self.notification_style_toggle
        )
        self.content_layout.addWidget(style_setting)
        
        notification_sounds = settings_manager.get_setting("notification_sounds", True)
        
        self.notification_sounds_toggle = ToggleSwitch()
        self.notification_sounds_toggle.setChecked(notification_sounds)
        self.notification_sounds_toggle.toggled.connect(self.save_notification_sounds)
        
        sounds_setting = self.create_setting_item(
            "speed.png",
            t("notifications.notification_sounds"),
            t("notifications.notification_sounds_hint"),
            self.notification_sounds_toggle
        )
        self.content_layout.addWidget(sounds_setting)
        
        self.content_layout.addStretch()
    
    def show_temp_files_settings(self) -> None:
        """Показать настройки временных файлов"""
        self._update_button_styles("temp_files")
        self.clear_content()
        
        from localization import t
        import os
        import tempfile
        
        title_container = WidgetFactory.create_section_title("tempfile.png", t("settings.files"))
        self.content_layout.addWidget(title_container)
        
        temp_dir = tempfile.gettempdir()
        app_temp_dir = os.path.join(temp_dir, "UTILHELP")
        
        # Подсчет файлов и размера
        file_count = 0
        total_size = 0
        if os.path.exists(app_temp_dir):
            for root, dirs, files in os.walk(app_temp_dir):
                file_count += len(files)
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                    except:
                        pass
        
        if total_size < 1024:
            size_str = f"{total_size} B"
        elif total_size < 1024 * 1024:
            size_str = f"{total_size / 1024:.2f} KB"
        elif total_size < 1024 * 1024 * 1024:
            size_str = f"{total_size / (1024 * 1024):.2f} MB"
        else:
            size_str = f"{total_size / (1024 * 1024 * 1024):.2f} GB"
        
        # Информационная карточка
        info_widget = QWidget()
        info_widget.setStyleSheet(StyleSheets.get_setting_item_style())
        info_layout = LayoutUtils.create_vertical_layout((20, 15, 20, 15), 10)
        info_widget.setLayout(info_layout)
        
        # Путь к папке
        folder_label = WidgetFactory.create_title_label(t("settings.temp_folder"), 14)
        info_layout.addWidget(folder_label)
        
        path_label = WidgetFactory.create_description_label(app_temp_dir)
        info_layout.addWidget(path_label)
        
        # Статистика
        stats_label = WidgetFactory.create_description_label(
            t("settings.files_stats", count=file_count, size=size_str)
        )
        info_layout.addWidget(stats_label)
        
        self.content_layout.addWidget(info_widget)
        
        clean_btn = QPushButton(t("settings.clean_temp"))
        clean_btn.setFixedHeight(45)
        clean_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        clean_btn.clicked.connect(lambda: self.clean_temp_files(app_temp_dir))
        self.content_layout.addWidget(clean_btn)
        
        self.content_layout.addStretch()
    
    def show_updates_settings(self) -> None:
        """Показать настройки обновлений"""
        self._update_button_styles("updates")
        self.clear_content()
        
        from localization import t
        
        title_container = WidgetFactory.create_section_title("updatetab.png", t("settings.updates"))
        self.content_layout.addWidget(title_container)
        
        info_widget = QWidget()
        info_widget.setStyleSheet(StyleSheets.get_setting_item_style())
        info_layout = LayoutUtils.create_vertical_layout((20, 15, 20, 15), 15)
        info_widget.setLayout(info_layout)
        
        info_title = WidgetFactory.create_title_label(t("settings.update_info_title"), 16)
        info_layout.addWidget(info_title)
        
        info_text = WidgetFactory.create_description_label(t("settings.update_info_text"))
        info_layout.addWidget(info_text)
        
        # Безопасность
        security_text = WidgetFactory.create_description_label(t("settings.update_security"))
        security_text.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        info_layout.addWidget(security_text)
        
        self.content_layout.addWidget(info_widget)
        
        check_btn = QPushButton(t("settings.check_updates"))
        check_btn.setFixedHeight(45)
        check_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        check_btn.clicked.connect(self.check_for_updates)
        self.content_layout.addWidget(check_btn)
        
        self.content_layout.addStretch()
    
    def show_about_settings(self) -> None:
        """Показать информацию о программе"""
        self._update_button_styles("about")
        self.clear_content()
        
        from localization import t
        
        title_container = WidgetFactory.create_section_title("info.png", t("settings.about"))
        self.content_layout.addWidget(title_container)
        
        logo_widget = QWidget()
        logo_layout = LayoutUtils.create_vertical_layout((20, 15, 20, 15), 10)
        logo_widget.setLayout(logo_layout)
        logo_widget.setStyleSheet(StyleSheets.get_setting_item_style())
        
        logo_label = WidgetFactory.create_icon_label("logo64x64.png", (64, 64))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(logo_label)
        
        app_name = WidgetFactory.create_title_label("UTILHELP", 20)
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(app_name)
        
        version_label = WidgetFactory.create_description_label(t("settings.version_label", version="1.0.1"))
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(version_label)
        
        self.content_layout.addWidget(logo_widget)
        
        info_widget = QWidget()
        info_widget.setStyleSheet(StyleSheets.get_setting_item_style())
        info_layout = LayoutUtils.create_vertical_layout((20, 15, 20, 15), 10)
        info_widget.setLayout(info_layout)
        
        # Разработчик
        dev_label = WidgetFactory.create_title_label(t("settings.developer"), 14)
        info_layout.addWidget(dev_label)
        
        dev_name = WidgetFactory.create_description_label("al1ster")
        info_layout.addWidget(dev_name)
        
        # Лицензия
        license_label = WidgetFactory.create_title_label(t("settings.license"), 14)
        info_layout.addWidget(license_label)
        
        license_text = WidgetFactory.create_description_label("MIT License")
        info_layout.addWidget(license_text)
        
        desc_label = WidgetFactory.create_title_label(t("settings.description"), 14)
        info_layout.addWidget(desc_label)
        
        desc_text = WidgetFactory.create_description_label(t("settings.description_full"))
        info_layout.addWidget(desc_text)
        
        self.content_layout.addWidget(info_widget)
        
        self.content_layout.addStretch()
    
    def show_contacts_settings(self) -> None:
        """Показать контактную информацию"""
        self._update_button_styles("contacts")
        self.clear_content()
        
        from localization import t
        import webbrowser
        
        title_container = WidgetFactory.create_section_title("contacts.png", t("settings.contacts"))
        self.content_layout.addWidget(title_container)
        
        info_widget = QWidget()
        info_widget.setStyleSheet(StyleSheets.get_setting_item_style())
        info_layout = LayoutUtils.create_vertical_layout((20, 15, 20, 15), 15)
        info_widget.setLayout(info_layout)
        
        contact_title = WidgetFactory.create_title_label(t("settings.contact_developer"), 16)
        info_layout.addWidget(contact_title)
        
        contact_info = WidgetFactory.create_description_label(t("settings.contact_info"))
        info_layout.addWidget(contact_info)
        
        self.content_layout.addWidget(info_widget)
        
        # Email
        email_widget = self.create_contact_item(
            "email.png",
            t("settings.email"),
            "al1ster13@gmail.com",
            lambda: self.copy_email_to_clipboard()
        )
        self.content_layout.addWidget(email_widget)
        
        # Telegram
        telegram_widget = self.create_contact_item(
            "telegram.png",
            t("settings.telegram"),
            "@utilhelp_channel",
            lambda: webbrowser.open("https://t.me/utilhelp_channel")
        )
        self.content_layout.addWidget(telegram_widget)
        
        # GitHub
        github_widget = self.create_contact_item(
            "github.png",
            t("settings.github"),
            "github.com/al1ster/utilhelp",
            lambda: webbrowser.open("https://github.com/al1ster/utilhelp")
        )
        self.content_layout.addWidget(github_widget)
        
        self.content_layout.addStretch()
    
    def _update_button_styles(self, active_section: str) -> None:
        """Обновить стили кнопок"""
        buttons = {
            "interface": self.interface_btn,
            "temp_files": self.temp_files_btn,
            "updates": self.updates_btn,
            "about": self.about_btn,
            "contacts": self.contacts_btn
        }
        
        for section, button in buttons.items():
            if section == active_section:
                button.setStyleSheet(StyleSheets.get_button_style(True))
            else:
                button.setStyleSheet(StyleSheets.get_button_style(False))
    
    def create_setting_item(self, icon: str, title: str, description: str, control_widget: QWidget) -> QWidget:
        """Создание элемента настройки"""
        item = QWidget()
        item.setFixedHeight(80)
        item.setStyleSheet(StyleSheets.get_setting_item_style())
        
        layout = LayoutUtils.create_horizontal_layout((20, 15, 20, 15), 15)
        item.setLayout(layout)
        
        icon_label = WidgetFactory.create_icon_label(icon, (24, 24))
        layout.addWidget(icon_label)
        
        text_layout = LayoutUtils.create_vertical_layout((0, 0, 0, 0), 2)
        
        title_label = WidgetFactory.create_title_label(title, 16)
        text_layout.addWidget(title_label)
        
        desc_label = WidgetFactory.create_description_label(description, word_wrap=False)
        text_layout.addWidget(desc_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        # Элемент управления
        layout.addWidget(control_widget)
        
        return item
    
    def save_snow_state(self, enabled: bool) -> None:
        """Сохранение состояния снегопада"""
        self.snow_enabled = enabled
        self.log_info(f"Snow effect {'enabled' if enabled else 'disabled'}")
    
    def save_notifications_state(self, enabled: bool) -> None:
        """Сохранение состояния уведомлений"""
        from settings_manager import settings_manager
        
        settings_manager.set_setting("notifications_enabled", enabled)
        self.log_info(f"Notifications {'enabled' if enabled else 'disabled'}")
    
    def save_notification_style(self, is_custom: bool) -> None:
        """Сохранение стиля уведомлений"""
        from settings_manager import settings_manager
        from localization import t
        
        style = "custom" if is_custom else "system"
        settings_manager.set_setting("notification_style", style)
        
        if hasattr(self, 'notification_style_toggle'):
            # Находим виджет настройки и обновляем описание
            for i in range(self.content_layout.count()):
                widget = self.content_layout.itemAt(i).widget()
                if widget and hasattr(widget, 'findChild'):
                    labels = widget.findChildren(QLabel)
                    for label in labels:
                        if "style_custom" in label.text() or "style_system" in label.text() or "Custom" in label.text() or "System" in label.text():
                            label.setText(t("notifications.style_custom") if is_custom else t("notifications.style_system"))
                            break
        
        self.log_info(f"Notification style set to: {style}")
    
    def save_notification_sounds(self, enabled: bool) -> None:
        """Сохранение настройки звуков уведомлений"""
        from settings_manager import settings_manager
        
        settings_manager.set_setting("notification_sounds", enabled)
        
        self.log_info(f"Notification sounds {'enabled' if enabled else 'disabled'}")
    
    def handle_theme_toggle(self, checked: bool) -> None:
        """Обработка переключения темы"""
        self.show_theme_development_message(checked)
    
    def show_theme_development_message(self, checked: bool) -> None:
        """Показать сообщение о том, что функция в стадии разработки"""
        if (self.theme_development_dialog is None or 
            not self.theme_development_dialog.isVisible()):
            
            self.theme_development_dialog = QMessageBox()
            self.theme_development_dialog.setWindowTitle("В разработке")
            self.theme_development_dialog.setText("Светлая тема находится в стадии разработки")
            self.theme_development_dialog.setInformativeText("Эта функция будет доступна в следующих версиях программы.")
            self.theme_development_dialog.setIcon(QMessageBox.Icon.Information)
            self.theme_development_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        self.theme_development_dialog.exec()
    
    def copy_email_to_clipboard(self) -> None:
        """Копирование email в буфер обмена с уведомлением"""
        from localization import t
        from custom_dialogs import CustomMessageDialog
        
        clipboard = QApplication.clipboard()
        clipboard.setText("al1ster13@gmail.com")
        
        # Показать уведомление о копировании
        dialog = CustomMessageDialog(
            t("settings.email_copied"),
            "al1ster13@gmail.com",
            "email.png",
            self
        )
        dialog.exec()
        
        self.log_info("Email copied to clipboard")
    
    def create_contact_item(self, icon: str, title: str, value: str, action) -> QWidget:
        """Создание элемента контакта"""
        item = QWidget()
        item.setFixedHeight(70)
        item.setStyleSheet(StyleSheets.get_setting_item_style())
        
        layout = LayoutUtils.create_horizontal_layout((20, 15, 20, 15), 15)
        item.setLayout(layout)
        
        icon_label = WidgetFactory.create_icon_label(icon, (32, 32))
        layout.addWidget(icon_label)
        
        text_layout = LayoutUtils.create_vertical_layout((0, 0, 0, 0), 2)
        
        title_label = WidgetFactory.create_title_label(title, 14)
        text_layout.addWidget(title_label)
        
        value_label = WidgetFactory.create_description_label(value)
        text_layout.addWidget(value_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        action_btn = QPushButton("→")
        action_btn.setFixedSize(40, 40)
        action_btn.setStyleSheet("""
            QPushButton {
                background-color: #666666;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #777777;
            }
            QPushButton:pressed {
                background-color: #555555;
            }
        """)
        action_btn.clicked.connect(action)
        layout.addWidget(action_btn)
        
        return item
    
    def clean_temp_files(self, temp_dir: str) -> None:
        """Очистка временных файлов"""
        from localization import t
        from custom_dialogs import CustomMessageDialog
        import shutil
        
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                dialog = CustomMessageDialog(
                    t("settings.temp_cleaned"),
                    t("settings.temp_deleted_many", count=1),
                    "complete.png",
                    self
                )
                dialog.exec()
                # Обновить отображение
                self.show_temp_files_settings()
            else:
                dialog = CustomMessageDialog(
                    t("settings.temp_not_found"),
                    "",
                    "info.png",
                    self
                )
                dialog.exec()
        except Exception as e:
            dialog = CustomMessageDialog(
                t("settings.temp_clean_error"),
                str(e),
                "error.png",
                self
            )
            dialog.exec()
            self.log_error(f"Failed to clean temp files: {e}")
    
    def check_for_updates(self) -> None:
        """Проверка обновлений"""
        from localization import t
        from custom_dialogs import CustomMessageDialog
        
        # Показать сообщение о проверке
        dialog = CustomMessageDialog(
            t("settings.checking_updates"),
            t("settings.no_updates"),
            "updatetab.png",
            self
        )
        dialog.exec()
        self.log_info("Checked for updates")