"""
Типы данных для UTILHELP
"""
from typing import TypedDict, Optional, List, Dict, Any, Union
from PyQt6.QtWidgets import QWidget


# Типы данных
class ProgramData(TypedDict):
    """Данные программы"""
    name: str
    description: str
    download_url: str
    icon_path: Optional[str]
    version: Optional[str]
    size: Optional[str]
    category: Optional[str]


class DriverData(TypedDict):
    """Данные драйвера"""
    name: str
    description: str
    download_url: str
    icon_path: Optional[str]
    version: Optional[str]
    manufacturer: Optional[str]
    device_type: Optional[str]


class NewsData(TypedDict):
    """Данные новости"""
    title: str
    content: str
    date: str
    image_url: Optional[str]
    source_url: Optional[str]


class DownloadInfo(TypedDict):
    """Информация о загрузке"""
    filename: str
    program_name: str
    file_type: str
    progress: int
    speed: str
    size: str
    status: str


class SettingsData(TypedDict):
    """Данные настроек"""
    snow_enabled: bool
    theme_light: bool
    auto_update: bool
    auto_scan: bool
    download_path: Optional[str]


# Типы коллекций
ProgramsList = List[ProgramData]
DriversList = List[DriverData]
NewsList = List[NewsData]
DownloadsList = List[DownloadInfo]

# Типы для JSON данных
JSONData = Dict[str, Any]
DataResponse = Dict[str, Union[ProgramsList, DriversList, NewsList]]

# Типы для UI
WidgetType = Union[QWidget, None]
StyleSheet = str

# Типы для логирования
LogLevel = str
LogMessage = str