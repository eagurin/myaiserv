from abc import abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base_mcp import BaseMCPComponent


class BasePrompt(BaseMCPComponent):
    """Базовый класс для всех промптов"""

    def __init__(self, name: str, description: str, arguments: List[Dict[str, Any]]):
        super().__init__(name, description)
        self.arguments = arguments
        self._system_prompt: Optional[str] = None

    def set_system_prompt(self, prompt: str) -> None:
        """Установка системного промпта"""
        self._system_prompt = prompt

    def validate_arguments(self, arguments: Dict[str, Any]) -> None:
        """Валидация аргументов промпта"""
        required_args = {
            arg["name"] for arg in self.arguments if arg.get("required", False)
        }
        missing_args = required_args - set(arguments.keys())
        if missing_args:
            raise ValueError(f"Missing required arguments: {', '.join(missing_args)}")

    @abstractmethod
    async def generate_messages(
        self, arguments: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Генерация сообщений для промпта"""
        pass

    async def execute(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Выполнение промпта"""
        try:
            # Валидируем аргументы
            self.validate_arguments(arguments)

            # Логируем выполнение
            await self.log_event(
                "execute",
                {
                    "arguments": arguments,
                    "timestamp": datetime.now().isoformat(),
                },
            )

            # Генерируем сообщения
            messages = await self.generate_messages(arguments)

            # Добавляем системный промпт если есть
            if self._system_prompt:
                messages.insert(
                    0,
                    {
                        "role": "system",
                        "content": {
                            "type": "text",
                            "text": self._system_prompt,
                        },
                    },
                )

            return messages

        except Exception as e:
            await self.handle_error(e)
            raise


class CodeAnalysisPrompt(BasePrompt):
    """Промпт для анализа кода"""

    def __init__(self):
        super().__init__(
            name="analyze-code",
            description="Analyze code for potential improvements and issues",
            arguments=[
                {
                    "name": "language",
                    "description": "Programming language of the code",
                    "required": True,
                },
                {
                    "name": "code",
                    "description": "Code to analyze",
                    "required": True,
                },
                {
                    "name": "focus",
                    "description": "Focus of analysis (performance/security/style)",
                    "required": False,
                },
            ],
        )

    async def generate_messages(
        self, arguments: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        return [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": f"Please analyze this {arguments['language']} code focusing on {arguments.get('focus', 'general improvements')}:\n\n{arguments['code']}",
                },
            }
        ]


class DataAnalysisPrompt(BasePrompt):
    """Промпт для анализа данных"""

    def __init__(self):
        super().__init__(
            name="analyze-data",
            description="Analyze data and provide insights",
            arguments=[
                {
                    "name": "data",
                    "description": "Data to analyze (JSON or CSV format)",
                    "required": True,
                },
                {
                    "name": "analysis_type",
                    "description": "Type of analysis to perform",
                    "required": True,
                },
            ],
        )

    async def generate_messages(
        self, arguments: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        return [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": f"Please perform a {arguments['analysis_type']} analysis on this data:\n\n{arguments['data']}",
                },
            }
        ]


class DocumentationPrompt(BasePrompt):
    """Промпт для генерации документации"""

    def __init__(self):
        super().__init__(
            name="generate-docs",
            description="Generate documentation for code or API",
            arguments=[
                {
                    "name": "content",
                    "description": "Content to document",
                    "required": True,
                },
                {
                    "name": "format",
                    "description": "Documentation format (markdown/rst/html)",
                    "required": False,
                },
            ],
        )

    async def generate_messages(
        self, arguments: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        format_type = arguments.get("format", "markdown")
        return [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": f"Please generate {format_type} documentation for:\n\n{arguments['content']}",
                },
            }
        ]


class SQLPrompt(BasePrompt):
    """Промпт для генерации SQL запросов"""

    def __init__(self):
        super().__init__(
            name="generate-sql",
            description="Generate SQL queries from natural language",
            arguments=[
                {
                    "name": "description",
                    "description": "Natural language description of the query",
                    "required": True,
                },
                {
                    "name": "dialect",
                    "description": "SQL dialect (mysql/postgresql/sqlite)",
                    "required": False,
                },
            ],
        )

    async def generate_messages(
        self, arguments: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        dialect = arguments.get("dialect", "postgresql")
        return [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": f"Generate a {dialect} SQL query for: {arguments['description']}",
                },
            }
        ]
