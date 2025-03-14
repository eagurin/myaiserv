"""
Фабрика для создания инструментов MCP.
"""

from typing import Dict, Optional, Type

from app.core.base.tool import MCPTool


class ToolFactory:
    """
    Фабрика для создания инструментов MCP.

    Реализует паттерн Factory Method для создания инструментов
    различных типов.
    """

    _registry: Dict[str, Type[MCPTool]] = {}

    @classmethod
    def register(cls, name: str, tool_class: Type[MCPTool]) -> None:
        """
        Регистрирует класс инструмента в реестре.

        Args:
            name: Имя типа инструмента
            tool_class: Класс инструмента
        """
        cls._registry[name] = tool_class

    @classmethod
    def create(cls, tool_type: str, **kwargs) -> Optional[MCPTool]:
        """
        Создает экземпляр инструмента по указанному типу.

        Args:
            tool_type: Тип инструмента из реестра
            **kwargs: Аргументы для создания инструмента

        Returns:
            Optional[MCPTool]: Экземпляр инструмента или None, если тип не найден
        """
        tool_class = cls._registry.get(tool_type)
        if not tool_class:
            return None

        return tool_class(**kwargs)

    @classmethod
    def get_registered_types(cls) -> Dict[str, Type[MCPTool]]:
        """
        Возвращает словарь зарегистрированных типов инструментов.

        Returns:
            Dict[str, Type[MCPTool]]: Словарь {имя_типа: класс_инструмента}
        """
        return cls._registry.copy()
