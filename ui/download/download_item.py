"""
Элемент загрузки
"""
from typing import Optional, Any
from ui.base.base_widget import BaseWidget


class DownloadItem(BaseWidget):
    """Элемент загрузки - каждый файл имеет свой прогресс и управление"""
    
    def __init__(
        self, 
        filename: str, 
        program_name: str, 
        file_type: str = "program", 
        icon_path: Optional[str] = None,
        parent: Optional[Any] = None
    ):
        super().__init__(parent)
        self.filename = filename
        self.program_name = program_name
        self.file_type = file_type
        self.icon_path = icon_path
        self.download_progress = 0
        self.download_speed = ""
        self.file_size = ""
        self.status = "pending"  # pending, downloading, completed, failed
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Настройка интерфейса элемента загрузки"""
        from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QProgressBar, QPushButton
        from PyQt6.QtGui import QPixmap
        from PyQt6.QtCore import Qt
        from resource_path import get_icon_path
        from theme_manager import theme_manager
        c = theme_manager.colors
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)
        
        icon_path = self.icon_path if self.icon_path else "file.png"
        full_icon_path = get_icon_path(icon_path)
        
        icon_label = QLabel()
        if full_icon_path:
            pixmap = QPixmap(full_icon_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, 
                                             Qt.TransformationMode.SmoothTransformation)
                icon_label.setPixmap(scaled_pixmap)
        icon_label.setFixedSize(32, 32)
        layout.addWidget(icon_label)
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        self.name_label = QLabel(self.filename)
        self.name_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 13px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
        """)
        info_layout.addWidget(self.name_label)
        
        self.progress_label = QLabel("0% • 0 KB/s")
        self.progress_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_hint']};
                font-size: 11px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
        """)
        info_layout.addWidget(self.progress_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(150)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {c['bg_input']};
                border: none;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {c['accent']};
                border-radius: 4px;
            }}
        """)
        layout.addWidget(self.progress_bar)
        
        self.action_btn = QPushButton("✕")
        self.action_btn.setFixedSize(28, 28)
        self.action_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['download_btn']};
                color: white;
                border: none;
                border-radius: 14px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {c['error']}; }}
            QPushButton:pressed {{ background-color: {c['error']}; }}
        """)
        self.action_btn.clicked.connect(self.cancel_download)
        layout.addWidget(self.action_btn)
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {c['bg_card']};
                border-radius: 8px;
            }}
        """)
        self.setFixedHeight(70)
    
    def update_progress(self, progress: int) -> None:
        """Обновить прогресс загрузки"""
        self.download_progress = progress
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setValue(progress)
        if hasattr(self, 'progress_label'):
            speed_text = f" • {self.download_speed}" if self.download_speed else ""
            self.progress_label.setText(f"{progress}%{speed_text}")
        self.log_debug(f"Download progress for {self.filename}: {progress}%")
    
    def update_speed(self, speed: str) -> None:
        """Обновить скорость загрузки"""
        self.download_speed = speed
        if hasattr(self, 'progress_label'):
            self.progress_label.setText(f"{self.download_progress}% • {speed}")
    
    def update_file_size(self, size: str) -> None:
        """Обновить размер файла"""
        self.file_size = size
    
    def set_status(self, status: str) -> None:
        """Установить статус загрузки"""
        self.status = status
        
        # Обновить UI в зависимости от статуса
        if hasattr(self, 'action_btn'):
            if status == "completed":
                self.action_btn.setText("✓")
                self.action_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #27ae60;
                        color: white;
                        border: none;
                        border-radius: 14px;
                        font-size: 14px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #229954;
                    }
                """)
            elif status == "failed":
                self.action_btn.setText("!")
                self.action_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border: none;
                        border-radius: 14px;
                        font-size: 14px;
                        font-weight: bold;
                    }
                """)
        
        if hasattr(self, 'progress_bar') and status == "completed":
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    background-color: #2d2d2d;
                    border: none;
                    border-radius: 4px;
                }
                QProgressBar::chunk {
                    background-color: #27ae60;
                    border-radius: 4px;
                }
            """)
        
        self.log_info(f"Download status for {self.filename}: {status}")
    
    def cancel_download(self) -> None:
        """Отменить загрузку"""
        self.set_status("cancelled")
        self.log_info(f"Download cancelled: {self.filename}")
    
    def get_download_info(self) -> dict:
        """Получить информацию о загрузке"""
        return {
            "filename": self.filename,
            "program_name": self.program_name,
            "file_type": self.file_type,
            "progress": self.download_progress,
            "speed": self.download_speed,
            "size": self.file_size,
            "status": self.status
        }