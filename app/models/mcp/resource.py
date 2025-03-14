"""
Модель ресурса MCP.
"""

from typing import Optional

from pydantic import BaseModel, Field

from app.models.mcp.enums import ResourceType


class Resource(BaseModel):
    """
    Модель ресурса MCP.

    Examples:
        >>> resource = Resource(
        ...     uri="file:///logs/app.log",
        ...     name="Application Logs",
        ...     description="Application runtime logs",
        ...     mime_type="text/plain"
        ... )

    Attributes:
        uri: Уникальный идентификатор ресурса
        name: Человекочитаемое имя ресурса
        description: Описание ресурса
        mime_type: MIME тип ресурса
        resource_type: Тип ресурса
    """

    uri: str = Field(..., description="Уникальный идентификатор ресурса")
    name: str = Field(..., description="Человекочитаемое имя ресурса")
    description: Optional[str] = Field(None, description="Описание ресурса")
    mime_type: Optional[str] = Field(None, description="MIME тип ресурса")
    resource_type: Optional[ResourceType] = Field(None, description="Тип ресурса")
