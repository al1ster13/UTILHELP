"""
Переключатели для настроек
"""
from typing import Optional
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, pyqtProperty
from PyQt6.QtGui import QPainter, QBrush, QColor
from ui.base.base_widget import BaseWidget


class ToggleSwitch(BaseWidget):
    """Переключатель"""
    toggled = pyqtSignal(bool)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFixedSize(40, 20)
        self.checked = False
        self._position = 4
        
        self.animation = QPropertyAnimation(self, b"position")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def setChecked(self, checked: bool) -> None:
        """Установить состояние переключателя"""
        if self.checked != checked:
            self.checked = checked
            self._position = 24 if self.checked else 4
            self.update()
    
    def isChecked(self) -> bool:
        """Получить состояние переключателя"""
        return self.checked
    
    def animate_toggle(self) -> None:
        """Анимация переключения"""
        if self.animation.state() == QPropertyAnimation.State.Running:
            self.animation.stop()
        
        self.animation.setStartValue(self._position)
        self.animation.setEndValue(24 if self.checked else 4)
        self.animation.start()
    
    def mousePressEvent(self, event) -> None:
        """Обработка клика мыши"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.checked = not self.checked
            self.animate_toggle()
            self.toggled.emit(self.checked)
    
    def paintEvent(self, event) -> None:
        """Отрисовка переключателя"""
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
    def position(self) -> float:
        """Свойство позиции для анимации"""
        return self._position
    
    @position.setter
    def position(self, value: float) -> None:
        """Установка позиции"""
        self._position = value
        self.update()


class DisabledToggleSwitch(ToggleSwitch):
    """Переключатель который не меняет состояние при клике - для функций в разработке"""
    
    def mousePressEvent(self, event) -> None:
        """Обработка клика - не меняет состояние"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggled.emit(self.checked)