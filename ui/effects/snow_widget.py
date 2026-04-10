"""
Виджет снегопада
"""
import random
from typing import List, Optional
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QBrush, QColor, QPen
from ui.base.base_widget import BaseWidget


class Snowflake:
    """Класс снежинки"""
    
    def __init__(self, x: float, y: float, size: float, speed: float):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.drift = random.uniform(-0.5, 0.5)  
        self.opacity = random.uniform(0.3, 0.8)


class SnowWidget(BaseWidget):
    """Виджет снегопада"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setStyleSheet("background: transparent;")  
        
        self.snowflakes: List[Snowflake] = []
        self.init_snowflakes()
        
        self.snow_timer = QTimer()
        self.snow_timer.timeout.connect(self.update_snowflakes)
        self.add_cleanup_timer(self.snow_timer)
        self.snow_timer.start(50)  
    
    def init_snowflakes(self) -> None:
        """Инициализация снежинок"""
        for _ in range(30):
            x = random.randint(0, max(1280, self.parent().width() if self.parent() else 1280))
            y = random.randint(-720, 0)
            size = random.randint(3, 8)  
            speed = random.uniform(1, 2.5)  
            self.snowflakes.append(Snowflake(x, y, size, speed))
    
    def reinit_snowflakes_for_size(self, new_width: int, new_height: int) -> None:
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
    
    def update_snowflakes(self) -> None:
        """Обновление позиций снежинок"""
        window_width = self.parent().width() if self.parent() else self.width()
        window_height = self.parent().height() if self.parent() else self.height()
        
        if window_width <= 0 or window_height <= 0:
            return
        
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
    
    def paintEvent(self, event) -> None:
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
            painter.drawLine(x - size//2, y - size//2, x + size//2, y + size//2)  # Диагональ 1
            painter.drawLine(x - size//2, y + size//2, x + size//2, y - size//2)  # Диагональ 2