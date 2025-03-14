"""
Базовые абстрактные классы для MCP компонентов.
"""

from app.core.base.component import MCPComponent
from app.core.base.observer import Observable, Observer
from app.core.base.prompt import MCPPrompt
from app.core.base.resource import MCPResource
from app.core.base.tool import MCPTool

__all__ = [
    "MCPComponent",
    "MCPTool",
    "MCPResource",
    "MCPPrompt",
    "Observable",
    "Observer",
]
