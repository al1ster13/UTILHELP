from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QListWidgetItem, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QCursor
from scroll_helper import configure_scroll_area
from typing import List, Tuple, Optional


class CatalogComboBox(QWidget):
    """
    Кастомный выпадающий список 
    Используется в programs_tab и drivers_tab для фильтрации по категориям
    """
    
    currentIndexChanged = pyqtSignal(int)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.items: List[Tuple[str, str]] = []  
        self.current_index: int = 0
        self.is_open: bool = False
        
        self._setup_ui()
        self._setup_animations()
        self._install_event_filter()
    
    def _setup_ui(self):
        """Настройка UI компонента"""
        from theme_manager import theme_manager
        c = theme_manager.colors

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self.button = QPushButton()
        self.button.setFixedHeight(35)
        self.button.setFixedWidth(207)
        self.button.clicked.connect(self.toggle_dropdown)
        self.button.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['bg_secondary']};
                border: 1px solid transparent;
                border-radius: 8px;
                padding-left: 15px;
                padding-right: 30px;
                color: {c['text_primary']};
                font-size: 14px;
                text-align: left;
                outline: none;
            }}
            QPushButton:hover {{
                background-color: {c['bg_hover']};
                border: 1px solid transparent;
            }}
            QPushButton:focus {{
                background-color: {c['bg_hover']};
                border: 1px solid transparent;
                outline: none;
            }}
        """)
        
        button_container = QWidget()
        button_container.setFixedSize(207, 35)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addWidget(self.button)
        
        self.arrow_label = QLabel("▼")
        self.arrow_label.setFixedSize(20, 35)
        self.arrow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.arrow_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 10px;
                background: transparent;
                border: none;
            }}
        """)
        self.arrow_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.arrow_label.setParent(button_container)
        self.arrow_label.move(182, 0)
        
        self.layout.addWidget(button_container)
        
        self.dropdown = QListWidget()
        self.dropdown.setFixedWidth(207)
        self.dropdown.setMaximumHeight(250)
        self.dropdown.hide()
        self.dropdown.itemClicked.connect(self.item_selected)
        
        self.dropdown.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.dropdown.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        configure_scroll_area(self.dropdown)
        
        self.dropdown.setStyleSheet(f"""
            QListWidget {{
                background-color: {c['bg_secondary']};
                border: none;
                border-radius: 8px;
                color: {c['text_primary']};
                outline: none;
                font-size: 14px;
                padding: 4px;
            }}
            QListWidget::item {{
                padding: 8px 11px;
                border: none;
                margin: 1px;
                border-radius: 6px;
            }}
            QListWidget::item:hover {{
                background-color: {c['bg_hover']};
            }}
            QListWidget::item:selected {{
                background-color: {c['bg_pressed']};
            }}
        """)
        
        self.layout.addWidget(self.dropdown)
    
    def _setup_animations(self):
        """Настройка анимаций"""
        self.opacity_effect = QGraphicsOpacityEffect(self.dropdown)
        self.dropdown.setGraphicsEffect(self.opacity_effect)
        
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(150)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.fade_animation.finished.connect(self._on_animation_finished)
    
    def _install_event_filter(self):
        """Установка фильтра событий для закрытия при клике вне списка"""
        if self.window():
            self.window().installEventFilter(self)
    
    def showEvent(self, event):
        """Обработка события показа виджета"""
        super().showEvent(event)
        self._install_event_filter()
    
    def addItem(self, text: str, data: str = ""):
        """Добавить элемент в список"""
        self.items.append((text, data))
        item = QListWidgetItem(text)
        item.setData(Qt.ItemDataRole.UserRole, data)
        self.dropdown.addItem(item)
        
        if len(self.items) == 1:
            self.button.setText(text)
    
    def clear(self):
        """Очистить список"""
        self.items.clear()
        self.dropdown.clear()
        self.current_index = 0
        self.button.setText("")
    
    def currentData(self) -> str:
        """Получить данные текущего элемента"""
        if 0 <= self.current_index < len(self.items):
            return self.items[self.current_index][1]
        return ""
    
    def setCurrentIndex(self, index: int):
        """Установить текущий индекс"""
        if 0 <= index < len(self.items):
            self.current_index = index
            self.button.setText(self.items[index][0])
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
        
        global_pos = self.button.mapToGlobal(self.button.rect().bottomLeft())
        parent_widget = self.window()
        local_pos = parent_widget.mapFromGlobal(global_pos)
        
        self.dropdown.setParent(parent_widget)
        self.dropdown.move(local_pos.x(), local_pos.y() + 5)
        
        item_height = 35  
        visible_items = min(len(self.items), 8)
        dropdown_height = visible_items * item_height + 8
        
        print(f"DEBUG: item_height={item_height}, visible_items={visible_items}, dropdown_height={dropdown_height}")
        
        self.dropdown.setFixedHeight(dropdown_height)
        
        self.dropdown.show()
        self.dropdown.raise_()
        
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()
    
    def hide_dropdown(self):
        """Скрыть выпадающий список"""
        print(f"DEBUG: hide_dropdown called, is_open={self.is_open}")
        if not self.is_open:
            return
        
        self.is_open = False
        self.arrow_label.setText("▼")
        
        if self.fade_animation.state() == self.fade_animation.State.Running:
            self.fade_animation.stop()
        
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.start()
        print(f"DEBUG: Animation started")
    
    def _on_animation_finished(self):
        """Завершение анимации"""
        print(f"DEBUG: _on_animation_finished called, is_open={self.is_open}, opacity={self.opacity_effect.opacity()}")
        if self.opacity_effect.opacity() < 0.1:
            self.dropdown.hide()
            print(f"DEBUG: Dropdown hidden")
    
    def item_selected(self, item: QListWidgetItem):
        """Обработка выбора элемента"""
        print(f"DEBUG: item_selected called, item={item.text() if item else None}")
        index = self.dropdown.row(item)
        if index != self.current_index:
            self.current_index = index
            self.button.setText(item.text())
            self.currentIndexChanged.emit(index)
        
        print(f"DEBUG: Hiding dropdown immediately")
        self.is_open = False
        self.arrow_label.setText("▼")
        self.dropdown.hide()
        
        self.hide_dropdown()
    
    def mousePressEvent(self, event):
        """Обработка клика мыши"""
        if self.is_open and not self.dropdown.geometry().contains(event.globalPosition().toPoint()):
            self.hide_dropdown()
        super().mousePressEvent(event)
    
    def eventFilter(self, obj, event):
        """Фильтр событий для закрытия dropdown при клике вне его"""
        from PyQt6.QtCore import QEvent
        
        if event.type() == QEvent.Type.MouseButtonPress and self.is_open:
            global_pos = event.globalPosition().toPoint()
            
            button_rect = self.button.rect()
            button_global_rect = self.button.mapToGlobal(button_rect.topLeft())
            button_global_rect = self.button.geometry()
            button_global_rect.moveTopLeft(self.button.mapToGlobal(self.button.rect().topLeft()))
            
            dropdown_rect = self.dropdown.geometry()
            
            if not button_global_rect.contains(global_pos) and not dropdown_rect.contains(global_pos):
                self.hide_dropdown()
        
        return super().eventFilter(obj, event)

    def apply_theme(self):
        """Применить тему к комбобоксу"""
        from theme_manager import theme_manager
        c = theme_manager.colors
        
        self.button.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['bg_secondary']};
                border: 1px solid transparent;
                border-radius: 8px;
                padding-left: 15px;
                padding-right: 30px;
                color: {c['text_primary']};
                font-size: 14px;
                text-align: left;
                outline: none;
            }}
            QPushButton:hover {{
                background-color: {c['bg_hover']};
                border: 1px solid transparent;
            }}
            QPushButton:focus {{
                background-color: {c['bg_hover']};
                border: 1px solid transparent;
                outline: none;
            }}
        """)
        
        self.arrow_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 10px;
                background: transparent;
                border: none;
            }}
        """)
        
        self.dropdown.setStyleSheet(f"""
            QListWidget {{
                background-color: {c['bg_secondary']};
                border: none;
                border-radius: 8px;
                color: {c['text_primary']};
                outline: none;
                font-size: 14px;
                padding: 4px;
            }}
            QListWidget::item {{
                padding: 8px 11px;
                border: none;
                margin: 1px;
                border-radius: 6px;
            }}
            QListWidget::item:hover {{
                background-color: {c['bg_hover']};
            }}
            QListWidget::item:selected {{
                background-color: {c['bg_pressed']};
            }}
        """)
