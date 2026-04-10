import os
import subprocess
import tempfile
import urllib.request
from urllib.parse import urlparse
import shutil
import time
import traceback
import ssl
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QProgressBar, QMessageBox, QWidget, QApplication, QScrollArea, QTextEdit)
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt6.QtGui import QPixmap, QPainter, QBrush, QColor
from temp_manager import get_temp_manager
from notification_manager import get_notification_manager
from logger import log_info, log_error, log_warning, log_debug


class CustomProgressBar(QWidget):
    """Прогресс бар"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(28)
        self.value = 0
        self.maximum = 100
        self.minimum = 0
        
    def setValue(self, value):
        self.value = max(self.minimum, min(self.maximum, value))
        self.update()
        
    def setMaximum(self, maximum):
        self.maximum = maximum
        self.update()
        
    def setMinimum(self, minimum):
        self.minimum = minimum
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        bg_rect = self.rect()
        painter.setBrush(QBrush(QColor(37, 37, 37))) 
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(bg_rect, 14, 14)
        
        if self.value > self.minimum:
            progress_ratio = (self.value - self.minimum) / (self.maximum - self.minimum)
            progress_width = int(progress_ratio * (self.width() - 6))
            progress_width = max(28, progress_width)  
            
            progress_rect = bg_rect.adjusted(3, 3, -self.width() + progress_width + 3, -3)
            painter.setBrush(QBrush(QColor(102, 102, 102))) 
            painter.drawRoundedRect(progress_rect, 11, 11)
        
        painter.setPen(QColor(255, 255, 255)) 
        painter.setFont(self.font())
        text = f"{int(self.value)}%"
        painter.drawText(bg_rect, Qt.AlignmentFlag.AlignCenter, text)
        
        painter.end()


class CustomMessageBox(QDialog):
    """Окно сообщений"""
    
    def __init__(self, title, message, icon_type="warning", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(600, 300)
        self.setMaximumSize(900, 700)
        self.resize(700, 400)  
        
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(20)
        
        header_layout = QHBoxLayout()
        
        icon_text = "!" if icon_type == "warning" else "×" if icon_type == "error" else "i"
        icon_label = QLabel(icon_text)
        icon_label.setStyleSheet("""
            font-size: 24px;
            margin-right: 10px;
            color: #ff6b6b;
        """)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: #ffffff;
            font-size: 16px;
            font-weight: bold;
        """)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
                
        message_widget = QTextEdit()
        message_widget.setPlainText(message)
        message_widget.setReadOnly(True)
        message_widget.setMinimumHeight(200)
        message_widget.setStyleSheet("""
            QTextEdit {
                color: #cccccc;
                font-size: 13px;
                font-family: 'Consolas', 'Courier New', monospace;
                background-color: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 15px;
                line-height: 1.5;
            }
            QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 14px;
                border-radius: 7px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 6px;
                min-height: 20px;
                margin: 1px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666666;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        layout.addWidget(message_widget)
        
        button_layout = QHBoxLayout()
        
        copy_btn = QPushButton("Копировать")
        copy_btn.clicked.connect(lambda: self.copy_to_clipboard(message))
        copy_btn.setFixedHeight(35)
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                color: #ffffff;
                border: none;
                padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QPushButton:pressed {
                background-color: #333333;
            }
            QPushButton:focus {
                outline: none;
                border: none;
            }
        """)
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setFixedHeight(35)
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #0d7377;
                color: #ffffff;
                border: none;
                padding: 8px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #14a085;
            }
            QPushButton:pressed {
                background-color: #0a5d61;
            }
            QPushButton:focus {
                outline: none;
                border: none;
            }
        """)
        
        button_layout.addWidget(copy_btn)
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        layout.addLayout(button_layout)
    
    def copy_to_clipboard(self, text):
        """Копировать текст в буфер обмена"""
        try:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
        except:
            pass
    
    @staticmethod
    def warning(parent, title, message):
        """Показать предупреждение"""
        dialog = CustomMessageBox(title, message, "warning", parent)
        return dialog.exec()
    
    @staticmethod
    def critical(parent, title, message):
        """Показать ошибку"""
        dialog = CustomMessageBox(title, message, "error", parent)
        return dialog.exec()
    
    @staticmethod
    def information(parent, title, message):
        """Показать информацию"""
        dialog = CustomMessageBox(title, message, "info", parent)
        return dialog.exec()


class DownloadThread(QThread):
    """Поток для скачивания файлов"""
    progress_updated = pyqtSignal(int, str, str)  
    download_finished = pyqtSignal(str)  
    download_error = pyqtSignal(str)  
    
    def __init__(self, url, filename):
        super().__init__()
        self.url = url
        self.filename = filename
        
        from temp_manager import get_temp_manager
        temp_manager = get_temp_manager()
        self.temp_dir = temp_manager.get_temp_dir()
        
        try:
            os.makedirs(self.temp_dir, exist_ok=True)
        except Exception as e:
            log_error(f"Ошибка создания временной папки: {e}")
        
        safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-()[]{}") or "download.tmp"
        self.file_path = os.path.join(self.temp_dir, safe_filename)
        
        try:
            from logger import log_info
            log_info(f"DownloadThread: temp_dir = {self.temp_dir}")
            log_info(f"DownloadThread: file_path = {self.file_path}")
        except:
            pass
    
    def run(self):
        """Скачивание файла"""
        self.cancelled = False
        self.start_time = None
        self.last_update_time = None
        self.last_downloaded = 0
        self.speed_samples = []  
        self.update_interval = 0.5  
        
        try:
            import ssl
            
            if not self.url or not isinstance(self.url, str):
                self.download_error.emit("Ошибка: некорректный URL")
                return
                
            parsed_url = urlparse(self.url)
            if parsed_url.scheme not in ['http', 'https']:
                self.download_error.emit(f"Ошибка: неподдерживаемый протокол {parsed_url.scheme}")
                return
                
            if parsed_url.scheme == 'http':
                log_warning(f"Загрузка по небезопасному HTTP протоколу: {self.url}")
            
            if not self.file_path:
                self.download_error.emit("Ошибка: не удалось создать путь для файла")
                return
            
            dir_path = os.path.dirname(self.file_path)
            if not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path, exist_ok=True)
                except Exception as e:
                    self.download_error.emit(f"Ошибка создания папки: {e}")
                    return
            
            if not os.access(dir_path, os.W_OK):
                self.download_error.emit(f"Нет прав на запись в папку: {dir_path}")
                return
            
            self.start_time = time.time()
            self.last_update_time = self.start_time
            
            def progress_hook(block_num, block_size, total_size):
                if self.cancelled:
                    return
                
                current_time = time.time()
                downloaded = block_num * block_size
                
                if total_size > 0:
                    percent = min(int((downloaded / total_size) * 100), 100)
                    
                    if current_time - self.last_update_time >= self.update_interval:
                        time_diff = current_time - self.last_update_time
                        bytes_diff = downloaded - self.last_downloaded
                        
                        if time_diff > 0 and bytes_diff > 0:
                            current_speed = bytes_diff / time_diff
                            
                            self.speed_samples.append(current_speed)
                            if len(self.speed_samples) > 5:
                                self.speed_samples.pop(0)
                            
                            avg_speed = sum(self.speed_samples) / len(self.speed_samples)
                        else:
                            avg_speed = 0
                        
                        speed = self.format_speed(avg_speed)
                        size = self.format_size(total_size)
                        
                        self.last_update_time = current_time
                        self.last_downloaded = downloaded
                        
                        self.progress_updated.emit(percent, speed, size)
            
            try:
                ssl_context = ssl.create_default_context()
                # ssl_context.check_hostname = True  # По умолчанию True
                # ssl_context.verify_mode = ssl.CERT_REQUIRED  # По умолчанию
                
                https_handler = urllib.request.HTTPSHandler(context=ssl_context)
                opener = urllib.request.build_opener(https_handler)
                
                opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')]
                
                urllib.request.install_opener(opener)
                
            except Exception as ssl_error:
                self.download_error.emit(f"Ошибка настройки SSL: {str(ssl_error)}")
                return
            
            try:
                urllib.request.urlretrieve(self.url, self.file_path, progress_hook)
                
                if not os.path.exists(self.file_path):
                    self.download_error.emit("Файл не был создан после скачивания")
                    return
                    
            except Exception as download_error:
                error_details = []
                error_details.append(f"Ошибка: {str(download_error)}")
                error_details.append(f"Путь: {self.file_path}")
                error_details.append(f"URL: {self.url}")
                
                dir_path = os.path.dirname(self.file_path)
                error_details.append(f"Папка существует: {os.path.exists(dir_path)}")
                if os.path.exists(dir_path):
                    error_details.append(f"Права на запись: {os.access(dir_path, os.W_OK)}")
                
                try:
                    temp_mgr = get_temp_manager()
                    debug_info = temp_mgr.get_debug_info()
                    error_details.append(f"Temp dir: {debug_info['temp_dir']}")
                    error_details.append(f"Temp dir доступна: {debug_info['temp_dir_exists']} / {debug_info['temp_dir_writable']}")
                except:
                    error_details.append("Не удалось получить информацию о temp manager")
                
                error_msg = "\n".join(error_details)
                self.download_error.emit(error_msg)
                return
            
            if not self.cancelled:
                self.download_finished.emit(self.file_path)
        
        except Exception as e:
            error_msg = f"Общая ошибка: {str(e)}\nПуть: {getattr(self, 'file_path', 'не определен')}"
            self.download_error.emit(error_msg)
    
    def cancel(self):
        """Отмена скачивания"""
        self.cancelled = True
        if os.path.exists(self.file_path):
            try:
                os.remove(self.file_path)
            except:
                pass
    
    def format_speed(self, bytes_per_second):
        """Форматирование скорости скачивания"""
        if bytes_per_second < 1024:
            return f"{bytes_per_second:.1f} B/s"
        elif bytes_per_second < 1024 * 1024:
            return f"{bytes_per_second / 1024:.1f} KB/s"
        else:
            return f"{bytes_per_second / (1024 * 1024):.1f} MB/s"
    
    def format_size(self, size):
        """Форматирование размера файла"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.1f} GB"


class DownloadDialog(QDialog):
    """Диалог скачивания с прогресс баром"""
    def __init__(self, program_name, download_url, parent=None):
        super().__init__(parent)
        self.program_name = program_name
        self.download_url = download_url
        self.download_thread = None
        
        parsed_url = urlparse(download_url)
        self.filename = os.path.basename(parsed_url.path)
        if not self.filename or '.' not in self.filename:
            self.filename = f"{program_name.replace(' ', '_')}_installer.exe"
        
        self.init_ui()
        self.start_download()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("Скачивание")
        self.setFixedSize(450, 220)
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #404040;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QPushButton:pressed {
                background-color: #333333;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(15)
        
        header_layout = QHBoxLayout()
        
        logo_label = QLabel()
        try:
            pixmap = QPixmap("utilhelpmain.png")
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(0, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                logo_label.setPixmap(scaled_pixmap)
            else:
                logo_label.setText("↓")
                logo_label.setStyleSheet("font-size: 20px;")
        except:
            logo_label.setText("↓")
            logo_label.setStyleSheet("font-size: 20px;")
        
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(logo_label)
        
        title_label = QLabel(f"Скачивание: {self.program_name}")
        title_label.setStyleSheet("""
            color: #ffffff;
            font-size: 16px;
            font-weight: bold;
            margin-left: 10px;
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        self.file_info_label = QLabel(f"Файл: {self.filename}")
        self.file_info_label.setStyleSheet("""
            color: #cccccc;
            font-size: 14px;
            margin: 5px 0px;
        """)
        layout.addWidget(self.file_info_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(28)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 14px;
                background-color: #252525;
                text-align: center;
                color: #ffffff;
                font-weight: bold;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background-color: #666666;
                border-radius: 14px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        self.speed_label = QLabel("Подготовка к скачиванию...")
        self.speed_label.setStyleSheet("""
            color: #888888;
            font-size: 13px;
            margin: 5px 0px;
        """)
        layout.addWidget(self.speed_label)
        
        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.clicked.connect(self.cancel_download)
        self.cancel_btn.setFixedHeight(35)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                font-size: 14px;
            }
        """)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
    
    def start_download(self):
        """Запуск скачивания"""
        self.download_thread = DownloadThread(self.download_url, self.filename)
        self.download_thread.progress_updated.connect(self.update_progress)
        self.download_thread.download_finished.connect(self.download_completed)
        self.download_thread.download_error.connect(self.download_failed)
        self.download_thread.start()
    
    def update_progress(self, percent, speed, size):
        """Обновление прогресса"""
        self.progress_bar.setValue(percent)
        self.speed_label.setText(f"Скорость: {speed} | Размер: {size} | {percent}%")
    
    def download_completed(self, file_path):
        """Скачивание завершено"""
        self.progress_bar.setValue(100)
        self.speed_label.setText("Скачивание завершено!")
        
        self.cancel_btn.setText(" Удалить")
        try:
            from resource_path import get_icon_path
            from PyQt6.QtGui import QIcon
            from PyQt6.QtCore import QSize
            delete_icon_path = get_icon_path("delete.png")
            if delete_icon_path:
                icon = QIcon(delete_icon_path)
                self.cancel_btn.setIcon(icon)
                self.cancel_btn.setIconSize(QSize(16, 16))
        except:
            pass
        
        try:
            from downloads_manager import get_downloads_manager
            manager = get_downloads_manager()
            
            filename = os.path.basename(file_path)
            dest_path = os.path.join(manager.downloads_dir, filename)
            
            if os.path.exists(file_path):
                shutil.move(file_path, dest_path)
                
                notification_manager = get_notification_manager()
                notification_manager.show_download_notification(self.program_name, success=True, item_type="program")
                
                manager.add_download(filename, self.program_name, "program")
                
                final_path = dest_path
            else:
                final_path = file_path
        except Exception as e:
            log_error(f"Ошибка перемещения файла: {e}")
            traceback.print_exc()
            final_path = file_path
        
        QTimer.singleShot(1000, lambda: self.show_download_complete(final_path))
    
    def show_download_complete(self, file_path):
        """Показать сообщение о завершении скачивания"""
        try:
            from PyQt6.QtWidgets import QMessageBox
            
            msg = QMessageBox(self)
            msg.setWindowTitle("Скачивание завершено")
            msg.setText(f"Файл {self.program_name} успешно скачан!")
            msg.setInformativeText(f"Расположение: {file_path}\n\nВыберите действие:")
            
            install_btn = msg.addButton("Установить", QMessageBox.ButtonRole.AcceptRole)
            open_folder_btn = msg.addButton("Открыть папку", QMessageBox.ButtonRole.ActionRole)
            close_btn = msg.addButton("Закрыть", QMessageBox.ButtonRole.RejectRole)
            
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #1a1a1a;
                    color: #ffffff;
                }
                QMessageBox QPushButton {
                    background-color: #404040;
                    color: #ffffff;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 6px;
                    font-weight: bold;
                    min-width: 80px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #555555;
                }
            """)
            
            msg.exec()
            
            if msg.clickedButton() == install_btn:
                self.simple_install(file_path)
            elif msg.clickedButton() == open_folder_btn:
                os.startfile(os.path.dirname(file_path))
                self.accept()
            else:
                self.accept()
                
        except Exception as e:
            CustomMessageBox.information(self, "Скачивание завершено", 
                              f"Файл {self.program_name} скачан:\n{file_path}\n\n"
                              f"Запустите его вручную для установки.")
            self.accept()
    
    def simple_install(self, file_path):
        """Установка с правами админа"""
        try:
            
            os.startfile(file_path)
            
            CustomMessageBox.information(self, "Установка запущена", 
                              f"Установщик {self.program_name} запущен.\n"
                              f"Следуйте инструкциям на экране.")
            self.accept()
            
        except Exception as e:
            CustomMessageBox.warning(self, "Ошибка установки", 
                              f"Не удалось запустить установку:\n{e}\n\n"
                              f"Запустите файл вручную: {file_path}")
            self.accept()
    
    def download_failed(self, error):
        """Ошибка скачивания"""
        try:
            import datetime
            log_text = f"\n=== ОШИБКА СКАЧИВАНИЯ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n"
            log_text += f"Программа: {self.program_name}\n"
            log_text += f"URL: {self.download_url}\n"
            log_text += f"Файл: {self.filename}\n"
            log_text += f"Ошибка:\n{error}\n"
            log_text += "=" * 60 + "\n"
            
            # Используем новую систему логирования вместо записи в файл
            log_error(f"Ошибка скачивания: {error}")
            log_error(f"URL: {self.url}")
            log_error(f"Файл: {self.file_path}")
            log_error(f"Детали: {log_text}")
        except Exception as log_error:
            log_error(f"Не удалось записать лог: {log_error}")
        
        notification_manager = get_notification_manager()
        notification_manager.show_download_notification(self.program_name, success=False, item_type="program")
        
        CustomMessageBox.critical(self, "Ошибка скачивания", error)
        self.reject()
    
    
    def cancel_download(self):
        """Отмена скачивания"""
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.cancel()
            self.download_thread.wait()
        
        self.reject()


class DownloadDialogWithMetadata(DownloadDialog):
    """Диалог скачивания с интеграцией метаданных"""
    def __init__(self, program_name, download_url, parent=None, icon_path=None, file_type="program"):
        self.icon_path = icon_path
        self.file_type = file_type
        super().__init__(program_name, download_url, parent)
        super().__init__(program_name, download_url, parent)
    
    def download_completed(self, file_path):
        """Скачивание завершено с сохранением метаданных"""
        self.progress_bar.setValue(100)
        self.speed_label.setText("Скачивание завершено!")
        
        self.cancel_btn.setText(" Удалить")
        try:
            from resource_path import get_icon_path
            from PyQt6.QtGui import QIcon
            from PyQt6.QtCore import QSize
            delete_icon_path = get_icon_path("delete.png")
            if delete_icon_path:
                icon = QIcon(delete_icon_path)
                self.cancel_btn.setIcon(icon)
                self.cancel_btn.setIconSize(QSize(16, 16))
        except:
            pass
        
        try:
            from downloads_manager import get_downloads_manager
            manager = get_downloads_manager()
            
            filename = os.path.basename(file_path)
            dest_path = os.path.join(manager.downloads_dir, filename)
            
            if os.path.exists(file_path):
                os.makedirs(manager.downloads_dir, exist_ok=True)
                
                shutil.move(file_path, dest_path)
                
                notification_manager = get_notification_manager()
                notification_manager.show_download_notification(self.program_name, success=True, item_type=self.file_type)
                
                manager.add_download(filename, self.program_name, self.file_type, self.icon_path)
                
                final_path = dest_path
            else:
                final_path = file_path
        except Exception as e:
            log_error(f"Ошибка перемещения файла: {e}")
            traceback.print_exc()
            final_path = file_path
        
        QTimer.singleShot(1000, lambda: self.show_download_complete(final_path))


class InstallationManager:
    """Менеджер установки программ и драйверов"""
    @staticmethod
    def install_program(program_name, download_url, parent=None, icon_path=None, file_type="program"):
        if not download_url or not download_url.startswith('http'):
            CustomMessageBox.warning(parent, "Ошибка", 
                              "Некорректная ссылка для скачивания!")
            return
        
        main_window = None
        if parent:
            current = parent
            while current:
                if hasattr(current, 'add_download'):
                    main_window = current
                    break
                current = current.parent()
        
        if main_window:
            main_window.add_download(program_name, download_url, icon_path, file_type)
        else:
            dialog = DownloadDialogWithMetadata(program_name, download_url, parent, icon_path, file_type)
            dialog.exec()
    
    @staticmethod
    def open_website(url, parent=None):
        """Открытие сайта в браузере"""
        if not url or not url.startswith('http'):
            CustomMessageBox.warning(parent, "Ошибка", 
                              "Некорректная ссылка!")
            return
        
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception as e:
            CustomMessageBox.critical(parent, "Ошибка", 
                               f"Не удалось открыть ссылку:\n{e}")