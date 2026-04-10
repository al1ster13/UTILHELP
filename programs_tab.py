from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QPushButton, QHBoxLayout, QFrame, QGridLayout, QLineEdit, QDialog, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal, QThread
from PyQt6.QtGui import QPixmap, QCursor
from scroll_helper import configure_scroll_area
from download_manager import InstallationManager, CustomMessageBox
from resource_path import get_db_path, get_icon_path
from favorites_manager import FavoritesManager
from system_scanner import CachedInstallationStatusManager, BackgroundScanner
from logger import log_info, log_error, log_warning, log_debug
from localization import t
from ui.components import CatalogComboBox, BaseInfoPanel
from typing import Dict, Any, Optional
import webbrowser


class ProgramInfoPanel(BaseInfoPanel):
    """Информационная панель программы - наследует BaseInfoPanel"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        self.installation_manager = None
        super().__init__(parent)
    
    def _get_icon_path(self, logo_name: str) -> Optional[str]:
        """Получить путь к иконке программы"""
        from logo_manager import get_logo_manager
        logo_manager = get_logo_manager()
        # Получаем путь к кэшированному логотипу или локальному fallback
        return logo_manager.get_cached_logo_path(logo_name)
    
    def _add_custom_info(self, item_data: Dict[str, Any]):
        """Добавить специфичную информацию для программ"""
        status = item_data.get("status", "")
        if status and status != "Доступно":
            self._add_info_row("📊", f"Статус: {status}")
    
    def _create_main_button(self, item_data: Dict[str, Any]) -> Optional[QPushButton]:
        """Создать основную кнопку действия"""
        button = QPushButton()
        button.setFixedHeight(45)
        button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        button_type = item_data.get("button_type", "download")
        status = item_data.get("status", "Доступно")
        
        if status == "Скоро":
            button.setText(t("buttons.coming_soon"))
            button.setEnabled(False)
        elif button_type == "website":
            button.setText(t("buttons.website"))
            button.clicked.connect(lambda: self._handle_website_click(item_data))
        else:
            button.setText(t("buttons.download"))
            button.clicked.connect(lambda: self._handle_download_click(item_data))
        
        from theme_manager import theme_manager
        c = theme_manager.colors
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['download_btn']};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 20px;
            }}
            QPushButton:hover {{ background-color: {c['download_hover']}; }}
            QPushButton:pressed {{ background-color: {c['download_press']}; }}
            QPushButton:disabled {{ background-color: {c['bg_tertiary']}; color: {c['text_disabled']}; }}
        """)
        
        return button
    
    def _create_website_button(self, item_data: Dict[str, Any]) -> QPushButton:
        """Создать кнопку сайта разработчика"""
        from theme_manager import theme_manager
        c = theme_manager.colors
        button = QPushButton(t("buttons.developer_website"))
        button.setFixedHeight(40)
        button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        button.clicked.connect(lambda: self._open_website(item_data.get("website", "")))
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['bg_button']};
                color: {c['text_primary']};
                border: none;
                border-radius: 6px;
                font-size: 12px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{ background-color: {c['bg_hover']}; }}
            QPushButton:pressed {{ background-color: {c['bg_pressed']}; }}
        """)
        return button
    
    def _handle_download_click(self, item_data: Dict[str, Any]):
        """Обработка клика на кнопку скачивания"""
        download_url = item_data.get("url", "")
        if download_url:
            icon_path = self._get_icon_path(item_data.get("logo", ""))
            InstallationManager.install_program(
                item_data["name"],
                download_url,
                self,
                icon_path,
                "program"
            )
        else:
            CustomMessageBox.warning(self, t("errors.no_url"), t("errors.no_url"))
    
    def _handle_website_click(self, item_data: Dict[str, Any]):
        """Обработка клика на кнопку сайта"""
        url = item_data.get("url", "")
        self._open_website(url)
    
    def _open_website(self, url: str):
        """Открыть сайт в браузере"""
        if url and url.strip():
            try:
                webbrowser.open(url)
            except Exception as e:
                CustomMessageBox.critical(
                    self,
                    t("errors.open_website_failed"),
                    t("errors.open_website_failed", error=str(e))
                )
        else:
            CustomMessageBox.warning(self, t("errors.no_website"), t("errors.no_website"))
    
    def show_program(self, program: Dict[str, Any]):
        """Показать информацию о программе (обратная совместимость)"""
        self.show_item(program)


class ProgramsTab(QWidget):
    """Панель с подробной информацией о программе"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(420, 480) 
        self.hide()
        
        self.main_container = QWidget(self)
        self.main_container.setGeometry(0, 0, 420, 480)
        from theme_manager import theme_manager
        c = theme_manager.colors
        self.main_container.setStyleSheet(f"""
            QWidget {{
                background-color: {c['bg_secondary']};
                border-radius: 15px;
            }}
        """)
        
        self.layout = QVBoxLayout(self.main_container)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel()
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 20px;
                font-weight: bold;
                background: transparent;
                border: none;
            }}
        """)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        
        close_btn = QPushButton()
        close_btn.setFixedSize(28, 28)  
        close_btn.clicked.connect(self.hide_panel)
        
        from PyQt6.QtCore import Qt
        
        from resource_path import get_icon_path
        from PyQt6.QtGui import QIcon
        from PyQt6.QtCore import QSize
        close_icon_path = get_icon_path("closemenu.png")
        if close_icon_path:
            icon = QIcon(close_icon_path)
            close_btn.setIcon(icon)
            close_btn.setIconSize(QSize(16, 16))
            close_btn.setFlat(True)
            from PyQt6.QtCore import Qt
            close_btn.setProperty("flat", True)
            close_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {c['bg_pressed']};
                    color: {c['text_primary']};
                    border: none;
                    border-radius: 12px;
                    font-size: 14px;
                    font-weight: bold;
                    text-align: center;
                    padding: 0px;
                    outline: none;
                }}
                QPushButton:hover {{ background-color: {c['bg_hover']}; }}
                QPushButton:focus {{ outline: none; border: none; }}
            """)
        else:
            close_btn.setText("✕")
            close_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {c['bg_pressed']};
                    color: {c['text_primary']};
                    border: none;
                    border-radius: 12px;
                    font-size: 14px;
                    font-weight: bold;
                    text-align: center;
                    padding: 0px;
                    outline: none;
                }}
                QPushButton:hover {{ background-color: {c['bg_hover']}; }}
                QPushButton:focus {{ outline: none; border: none; }}
            """)

        header_layout.addWidget(close_btn)
        
        self.layout.addLayout(header_layout)
        
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 60px;
                margin: 15px 0px;
                background: transparent;
                border: none;
            }}
        """)
        self.layout.addWidget(self.logo_label)
        
        self.category_label = QLabel()
        self.category_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.category_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_secondary']};
                font-size: 14px;
                margin: 5px 0px 5px 0px;
                background: transparent;
                border: none;
            }}
        """)
        self.layout.addWidget(self.category_label)
        
        from PyQt6.QtWidgets import QScrollArea
        
        self.desc_label = QLabel()
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 14px;
                line-height: 1.5;
                background: transparent;
                border: none;
                padding: 0px;
            }}
        """)
        
        self.desc_scroll = QScrollArea()
        self.desc_scroll.setWidget(self.desc_label)
        self.desc_scroll.setWidgetResizable(True)
        self.desc_scroll.setFixedHeight(160)
        self.desc_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.desc_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        configure_scroll_area(self.desc_scroll)
        
        self.desc_scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background: transparent;
                margin-left: 3px;
            }}
            QScrollBar:vertical {{
                background-color: {c['scrollbar_bg']};
                width: 8px;
                border-radius: 4px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {c['scrollbar_handle']};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {c['scrollbar_hover']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none; background: none; height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
        
        self.layout.addWidget(self.desc_scroll)
        
        self.buttons_container = QWidget()
        self.buttons_container.setFixedHeight(100)  
        self.buttons_container.setStyleSheet("background: transparent;")  
        buttons_layout = QVBoxLayout(self.buttons_container)
        buttons_layout.setContentsMargins(0, 10, 0, 0)
        buttons_layout.setSpacing(5)
       
        buttons_layout.addStretch()
        
        self.download_btn = QPushButton()
        self.download_btn.clicked.connect(self.handle_button_click)
        self.download_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['download_btn']};
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                outline: none;
            }}
            QPushButton:hover {{ background-color: {c['download_hover']}; }}
            QPushButton:pressed {{ background-color: {c['download_press']}; }}
            QPushButton:disabled {{ background-color: {c['bg_tertiary']}; color: {c['text_disabled']}; }}
            QPushButton:focus {{ outline: none; border: none; }}
        """)
        buttons_layout.addWidget(self.download_btn)
        
        self.website_btn = QPushButton(t("buttons.developer_website"))
        self.website_btn.clicked.connect(self.open_developer_website)
        self.website_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['bg_button']};
                color: {c['text_primary']};
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: normal;
                font-size: 12px;
                outline: none;
            }}
            QPushButton:hover {{ background-color: {c['bg_hover']}; }}
            QPushButton:pressed {{ background-color: {c['bg_pressed']}; }}
            QPushButton:disabled {{ background-color: {c['bg_tertiary']}; color: {c['text_disabled']}; }}
            QPushButton:focus {{ outline: none; border: none; }}
        """)
        buttons_layout.addWidget(self.website_btn)
        
        self.layout.addWidget(self.buttons_container)
        
        self.current_program_data = None
        
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(250)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.is_animating = False
        
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def keyPressEvent(self, event):
        """Обработка нажатий клавиш"""
        if event.key() == Qt.Key.Key_Escape:
            self.hide_panel()
        else:
            super().keyPressEvent(event)

    def show_program(self, program):
        """Показать информацию о программе"""
        if self.is_animating:
            return
        
        self.current_program_data = program
        
        self.title_label.setText(program["name"])
        
        from image_helper import load_program_image
        
        self.logo_label.setText("📦")
        
        def on_logo_loaded(logo_name, pixmap):
            if pixmap and not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.logo_label.setPixmap(scaled_pixmap)
        
        pixmap = load_program_image(program["logo"], callback=on_logo_loaded)
        if pixmap and not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(scaled_pixmap)
        
        self.category_label.setText(t("info.category", category=program['category']))
        self.desc_label.setText(program["description"])
        
        if program["status"] == "Скоро":
            if program["button_type"] == "website":
                self.download_btn.setText(t("buttons.coming_soon"))
            else:
                self.download_btn.setText(t("buttons.coming_soon"))
            self.download_btn.setEnabled(False)
        else:
            if program["button_type"] == "website":
                self.download_btn.setText(t("buttons.website"))
            else:
                self.download_btn.setText(t("buttons.download"))
            self.download_btn.setEnabled(True)
        
        if program.get("website") and program["website"].strip():
            self.website_btn.show()
            self.website_btn.setEnabled(True)
        else:
            self.website_btn.hide()
        
        parent_rect = self.parent().rect()
        x = parent_rect.width() - self.width() - 20
        y = (parent_rect.height() - self.height()) // 2
        self.move(x, y)
        
        try:
            self.fade_animation.finished.disconnect()
        except:
            pass
        
        self.show()
        self.is_animating = True
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.finished.connect(self.on_show_finished)
        self.fade_animation.start()
        
        self.setFocus()

    def handle_button_click(self):
        """Обработка нажатия на кнопку"""
        if not self.current_program_data:
            return
        
        program = self.current_program_data
        
        if program["button_type"] == "website":
            InstallationManager.open_website(program.get("url", ""), self)
        else:
            download_url = program.get("url", "")
            if download_url:
                from resource_path import get_program_image_path
                icon_path = get_program_image_path(program.get("logo", ""))
                
                InstallationManager.install_program(
                    program["name"], 
                    download_url, 
                    self, 
                    icon_path, 
                    "program"
                )
            else:
                CustomMessageBox.warning(self, "Ошибка", 
                                  "Ссылка для скачивания не указана!")

    def open_developer_website(self):
        """Открыть сайт разработчика"""
        if not self.current_program_data:
            return
        
        website_url = self.current_program_data.get("website", "")
        if website_url and website_url.strip():
            try:
                import webbrowser
                webbrowser.open(website_url)
            except Exception as e:
                from download_manager import CustomMessageBox
                CustomMessageBox.critical(self, "Ошибка", 
                                   f"Не удалось открыть сайт:\n{e}")
        else:
            from download_manager import CustomMessageBox
            CustomMessageBox.warning(self, "Ошибка", 
                              "Сайт разработчика не указан!")

    def hide_panel(self):
        """Скрыть панель с анимацией"""
        if self.is_animating:
            return
        
        self.is_animating = True
        
        try:
            self.fade_animation.finished.disconnect()
        except:
            pass
        
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.finished.connect(self.on_hide_finished)
        self.fade_animation.start()

    def on_show_finished(self):
        """Завершение анимации показа"""
        self.is_animating = False
        try:
            self.fade_animation.finished.disconnect()
        except:
            pass

    def on_hide_finished(self):
        """Завершение анимации скрытия"""
        self.hide()
        self.is_animating = False
        try:
            self.fade_animation.finished.disconnect()
        except:
            pass
class ProgramsTab(QWidget):
    """Вкладка программ - каталог полезных утилит"""

    def __init__(self):
        super().__init__()
        
        self.all_programs = []
        self.filtered_programs = []
        self.current_program = None
        self.current_columns = 3  
        self.favorites_manager = FavoritesManager()
        self.status_manager = CachedInstallationStatusManager()
        self.background_scanner = None
        self.scan_in_progress = False
        
        from settings_manager import settings_manager
        self.view_mode = settings_manager.get_setting("view_mode", "grid")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        from theme_manager import theme_manager, get_tab_stylesheet
        c = theme_manager.colors

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {c['bg_main']};
                border-radius: 10px;
            }}
            QScrollBar:vertical {{
                background-color: transparent;
                width: 16px;
                border-radius: 8px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {c['scrollbar_handle']};
                border-radius: 8px;
                min-height: 30px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {c['scrollbar_hover']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)

        self.title_label = QLabel(t("tabs.programs"))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 28px;
                font-weight: bold;
                margin: 20px 0px;
                letter-spacing: 2px;
            }}
        """)
        self.layout.addWidget(self.title_label)
        
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(100, 0, 100, 15)
        search_layout.setSpacing(15)
        
        self.category_filter = CatalogComboBox()
        self.category_filter.addItem(t("categories.all"), "")
        self.category_filter.addItem(t("categories.favorites"), "favorites")
        self.category_filter.currentIndexChanged.connect(self.filter_programs)
        
        search_layout.addWidget(self.category_filter)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(t("search.programs_placeholder"))
        self.search_input.textChanged.connect(self.filter_programs)
        self.search_input.setFixedHeight(35)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {c['bg_input']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                padding: 8px 15px;
                color: {c['text_primary']};
                font-size: 14px;
                outline: none;
            }}
            QLineEdit:focus {{
                border: 1px solid {c['accent']};
                outline: none;
            }}
            QLineEdit:hover {{
                border: 1px solid {c['border_hover']};
            }}
        """)
        
        search_layout.addWidget(self.search_input)
        
        
        from resource_path import get_icon_path
        from PyQt6.QtGui import QIcon
        from PyQt6.QtCore import QSize
        
        self.scan_button = QPushButton()
        self.update_scan_button_icon(False)  
            
        self.scan_button.setFixedSize(35, 35)
        self.scan_button.clicked.connect(self.start_system_scan)
        self.scan_button.setToolTip(t("search.scan_tooltip"))
        self.scan_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['bg_pressed']};
                border: none;
                border-radius: 8px;
                color: {c['text_primary']};
                font-size: 16px;
                font-weight: bold;
                outline: none;
            }}
            QPushButton:hover {{ background-color: {c['bg_hover']}; }}
            QPushButton:pressed {{ background-color: {c['border_hover']}; }}
            QPushButton:disabled {{ background-color: {c['bg_tertiary']}; color: {c['text_disabled']}; }}
            QToolTip {{
                background-color: {c['bg_secondary']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }}
        """)
        
        search_layout.addWidget(self.scan_button)
        
        self.view_mode_button = QPushButton()
        self.view_mode_button.setFixedSize(35, 35)
        self.view_mode_button.clicked.connect(self.toggle_view_mode)
        self.view_mode_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['bg_pressed']};
                border: none;
                border-radius: 8px;
                color: {c['text_primary']};
                font-size: 18px;
                font-weight: bold;
                outline: none;
            }}
            QPushButton:hover {{ background-color: {c['bg_hover']}; }}
            QPushButton:pressed {{ background-color: {c['border_hover']}; }}
            QToolTip {{
                background-color: {c['bg_secondary']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }}
        """)
        
        search_layout.addWidget(self.view_mode_button)
        self.layout.addLayout(search_layout)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        configure_scroll_area(self.scroll_area)
        
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background-color: transparent;
                width: 16px;
                margin: 8px 0px 7px 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {c['scrollbar_handle']};
                border-radius: 8px;
                min-height: 30px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {c['scrollbar_hover']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
        
        self.programs_content = QWidget()
        self.programs_grid = QGridLayout(self.programs_content)
        self.programs_grid.setContentsMargins(55, 10, 45, 10)  
        self.programs_grid.setHorizontalSpacing(120)  
        self.programs_grid.setVerticalSpacing(50)     
        self.programs_grid.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.programs_data = []
        
        self.scroll_area.setWidget(self.programs_content)
        self.layout.addWidget(self.scroll_area)
        
        self.info_panel = ProgramInfoPanel(self)
        
        self.update_view_mode_button()

    def set_data(self, programs_data):
        """Установить данные программ из JSON"""
        self.programs_data = programs_data
        log_info(f"Programs tab: получено {len(programs_data)} программ")
        
        self.all_programs = []
        categories_set = set()
        
        for program in programs_data:
            category_str = program.get('category', '')
            categories_list = [cat.strip() for cat in category_str.split(',') if cat.strip()]
            
            program_dict = {
                "name": program.get('name', ''),
                "description": program.get('description', ''),
                "description_en": program.get('description_en', ''),
                "category": category_str,  
                "categories": categories_list,  
                "logo": program.get('logo', ''),
                "status": program.get('status', 'Скоро'),
                "keywords": program.get('keywords', '').split(',') if program.get('keywords') else [],
                "button_type": program.get('button_type', 'download'),
                "url": program.get('url', ''),
                "website": program.get('website', '')
            }
            self.all_programs.append(program_dict)
            
            for cat in categories_list:
                categories_set.add(cat)
        
        self.category_filter.clear()
        self.category_filter.addItem(t("categories.all"), "")
        self.category_filter.addItem(t("categories.favorites"), "favorites")
        for category in sorted(categories_set):
            from localization import translate_category
            translated_category = translate_category(category)
            self.category_filter.addItem(translated_category, category)
        
        self.filtered_programs = self.all_programs.copy()
        
        self.display_programs()

    def display_programs(self):
        """Отображение программ в зависимости от выбранного режима"""
        if self.view_mode == "list":
            self.display_programs_list()
        else:
            self.display_programs_grid()
    
    def display_programs_grid(self):
        """Отображение программ в виде сетки"""
        self.programs_grid.setVerticalSpacing(50)
        self.programs_grid.setHorizontalSpacing(120)
        
        for i in reversed(range(self.programs_grid.count())):
            child = self.programs_grid.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        window_width = self.width()
        if window_width >= 1600:  
            columns = 4
        else:  
            columns = 3
        
        sorted_programs = sorted(self.filtered_programs, key=lambda x: x.get('name', '').lower())
        
        row = 0
        col = 0
        for program in sorted_programs:
            card = self.create_program_card(program)
            self.programs_grid.addWidget(card, row, col)
            
            col += 1
            if col >= columns:
                col = 0
                row += 1
    
    def display_programs_list(self):
        """Отображение программ в виде списка"""
        self.programs_grid.setVerticalSpacing(15)  
        self.programs_grid.setHorizontalSpacing(0)
        
        for i in reversed(range(self.programs_grid.count())):
            child = self.programs_grid.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        sorted_programs = sorted(self.filtered_programs, key=lambda x: x.get('name', '').lower())
        
        for row, program in enumerate(sorted_programs):
            card = self.create_program_card_list(program)
            self.programs_grid.addWidget(card, row, 0)

    def create_program_card(self, program):
        """Создание квадратной карточки программы"""
        from theme_manager import theme_manager, colorize_pixmap
        c = theme_manager.colors

        card = QFrame()
        card.setFixedSize(220, 250)

        def card_mouse_press(event):
            if event.button() == Qt.MouseButton.LeftButton:
                child = card.childAt(event.pos())
                if child and child.objectName() == "favorite_btn":
                    return
                self.show_program_info(program)

        card.mousePressEvent = card_mouse_press

        card.setStyleSheet(f"""
            QFrame {{
                background-color: {c['bg_tertiary']};
                border: none;
                border-radius: 15px;
                padding: 0px;
            }}
            QFrame:hover {{
                background-color: {c['bg_hover']};
                border: 2px solid {c['border_hover']};
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(10, 10, 10, 10)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.setSpacing(10)
        
        top_container = QWidget()
        top_container.setFixedHeight(30)
        top_container.setStyleSheet("background: transparent;")
        top_layout = QHBoxLayout(top_container)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        status = self.status_manager.get_program_status(program["name"])
        if status["installed"]:
            status_label = QLabel()
            status_label.setFixedSize(24, 24)
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            from resource_path import get_icon_path
            icon_path = get_icon_path("installed.png")
            if icon_path:
                from PyQt6.QtGui import QPixmap
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    status_label.setPixmap(scaled_pixmap)
                else:
                    status_label.setText("✓")
            else:
                status_label.setText("✓")
            
            status_label.setStyleSheet(f"""
                QLabel {{
                    background-color: transparent;
                    border: none;
                    min-width: 24px;
                    max-width: 24px;
                    min-height: 24px;
                    max-height: 24px;
                }}
                QToolTip {{
                    background-color: {c['bg_secondary']};
                    color: {c['text_primary']};
                    border: 1px solid {c['border']};
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 12px;
                }}
            """)
            status_label.setToolTip(t("status.installed_tooltip", name=status['exact_name'], version=status['version']))
            top_layout.addWidget(status_label)
        
        top_layout.addStretch()
        
        favorite_btn = QPushButton()
        favorite_btn.setFixedSize(28, 28)
        favorite_btn.setObjectName("favorite_btn")
        is_favorite = self.favorites_manager.is_favorite(program["name"], "programs")
        favorite_btn.setText("♥" if is_favorite else "♡")
        favorite_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {'#ff4757' if is_favorite else '#666666'};
                font-size: 22px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                color: #ff4757;
            }}
        """)
        favorite_btn.clicked.connect(lambda: self.toggle_favorite(program, favorite_btn))
        
        def favorite_mouse_press(event):
            event.accept()
            self.toggle_favorite(program, favorite_btn)
        
        favorite_btn.mousePressEvent = favorite_mouse_press
        
        top_layout.addWidget(favorite_btn)
        card_layout.addWidget(top_container)
        
        from image_helper import load_program_image
        
        logo_label = QLabel("📦")
        
        def on_logo_loaded(logo_name, pixmap):
            if pixmap and not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                if theme_manager.is_light():
                    scaled_pixmap = colorize_pixmap(scaled_pixmap, c['text_secondary'])
                logo_label.setPixmap(scaled_pixmap)
        
        pixmap = load_program_image(program["logo"], callback=on_logo_loaded)
        if pixmap and not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            if theme_manager.is_light():
                scaled_pixmap = colorize_pixmap(scaled_pixmap, c['text_secondary'])
            logo_label.setPixmap(scaled_pixmap)
        
        logo_container = QWidget()
        logo_container.setFixedSize(200, 100)  
        logo_container.setStyleSheet("background: transparent;")
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.addStretch()
        logo_layout.addWidget(logo_label)
        logo_layout.addStretch()
        
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setFixedSize(100, 100)
        logo_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 48px;
                font-family: 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', sans-serif;
                background: transparent;
                border: none;
                qproperty-alignment: AlignCenter;
            }}
        """)
        
        card_layout.addWidget(logo_container)
        
        card_layout.addStretch()
        
        name_label = QLabel(program["name"])
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setFixedHeight(60)
        name_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 15px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
                text-align: center;
                line-height: 1.3;
                padding: 5px;
            }}
        """)
        card_layout.addWidget(name_label)
        
        return card
    
    def create_program_card_list(self, program):
        """Создание горизонтальной карточки программы для режима списка"""
        from theme_manager import theme_manager, colorize_pixmap
        c = theme_manager.colors

        card = QFrame()
        card.setFixedHeight(80)
        card.setMinimumWidth(600)

        def card_mouse_press(event):
            if event.button() == Qt.MouseButton.LeftButton:
                child = card.childAt(event.pos())
                if child and child.objectName() == "favorite_btn":
                    return
                self.show_program_info(program)

        card.mousePressEvent = card_mouse_press

        card.setStyleSheet(f"""
            QFrame {{
                background-color: {c['bg_tertiary']};
                border: none;
                border-radius: 10px;
                padding: 0px;
            }}
            QFrame:hover {{
                background-color: {c['bg_hover']};
                border: 2px solid {c['border_hover']};
            }}
        """)

        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(15, 10, 15, 10)
        card_layout.setSpacing(15)

        from image_helper import load_program_image
        
        logo_label = QLabel("📦")
        logo_label.setFixedSize(60, 60)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        def on_logo_loaded(logo_name, pixmap):
            if pixmap and not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                if theme_manager.is_light():
                    scaled_pixmap = colorize_pixmap(scaled_pixmap, c['text_secondary'])
                logo_label.setPixmap(scaled_pixmap)
        
        pixmap = load_program_image(program["logo"], callback=on_logo_loaded)
        if pixmap and not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            if theme_manager.is_light():
                scaled_pixmap = colorize_pixmap(scaled_pixmap, c['text_secondary'])
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label = QLabel("📦")

        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setFixedSize(60, 60)
        logo_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 32px;
                background: transparent;
                border: none;
            }}
        """)
        card_layout.addWidget(logo_label)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)

        name_label = QLabel(program["name"])
        name_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 16px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
            }}
        """)
        info_layout.addWidget(name_label)

        from settings_manager import settings_manager
        current_language = settings_manager.get_setting("language", "ru")

        if current_language == "en" and "description_en" in program:
            description = program.get("description_en", program.get("description", ""))
        else:
            description = program.get("description", "")

        if len(description) > 100:
            description = description[:97] + "..."
        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_secondary']};
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
            }}
        """)
        info_layout.addWidget(desc_label)
        card_layout.addLayout(info_layout, 1)
        
        status = self.status_manager.get_program_status(program["name"])
        if status["installed"]:
            status_label = QLabel()
            status_label.setFixedSize(24, 24)
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            from resource_path import get_icon_path
            icon_path = get_icon_path("installed.png")
            if icon_path:
                from PyQt6.QtGui import QPixmap
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    status_label.setPixmap(scaled_pixmap)
                else:
                    status_label.setText("✓")
            else:
                status_label.setText("✓")
            
            status_label.setStyleSheet(f"""
                QLabel {{
                    background-color: transparent;
                    border: none;
                }}
                QToolTip {{
                    background-color: {c['bg_secondary']};
                    color: {c['text_primary']};
                    border: 1px solid {c['border']};
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 12px;
                }}
            """)
            status_label.setToolTip(t("status.installed_tooltip", name=status['exact_name'], version=status['version']))
            card_layout.addWidget(status_label)
        
        favorite_btn = QPushButton()
        favorite_btn.setFixedSize(28, 28)
        favorite_btn.setObjectName("favorite_btn")
        is_favorite = self.favorites_manager.is_favorite(program["name"], "programs")
        favorite_btn.setText("♥" if is_favorite else "♡")
        favorite_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {'#ff4757' if is_favorite else '#666666'};
                font-size: 22px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                color: #ff4757;
            }}
        """)
        favorite_btn.clicked.connect(lambda: self.toggle_favorite(program, favorite_btn))
        
        def favorite_mouse_press(event):
            event.accept()
            self.toggle_favorite(program, favorite_btn)
        
        favorite_btn.mousePressEvent = favorite_mouse_press
        
        card_layout.addWidget(favorite_btn)
        
        return card

    def toggle_favorite(self, program, button):
        """Переключить статус избранного для программы"""
        program_name = program["name"]
        is_favorite = self.favorites_manager.is_favorite(program_name, "programs")
        
        if is_favorite:
            self.favorites_manager.remove_from_favorites(program_name, "programs")
            button.setText("♡")
            button.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    color: #666666;
                    font-size: 22px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    color: #ff4757;
                }
            """)
        else:
            self.favorites_manager.add_to_favorites(program_name, "programs")
            button.setText("♥")
            button.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    color: #ff4757;
                    font-size: 22px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    color: #ff4757;
                }
            """)

    def show_program_info(self, program):
        """Показать информационную панель программы"""
        if self.current_program and self.current_program["name"] == program["name"]:
            self.info_panel.hide_panel()
            self.current_program = None
        else:
            self.current_program = program
            self.info_panel.show_program(program)

    def filter_programs(self):
        search_text = self.search_input.text().lower()
        selected_category = self.category_filter.currentData()
        
        self.filtered_programs = []
        for program in self.all_programs:
            if selected_category == "favorites":
                if not self.favorites_manager.is_favorite(program["name"], "programs"):
                    continue
            elif selected_category:
                if selected_category not in program.get("categories", []):
                    continue
            
            if search_text:
                if not (search_text in program["name"].lower() or
                        search_text in program["description"].lower() or
                        search_text in program["category"].lower() or
                        any(search_text in keyword for keyword in program["keywords"])):
                    continue
            
            self.filtered_programs.append(program)
        
        self.display_programs()

    def refresh_programs(self):
        """Обновление списка программ"""
        pass
    
    def reset_search_and_scroll(self):
        """Сброс поиска и прокрутки при переключении вкладки"""
        if hasattr(self, 'search_input'):
            self.search_input.clear()

    def apply_theme(self):
        """Обновить стили при смене темы"""
        from theme_manager import theme_manager
        c = theme_manager.colors
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {c['bg_main']};
                border-radius: 10px;
            }}
        """)
        
        if hasattr(self, 'title_label'):
            self.title_label.setStyleSheet(f"""
                QLabel {{
                    color: {c['text_primary']};
                    font-size: 28px;
                    font-weight: bold;
                    margin: 20px 0px;
                    letter-spacing: 2px;
                }}
            """)
        
        if hasattr(self, 'search_input'):
            self.search_input.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {c['bg_input']};
                    border: 1px solid {c['border']};
                    border-radius: 8px;
                    padding: 8px 15px;
                    color: {c['text_primary']};
                    font-size: 14px;
                    outline: none;
                }}
                QLineEdit:focus {{ border: 1px solid {c['accent']}; }}
                QLineEdit:hover {{ border: 1px solid {c['border_hover']}; }}
            """)
        
        if hasattr(self, 'scroll_area'):
            self.scroll_area.setStyleSheet(f"""
                QScrollArea {{
                    border: none;
                    background-color: transparent;
                }}
                QScrollBar:vertical {{
                    background-color: transparent;
                    width: 16px;
                    margin: 8px 0px 7px 0px;
                }}
                QScrollBar::handle:vertical {{
                    background-color: {c['scrollbar_handle']};
                    border-radius: 8px;
                    min-height: 30px;
                    margin: 2px;
                }}
                QScrollBar::handle:vertical:hover {{
                    background-color: {c['scrollbar_hover']};
                }}
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                    border: none;
                    background: none;
                    height: 0px;
                }}
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                    background: none;
                }}
            """)
        
        btn_style = f"""
            QPushButton {{
                background-color: {c['bg_pressed']};
                border: none;
                border-radius: 8px;
                color: {c['text_primary']};
                font-size: 16px;
                font-weight: bold;
                outline: none;
            }}
            QPushButton:hover {{ background-color: {c['bg_hover']}; }}
            QPushButton:pressed {{ background-color: {c['border_hover']}; }}
        """
        
        btn_style_with_padding = f"""
            QPushButton {{
                background-color: {c['bg_pressed']};
                border: none;
                border-radius: 8px;
                color: {c['text_primary']};
                font-size: 16px;
                font-weight: bold;
                outline: none;
            }}
            QPushButton:hover {{ background-color: {c['bg_hover']}; }}
            QPushButton:pressed {{ background-color: {c['border_hover']}; }}
        """
        
        if hasattr(self, 'scan_button'):
            self.scan_button.setStyleSheet(btn_style)
            self.update_scan_button_icon(False)
        if hasattr(self, 'view_mode_button'):
            self.view_mode_button.setStyleSheet(btn_style_with_padding)
            self.update_view_mode_button()
        
        if hasattr(self, 'category_filter') and hasattr(self.category_filter, 'apply_theme'):
            self.category_filter.apply_theme()
        
        if hasattr(self, 'info_panel') and hasattr(self.info_panel, 'apply_theme'):
            self.info_panel.apply_theme()
        
        self.display_programs()
        
        self.update()
        if hasattr(self, 'programs_content'):
            self.programs_content.update()
    
    def toggle_view_mode(self):
        """Переключение режима просмотра между плиткой и списком"""
        from settings_manager import settings_manager
        
        self.view_mode = "list" if self.view_mode == "grid" else "grid"
        
        settings_manager.set_setting("view_mode", self.view_mode)
        
        if hasattr(self, 'main_window') and hasattr(self.main_window, 'drivers_tab'):
            self.main_window.drivers_tab.sync_view_mode(self.view_mode)
        
        self.update_view_mode_button()
        
        # Перерисовываем программы
        self.display_programs()
    
    def update_view_mode_button(self):
        """Обновление иконки и подсказки кнопки режима просмотра"""
        from resource_path import get_icon_path
        from PyQt6.QtGui import QIcon, QPixmap
        from PyQt6.QtCore import QSize
        from theme_manager import theme_manager, colorize_pixmap

        icon_name = "iconlist.png" if self.view_mode == "grid" else "icontab.png"
        icon_path = get_icon_path(icon_name)
        if icon_path:
            original_pixmap = QPixmap(icon_path)
            if not original_pixmap.isNull():
                scaled_pixmap = original_pixmap.scaled(21, 21, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                if theme_manager.is_light():
                    scaled_pixmap = colorize_pixmap(scaled_pixmap, theme_manager.colors['text_secondary'])
                self.view_mode_button.setIcon(QIcon(scaled_pixmap))
                self.view_mode_button.setIconSize(QSize(21, 21))
                self.view_mode_button.setText("")
            else:
                self.view_mode_button.setText("☰" if self.view_mode == "grid" else "⊞")
        else:
            self.view_mode_button.setText("☰" if self.view_mode == "grid" else "⊞")

        self.view_mode_button.setToolTip(t("view_mode.switch_to_list") if self.view_mode == "grid" else t("view_mode.switch_to_grid"))

    def sync_view_mode(self, mode):
        """Синхронизация режима просмотра с другой вкладкой"""
        if self.view_mode != mode:
            self.view_mode = mode
            self.update_view_mode_button()
            self.display_programs()

    def update_scan_button_icon(self, scanning=False):
        """Обновление иконки кнопки сканирования"""
        from resource_path import get_icon_path
        from PyQt6.QtGui import QIcon, QPixmap
        from PyQt6.QtCore import QSize
        from theme_manager import theme_manager, colorize_pixmap

        update_icon_path = get_icon_path("update.png")
        if update_icon_path:
            pixmap = QPixmap(update_icon_path)
            if theme_manager.is_light():
                pixmap = colorize_pixmap(pixmap, theme_manager.colors['text_secondary'])
            self.scan_button.setIcon(QIcon(pixmap))
            self.scan_button.setIconSize(QSize(18, 18))
            self.scan_button.setText("")
        else:
            if scanning:
                self.scan_button.setText("⟳")
            else:
                self.scan_button.setText("⟲")

    def resizeEvent(self, event):
        """Обработка изменения размера окна"""
        super().resizeEvent(event)
        
        window_width = self.width()
        if window_width >= 1600:
            new_columns = 4
        else:
            new_columns = 3
        
        if hasattr(self, 'current_columns') and new_columns != self.current_columns:
            self.current_columns = new_columns
            if hasattr(self, 'filtered_programs') and self.filtered_programs:
                self.display_programs()
    def start_system_scan(self):
        """Запуск сканирования системы"""
        if self.scan_in_progress:
            return
        
        self.scan_in_progress = True
        self.update_scan_button_icon(True)  
        self.scan_button.setEnabled(False)
        
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self.perform_scan)
    
    def perform_scan(self):
        """Выполнение сканирования в отдельном потоке"""
        try:
            success = self.status_manager.perform_system_scan()
            if success and hasattr(self, 'all_programs'):
                self.status_manager.check_programs_status(self.all_programs)
                self.display_programs()
        except Exception as e:
            log_error(f"Ошибка сканирования: {e}")
        finally:
            self.scan_in_progress = False
            self.update_scan_button_icon(False) 
            self.scan_button.setEnabled(True)
    
    def cleanup(self):
        """Очистка ресурсов при закрытии вкладки"""
        try:
            if self.background_scanner and self.background_scanner.isRunning():
                self.background_scanner.quit()
                self.background_scanner.wait(3000)  # Ждем максимум 3 секунды
                if self.background_scanner.isRunning():
                    self.background_scanner.terminate()
                    self.background_scanner.wait(1000)
                self.background_scanner = None
            
            if hasattr(self, 'combo_box') and self.combo_box:
                self.combo_box.currentIndexChanged.disconnect()
            
            # Очищаем анимации
            if hasattr(self, 'info_panel') and self.info_panel:
                if hasattr(self.info_panel, 'fade_animation'):
                    self.info_panel.fade_animation.stop()
                    
        except Exception as e:
            log_error(f"Ошибка при очистке ProgramsTab: {e}")
    
    def update_translations(self):
        """Обновление переводов при смене языка"""
        from localization import t, translate_category
        
        if hasattr(self, 'title_label'):
            self.title_label.setText(t("tabs.programs"))
        
        if hasattr(self, 'search_input'):
            self.search_input.setPlaceholderText(t("search.programs_placeholder"))
        
        if hasattr(self, 'category_filter'):
            current_data = self.category_filter.currentData()
            
            self.category_filter.clear()
            self.category_filter.addItem(t("categories.all"), "")
            self.category_filter.addItem(t("categories.favorites"), "favorites")
            
            categories_set = set()
            for program in self.all_programs:
                if "category" in program:
                    categories = program["category"].split(",")
                    for cat in categories:
                        cat = cat.strip()
                        if cat:
                            categories_set.add(cat)
            
            for category in sorted(categories_set):
                translated_category = translate_category(category)
                self.category_filter.addItem(translated_category, category)
            
            for i, (text, data) in enumerate(self.category_filter.items):
                if data == current_data:
                    self.category_filter.setCurrentIndex(i)
                    break
        
        self.display_programs()
        
        if hasattr(self, 'info_panel') and self.info_panel.isVisible():
            self.info_panel.refresh_content()
    
    def __del__(self):
        """Деструктор"""
        self.cleanup()