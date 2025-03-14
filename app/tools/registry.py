"""
Регистрация инструментов MCP.
"""

from app.core.factories.tool_factory import ToolFactory
from app.services.mcp_service import mcp_service
from app.tools.file import FileSystemTool
from app.tools.weather import WeatherTool

try:
    from app.tools.text import TextProcessorTool

    HAS_TEXT_PROCESSOR = True
except ImportError:
    HAS_TEXT_PROCESSOR = False

try:
    from app.tools.search import SearchTool

    HAS_SEARCH_TOOL = True
except ImportError:
    HAS_SEARCH_TOOL = False


# Регистрируем инструменты в фабрике
ToolFactory.register("file_operations", FileSystemTool)
ToolFactory.register("weather", WeatherTool)

if HAS_TEXT_PROCESSOR:
    ToolFactory.register("text_processor", TextProcessorTool)

if HAS_SEARCH_TOOL:
    ToolFactory.register("search", SearchTool)


async def register_tools() -> None:
    """Регистрация инструментов с MCP Service."""

    # Регистрируем файловый инструмент
    file_tool = ToolFactory.create("file_operations")
    if file_tool:
        await file_tool.initialize()
        await mcp_service.register_tool(file_tool)

    # Регистрируем инструмент погоды
    weather_tool = ToolFactory.create("weather")
    if weather_tool:
        await weather_tool.initialize()
        await mcp_service.register_tool(weather_tool)

    # Регистрируем инструмент обработки текста
    if HAS_TEXT_PROCESSOR:
        try:
            text_processor_tool = ToolFactory.create("text_processor")
            if text_processor_tool:
                await text_processor_tool.initialize()
                await mcp_service.register_tool(text_processor_tool)
        except Exception as e:
            print(f"Не удалось зарегистрировать инструмент обработки текста: {e}")

    # Регистрируем инструмент поиска
    if HAS_SEARCH_TOOL:
        try:
            search_tool = ToolFactory.create("search")
            if search_tool:
                await search_tool.initialize()
                await mcp_service.register_tool(search_tool)
        except Exception as e:
            print(f"Не удалось зарегистрировать инструмент поиска: {e}")
