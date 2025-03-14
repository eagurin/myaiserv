"""
Пример инструмента для MCP.
"""

# Просто импортируем функцию register_tools из registry.py
from app.tools.registry import register_tools

# Явно экспортируем функцию
__all__ = ["register_tools"]

# Функция уже определена в registry.py, поэтому нам не нужно её переопределять здесь.
