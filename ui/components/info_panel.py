"""
Базовый класс для информационных панелей программ и драйверов
Устраняет дублирование между ProgramInfoPanel и DriverInfoPanel
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QFrame, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QPixmap, QCursor
from typing import Dict, Any, Optional
from resource_path import get_icon_path
from localization import t


class BaseInfoPanel(QWidget):
    """
    Базовый класс для информационных панелей
    
    Содержит общую логику для отображения информации о программах/драйверах
    Наследники должны реализовать специфичные методы
    """
    
    closed = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.current_item_data: Optional[Dict[str, Any]] = None
        self.is_animating: bool = False
        
        self._setup_ui()
        self._setup_animations()
    
    def _setup_ui(self):
        """Настройка UI панели"""
        self.setFixedSize(420, 480)
        self.hide()
        
        # Главный контейнер с фоном
        self.main_container = QWidget(self)
        self.main_container.setGeometry(0, 0, 420, 480)
        self.main_container.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-radius: 15px;
            }
        """)
        
        container_layout = QVBoxLayout(self.main_container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(15)
        
        # Контент напрямую без скролла
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background-color: transparent;")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(15)
        
        container_layout.addWidget(self.content_widget)
    
    def _setup_animations(self):
        """Настройка анимаций"""
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.fade_animation.finished.connect(self.on_animation_finished)
    
    def show_item(self, item_data: Dict[str, Any]):
        """
        Показать информацию об элементе
        
        Args:
            item_data: Данные программы или драйвера
        """
        if self.is_animating:
            return
        
        self.current_item_data = item_data
        self.is_animating = True
        
        # Очищаем старый контент
        self._clear_content()
        
        self._create_header(item_data)  # Заголовок + иконка
        self._create_info_section(item_data)  # Категория
        self._create_description(item_data)  # Описание
        self._create_buttons(item_data)  # Кнопки
        
        # Позиционируем панель справа
        if self.parent():
            parent_rect = self.parent().rect()
            x = parent_rect.width() - self.width() - 20
            y = (parent_rect.height() - self.height()) // 2
            self.move(x, y)
        
        # Показываем с анимацией
        self.show()
        self.raise_()
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()
    
    def hide_panel(self):
        """Скрыть панель с анимацией"""
        if self.is_animating:
            return
        
        self.is_animating = True
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.start()
    
    def refresh_content(self):
        """Обновить содержимое панели (для смены языка)"""
        if self.current_item_data and self.isVisible():
            # Перерисовываем контент без анимации
            self._clear_content()
            self._create_header(self.current_item_data)
            self._create_info_section(self.current_item_data)
            self._create_description(self.current_item_data)
            self._create_buttons(self.current_item_data)
    
    def on_animation_finished(self):
        """Завершение анимации"""
        self.is_animating = False
        
        if self.opacity_effect.opacity() == 0.0:
            self.hide()
            self.closed.emit()
    
    def _clear_content(self):
        """Очистить контент"""
        # Удаляем все виджеты из layout
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                widget = item.widget()
                widget.setParent(None)
                widget.deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
    
    def _clear_layout(self, layout):
        """Рекурсивно очистить layout"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                widget = item.widget()
                widget.setParent(None)
                widget.deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
    
    def _create_header(self, item_data: Dict[str, Any]):
        """Создать заголовок с названием и кнопкой закрытия"""
        header_layout = QHBoxLayout()
        
        name_label = QLabel(item_data.get("name", ""))
        name_label.setWordWrap(False)
        name_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 20px;
                font-weight: bold;
                background-color: transparent;
            }
        """)
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        
        from resource_path import get_icon_path as get_system_icon
        from PyQt6.QtGui import QIcon
        from PyQt6.QtCore import QSize
        
        close_btn = QPushButton()
        close_btn.setFixedSize(28, 28)
        close_btn.clicked.connect(self.hide_panel)
        
        close_icon_path = get_system_icon("closemenu.png")
        if close_icon_path:
            icon = QIcon(close_icon_path)
            close_btn.setIcon(icon)
            close_btn.setIconSize(QSize(16, 16))
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
            }
            QPushButton:hover {
                background-color: #777777;
            }
        """)
        
        header_layout.addWidget(close_btn)
        
        self.content_layout.addLayout(header_layout)
        
        icon_container = QWidget()
        icon_container.setFixedHeight(120)
        icon_container.setStyleSheet("background-color: transparent;")
        icon_container_layout = QVBoxLayout(icon_container)
        icon_container_layout.setContentsMargins(0, 0, 0, 0)
        icon_container_layout.setSpacing(0)
        
        # Большая иконка по центру
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo_name = item_data.get("logo", "")
        if logo_name:
            icon_path = self._get_icon_path(logo_name)
            if icon_path:
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    icon_label.setPixmap(scaled_pixmap)
                else:
                    icon_label.setText("📦")
                    icon_label.setStyleSheet("""
                        QLabel {
                            color: #ffffff;
                            font-size: 60px;
                            background-color: transparent;
                        }
                    """)
            else:
                icon_label.setText("📦")
                icon_label.setStyleSheet("""
                    QLabel {
                        color: #ffffff;
                        font-size: 60px;
                        background-color: transparent;
                    }
                """)
        
        icon_label.setStyleSheet(icon_label.styleSheet() + "background-color: transparent;")
        
        # Центрируем иконку в контейнере
        icon_container_layout.addStretch()
        icon_container_layout.addWidget(icon_label)
        icon_container_layout.addStretch()
        
        self.content_layout.addWidget(icon_container)
    
    def _create_description(self, item_data: Dict[str, Any]):
        """Создать описание в скролл-области"""
        from localization import get_localized_description
        
        description = get_localized_description(item_data)
        if description:
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    font-size: 14px;
                    line-height: 1.5;
                    background-color: transparent;
                    padding: 0px;
                }
            """)
            
            # Скролл-область для описания
            from scroll_helper import configure_scroll_area
            desc_scroll = QScrollArea()
            desc_scroll.setWidget(desc_label)
            desc_scroll.setWidgetResizable(True)
            desc_scroll.setFixedHeight(140)
            desc_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            desc_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            
            configure_scroll_area(desc_scroll)
            
            desc_scroll.setStyleSheet("""
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
            
            self.content_layout.addWidget(desc_scroll)
    
    def _create_info_section(self, item_data: Dict[str, Any]):
        """Создать секцию с дополнительной информацией"""
        # Категория
        category = item_data.get("category", "")
        if category:
            # Переводим каждую категорию (может быть несколько через запятую)
            from localization import translate_category
            categories = [cat.strip() for cat in category.split(',')]
            translated_categories = [translate_category(cat) for cat in categories]
            translated_category_str = ', '.join(translated_categories)
            
            category_label = QLabel(t("info.category", category=translated_category_str))
            category_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            category_label.setStyleSheet("""
                QLabel {
                    color: #cccccc;
                    font-size: 14px;
                    margin: 5px 0px 5px 0px;
                    background-color: transparent;
                }
            """)
            self.content_layout.addWidget(category_label)
        
        # Дополнительная информация от наследников
        self._add_custom_info(item_data)
    
    def _add_info_row(self, icon: str, text: str):
        """Добавить строку информации"""
        row_layout = QHBoxLayout()
        row_layout.setSpacing(10)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                background-color: transparent;
            }
        """)
        row_layout.addWidget(icon_label)
        
        text_label = QLabel(text)
        text_label.setWordWrap(True)
        text_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 14px;
                background-color: transparent;
            }
        """)
        row_layout.addWidget(text_label, 1)
        
        self.content_layout.addLayout(row_layout)
    
    def _create_buttons(self, item_data: Dict[str, Any]):
        """Создать кнопки действий"""
        buttons_container = QWidget()
        buttons_container.setFixedHeight(100)
        buttons_container.setStyleSheet("background: transparent;")
        buttons_layout = QVBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 10, 0, 0)
        buttons_layout.setSpacing(5)
        
        buttons_layout.addStretch()
        
        # Основная кнопка
        main_button = self._create_main_button(item_data)
        if main_button:
            buttons_layout.addWidget(main_button)
        
        # Дополнительная кнопка (сайт разработчика)
        if item_data.get("website"):
            website_button = self._create_website_button(item_data)
            buttons_layout.addWidget(website_button)
        
        self.content_layout.addWidget(buttons_container)
    
    def _get_icon_path(self, logo_name: str) -> Optional[str]:
        """Получить путь к иконке (реализуется в наследниках)"""
        raise NotImplementedError("Subclasses must implement _get_icon_path")
    
    def _add_custom_info(self, item_data: Dict[str, Any]):
        """Добавить специфичную информацию (реализуется в наследниках)"""
        raise NotImplementedError("Subclasses must implement _add_custom_info")
    
    def _create_main_button(self, item_data: Dict[str, Any]) -> Optional[QPushButton]:
        """Создать основную кнопку действия (реализуется в наследниках)"""
        raise NotImplementedError("Subclasses must implement _create_main_button")
    
    def _create_website_button(self, item_data: Dict[str, Any]) -> QPushButton:
        """Создать кнопку сайта разработчика (реализуется в наследниках)"""
        raise NotImplementedError("Subclasses must implement _create_website_button")
