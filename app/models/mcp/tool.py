"""
Модель инструмента MCP.
"""

from typing import Any, Dict

from pydantic import BaseModel, Field


class Tool(BaseModel):
    """
    Модель инструмента MCP.

    Examples:
        >>> tool = Tool(
        ...     name="calculate_sum",
        ...     description="Add two numbers",
        ...     input_schema={
        ...         "type": "object",
        ...         "properties": {
        ...             "a": {"type": "number"},
        ...             "b": {"type": "number"}
        ...         },
        ...         "required": ["a", "b"]
        ...     }
        ... )

    Attributes:
        name: Уникальное имя инструмента
        description: Описание функциональности
        input_schema: JSON Schema входных параметров
        requires_approval: Требуется ли одобрение
    """

    name: str = Field(..., description="Уникальное имя инструмента")
    description: str = Field(..., description="Описание функциональности")
    input_schema: Dict[str, Any] = Field(
        ..., description="JSON Schema входных параметров"
    )
    requires_approval: bool = Field(False, description="Требуется ли одобрение")
