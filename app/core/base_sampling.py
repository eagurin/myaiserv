from abc import abstractmethod
from datetime import datetime
from typing import Any, Dict, List

from app.utils.prompt_loader import prompt_loader

from .base_mcp import BaseMCPComponent


class BaseSampler(BaseMCPComponent):
    """Базовый класс для сэмплинга"""

    def __init__(self, name: str):
        super().__init__(name)
        self._model_preferences: Dict[str, Any] = {}
        self._system_prompts = prompt_loader.load_prompts("system_prompts")

    def set_model_preferences(self, preferences: Dict[str, Any]) -> None:
        """Установка предпочтений модели"""
        self._model_preferences = preferences

    @abstractmethod
    async def determine_task_type(self, messages: List[Dict[str, Any]]) -> str:
        """Определение типа задачи на основе сообщений"""
        pass

    @abstractmethod
    async def prepare_context(
        self, messages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Подготовка контекста для сэмплинга"""
        pass

    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение сэмплинга"""
        try:
            # Определяем тип задачи
            task_type = await self.determine_task_type(request.get("messages", []))

            # Получаем системный промпт
            if task_type in self._system_prompts:
                request["systemPrompt"] = self._system_prompts[task_type]

            # Добавляем предпочтения модели
            if self._model_preferences:
                request["modelPreferences"] = self._model_preferences

            # Подготавливаем контекст
            if request.get("includeContext") != "none":
                context = await self.prepare_context(request.get("messages", []))
                request["messages"].extend(context)

            # Логируем выполнение
            await self.log_event(
                "execute",
                {
                    "task_type": task_type,
                    "timestamp": datetime.now().isoformat(),
                },
            )

            return request

        except Exception as e:
            await self.handle_error(e)
            raise


class KeywordSampler(BaseSampler):
    """Сэмплер на основе ключевых слов"""

    def __init__(self):
        super().__init__("keyword_sampler")
        self._keywords = {
            "code_assistant": ["code", "programming", "function", "class"],
            "data_analyst": ["data", "analysis", "statistics", "dataset"],
            "documentation_writer": [
                "documentation",
                "docs",
                "guide",
                "manual",
            ],
            "sql_expert": ["sql", "query", "database", "table"],
            "security_analyst": [
                "security",
                "vulnerability",
                "secure",
                "threat",
            ],
        }

    async def determine_task_type(self, messages: List[Dict[str, Any]]) -> str:
        """Определение типа задачи по ключевым словам"""
        content = " ".join(
            msg.get("content", {}).get("text", "").lower() for msg in messages
        )

        for task_type, keywords in self._keywords.items():
            if any(word in content for word in keywords):
                return task_type

        return "code_assistant"  # По умолчанию

    async def initialize(self) -> None:
        """Initialize the keyword sampler"""
        pass  # No initialization needed for keyword-based sampling

    async def cleanup(self) -> None:
        """Cleanup the keyword sampler"""
        pass  # No cleanup needed for keyword-based sampling

    async def prepare_context(
        self, messages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Подготовка контекста на основе типа задачи"""
        task_type = await self.determine_task_type(messages)

        # Здесь можно добавить специфичный для задачи контекст
        context = []

        if task_type == "code_assistant":
            context.append(
                {
                    "role": "system",
                    "content": {
                        "type": "text",
                        "text": "Consider best practices and potential optimizations.",
                    },
                }
            )
        elif task_type == "data_analyst":
            context.append(
                {
                    "role": "system",
                    "content": {
                        "type": "text",
                        "text": "Focus on statistical significance and data quality.",
                    },
                }
            )

        return context


class MLSampler(BaseSampler):
    """Сэмплер на основе машинного обучения"""

    def __init__(self):
        super().__init__("ml_sampler")
        self._model = None  # Здесь можно инициализировать ML модель

    async def determine_task_type(self, messages: List[Dict[str, Any]]) -> str:
        """Определение типа задачи с помощью ML"""
        # Здесь должна быть реализация классификации с помощью ML
        return "code_assistant"

    async def prepare_context(
        self, messages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Подготовка контекста с помощью ML"""
        # Здесь должна быть реализация генерации контекста с помощью ML
        return []

    async def initialize(self) -> None:
        """Инициализация ML модели"""
        # Здесь должна быть инициализация ML модели
        pass

    async def cleanup(self) -> None:
        """Очистка ресурсов ML модели"""
        # Здесь должна быть очистка ресурсов ML модели
        pass
