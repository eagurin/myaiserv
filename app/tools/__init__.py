"""
Инструменты MCP.

Этот пакет содержит инструменты, которые могут быть использованы
через MCP API.
"""

from app.tools.file import FileSystemTool
from app.tools.registry import register_tools
from app.tools.weather import WeatherTool

# Импортируем дополнительные инструменты, если они доступны
try:
    from app.tools.text import TextProcessorTool
except ImportError:
    TextProcessorTool = None

try:
    from app.tools.search import SearchTool
except ImportError:
    SearchTool = None

__all__ = [
    "FileSystemTool",
    "WeatherTool",
    "register_tools",
]

# Добавляем дополнительные инструменты в __all__, если они доступны
if TextProcessorTool is not None:
    __all__.append("TextProcessorTool")

if SearchTool is not None:
    __all__.append("SearchTool")
