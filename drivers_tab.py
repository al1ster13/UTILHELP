from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QPushButton, QHBoxLayout, QFrame, QGridLayout, QLineEdit, QDialog, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal
from PyQt6.QtGui import QPixmap, QCursor
from scroll_helper import configure_scroll_area
from download_manager import InstallationManager, CustomMessageBox
from resource_path import get_db_path, get_icon_path
from gpu_detector import GPUDetector, CPUDetector
from favorites_manager import FavoritesManager
from system_scanner import CachedInstallationStatusManager, BackgroundScanner
from localization import t
from ui.components import CatalogComboBox, BaseInfoPanel
from typing import Dict, Any, Optional
import webbrowser


class DriverInfoPanel(BaseInfoPanel):
    """Информационная панель драйвера - наследует BaseInfoPanel"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        self.installation_manager = None
        super().__init__(parent)
    
    def _get_icon_path(self, logo_name: str) -> Optional[str]:
        """Получить путь к иконке драйвера"""
        from logo_manager import get_logo_manager
        logo_manager = get_logo_manager()
        # Получаем путь к кэшированному логотипу или локальному fallback
        return logo_manager.get_cached_logo_path(logo_name)
    
    def _add_custom_info(self, item_data: Dict[str, Any]):
        """Добавить специфичную информацию для драйверов"""
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
                "driver"
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
    
    def show_driver(self, driver: Dict[str, Any]):
        """Показать информацию о драйвере (обратная совместимость)"""
        self.show_item(driver)
class DriversTab(QWidget):

    def __init__(self):
        super().__init__()
        
        self.all_drivers = []
        self.filtered_drivers = []
        self.current_driver = None
        self.current_columns = 3  
        self.favorites_manager = FavoritesManager()
        self.status_manager = CachedInstallationStatusManager()
        self.background_scanner = None
        self.scan_in_progress = False
        
        from settings_manager import settings_manager
        self.view_mode = settings_manager.get_setting("view_mode", "grid")
        
        self.user_gpu_vendor = GPUDetector.detect_gpu_vendor()
        self.user_cpu_vendor = CPUDetector.detect_cpu_vendor()
        print(f"Обнаружен GPU: {self.user_gpu_vendor}")  
        print(f"Обнаружен CPU: {self.user_cpu_vendor}")  
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        from theme_manager import theme_manager
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

        self.title_label = QLabel(t("tabs.drivers"))
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
        self.category_filter.currentIndexChanged.connect(self.filter_drivers)
        
        search_layout.addWidget(self.category_filter)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(t("search.drivers_placeholder"))
        self.search_input.textChanged.connect(self.filter_drivers)
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
        
        self.drivers_content = QWidget()
        self.drivers_grid = QGridLayout(self.drivers_content)
        self.drivers_grid.setContentsMargins(55, 10, 45, 10)  
        self.drivers_grid.setHorizontalSpacing(120)  
        self.drivers_grid.setVerticalSpacing(50)     
        self.drivers_grid.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.drivers_data = []
        
        self.scroll_area.setWidget(self.drivers_content)
        self.layout.addWidget(self.scroll_area)
        
        self.info_panel = DriverInfoPanel(self)
        
        self.update_view_mode_button()

    def set_data(self, drivers_data):
        """Установить данные драйверов из JSON"""
        self.drivers_data = drivers_data
        print(f"Drivers tab: получено {len(drivers_data)} драйверов")
        
        self.all_drivers = []
        categories_set = set()
        
        for driver in drivers_data:
            category_str = driver.get('category', '')
            categories_list = [cat.strip() for cat in category_str.split(',') if cat.strip()]
            
            driver_dict = {
                "name": driver.get('name', ''),
                "description": driver.get('description', ''),
                "description_en": driver.get('description_en', ''),
                "category": category_str,  
                "categories": categories_list,  
                "logo": driver.get('logo', ''),
                "status": driver.get('status', 'Скоро'),
                "keywords": driver.get('keywords', '').split(',') if driver.get('keywords') else [],
                "button_type": driver.get('button_type', 'download'),
                "url": driver.get('url', ''),
                "website": driver.get('website', '')
            }
            self.all_drivers.append(driver_dict)
            
            for cat in categories_list:
                categories_set.add(cat)
        
        self.category_filter.clear()
        self.category_filter.addItem(t("categories.all"), "")
        self.category_filter.addItem(t("categories.favorites"), "favorites")
        for category in sorted(categories_set):
            from localization import translate_category
            translated_category = translate_category(category)
            self.category_filter.addItem(translated_category, category)
        
        self.filtered_drivers = self.all_drivers.copy()
        
        self.display_drivers()

    def display_drivers(self):
        """Отображение драйверов в зависимости от выбранного режима"""
        if self.view_mode == "list":
            self.display_drivers_list()
        else:
            self.display_drivers_grid()
    
    def display_drivers_grid(self):
        """Отображение драйверов в виде сетки"""
        self.drivers_grid.setVerticalSpacing(50)
        self.drivers_grid.setHorizontalSpacing(120)
        
        for i in reversed(range(self.drivers_grid.count())):
            child = self.drivers_grid.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        window_width = self.width()
        if window_width >= 1600:  
            columns = 4
        else:  
            columns = 3
        
        sorted_drivers = sorted(self.filtered_drivers, key=lambda x: x.get('name', '').lower())
        
        row = 0
        col = 0
        for driver in sorted_drivers:
            card = self.create_driver_card(driver)
            self.drivers_grid.addWidget(card, row, col)
            
            col += 1
            if col >= columns:  
                col = 0
                row += 1
    
    def display_drivers_list(self):
        """Отображение драйверов в виде списка"""
        self.drivers_grid.setVerticalSpacing(15)  
        self.drivers_grid.setHorizontalSpacing(0)
        
        for i in reversed(range(self.drivers_grid.count())):
            child = self.drivers_grid.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        sorted_drivers = sorted(self.filtered_drivers, key=lambda x: x.get('name', '').lower())
        
        for row, driver in enumerate(sorted_drivers):
            card = self.create_driver_card_list(driver)
            self.drivers_grid.addWidget(card, row, 0)

    def create_driver_card(self, driver):
        """Создание карточки драйвера"""
        from theme_manager import theme_manager, colorize_pixmap
        c = theme_manager.colors

        card = QFrame()
        card.setFixedSize(220, 250)

        def card_mouse_press(event):
            if event.button() == Qt.MouseButton.LeftButton:
                child = card.childAt(event.pos())
                if child and child.objectName() == "favorite_btn":
                    return
                self.show_driver_info(driver)

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
        
        status = self.status_manager.get_driver_status(driver["name"])
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
            status_label.setToolTip(t("status.installed_short", name=status['exact_name'], version=status['version']))
            top_layout.addWidget(status_label)
        
        top_layout.addStretch()
        
        favorite_btn = QPushButton()
        favorite_btn.setFixedSize(28, 28)
        favorite_btn.setObjectName("favorite_btn")
        is_favorite = self.favorites_manager.is_favorite(driver["name"], "drivers")
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
        favorite_btn.clicked.connect(lambda: self.toggle_favorite(driver, favorite_btn))
        
        def favorite_mouse_press(event):
            event.accept()
            self.toggle_favorite(driver, favorite_btn)
        
        favorite_btn.mousePressEvent = favorite_mouse_press
        
        top_layout.addWidget(favorite_btn)
        card_layout.addWidget(top_container)
        
        from image_helper import load_program_image
        
        logo_label = QLabel("🔧")
        
        def on_logo_loaded(logo_name, pixmap):
            if pixmap and not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                if theme_manager.is_light():
                    scaled_pixmap = colorize_pixmap(scaled_pixmap, c['text_secondary'])
                logo_label.setPixmap(scaled_pixmap)
        
        pixmap = load_program_image(driver["logo"], callback=on_logo_loaded)
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
                background: transparent;
                border: none;
                qproperty-alignment: AlignCenter;
            }}
        """)
        
        card_layout.addWidget(logo_container)
        
        card_layout.addSpacing(26)
        
        recommendation_area = QWidget()
        recommendation_area.setFixedHeight(45)
        recommendation_area.setStyleSheet("background: transparent;")
        recommendation_area_layout = QVBoxLayout(recommendation_area)
        recommendation_area_layout.setContentsMargins(0, 0, 0, 0)
        recommendation_area_layout.setSpacing(2)
        
        show_cpu_recommendation = CPUDetector.should_show_cpu_recommendation(driver["name"], self.user_cpu_vendor)
        show_gpu_recommendation = GPUDetector.should_show_recommendation(driver["name"], self.user_gpu_vendor)
        
        recommendation_container = QWidget()
        recommendation_container.setStyleSheet("background: transparent;")
        recommendation_layout = QVBoxLayout(recommendation_container)  
        recommendation_layout.setContentsMargins(0, 0, 0, 0)
        recommendation_layout.setSpacing(2)
        
        if show_cpu_recommendation or show_gpu_recommendation:
            if show_cpu_recommendation:
                cpu_container = QWidget()
                cpu_container.setStyleSheet("background: transparent;")
                cpu_layout = QHBoxLayout(cpu_container)
                cpu_layout.setContentsMargins(0, 0, 0, 0)
                cpu_layout.addStretch()
                
                cpu_label = QLabel(t("status.for_your_cpu"))
                cpu_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                cpu_label.setWordWrap(False)
                cpu_label.setFixedWidth(140)
                cpu_label.setStyleSheet(f"""
                    QLabel {{
                        color: {c['text_secondary']};
                        font-size: 9px;
                        font-weight: bold;
                        background: {c['bg_tertiary']};
                        border: 1px solid {c['border']};
                        border-radius: 4px;
                        padding: 2px 6px;
                        margin: 1px;
                    }}
                """)
                
                cpu_layout.addWidget(cpu_label)
                cpu_layout.addStretch()
                recommendation_layout.addWidget(cpu_container)
            
            if show_gpu_recommendation:
                gpu_container = QWidget()
                gpu_container.setStyleSheet("background: transparent;")
                gpu_layout = QHBoxLayout(gpu_container)
                gpu_layout.setContentsMargins(0, 0, 0, 0)
                gpu_layout.addStretch()
                
                gpu_label = QLabel(t("status.for_your_gpu"))
                gpu_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                gpu_label.setWordWrap(False)
                gpu_label.setFixedWidth(140)
                gpu_label.setStyleSheet(f"""
                    QLabel {{
                        color: {c['text_secondary']};
                        font-size: 9px;
                        font-weight: bold;
                        background: {c['bg_tertiary']};
                        border: 1px solid {c['border']};
                        border-radius: 4px;
                        padding: 2px 6px;
                        margin: 1px;
                    }}
                """)
                
                gpu_layout.addWidget(gpu_label)
                gpu_layout.addStretch()
                recommendation_layout.addWidget(gpu_container)
            
            recommendation_area_layout.addSpacing(10)
        
        recommendation_area_layout.addWidget(recommendation_container)
        
        recommendation_area_layout.addStretch()
        card_layout.addWidget(recommendation_area)
        
        name_label = QLabel(driver["name"])
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

    def create_driver_card_list(self, driver):
        """Создание горизонтальной карточки драйвера для режима списка"""
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
                self.show_driver_info(driver)

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
        
        logo_label = QLabel("🔧")
        logo_label.setFixedSize(60, 60)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        def on_logo_loaded(logo_name, pixmap):
            if pixmap and not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                if theme_manager.is_light():
                    scaled_pixmap = colorize_pixmap(scaled_pixmap, c['text_secondary'])
                logo_label.setPixmap(scaled_pixmap)
        
        pixmap = load_program_image(driver["logo"], callback=on_logo_loaded)
        if pixmap and not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            if theme_manager.is_light():
                scaled_pixmap = colorize_pixmap(scaled_pixmap, c['text_secondary'])
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label = QLabel("💿")

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

        name_label = QLabel(driver["name"])
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

        if current_language == "en" and "description_en" in driver:
            description = driver.get("description_en", driver.get("description", ""))
        else:
            description = driver.get("description", "")

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

        show_cpu_recommendation = CPUDetector.should_show_cpu_recommendation(driver["name"], self.user_cpu_vendor)
        show_gpu_recommendation = GPUDetector.should_show_recommendation(driver["name"], self.user_gpu_vendor)

        if show_cpu_recommendation or show_gpu_recommendation:
            rec_layout = QVBoxLayout()
            rec_layout.setSpacing(3)
            rec_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            _rec_style = f"""
                QLabel {{
                    color: {c['text_secondary']};
                    font-size: 10px;
                    font-weight: bold;
                    background: {c['bg_tertiary']};
                    border: 1px solid {c['border']};
                    border-radius: 4px;
                    padding: 3px 8px;
                }}
            """
            if show_cpu_recommendation:
                cpu_label = QLabel(t("status.for_your_cpu"))
                cpu_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                cpu_label.setStyleSheet(_rec_style)
                rec_layout.addWidget(cpu_label)

            if show_gpu_recommendation:
                gpu_label = QLabel(t("status.for_your_gpu"))
                gpu_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                gpu_label.setStyleSheet(_rec_style)
                rec_layout.addWidget(gpu_label)

            card_layout.addLayout(rec_layout)
        
        status = self.status_manager.get_driver_status(driver["name"])
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
        is_favorite = self.favorites_manager.is_favorite(driver["name"], "drivers")
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
        favorite_btn.clicked.connect(lambda: self.toggle_favorite(driver, favorite_btn))
        
        def favorite_mouse_press(event):
            event.accept()
            self.toggle_favorite(driver, favorite_btn)
        
        favorite_btn.mousePressEvent = favorite_mouse_press
        
        card_layout.addWidget(favorite_btn)
        
        return card

    def toggle_favorite(self, driver, button):
        """Переключить статус избранного для драйвера"""
        driver_name = driver["name"]
        is_favorite = self.favorites_manager.is_favorite(driver_name, "drivers")
        
        if is_favorite:
            self.favorites_manager.remove_from_favorites(driver_name, "drivers")
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
            self.favorites_manager.add_to_favorites(driver_name, "drivers")
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

    def show_driver_info(self, driver):
        """Показать информационную панель драйвера"""
        if self.current_driver and self.current_driver["name"] == driver["name"]:
            self.info_panel.hide_panel()
            self.current_driver = None
        else:
            self.current_driver = driver
            self.info_panel.show_driver(driver)

    def filter_drivers(self):
        """Фильтрация драйверов по поисковому запросу и категории"""
        search_text = self.search_input.text().lower()
        selected_category = self.category_filter.currentData()
        
        self.filtered_drivers = []
        for driver in self.all_drivers:
            if selected_category == "favorites":
                if not self.favorites_manager.is_favorite(driver["name"], "drivers"):
                    continue
            elif selected_category:
                if selected_category not in driver.get("categories", []):
                    continue
            
            if search_text:
                if not (search_text in driver["name"].lower() or
                        search_text in driver["description"].lower() or
                        search_text in driver["category"].lower() or
                        any(search_text in keyword for keyword in driver["keywords"])):
                    continue
            
            self.filtered_drivers.append(driver)
        
        self.display_drivers()

    
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
        
        self.display_drivers()
        self.search_input.clearFocus()
        
        self.update()
        if hasattr(self, 'drivers_content'):
            self.drivers_content.update()
        
        if hasattr(self, 'category_filter') and hasattr(self.category_filter, 'is_open'):
            if self.category_filter.is_open:
                self.category_filter.hide_dropdown()
        
        if hasattr(self, 'category_filter'):
            self.category_filter.setCurrentIndex(0)
            self.filter_drivers()
        
        if hasattr(self, 'scroll_area'):
            self.scroll_area.verticalScrollBar().setValue(0)
        
        if hasattr(self, 'info_panel') and self.info_panel.isVisible():
            self.info_panel.hide_panel()
            self.current_driver = None
    
    def toggle_view_mode(self):
        """Переключение режима просмотра между плиткой и списком"""
        from settings_manager import settings_manager
        
        self.view_mode = "list" if self.view_mode == "grid" else "grid"
        
        settings_manager.set_setting("view_mode", self.view_mode)
        
        if hasattr(self, 'main_window') and hasattr(self.main_window, 'programs_tab'):
            self.main_window.programs_tab.sync_view_mode(self.view_mode)
        
        self.update_view_mode_button()
        
        self.display_drivers()
    
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
            self.display_drivers()

    
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
            self.scan_button.setText("⟳" if scanning else "⟲")

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
            if hasattr(self, 'filtered_drivers') and self.filtered_drivers:
                self.display_drivers()
    
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
            if success and hasattr(self, 'all_drivers'):
                self.status_manager.check_drivers_status(self.all_drivers)
                self.display_drivers()
        except Exception as e:
            print(f"Ошибка сканирования: {e}")
        finally:
            self.scan_in_progress = False
            self.update_scan_button_icon(False)  
            self.scan_button.setEnabled(True)
    
    def cleanup(self):
        """Очистка ресурсов при закрытии вкладки"""
        try:
            if self.background_scanner and self.background_scanner.isRunning():
                self.background_scanner.quit()
                self.background_scanner.wait(3000)  
                if self.background_scanner.isRunning():
                    self.background_scanner.terminate()
                    self.background_scanner.wait(1000)
                self.background_scanner = None
            
            if hasattr(self, 'combo_box') and self.combo_box:
                self.combo_box.currentIndexChanged.disconnect()
            
            if hasattr(self, 'info_panel') and self.info_panel:
                if hasattr(self.info_panel, 'fade_animation'):
                    self.info_panel.fade_animation.stop()
                    
        except Exception as e:
            print(f"Ошибка при очистке DriversTab: {e}")
    
    def update_translations(self):
        """Обновление переводов при смене языка"""
        from localization import t, translate_category
        
        if hasattr(self, 'title_label'):
            self.title_label.setText(t("tabs.drivers"))
        
        if hasattr(self, 'search_input'):
            self.search_input.setPlaceholderText(t("search.drivers_placeholder"))
        
        if hasattr(self, 'category_filter'):
            current_data = self.category_filter.currentData()
            
            self.category_filter.clear()
            self.category_filter.addItem(t("categories.all"), "")
            self.category_filter.addItem(t("categories.favorites"), "favorites")
            
            categories_set = set()
            for driver in self.all_drivers:
                if "category" in driver:
                    categories = driver["category"].split(",")
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
        
        self.display_drivers()
        
        if hasattr(self, 'info_panel') and self.info_panel.isVisible():
            self.info_panel.refresh_content()
    
    def __del__(self):
        """Деструктор"""
        self.cleanup()