from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea, 
                             QPushButton, QHBoxLayout, QFrame, QGridLayout, QMessageBox,
                             QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap
import os
import subprocess
import ctypes
import sys
from downloads_manager import get_downloads_manager
from scroll_helper import configure_scroll_area


def run_file_as_admin(file_path):
    """Запустить файл с правами администратора"""
    try:
        if sys.platform == "win32":
            result = ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                file_path,
                None,
                None,
                1
            )
            return result > 32
        else:
            subprocess.Popen(['sudo', file_path])
            return True
    except Exception as e:
        print(f"Ошибка запуска с правами администратора: {e}")
        return False


class DownloadsTab(QWidget):
    """Вкладка загрузок"""
    def __init__(self):
        super().__init__()
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 10px;
            }
        """)
        
        title_label = QLabel("БИБЛИОТЕКА")
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
        
        self.info_layout = QHBoxLayout()
        self.info_layout.setContentsMargins(100, 0, 100, 15)
        
        self.count_label = QLabel()
        self.count_label.setTextFormat(Qt.TextFormat.RichText)
        self.count_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 15px;
                font-weight: bold;
                background: transparent;
                padding: 8px 15px 8px 15px;
                border-radius: 8px;
                border: 1px solid rgba(85, 85, 85, 0.5);
                line-height: 26px;
            }
        """)
        self.info_layout.addWidget(self.count_label)
        
        self.info_layout.addStretch()
        
        self.size_label = QLabel()
        self.size_label.setTextFormat(Qt.TextFormat.RichText)
        self.size_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 15px;
                font-weight: bold;
                background: transparent;
                padding: 8px 15px 8px 15px;
                border-radius: 8px;
                border: 1px solid rgba(85, 85, 85, 0.5);
                line-height: 26px;
            }
        """)
        self.info_layout.addWidget(self.size_label)
        
        self.layout.addLayout(self.info_layout)
        
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
        
        self.downloads_content = QWidget()
        self.downloads_grid = QGridLayout(self.downloads_content)
        self.downloads_grid.setContentsMargins(20, 10, 20, 10)
        self.downloads_grid.setSpacing(20)
        
        self.scroll_area.setWidget(self.downloads_content)
        self.layout.addWidget(self.scroll_area)
        
        self.load_downloads()

    def load_downloads(self):
        """Загрузка списка загрузок"""
        manager = get_downloads_manager()
        downloads = manager.get_downloads()
        
        from resource_path import get_icon_path
        
        count_text = f"Файлов: {len(downloads)}"
        box_icon_path = get_icon_path("box.png")
        if box_icon_path:
            self.count_label.setText(f'<img src="{box_icon_path}" width="20" height="20" style="vertical-align: top; margin-right: 5px;"> {count_text}')
        else:
            self.count_label.setText(f"📦 {count_text}")
        
        size_text = f"Общий размер: {manager.get_total_size()}"
        filesize_icon_path = get_icon_path("filesize.png")
        if filesize_icon_path:
            self.size_label.setText(f'<img src="{filesize_icon_path}" width="20" height="20" style="vertical-align: top; margin-right: 5px;"> {size_text}')
        else:
            self.size_label.setText(f"💾 {size_text}")
        
        for i in reversed(range(self.downloads_grid.count())):
            child = self.downloads_grid.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        if not downloads:
            empty_container = QFrame()
            empty_container.setStyleSheet("""
                QFrame {
                    background-color: rgba(85, 85, 85, 0.2);
                    border: 1px solid rgba(102, 102, 102, 0.4);
                    border-radius: 20px;
                }
            """)
            
            empty_layout = QVBoxLayout(empty_container)
            empty_layout.setContentsMargins(50, 50, 50, 50)
            empty_layout.setSpacing(15)
            
            empty_icon = QLabel()
            empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            from resource_path import get_icon_path
            books_icon_path = get_icon_path("books.png")
            if books_icon_path:
                books_pixmap = QPixmap(books_icon_path)
                if not books_pixmap.isNull():
                    scaled_books = books_pixmap.scaled(96, 96, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    empty_icon.setPixmap(scaled_books)
                else:
                    empty_icon.setText("📚")
                    empty_icon.setStyleSheet("""
                        QLabel {
                            color: #cccccc;
                            font-size: 72px;
                            background: transparent;
                            border: none;
                        }
                    """)
            else:
                empty_icon.setText("📚")
                empty_icon.setStyleSheet("""
                    QLabel {
                        color: #cccccc;
                        font-size: 72px;
                        background: transparent;
                        border: none;
                    }
                """)
            
            empty_icon.setStyleSheet(empty_icon.styleSheet() + "background: transparent; border: none;")
            empty_layout.addWidget(empty_icon)
            
            empty_label = QLabel("Библиотека пуста")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("""
                QLabel {
                    color: #cccccc;
                    font-size: 24px;
                    font-weight: bold;
                    background: transparent;
                    border: none;
                }
            """)
            empty_layout.addWidget(empty_label)
            
            hint_label = QLabel("Скачайте программы или драйверы,\nи они появятся здесь")
            hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            hint_label.setStyleSheet("""
                QLabel {
                    color: #888888;
                    font-size: 14px;
                    background: transparent;
                    border: none;
                    line-height: 1.5;
                }
            """)
            empty_layout.addWidget(hint_label)
            
            self.downloads_grid.addWidget(empty_container, 0, 0, 1, 3)
        else:
            row = 0
            col = 0
            for download in downloads:
                card = self.create_download_card(download)
                self.downloads_grid.addWidget(card, row, col)
                
                col += 1
                if col >= 3:
                    col = 0
                    row += 1

    def create_download_card(self, download):
        """Создание карточки загрузки"""
        card = QFrame()
        card.setFixedSize(300, 260)
        card.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 18px;
                padding: 0px;
            }
            QFrame:hover {
                background-color: #353535;
                border: 2px solid #666666;
            }
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 10, 20, 15)
        card_layout.setSpacing(8)
        
        icon_container = QFrame()
        icon_container.setFixedSize(100, 100)
        icon_container.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
            }
        """)
        
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
            }
        """)
        
        if download.get("icon_path") and os.path.exists(download["icon_path"]):
            pixmap = QPixmap(download["icon_path"])
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    85, 85,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                icon_label.setPixmap(scaled_pixmap)
            else:
                from resource_path import get_icon_path
                box_icon_path = get_icon_path("fallbackbox.png")
                if box_icon_path:
                    box_pixmap = QPixmap(box_icon_path)
                    if not box_pixmap.isNull():
                        scaled_box = box_pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        icon_label.setPixmap(scaled_box)
                    else:
                        icon_label.setText("📦")
                        icon_label.setStyleSheet("""
                            QLabel {
                                color: #cccccc;
                                font-size: 52px;
                                background: transparent;
                                border: none;
                            }
                        """)
                else:
                    icon_label.setText("📦")
                    icon_label.setStyleSheet("""
                        QLabel {
                            color: #cccccc;
                            font-size: 52px;
                            background: transparent;
                            border: none;
                        }
                    """)
        else:
            from resource_path import get_icon_path
            box_icon_path = get_icon_path("fallbackbox.png")
            if box_icon_path:
                box_pixmap = QPixmap(box_icon_path)
                if not box_pixmap.isNull():
                    scaled_box = box_pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    icon_label.setPixmap(scaled_box)
                else:
                    icon_label.setText("📦")
                    icon_label.setStyleSheet("""
                        QLabel {
                            color: #cccccc;
                            font-size: 52px;
                            background: transparent;
                            border: none;
                        }
                    """)
            else:
                icon_label.setText("📦")
                icon_label.setStyleSheet("""
                    QLabel {
                        color: #cccccc;
                        font-size: 52px;
                        background: transparent;
                        border: none;
                    }
                """)
        
        icon_layout.addWidget(icon_label)
        
        icon_container_layout = QHBoxLayout()
        icon_container_layout.addStretch()
        icon_container_layout.addWidget(icon_container)
        icon_container_layout.addStretch()
        card_layout.addLayout(icon_container_layout)
        
        card_layout.addSpacing(42)
        
        name_label = QLabel(download["original_name"])
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setFixedHeight(35)
        name_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 13px;
                font-weight: bold;
                background: transparent;
                border: none;
                padding: 0px 5px;
            }
        """)
        card_layout.addWidget(name_label)
        
        info_container = QFrame()
        info_container.setStyleSheet("""
            QFrame {
                background-color: rgba(58, 58, 58, 0.5);
                border-radius: 8px;
                border: 1px solid #555555;
            }
        """)
        info_layout = QHBoxLayout(info_container)
        info_layout.setContentsMargins(0, 5, 10, 5)
        info_layout.setSpacing(8)
        
        size_container = QHBoxLayout()
        size_container.setSpacing(5)
        size_container.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        from resource_path import get_icon_path
        filesize_icon_path = get_icon_path("filesize.png")
        if filesize_icon_path:
            filesize_icon = QLabel()
            filesize_pixmap = QPixmap(filesize_icon_path)
            if not filesize_pixmap.isNull():
                scaled_filesize = filesize_pixmap.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                filesize_icon.setPixmap(scaled_filesize)
                filesize_icon.setStyleSheet("background: transparent; border: none;")
                filesize_icon.setAlignment(Qt.AlignmentFlag.AlignVCenter)
                size_container.addWidget(filesize_icon)
        
        size_label = QLabel(download['file_size'])
        size_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 11px;
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)
        size_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        size_container.addWidget(size_label)
        
        size_widget = QWidget()
        size_widget.setLayout(size_container)
        size_widget.setStyleSheet("background: transparent; border: none;")
        info_layout.addWidget(size_widget)
        
        info_layout.addStretch()
        
        date_container = QHBoxLayout()
        date_container.setSpacing(5)
        date_container.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        date_container.setContentsMargins(0, 0, 0, 0)
        
        calendar_icon_path = get_icon_path("calendar.png")
        if calendar_icon_path:
            calendar_icon = QLabel()
            calendar_pixmap = QPixmap(calendar_icon_path)
            if not calendar_pixmap.isNull():
                scaled_calendar = calendar_pixmap.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                calendar_icon.setPixmap(scaled_calendar)
                calendar_icon.setStyleSheet("background: transparent; border: none;")
                calendar_icon.setAlignment(Qt.AlignmentFlag.AlignVCenter)
                calendar_icon.setFixedSize(16, 16)
                date_container.addWidget(calendar_icon)
        
        date_label = QLabel(download['download_date'].split()[0])
        date_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 11px;
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)
        date_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        date_container.addWidget(date_label)
        
        date_widget = QWidget()
        date_widget.setLayout(date_container)
        date_widget.setStyleSheet("background: transparent; border: none;")
        info_layout.addWidget(date_widget)
        
        card_layout.addWidget(info_container)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        run_btn = QPushButton("▶ Запустить")
        run_btn.setFixedHeight(36)
        run_btn.clicked.connect(lambda: self.run_file(download))
        run_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: 1px solid #4CAF50;
                padding: 8px 16px;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                outline: none;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #5CBF60;
                border: 1px solid #5CBF60;
            }
            QPushButton:pressed {
                background-color: #45a049;
            }
        """)
        buttons_layout.addWidget(run_btn)
        
        delete_btn = QPushButton()
        delete_btn.setFixedSize(32, 32)
        delete_btn.clicked.connect(lambda: self.delete_file(download))
        
        from resource_path import get_icon_path
        from PyQt6.QtGui import QIcon
        from PyQt6.QtCore import QSize
        
        delete_icon_path = get_icon_path("deletelibrary.png")
        if delete_icon_path:
            delete_icon = QIcon(delete_icon_path)
            delete_btn.setIcon(delete_icon)
            delete_btn.setIconSize(QSize(16, 16))
        else:
            delete_btn.setText("🗑")
        
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(244, 67, 54, 0.1);
                color: #f44336;
                border: 1px solid rgba(244, 67, 54, 0.3);
                border-radius: 16px;
                font-size: 14px;
                font-weight: bold;
                outline: none;
            }
            QPushButton:hover {
                background-color: rgba(244, 67, 54, 0.2);
                border: 1px solid rgba(244, 67, 54, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(244, 67, 54, 0.3);
                border: 1px solid #f44336;
            }
        """)
        buttons_layout.addWidget(delete_btn)
        
        card_layout.addLayout(buttons_layout)
        
        return card

    def run_file(self, download):
        """Запустить файл"""
        try:
            filepath = download["filepath"]
            file_extension = filepath.lower().split('.')[-1]
            
            if file_extension in ['zip', 'rar', '7z', 'tar', 'gz', 'bz2']:
                os.startfile(filepath)
            else:
                success = run_file_as_admin(filepath)
                if not success:
                    os.startfile(filepath)
                    
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось запустить файл:\n{e}")

    def delete_file(self, download):
        """Удалить файл"""
        dialog = QWidget(self, Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        dialog.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        dialog.setFixedSize(400, 200)
        
        container = QWidget(dialog)
        container.setGeometry(0, 0, 400, 200)
        container.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border: 2px solid #555555;
                border-radius: 15px;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        title_label = QLabel("Подтверждение")
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(title_label)
        
        message_label = QLabel(f"Удалить файл '{download['original_name']}'?")
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 14px;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(message_label)
        
        layout.addStretch()
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setFixedHeight(35)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                color: #ffffff;
                border: none;
                padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                outline: none;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QPushButton:pressed {
                background-color: #333333;
            }
        """)
        
        def close_with_animation():
            from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
            
            opacity_effect = QGraphicsOpacityEffect(dialog)
            dialog.setGraphicsEffect(opacity_effect)
            
            fade_out = QPropertyAnimation(opacity_effect, b"opacity")
            fade_out.setDuration(200)
            fade_out.setStartValue(1.0)
            fade_out.setEndValue(0.0)
            fade_out.setEasingCurve(QEasingCurve.Type.OutQuad)
            fade_out.finished.connect(dialog.close)
            fade_out.start()
            
            dialog.fade_animation = fade_out
        
        cancel_btn.clicked.connect(close_with_animation)
        buttons_layout.addWidget(cancel_btn)
        
        buttons_layout.addStretch()
        
        delete_btn = QPushButton("Удалить")
        delete_btn.setFixedHeight(35)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: #ffffff;
                border: none;
                padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                outline: none;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #c62828;
            }
        """)
        
        def confirm_delete():
            close_with_animation()
            
            QTimer.singleShot(250, lambda: perform_delete())
        
        def perform_delete():
            manager = get_downloads_manager()
            if manager.delete_download(download["filename"]):
                try:
                    main_window = self.window()
                    if hasattr(main_window, 'current_downloads'):
                        for download_item in main_window.current_downloads[:]:
                            if (hasattr(download_item, 'downloaded_file_path') and 
                                download_item.downloaded_file_path and
                                os.path.basename(download_item.downloaded_file_path) == download["filename"]):
                                main_window.remove_download(download_item)
                                break
                except Exception as e:
                    print(f"Ошибка синхронизации с панелью загрузок: {e}")
                
                self.load_downloads()
            else:
                error_dialog = QWidget(self, Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
                error_dialog.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
                error_dialog.setFixedSize(300, 150)
                
                error_container = QWidget(error_dialog)
                error_container.setGeometry(0, 0, 300, 150)
                error_container.setStyleSheet("""
                    QWidget {
                        background-color: #2d2d2d;
                        border: 2px solid #555555;
                        border-radius: 15px;
                    }
                """)
                
                error_layout = QVBoxLayout(error_container)
                error_layout.setContentsMargins(30, 30, 30, 30)
                error_layout.setSpacing(20)
                
                error_label = QLabel("Не удалось удалить файл")
                error_label.setStyleSheet("""
                    QLabel {
                        color: #f44336;
                        font-size: 16px;
                        font-weight: bold;
                        background: transparent;
                        border: none;
                    }
                """)
                error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                error_layout.addWidget(error_label)
                
                ok_btn = QPushButton("OK")
                ok_btn.setFixedHeight(35)
                ok_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f44336;
                        color: #ffffff;
                        border: none;
                        padding: 8px 20px;
                        border-radius: 8px;
                        font-weight: bold;
                        font-size: 14px;
                        outline: none;
                    }
                    QPushButton:hover {
                        background-color: #da190b;
                    }
                """)
                ok_btn.clicked.connect(error_dialog.close)
                error_layout.addWidget(ok_btn)
                
                parent_rect = self.window().geometry()
                x = parent_rect.x() + (parent_rect.width() - error_dialog.width()) // 2
                y = parent_rect.y() + (parent_rect.height() - error_dialog.height()) // 2
                error_dialog.move(x, y)
                
                error_dialog.show()
        
        delete_btn.clicked.connect(confirm_delete)
        buttons_layout.addWidget(delete_btn)
        
        layout.addLayout(buttons_layout)
        
        parent_rect = self.window().geometry()
        x = parent_rect.x() + (parent_rect.width() - dialog.width()) // 2
        y = parent_rect.y() + (parent_rect.height() - dialog.height()) // 2
        dialog.move(x, y)
        
        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
        
        opacity_effect = QGraphicsOpacityEffect(dialog)
        dialog.setGraphicsEffect(opacity_effect)
        
        fade_in = QPropertyAnimation(opacity_effect, b"opacity")
        fade_in.setDuration(200)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        dialog.show()
        fade_in.start()
        
        dialog.show_animation = fade_in

    def refresh_downloads(self):
        """Обновить список загрузок"""
        self.load_downloads()

    def reset_search_and_scroll(self):
        """Сброс прокрутки при переключении вкладки"""
        if hasattr(self, 'scroll_area'):
            self.scroll_area.verticalScrollBar().setValue(0)
        
        self.load_downloads()
