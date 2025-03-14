"""
Модели промптов MCP.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class PromptArgument(BaseModel):
    """
    Аргумент для промпта MCP.

    Attributes:
        name: Имя аргумента
        description: Описание аргумента
        required: Является ли аргумент обязательным
    """

    name: str = Field(..., description="Имя аргумента")
    description: Optional[str] = Field(None, description="Описание аргумента")
    required: bool = Field(False, description="Является ли аргумент обязательным")


class Prompt(BaseModel):
    """
    Модель промпта MCP.

    Attributes:
        name: Уникальное имя промпта
        description: Описание промпта
        arguments: Список аргументов промпта
    """

    name: str = Field(..., description="Уникальное имя промпта")
    description: Optional[str] = Field(None, description="Описание промпта")
    arguments: Optional[List[PromptArgument]] = Field(
        None, description="Список аргументов промпта"
    )
