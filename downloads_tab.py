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
from localization import t


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
    
    def load_icon_pixmap(self, icon_name, size=None):
        """Загрузить иконку с перекраской для светлой темы"""
        from theme_manager import theme_manager, colorize_pixmap
        from resource_path import get_icon_path
        
        icon_path = get_icon_path(icon_name)
        if icon_path:
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                if size:
                    pixmap = pixmap.scaled(size[0], size[1], Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                
                # В светлой теме перекрашиваем иконки UI
                if theme_manager.is_light():
                    pixmap = colorize_pixmap(pixmap, theme_manager.colors['text_secondary'])
                
                return pixmap
        return QPixmap()
    
    def __init__(self):
        super().__init__()
        
        from settings_manager import settings_manager
        self.view_mode = settings_manager.get_setting("library_view_mode", "grid")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        from theme_manager import theme_manager
        c = theme_manager.colors

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {c['bg_main']};
                border-radius: 10px;
            }}
        """)

        self.title_label = QLabel(t("tabs.library"))
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

        self.info_layout = QHBoxLayout()
        self.info_layout.setContentsMargins(100, 0, 100, 15)

        self.count_container = QWidget()
        count_layout = QHBoxLayout(self.count_container)
        count_layout.setContentsMargins(8, 8, 8, 8)
        count_layout.setSpacing(8)
        self.count_container.setStyleSheet(f"""
            QWidget {{
                background: transparent;
                border: none;
                border-radius: 8px;
            }}
        """)
        
        self.count_icon = QLabel()
        self.count_icon.setStyleSheet("background: transparent; border: none;")
        count_layout.addWidget(self.count_icon)
        
        self.count_label = QLabel()
        self.count_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_secondary']};
                font-size: 15px;
                font-weight: bold;
                background: transparent;
                border: none;
            }}
        """)
        count_layout.addWidget(self.count_label)
        
        self.info_layout.addWidget(self.count_container)
        self.info_layout.addStretch()

        self.size_container = QWidget()
        size_layout = QHBoxLayout(self.size_container)
        size_layout.setContentsMargins(8, 8, 8, 8)
        size_layout.setSpacing(8)
        self.size_container.setStyleSheet(f"""
            QWidget {{
                background: transparent;
                border: none;
                border-radius: 8px;
            }}
        """)
        
        self.size_icon = QLabel()
        self.size_icon.setStyleSheet("background: transparent; border: none;")
        size_layout.addWidget(self.size_icon)
        
        self.size_label = QLabel()
        self.size_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_secondary']};
                font-size: 15px;
                font-weight: bold;
                background: transparent;
                border: none;
            }}
        """)
        size_layout.addWidget(self.size_label)
        
        self.info_layout.addWidget(self.size_container)

        self.layout.addLayout(self.info_layout)
        
        view_button_container = QHBoxLayout()
        view_button_container.setContentsMargins(0, 0, 20, 10)
        view_button_container.addStretch()
        
        self.delete_all_button = QPushButton()
        self.delete_all_button.setFixedSize(40, 40)
        self.delete_all_button.clicked.connect(self.delete_all_files)
        self.delete_all_button.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(244, 67, 54, 0.15);
                border: none;
                border-radius: 8px;
                color: #f44336;
                font-size: 16px;
                font-weight: bold;
                outline: none;
            }}
            QPushButton:hover {{ background-color: rgba(244, 67, 54, 0.25); }}
            QPushButton:pressed {{ background-color: rgba(244, 67, 54, 0.35); }}
        """)
        
        from resource_path import get_icon_path
        from PyQt6.QtGui import QIcon, QPainter, QColor
        from PyQt6.QtCore import QSize
        
        delete_icon_path = get_icon_path("trashlib.png")
        if delete_icon_path:
            delete_pixmap = QPixmap(delete_icon_path)
            if not delete_pixmap.isNull():
                from theme_manager import colorize_pixmap
                red_pixmap = colorize_pixmap(delete_pixmap, "#f44336")
                delete_icon = QIcon(red_pixmap)
                self.delete_all_button.setIcon(delete_icon)
                self.delete_all_button.setIconSize(QSize(20, 20))
            else:
                self.delete_all_button.setText("🗑")
        else:
            self.delete_all_button.setText("🗑")
        
        view_button_container.addWidget(self.delete_all_button)
        
        self.view_mode_button = QPushButton()
        self.view_mode_button.setFixedSize(40, 40)
        self.view_mode_button.clicked.connect(self.toggle_view_mode)
        self.view_mode_button.setStyleSheet(f"""
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
        """)
        view_button_container.addWidget(self.view_mode_button)
        self.layout.addLayout(view_button_container)
        
        self.update_view_mode_button()

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
        
        count_text = t("library.files_count", count=len(downloads))
        box_pixmap = self.load_icon_pixmap("box.png", (20, 20))
        if not box_pixmap.isNull():
            self.count_icon.setPixmap(box_pixmap)
        self.count_label.setText(count_text)
        
        size_text = t("library.total_size", size=manager.get_total_size())
        filesize_pixmap = self.load_icon_pixmap("filesize.png", (20, 20))
        if not filesize_pixmap.isNull():
            self.size_icon.setPixmap(filesize_pixmap)
        self.size_label.setText(size_text)
        
        for i in reversed(range(self.downloads_grid.count())):
            child = self.downloads_grid.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        if not downloads:
            from theme_manager import theme_manager
            c = theme_manager.colors
            
            if hasattr(self, 'view_mode_button'):
                self.view_mode_button.hide()
            if hasattr(self, 'delete_all_button'):
                self.delete_all_button.hide()

            empty_container = QFrame()
            empty_container.setStyleSheet(f"""
                QFrame {{
                    background-color: {c['bg_tertiary']};
                    border: none;
                    border-radius: 20px;
                }}
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
                    if theme_manager.is_light():
                        from theme_manager import colorize_pixmap
                        scaled_books = colorize_pixmap(scaled_books, c['text_secondary'])
                    empty_icon.setPixmap(scaled_books)
                else:
                    empty_icon.setText("📚")
                empty_icon.setStyleSheet("background: transparent; border: none;")
            else:
                empty_icon.setText("📚")
                empty_icon.setStyleSheet(f"""
                    QLabel {{
                        color: {c['text_secondary']}; font-size: 72px;
                        background: transparent; border: none; }}
                """)
            
            empty_layout.addWidget(empty_icon)
            
            empty_label = QLabel(t("library.empty_title"))
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet(f"""
                QLabel {{
                    color: {c['text_primary']};
                    font-size: 24px;
                    font-weight: bold;
                    background: transparent;
                    border: none;
                }}
            """)
            empty_layout.addWidget(empty_label)

            hint_label = QLabel(t("library.empty_hint"))
            hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            hint_label.setStyleSheet(f"""
                QLabel {{
                    color: {c['text_hint']};
                    font-size: 14px;
                    background: transparent; border: none; line-height: 1.5;
                }}
            """)
            empty_layout.addWidget(hint_label)
            
            self.downloads_grid.addWidget(empty_container, 0, 0, 1, 3)
        else:
            if hasattr(self, 'view_mode_button'):
                self.view_mode_button.show()
            if hasattr(self, 'delete_all_button'):
                self.delete_all_button.show()
            if self.view_mode == "grid":
                self.display_downloads_grid(downloads)
            else:
                self.display_downloads_list(downloads)
    
    def display_downloads_grid(self, downloads):
        """Отображение загрузок в виде сетки"""
        self.downloads_grid.setVerticalSpacing(20)
        self.downloads_grid.setHorizontalSpacing(20)
        
        row = 0
        col = 0
        for download in downloads:
            card = self.create_download_card(download)
            self.downloads_grid.addWidget(card, row, col)
            
            col += 1
            if col >= 3:
                col = 0
                row += 1
    
    def display_downloads_list(self, downloads):
        """Отображение загрузок в виде списка"""
        self.downloads_grid.setVerticalSpacing(15)
        self.downloads_grid.setHorizontalSpacing(0)
        
        for row, download in enumerate(downloads):
            card = self.create_download_card_list(download)
            self.downloads_grid.addWidget(card, row, 0)

    def create_download_card(self, download):
        """Создание карточки загрузки"""
        from theme_manager import theme_manager
        c = theme_manager.colors

        card = QFrame()
        card.setFixedSize(300, 260)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {c['bg_card']};
                border: 2px solid {c['card_border']};
                border-radius: 18px;
                padding: 0px;
            }}
            QFrame:hover {{
                background-color: {c['bg_hover']};
                border: 2px solid {c['border_hover']};
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 10, 20, 15)
        card_layout.setSpacing(8)
        
        icon_container = QFrame()
        icon_container.setFixedSize(100, 100)
        icon_container.setStyleSheet("""
            QFrame {
                background: transparent; border: none; }
        """)
        
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                background: transparent; border: none; }
        """)
        
        icon_path = download.get("icon_path")
        if icon_path:
            icon_exists = icon_path.startswith(":/") or os.path.exists(icon_path)
            
            if icon_exists:
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        85, 85,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    # В светлой теме перекрашиваем иконки программ
                    from theme_manager import theme_manager, colorize_pixmap
                    if theme_manager.is_light():
                        scaled_pixmap = colorize_pixmap(scaled_pixmap, theme_manager.colors['text_secondary'])
                    
                    icon_label.setPixmap(scaled_pixmap)
                else:
                    # Fallback на коробку
                    box_pixmap = self.load_icon_pixmap("fallbackbox.png", (64, 64))
                    if box_pixmap and not box_pixmap.isNull():
                        icon_label.setPixmap(box_pixmap)
                    else:
                        icon_label.setText("📦")
                        icon_label.setStyleSheet(f"""
                            QLabel {{
                                color: {c['text_secondary']}; font-size: 52px
                                background: transparent; border: none; }}
                        """)
            else:
                box_pixmap = self.load_icon_pixmap("fallbackbox.png", (64, 64))
                if box_pixmap and not box_pixmap.isNull():
                    icon_label.setPixmap(box_pixmap)
                else:
                    icon_label.setText("📦")
                    icon_label.setStyleSheet(f"""
                        QLabel {{
                            color: {c['text_secondary']}; font-size: 52px
                            background: transparent; border: none; }}
                    """)
        else:
            box_pixmap = self.load_icon_pixmap("fallbackbox.png", (64, 64))
            if box_pixmap and not box_pixmap.isNull():
                icon_label.setPixmap(box_pixmap)
            else:
                icon_label.setText("📦")
                icon_label.setStyleSheet(f"""
                    QLabel {{
                        color: {c['text_secondary']}; font-size: 52px
                        background: transparent; border: none; }}
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
        name_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 13px; font-weight: bold; background: transparent; border: none; padding: 0px 5px;
            }}
        """)
        card_layout.addWidget(name_label)

        info_container = QFrame()
        info_container.setStyleSheet(f"""
            QFrame {{
                background-color: {c['bg_tertiary']};
                border-radius: 8px;
                border: 1px solid {c['border']};
            }}
        """)
        info_layout = QHBoxLayout(info_container)
        info_layout.setContentsMargins(0, 5, 10, 5)
        info_layout.setSpacing(8)
        
        size_container = QHBoxLayout()
        size_container.setSpacing(5)
        size_container.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        from resource_path import get_icon_path
        filesize_pixmap = self.load_icon_pixmap("filesize.png", (16, 16))
        if not filesize_pixmap.isNull():
            filesize_icon = QLabel()
            filesize_icon.setPixmap(filesize_pixmap)
            filesize_icon.setStyleSheet("background: transparent; border: none")
            filesize_icon.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            size_container.addWidget(filesize_icon)
        
        size_label = QLabel(download['file_size'])
        size_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_secondary']}; font-size: 11px; font-weight: bold; background: transparent; border: none; }}
        """)
        size_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        size_container.addWidget(size_label)
        
        size_widget = QWidget()
        size_widget.setLayout(size_container)
        size_widget.setStyleSheet("background: transparent; border: none")
        info_layout.addWidget(size_widget)
        
        info_layout.addStretch()
        
        date_container = QHBoxLayout()
        date_container.setSpacing(5)
        date_container.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        date_container.setContentsMargins(0, 0, 0, 0)
        
        calendar_pixmap = self.load_icon_pixmap("calendar.png", (16, 16))
        if not calendar_pixmap.isNull():
            calendar_icon = QLabel()
            calendar_icon.setPixmap(calendar_pixmap)
            calendar_icon.setStyleSheet("background: transparent; border: none")
            calendar_icon.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            calendar_icon.setFixedSize(16, 16)
            date_container.addWidget(calendar_icon)
        
        date_label = QLabel(download['download_date'].split()[0])
        date_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_secondary']}; font-size: 11px; font-weight: bold; background: transparent; border: none; }}
        """)
        date_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        date_container.addWidget(date_label)
        
        date_widget = QWidget()
        date_widget.setLayout(date_container)
        date_widget.setStyleSheet("background: transparent; border: none")
        info_layout.addWidget(date_widget)
        
        card_layout.addWidget(info_container)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        run_btn = QPushButton(t("buttons.run"))
        run_btn.setFixedHeight(36)
        run_btn.clicked.connect(lambda: self.run_file(download))
        run_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: 1px solid #4CAF50;
                padding: 8px 16px;
                border-radius: 8px;
                font-size: 13px; font-weight: bold;
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
        
        from PyQt6.QtGui import QIcon
        from PyQt6.QtCore import QSize
        
        delete_pixmap = self.load_icon_pixmap("deletelibrary.png", (16, 16))
        if delete_pixmap and not delete_pixmap.isNull():
            delete_icon = QIcon(delete_pixmap)
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
                font-size: 14px; font-weight: bold;
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
    
    def create_download_card_list(self, download):
        """Создание карточки загрузки в виде списка"""
        from theme_manager import theme_manager
        c = theme_manager.colors

        card = QFrame()
        card.setFixedHeight(90)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {c['bg_card']};
                border: 2px solid {c['card_border']};
                border-radius: 12px;
                padding: 0px;
            }}
            QFrame:hover {{
                background-color: {c['bg_hover']};
                border: 2px solid {c['border_hover']};
            }}
        """)
        
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(15, 10, 15, 10)
        card_layout.setSpacing(5)
        
        icon_label = QLabel()
        icon_label.setFixedSize(60, 60)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("background: transparent; border: none;")
        
        icon_path = download.get("icon_path")
        if icon_path:
            icon_exists = icon_path.startswith(":/") or os.path.exists(icon_path)
            
            if icon_exists:
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    from theme_manager import colorize_pixmap
                    if theme_manager.is_light():
                        scaled_pixmap = colorize_pixmap(scaled_pixmap, theme_manager.colors['text_secondary'])
                    icon_label.setPixmap(scaled_pixmap)
                else:
                    box_pixmap = self.load_icon_pixmap("fallbackbox.png", (40, 40))
                    if box_pixmap and not box_pixmap.isNull():
                        icon_label.setPixmap(box_pixmap)
                    else:
                        icon_label.setText("📦")
                        icon_label.setStyleSheet(f"QLabel {{ color: {c['text_secondary']}; font-size: 32px; background: transparent; border: none; }}")
            else:
                box_pixmap = self.load_icon_pixmap("fallbackbox.png", (40, 40))
                if box_pixmap and not box_pixmap.isNull():
                    icon_label.setPixmap(box_pixmap)
                else:
                    icon_label.setText("📦")
                    icon_label.setStyleSheet(f"QLabel {{ color: {c['text_secondary']}; font-size: 32px; background: transparent; border: none; }}")
        else:
            box_pixmap = self.load_icon_pixmap("fallbackbox.png", (40, 40))
            if box_pixmap and not box_pixmap.isNull():
                icon_label.setPixmap(box_pixmap)
            else:
                icon_label.setText("📦")
                icon_label.setStyleSheet(f"QLabel {{ color: {c['text_secondary']}; font-size: 32px; background: transparent; border: none; }}")
        
        card_layout.addWidget(icon_label)
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        name_label = QLabel(download["original_name"])
        name_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 14px;
                font-weight: bold;
                background: transparent;
                border: none;
            }}
        """)
        info_layout.addWidget(name_label)
        
        details_layout = QHBoxLayout()
        details_layout.setSpacing(15)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        filesize_pixmap = self.load_icon_pixmap("filesize.png", (14, 14))
        if not filesize_pixmap.isNull():
            filesize_icon = QLabel()
            filesize_icon.setPixmap(filesize_pixmap)
            filesize_icon.setFixedSize(14, 14)
            filesize_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            filesize_icon.setStyleSheet("background: transparent; border: none")
            details_layout.addWidget(filesize_icon)
        
        size_label = QLabel(download['file_size'])
        size_label.setStyleSheet(f"QLabel {{ color: {c['text_secondary']}; font-size: 12px; background: transparent; border: none; }}")
        size_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        details_layout.addWidget(size_label)
        
        calendar_pixmap = self.load_icon_pixmap("calendar.png", (14, 14))
        if not calendar_pixmap.isNull():
            calendar_icon = QLabel()
            calendar_icon.setPixmap(calendar_pixmap)
            calendar_icon.setFixedSize(14, 14)
            calendar_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            calendar_icon.setStyleSheet("background: transparent; border: none")
            details_layout.addWidget(calendar_icon)
        
        date_label = QLabel(download['download_date'].split()[0])
        date_label.setStyleSheet(f"QLabel {{ color: {c['text_secondary']}; font-size: 12px; background: transparent; border: none; }}")
        date_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        details_layout.addWidget(date_label)
        
        details_layout.addStretch()
        
        info_layout.addLayout(details_layout)
        
        card_layout.addLayout(info_layout, 1)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        run_btn = QPushButton(t("buttons.run"))
        run_btn.setFixedSize(120, 36)
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
        
        from PyQt6.QtGui import QIcon
        from PyQt6.QtCore import QSize
        
        delete_pixmap = self.load_icon_pixmap("deletelibrary.png", (16, 16))
        if delete_pixmap and not delete_pixmap.isNull():
            delete_icon = QIcon(delete_pixmap)
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
        from theme_manager import theme_manager
        c = theme_manager.colors

        dialog = QWidget(self, Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        dialog.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        dialog.setFixedSize(400, 200)
        
        container = QWidget(dialog)
        container.setGeometry(0, 0, 400, 200)
        container.setStyleSheet(f"""
            QWidget {{
                background-color: {c['bg_secondary']};
                border: 2px solid {c['border_hover']};
                border-radius: 15px;
            }}
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        title_label = QLabel(t("library.confirmation"))
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                font-size: 18px; font-weight: bold; background: transparent; border: none; }}
        """)
        layout.addWidget(title_label)
        
        message_label = QLabel(t("library.delete_confirm", name=download['original_name']))
        message_label.setWordWrap(True)
        message_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_secondary']};
                font-size: 14px;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(message_label)
        
        layout.addStretch()
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        cancel_btn = QPushButton(t("buttons.cancel"))
        cancel_btn.setFixedHeight(35)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['bg_button']};
                color: {c['text_primary']};
                border: none; padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px
                outline: none;
            }}
            QPushButton:hover {{ background-color: {c['bg_hover']}; }}
            QPushButton:pressed {{ background-color: {c['bg_pressed']}; }}
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
        
        delete_btn = QPushButton(t("buttons.delete"))
        delete_btn.setFixedHeight(35)
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                outline: none;
            }}
            QPushButton:hover {{ background-color: #da190b; }}
            QPushButton:pressed {{ background-color: #c62828; }}
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
                error_container.setStyleSheet(f"""
                    QWidget {{
                        background-color: {c['bg_secondary']};
                        border: 2px solid {c['border_hover']};
                        border-radius: 15px;
                    }}
                """)
                
                error_layout = QVBoxLayout(error_container)
                error_layout.setContentsMargins(30, 30, 30, 30)
                error_layout.setSpacing(20)
                
                error_label = QLabel(t("library.delete_error"))
                error_label.setStyleSheet(f"""
                    QLabel {{
                        color: {c['error']};
                        font-size: 16px; font-weight: bold; background: transparent; border: none; }}
                """)
                error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                error_layout.addWidget(error_label)
                
                ok_btn = QPushButton("OK")
                ok_btn.setFixedHeight(35)
                ok_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {c['error']};
                        color: white;
                        border: none; padding: 8px 20px;
                        border-radius: 8px;
                        font-weight: bold;
                        font-size: 14px
                        outline: none;
                    }}
                    QPushButton:hover {{ background-color: #da190b; }}
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
    
    def delete_all_files(self):
        """Удалить все файлы из библиотеки"""
        from theme_manager import theme_manager
        c = theme_manager.colors
        
        manager = get_downloads_manager()
        downloads = manager.get_downloads()
        
        # Если нет файлов, ничего не делаем
        if not downloads:
            return
        
        dialog = QWidget(self, Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        dialog.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        dialog.setFixedSize(450, 220)
        
        container = QWidget(dialog)
        container.setGeometry(0, 0, 450, 220)
        container.setStyleSheet(f"""
            QWidget {{
                background-color: {c['bg_secondary']};
                border: 2px solid {c['error']};
                border-radius: 15px;
            }}
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        title_label = QLabel(t("library.confirmation"))
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {c['error']};
                font-size: 18px; font-weight: bold; background: transparent; border: none; }}
        """)
        layout.addWidget(title_label)
        
        message_label = QLabel(t("library.delete_all_confirm", count=len(downloads)))
        message_label.setWordWrap(True)
        message_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_secondary']}; font-size: 14px;
                background: transparent; border: none; }}
        """)
        layout.addWidget(message_label)
        
        warning_label = QLabel(t("library.delete_all_warning"))
        warning_label.setWordWrap(True)
        warning_label.setStyleSheet(f"""
            QLabel {{
                color: {c['error']};
                font-size: 13px;
                font-weight: bold;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(warning_label)
        
        layout.addStretch()
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        cancel_btn = QPushButton(t("buttons.cancel"))
        cancel_btn.setFixedHeight(35)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['bg_button']};
                color: {c['text_primary']};
                border: none; padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                outline: none;
            }}
            QPushButton:hover {{ background-color: {c['bg_hover']}; }}
            QPushButton:pressed {{ background-color: {c['bg_pressed']}; }}
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
        
        delete_btn = QPushButton(t("library.delete_all"))
        delete_btn.setFixedHeight(35)
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                outline: none;
            }}
            QPushButton:hover {{ background-color: #da190b; }}
            QPushButton:pressed {{ background-color: #c62828; }}
        """)
        
        def confirm_delete_all():
            close_with_animation()
            QTimer.singleShot(250, lambda: perform_delete_all())
        
        def perform_delete_all():
            import shutil
            
            manager.delete_all_downloads()
            
            try:
                downloads_dir = manager.downloads_dir
                if os.path.exists(downloads_dir):
                    shutil.rmtree(downloads_dir)
                    os.makedirs(downloads_dir, exist_ok=True)
            except Exception as e:
                print(f"Ошибка при удалении папки загрузок: {e}")
            
            try:
                main_window = self.window()
                if hasattr(main_window, 'current_downloads'):
                    for download_item in main_window.current_downloads[:]:
                        main_window.remove_download(download_item)
            except Exception as e:
                print(f"Ошибка синхронизации с панелью загрузок: {e}")
            
            self.load_downloads()
        
        delete_btn.clicked.connect(confirm_delete_all)
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
    
    def update_translations(self):
        """Обновление переводов при смене языка"""
        from localization import t
        
        if hasattr(self, 'title_label'):
            self.title_label.setText(t("tabs.library"))
        
        self.load_downloads()

    def load_icon_pixmap(self, icon_name, size=None):
        """Загрузить иконку с правильным путем и цветом для темы"""
        from theme_manager import theme_manager, colorize_pixmap
        from resource_path import get_icon_path

        icon_path = get_icon_path(icon_name)
        if icon_path:
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull() and size:
                pixmap = pixmap.scaled(size[0], size[1], Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            
            if not pixmap.isNull() and theme_manager.is_light():
                pixmap = colorize_pixmap(pixmap, theme_manager.colors['text_secondary'])
            
            return pixmap
        return QPixmap()

    def apply_theme(self):
        """Применить тему к вкладке библиотеки"""
        from theme_manager import theme_manager
        from logger import log_info
        c = theme_manager.colors
        
        log_info("DownloadsTab.apply_theme вызван")
        
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
                    font-size: 28px; font-weight: bold;
                    margin: 20px 0px;
                    letter-spacing: 2px;
                }}
            """)
        
        _info_label_style = f"""
            QLabel {{
                color: {c['text_secondary']}; font-size: 15px; font-weight: bold; background: transparent;
                border: none;
            }}
        """
        if hasattr(self, 'count_label'):
            self.count_label.setStyleSheet(_info_label_style)
        if hasattr(self, 'size_label'):
            self.size_label.setStyleSheet(_info_label_style)
        
        if hasattr(self, 'scroll_area'):
            self.scroll_area.setStyleSheet(f"""
                QScrollArea {{
                    border: none; background-color: transparent;
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
                    border: none; background: none;
                    height: 0px;
                }}
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                    background: none;
                }}
            """)
        
        if hasattr(self, 'downloads_content'):
            self.downloads_content.setStyleSheet(f"""
                QWidget {{
                    background-color: transparent;
                    border: none; }}
            """)
        
        if hasattr(self, 'view_mode_button'):
            self.view_mode_button.setStyleSheet(f"""
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
            """)
            self.update_view_mode_button()
        
        if hasattr(self, 'delete_all_button'):
            self.delete_all_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(244, 67, 54, 0.15);
                    border: none;
                    border-radius: 8px;
                    color: #f44336;
                    font-size: 16px;
                    font-weight: bold;
                    outline: none;
                }}
                QPushButton:hover {{ background-color: rgba(244, 67, 54, 0.25); }}
                QPushButton:pressed {{ background-color: rgba(244, 67, 54, 0.35); }}
            """)
            from resource_path import get_icon_path
            from PyQt6.QtGui import QIcon
            from PyQt6.QtCore import QSize
            
            delete_icon_path = get_icon_path("trashlib.png")
            if delete_icon_path:
                delete_pixmap = QPixmap(delete_icon_path)
                if not delete_pixmap.isNull():
                    from theme_manager import colorize_pixmap
                    red_pixmap = colorize_pixmap(delete_pixmap, "#f44336")
                    delete_icon = QIcon(red_pixmap)
                    self.delete_all_button.setIcon(delete_icon)
                    self.delete_all_button.setIconSize(QSize(20, 20))
        
        if hasattr(self, 'count_icon'):
            box_pixmap = self.load_icon_pixmap("box.png", (20, 20))
            if not box_pixmap.isNull():
                self.count_icon.setPixmap(box_pixmap)
        
        if hasattr(self, 'size_icon'):
            filesize_pixmap = self.load_icon_pixmap("filesize.png", (20, 20))
            if not filesize_pixmap.isNull():
                self.size_icon.setPixmap(filesize_pixmap)
        
        self.load_downloads()
    
    def toggle_view_mode(self):
        """Переключение режима просмотра между плиткой и списком"""
        from settings_manager import settings_manager
        
        self.view_mode = "list" if self.view_mode == "grid" else "grid"
        
        settings_manager.set_setting("library_view_mode", self.view_mode)
        
        self.update_view_mode_button()
        
        self.load_downloads()
    
    def update_view_mode_button(self):
        """Обновить иконку кнопки переключения вида"""
        from resource_path import get_icon_path
        from PyQt6.QtGui import QIcon
        from PyQt6.QtCore import QSize
        
        if self.view_mode == "grid":
            icon_path = get_icon_path("iconlist.png")
        else:
            icon_path = get_icon_path("icontab.png")
        
        if icon_path:
            pixmap = self.load_icon_pixmap(os.path.basename(icon_path), (20, 20))
            if pixmap and not pixmap.isNull():
                icon = QIcon(pixmap)
                self.view_mode_button.setIcon(icon)
                self.view_mode_button.setIconSize(QSize(20, 20))
                self.view_mode_button.setText("")
            else:
                self.view_mode_button.setIcon(QIcon())
                self.view_mode_button.setText("⊞" if self.view_mode == "grid" else "☰")
        else:
            self.view_mode_button.setIcon(QIcon())
            self.view_mode_button.setText("⊞" if self.view_mode == "grid" else "☰")







