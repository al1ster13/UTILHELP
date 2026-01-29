from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QPushButton, QHBoxLayout, QFrame, QGridLayout, QLineEdit, QDialog, QGraphicsOpacityEffect, QComboBox, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal
from PyQt6.QtGui import QPixmap
from scroll_helper import configure_scroll_area
from download_manager import InstallationManager, CustomMessageBox
from resource_path import get_db_path
from gpu_detector import GPUDetector, CPUDetector
from scroll_helper import configure_scroll_area
from favorites_manager import FavoritesManager
from system_scanner import CachedInstallationStatusManager, BackgroundScanner


class CustomComboBox(QWidget):
    """Выпадающий список"""
    currentIndexChanged = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = []
        self.current_index = 0
        self.is_open = False
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self.button = QPushButton()
        self.button.setFixedHeight(35)
        self.button.setFixedWidth(200)
        self.button.clicked.connect(self.toggle_dropdown)
        self.button.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid transparent;
                border-radius: 8px;
                padding: 8px 15px;
                color: #ffffff;
                font-size: 14px;
                text-align: left;
                outline: none;
            }
            QPushButton:hover {
                background-color: #353535;
                border: 1px solid transparent;
            }
            QPushButton:focus {
                background-color: #353535;
                border: 1px solid transparent;
                outline: none;
            }
        """)
        
        button_container = QWidget()
        button_container.setFixedSize(200, 35)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addWidget(self.button)
        
        self.arrow_label = QLabel("▼")
        self.arrow_label.setFixedSize(20, 35)
        self.arrow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.arrow_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 10px;
                background: transparent;
                border: none;
            }
        """)
        self.arrow_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.arrow_label.setParent(button_container)
        self.arrow_label.move(175, 0)
        
        self.layout.addWidget(button_container)
        
        self.dropdown = QListWidget()
        self.dropdown.setFixedWidth(192)  
        self.dropdown.setMaximumHeight(300)  
        self.dropdown.hide()
        self.dropdown.itemClicked.connect(self.item_selected)
        
        self.dropdown.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.dropdown.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        configure_scroll_area(self.dropdown)
        
        self.dropdown.setStyleSheet("""
            QListWidget {
                background-color: #2d2d2d;
                border: none;
                color: #ffffff;
                outline: none;
                font-size: 14px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px 11px;
                border: none;
                margin: 1px;
                border-radius: 4px;
                min-height: 20px;
            }
            QListWidget::item:hover {
                background-color: #404040;
            }
            QListWidget::item:selected {
                background-color: #404040;
            }
        """)
        

        self.opacity_effect = QGraphicsOpacityEffect()
        self.dropdown.setGraphicsEffect(self.opacity_effect)
        
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(150)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def keyPressEvent(self, event):
        """Обработка нажатий клавиш"""
        if event.key() == Qt.Key.Key_Escape and self.is_open:
            self.hide_dropdown()
        else:
            super().keyPressEvent(event)
    
    def eventFilter(self, obj, event):
        """Фильтр событий для закрытия списка при клике вне его"""
        if event.type() == event.Type.MouseButtonPress and self.is_open:
            if (obj != self.dropdown and obj != self.button and 
                not self.dropdown.isAncestorOf(obj) and 
                not self.button.isAncestorOf(obj) and
                obj != self.arrow_label):  
                self.hide_dropdown()
        return super().eventFilter(obj, event)
    
    def addItem(self, text, data=None):
        """Добавить элемент в список"""
        self.items.append({"text": text, "data": data})
        
        item = QListWidgetItem(text)
        if data is not None:
            item.setData(Qt.ItemDataRole.UserRole, data)
        self.dropdown.addItem(item)
        
        if len(self.items) == 1:
            self.button.setText(text)
    
    def currentData(self):
        """Получить данные текущего элемента"""
        if 0 <= self.current_index < len(self.items):
            return self.items[self.current_index]["data"]
        return None
    
    def setCurrentIndex(self, index):
        """Установить текущий индекс"""
        if 0 <= index < len(self.items):
            self.current_index = index
            self.button.setText(self.items[index]["text"])
            self.dropdown.setCurrentRow(index)
    
    def toggle_dropdown(self):
        """Переключить видимость выпадающего списка"""
        if self.is_open:
            self.hide_dropdown()
        else:
            self.show_dropdown()
    
    def show_dropdown(self):
        """Показать выпадающий список"""
        if self.is_open:
            return
        
        self.is_open = True
        self.arrow_label.setText("▲")
        
        try:
            self.fade_animation.finished.disconnect()
        except:
            pass
        
        if self.parent():
            self.dropdown.setParent(self.parent())
        
        button_global_pos = self.button.mapToGlobal(self.button.rect().bottomLeft())
        parent_global_pos = self.parent().mapToGlobal(self.parent().rect().topLeft())
        
        relative_x = button_global_pos.x() - parent_global_pos.x() + 4
        relative_y = button_global_pos.y() - parent_global_pos.y() + 5
        
        self.dropdown.move(relative_x, relative_y)
        self.dropdown.show()
        self.dropdown.raise_()  
        
        if self.parent():
            main_window = self.parent()
            while main_window.parent():
                main_window = main_window.parent()
            main_window.installEventFilter(self)
            
            for child in main_window.findChildren(QWidget):
                child.installEventFilter(self)
        
        self.setFocus()
        
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()
    
    def hide_dropdown(self):
        """Скрыть выпадающий список"""
        if not self.is_open:
            return
        
        self.is_open = False
        self.arrow_label.setText("▼")
        
        if self.parent():
            main_window = self.parent()
            while main_window.parent():
                main_window = main_window.parent()
            main_window.removeEventFilter(self)
            
            for child in main_window.findChildren(QWidget):
                child.removeEventFilter(self)
        
        try:
            self.fade_animation.finished.disconnect()
        except:
            pass
        
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.finished.connect(self._on_hide_finished)
        self.fade_animation.start()
    
    def _on_hide_finished(self):
        """Завершение анимации скрытия"""
        self.dropdown.hide()
        try:
            self.fade_animation.finished.disconnect()
        except:
            pass
    
    def item_selected(self, item):
        """Обработка выбора элемента"""
        row = self.dropdown.row(item)
        if row != self.current_index:
            self.current_index = row
            self.button.setText(item.text())
            self.currentIndexChanged.emit(row)
        
        self.hide_dropdown()
    
    def clear(self):
        """Очистить список"""
        self.items.clear()
        self.dropdown.clear()
        self.current_index = 0
        self.button.setText("")


class DriverInfoPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(420, 480)  
        self.hide()

        self.main_container = QWidget(self)
        self.main_container.setGeometry(0, 0, 420, 480)
        self.main_container.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-radius: 15px;
            }
        """)
        
        self.layout = QVBoxLayout(self.main_container)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel()
        self.title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 20px;
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        
        close_btn = QPushButton()
        close_btn.setFixedSize(28, 28)  
        close_btn.clicked.connect(self.hide_panel)
        
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
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: #666666;
                    color: #ffffff;
                    border: none;
                    border-radius: 12px;
                    font-size: 14px;
                    font-weight: bold;
                    text-align: center;
                    padding: 0px;
                    outline: none;
                }
                QPushButton:hover {
                    background-color: #777777;
                }
                QPushButton:focus {
                    outline: none;
                    border: none;
                }
            """)
        else:
            close_btn.setText("✕")  
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: #666666;
                    color: #ffffff;
                    border: none;
                    border-radius: 12px;
                    font-size: 14px;
                    font-weight: bold;
                    text-align: center;
                    padding: 0px;
                    outline: none;
                }
                QPushButton:hover {
                    background-color: #777777;
                }
                QPushButton:focus {
                    outline: none;
                    border: none;
                }
            """)

        header_layout.addWidget(close_btn)
        
        self.layout.addLayout(header_layout)
        
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 60px;
                margin: 15px 0px;
                background: transparent;
                border: none;
            }
        """)
        self.layout.addWidget(self.logo_label)
        
        self.category_label = QLabel()
        self.category_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.category_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 14px;
                margin: 5px 0px 5px 0px;
                background: transparent;
                border: none;
            }
        """)
        self.layout.addWidget(self.category_label)
        
        from PyQt6.QtWidgets import QScrollArea
        
        self.desc_label = QLabel()
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                line-height: 1.5;
                background: transparent;
                border: none;
                padding: 0px;
            }
        """)
        
        self.desc_scroll = QScrollArea()
        self.desc_scroll.setWidget(self.desc_label)
        self.desc_scroll.setWidgetResizable(True)
        self.desc_scroll.setFixedHeight(160)  
        self.desc_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.desc_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        configure_scroll_area(self.desc_scroll)
        
        self.desc_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
                margin-left: 3px;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 8px;
                border-radius: 4px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666666;
            }
            QScrollBar::handle:vertical:pressed {
                background-color: #777777;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
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
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: #666666;
                color: #ffffff;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                outline: none;
            }
            QPushButton:hover {
                background-color: #777777;
            }
            QPushButton:pressed {
                background-color: #555555;
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
                color: #bdc3c7;
            }
            QPushButton:focus {
                outline: none;
                border: none;
            }
        """)
        buttons_layout.addWidget(self.download_btn)
        
        self.website_btn = QPushButton("Перейти на сайт разработчика")
        self.website_btn.clicked.connect(self.open_developer_website)
        self.website_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: normal;
                font-size: 12px;
                outline: none;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #666666;
            }
            QPushButton:focus {
                outline: none;
                border: none;
            }
        """)
        buttons_layout.addWidget(self.website_btn)
        
        self.layout.addWidget(self.buttons_container)
        
        self.current_driver_data = None
        
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

    def show_driver(self, driver):
        if self.is_animating:
            return
        
        self.current_driver_data = driver
        
        self.title_label.setText(driver["name"])
        
        from image_helper import load_program_image
        pixmap = load_program_image(driver["logo"])
        if pixmap and not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(scaled_pixmap)
        else:
            self.logo_label.setText("🔧") 
        
        self.category_label.setText(f"Категория: {driver['category']}")
        self.desc_label.setText(driver["description"])
        
        if driver["status"] == "Скоро":
            if driver["button_type"] == "website":
                self.download_btn.setText("Скоро будет доступно")
            else:
                self.download_btn.setText("Скоро будет доступно")
            self.download_btn.setEnabled(False)
        else:
            if driver["button_type"] == "website":
                self.download_btn.setText("Перейти на сайт")
            else:
                self.download_btn.setText("Скачать и установить")
            self.download_btn.setEnabled(True)
        
        if driver.get("website") and driver["website"].strip():
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
        if not self.current_driver_data:
            return
        
        driver = self.current_driver_data
        
        if driver["button_type"] == "website":
            InstallationManager.open_website(driver.get("url", ""), self)
        else:
            download_url = driver.get("url", "")
            if download_url:
                from resource_path import get_program_image_path
                icon_path = get_program_image_path(driver.get("logo", ""))
                
                InstallationManager.install_program(
                    driver["name"], 
                    download_url, 
                    self, 
                    icon_path, 
                    "driver"
                )
            else:
                CustomMessageBox.warning(self, "Ошибка", 
                                  "Ссылка для скачивания не указана!")

    def open_developer_website(self):
        if not self.current_driver_data:
            return
        
        website_url = self.current_driver_data.get("website", "")
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
        self.is_animating = False
        try:
            self.fade_animation.finished.disconnect()
        except:
            pass

    def on_hide_finished(self):
        self.hide()
        self.is_animating = False
        try:
            self.fade_animation.finished.disconnect()
        except:
            pass
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
        
        self.user_gpu_vendor = GPUDetector.detect_gpu_vendor()
        self.user_cpu_vendor = CPUDetector.detect_cpu_vendor()
        print(f"Обнаружен GPU: {self.user_gpu_vendor}")  
        print(f"Обнаружен CPU: {self.user_cpu_vendor}")  
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 10px;
            }
            QScrollBar:vertical {
                background-color: transparent;
                width: 16px;
                border-radius: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 8px;
                min-height: 30px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666666;
            }
            QScrollBar::handle:vertical:pressed {
                background-color: #777777;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        title_label = QLabel("ДРАЙВЕРЫ")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 28px;
                font-weight: bold;
                margin: 20px 0px;
                letter-spacing: 2px;
            }
        """)
        self.layout.addWidget(title_label)
        
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(100, 0, 100, 15)
        search_layout.setSpacing(15)
        
        self.category_filter = CustomComboBox()
        self.category_filter.addItem("Все категории", "")
        self.category_filter.addItem("Избранное", "favorites")
        self.category_filter.currentIndexChanged.connect(self.filter_drivers)
        
        search_layout.addWidget(self.category_filter)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск драйверов...")
        self.search_input.textChanged.connect(self.filter_drivers)
        self.search_input.setFixedHeight(35)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid transparent;
                border-radius: 8px;
                padding: 8px 15px;
                color: #ffffff;
                font-size: 14px;
                outline: none;
            }
            QLineEdit:focus {
                background-color: #353535;
                border: 1px solid transparent;
                outline: none;
            }
        """)
        
        search_layout.addWidget(self.search_input)
        
        from resource_path import get_icon_path
        from PyQt6.QtGui import QIcon
        from PyQt6.QtCore import QSize
        
        self.scan_button = QPushButton()
        self.update_scan_button_icon(False) 
            
        self.scan_button.setFixedSize(35, 35)
        self.scan_button.clicked.connect(self.start_system_scan)
        self.scan_button.setToolTip("Сканировать систему на наличие установленных драйверов\nи отметить их зелеными галочками")
        self.scan_button.setStyleSheet("""
            QPushButton {
                background-color: #666666;
                border: none;
                border-radius: 17px;
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                outline: none;
                padding-left: 2px;
            }
            QPushButton:hover {
                background-color: #777777;
            }
            QPushButton:pressed {
                background-color: #555555;
            }
            QPushButton:disabled {
                background-color: #444444;
                color: #999999;
            }
            QToolTip {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
        """)
        
        search_layout.addWidget(self.scan_button)
        self.layout.addLayout(search_layout)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        configure_scroll_area(self.scroll_area)
        
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: transparent;
                width: 16px;
                margin: 8px 0px 7px 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 8px;
                min-height: 30px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666666;
            }
            QScrollBar::handle:vertical:pressed {
                background-color: #777777;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
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
        self.category_filter.addItem("Все категории", "")
        self.category_filter.addItem("Избранное", "favorites")
        for category in sorted(categories_set):
            self.category_filter.addItem(category, category)
        
        self.filtered_drivers = self.all_drivers.copy()
        
        self.display_drivers()

    def display_drivers(self):
        """Отображение драйверов в виде сетки"""
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

    def create_driver_card(self, driver):
        """Создание карточки драйвера"""
        card = QFrame()
        card.setFixedSize(220, 250)  
        
        def card_mouse_press(event):
            if event.button() == Qt.MouseButton.LeftButton:
                child = card.childAt(event.pos())
                if child and child.objectName() == "favorite_btn":
                    return
                self.show_driver_info(driver)
        
        card.mousePressEvent = card_mouse_press
        
        colors = {
            'bg_secondary': '#252525',
            'bg_button': '#2d2d2d', 
            'border': '#404040',
            'text_primary': '#ffffff'
        }
        
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['bg_secondary']};
                border: none;
                border-radius: 15px;
                padding: 0px;
            }}
            QFrame:hover {{
                background-color: {colors['bg_button']};
                border: 2px solid {colors['border']};
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
            
            # Загружаем иконку installed.png
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
            
            status_label.setStyleSheet("""
                QLabel {
                    background-color: transparent;
                    border: none;
                    min-width: 24px;
                    max-width: 24px;
                    min-height: 24px;
                    max-height: 24px;
                }
                QToolTip {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 12px;
                }
            """)
            status_label.setToolTip(f"Установлен: {status['exact_name']}\nВерсия: {status['version']}")
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
        pixmap = load_program_image(driver["logo"])
        if pixmap and not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label = QLabel()
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label = QLabel("🔧")  
        
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
        logo_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 48px;
                font-family: 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', sans-serif;
                background: transparent;
                border: none;
                qproperty-alignment: AlignCenter;
            }
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
                
                cpu_label = QLabel("⭐ Для вашего CPU")
                cpu_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                cpu_label.setWordWrap(False)
                cpu_label.setFixedWidth(140)
                cpu_label.setStyleSheet("""
                    QLabel {
                        color: #cccccc;
                        font-size: 9px;
                        font-weight: bold;
                        background: rgba(128, 128, 128, 0.1);
                        border: 1px solid #888888;
                        border-radius: 4px;
                        padding: 2px 6px;
                        margin: 1px;
                    }
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
                
                gpu_label = QLabel("⭐ Для вашей GPU")
                gpu_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                gpu_label.setWordWrap(False)
                gpu_label.setFixedWidth(140)
                gpu_label.setStyleSheet("""
                    QLabel {
                        color: #cccccc;
                        font-size: 9px;
                        font-weight: bold;
                        background: rgba(128, 128, 128, 0.1);
                        border: 1px solid #888888;
                        border-radius: 4px;
                        padding: 2px 6px;
                        margin: 1px;
                    }
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
                color: {colors['text_primary']};
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
        
        self.update_favorites_tab()
        
        self.update_favorites_tab()

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
            self.search_input.clearFocus()
        
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
    
    def update_scan_button_icon(self, scanning=False):
        """Обновление иконки кнопки сканирования"""
        from resource_path import get_icon_path
        from PyQt6.QtGui import QIcon
        from PyQt6.QtCore import QSize
        
        update_icon_path = get_icon_path("update.png")
        if update_icon_path:
            icon = QIcon(update_icon_path)
            self.scan_button.setIcon(icon)
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