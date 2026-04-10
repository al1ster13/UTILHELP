import re
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser, QPushButton, QHBoxLayout, QLabel, QScrollArea
from PyQt6.QtCore import Qt, QUrl, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QDesktopServices
from custom_dialogs import CustomNewsDialog
from scroll_helper import configure_scroll_area
from scroll_helper import configure_scroll_area
from localization import t


class NewsTab(QWidget):
    """Вкладка новостей - показывает актуальные новости и обновления"""

    def __init__(self):
        super().__init__()
        
        self.current_news_dialog = None
        
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

        self.title_label = QLabel(t("tabs.news"))
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
                background-color: {c['scrollbar_bg']};
                width: 16px;
                border-radius: 0px;
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
                background: transparent;
                height: 0px;
                width: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: {c['scrollbar_bg']};
            }}
        """)

        self.news_content = QTextBrowser()
        self.news_content.setOpenExternalLinks(False)
        self.news_content.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.news_content.anchorClicked.connect(self.handle_news_click)
        self.news_content.setStyleSheet(f"""
            QTextBrowser {{
                background-color: {c['news_bg']};
                border: none;
                border-radius: 10px;
                padding: 20px 0px 20px 20px;
                color: {c['text_primary']};
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
        """)
        
        self.scroll_area.setWidget(self.news_content)
        configure_scroll_area(self.scroll_area)
        
        self.layout.addWidget(self.scroll_area)
        
        self.news_data = []

    def set_data(self, news_data):
        """Установить данные новостей из JSON"""
        self.news_data = news_data
        self.load_news_from_data()

    def load_news_from_data(self):
        """Загрузка новостей из данных"""
        from theme_manager import theme_manager
        c = theme_manager.colors

        try:
            if not self.news_data:
                self.news_content.setText(f"""
                    <div style="text-align: center; color: {c['text_hint']}; padding: 50px;">
                        <h2 style="color: {c['text_primary']};">{t("news.no_news")}</h2>
                        <p>{t("news.check_connection")}</p>
                    </div>
                """)
                return
            
            sorted_news = sorted(self.news_data, key=lambda x: x.get('datetime_sort', ''), reverse=True)
            
            from localization import get_localized_news_title
            
            from theme_manager import theme_manager
            c = theme_manager.colors

            html_content = ""
            for news_item in sorted_news:
                news_id = news_item.get('id', 0)
                title = get_localized_news_title(news_item)
                date = news_item.get('date', '')
                time_val = news_item.get('time', '')

                if date and time_val:
                    datetime_display = f"{date} {t('news.at')} {time_val}"
                elif date:
                    datetime_display = date
                else:
                    datetime_display = ""

                html_content += f"""
                <div style="margin-bottom: 20px; padding: 10px;">
                    <div style="font-size: 20px; color: {c['text_primary']}; font-weight: bold; margin-bottom: 4px;">
                        <a href="news_{news_id}" style="color: {c['text_primary']}; text-decoration: none;">
                            {title}
                        </a>
                    </div>
                    <div style="color: {c['text_secondary']}; font-size: 12px; font-weight: bold;">
                        {datetime_display}
                    </div>
                </div>
                <hr style="border: none; height: 1px; background-color: {c['border']}; margin: 10px 0;">
                """

            self.news_content.setText(html_content)
            
        except Exception as e:
            from theme_manager import theme_manager
            c = theme_manager.colors
            self.news_content.setText(f"""
                <div style="text-align: center; color: {c['error']}; padding: 50px;">
                    <h3>{t("news.load_error")}</h3>
                    <p>{str(e)}</p>
                </div>
            """)


    def handle_news_click(self, url):
        url_str = url.toString()
        if url_str.startswith("news_"):
            news_id = url_str.replace("news_", "")
            self.show_news_details(news_id)  
        else:
            QDesktopServices.openUrl(QUrl(url_str))

    def show_news_details(self, news_id):
        try:
            if self.current_news_dialog is not None:
                try:
                    self.current_news_dialog.close()
                    self.current_news_dialog = None
                except:
                    pass
            
            news_item = None
            for item in self.news_data:
                if str(item.get('id', '')) == str(news_id):
                    news_item = item
                    break
            
            if news_item:
                from localization import get_localized_news_title, get_localized_news_content
                
                title = get_localized_news_title(news_item)
                content = get_localized_news_content(news_item)
                date = news_item.get('date', '')
                time = news_item.get('time', '')
                
                # Формируем дату с переводом
                if date and time:
                    datetime_display = f"{date} {t('news.at')} {time}"
                elif date:
                    datetime_display = date
                else:
                    datetime_display = ""
                
                from theme_manager import theme_manager
                c = theme_manager.colors

                detailed_content = f"""
                <div style="padding: 0px; margin: 0px;">
                    <h2 style="color: {c['text_primary']}; font-size: 24px; font-weight: bold; margin: 0px 0px 5px 0px; text-align: center;">
                        {title}
                    </h2>
                    <p style="color: {c['text_hint']}; font-size: 12px; margin: 0px 0px 15px 0px; text-align: center;">
                        {datetime_display}
                    </p>
                    <div style="color: {c['text_primary']}; line-height: 1.6; font-size: 13px; margin-top: 15px;">
                        {content}
                    </div>
                </div>
                """
                
                dialog = CustomNewsDialog(title, detailed_content, self)
                self.current_news_dialog = dialog  

                dialog.finished.connect(self.on_news_dialog_closed)
                
                dialog.show()
                dialog.start_fade_in()
                
                dialog.exec()
            else:
                error_content = f"""
                <div style="padding: 20px; text-align: center;">
                    <p style="color: #ff4757; font-size: 14px;">
                        {t("news.not_found")}
                    </p>
                </div>
                """
                dialog = CustomNewsDialog(t("errors.download_failed"), error_content, self)
                dialog.finished.connect(self.on_news_dialog_closed)
                dialog.exec()
                
        except Exception as e:
            error_content = f"""
            <div style="padding: 20px; text-align: center;">
                <p style="color: #ff4757; font-size: 14px;">
                    {t("news.load_error")}: {str(e)}
                </p>
            </div>
            """
            dialog = CustomNewsDialog(t("news.load_error"), error_content, self)
            dialog.finished.connect(self.on_news_dialog_closed)
            dialog.exec()

    
    def on_news_dialog_closed(self):
        """Обработчик закрытия диалога новости"""
        self.current_news_dialog = None
        self.load_news_from_data()
    
    def reset_search_and_scroll(self):
        """Сброс прокрутки при переключении вкладки"""
        if hasattr(self, 'scroll_area'):
            self.scroll_area.verticalScrollBar().setValue(0)
        
        if self.current_news_dialog is not None:
            try:
                self.current_news_dialog.close()
                self.current_news_dialog = None
            except:
                pass

    def update_translations(self):
        """Обновление переводов при смене языка"""
        from localization import t
        
        if self.current_news_dialog is not None:
            try:
                self.current_news_dialog.close()
                self.current_news_dialog = None
            except:
                pass
        
        if hasattr(self, 'title_label'):
            self.title_label.setText(t("tabs.news"))
        
        self.load_news_from_data()

    def apply_theme(self):
        """Применить тему к вкладке новостей"""
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
        
        if hasattr(self, 'scroll_area'):
            self.scroll_area.setStyleSheet(f"""
                QScrollArea {{
                    border: none;
                    background-color: transparent;
                }}
                QScrollBar:vertical {{
                    background-color: {c['scrollbar_bg']};
                    width: 16px;
                    border-radius: 0px;
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
                    background: transparent;
                    height: 0px;
                    width: 0px;
                }}
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                    background: {c['scrollbar_bg']};
                }}
            """)
        
        if hasattr(self, 'news_content'):
            self.news_content.setStyleSheet(f"""
                QTextBrowser {{
                    background-color: {c['news_bg']};
                    border: none;
                    border-radius: 10px;
                    padding: 20px 0px 20px 20px;
                    color: {c['text_primary']};
                    font-size: 14px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }}
            """)
        
        self.load_news_from_data()
