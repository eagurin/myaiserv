"""
Инструмент поиска.

Предоставляет функциональность для выполнения различных типов поиска.
"""

import logging
from typing import Any, Dict, Optional, Protocol

import httpx

from app.core.base.tool import MCPTool
from app.tools.search.strategies import (
    FacetedSearchStrategy,
    SemanticSearchStrategy,
    TextSearchStrategy,
)

logger = logging.getLogger(__name__)


class SearchStrategy(Protocol):
    """
    Протокол для стратегий поиска.
    """

    async def search(
        self,
        query: str,
        index: str,
        params: Dict[str, Any],
        client: httpx.AsyncClient,
    ) -> Dict[str, Any]:
        """
        Выполняет поиск.

        Args:
            query: Поисковый запрос
            index: Индекс для поиска
            params: Дополнительные параметры
            client: HTTP клиент

        Returns:
            Dict[str, Any]: Результаты поиска
        """
        ...


class SearchStrategyFactory:
    """
    Фабрика для создания стратегий поиска.
    """

    @staticmethod
    def get_strategy(operation_type: str) -> SearchStrategy:
        """
        Возвращает стратегию поиска по типу операции.

        Args:
            operation_type: Тип операции поиска

        Returns:
            SearchStrategy: Стратегия поиска

        Raises:
            ValueError: Если указан неизвестный тип операции
        """
        strategies = {
            "text": TextSearchStrategy(),
            "semantic": SemanticSearchStrategy(),
            "faceted": FacetedSearchStrategy(),
        }

        if operation_type not in strategies:
            raise ValueError(
                f"Неизвестный тип операции поиска: {operation_type}. "
                f"Доступные типы: {', '.join(strategies.keys())}"
            )

        return strategies[operation_type]


class SearchTool(MCPTool):
    """
    Инструмент для выполнения поисковых операций.

    Поддерживает различные типы поиска:
    - Полнотекстовый поиск
    - Семантический поиск
    - Фасетный поиск
    """

    input_schema = {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["text", "semantic", "faceted"],
                "description": "Тип операции поиска",
            },
            "query": {
                "type": "string",
                "description": "Поисковый запрос",
            },
            "index": {
                "type": "string",
                "description": "Индекс Elasticsearch для поиска",
            },
            "params": {
                "type": "object",
                "description": "Дополнительные параметры поиска",
                "properties": {
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Поля для поиска",
                    },
                    "size": {
                        "type": "integer",
                        "description": "Количество результатов",
                    },
                    "from_": {
                        "type": "integer",
                        "description": "Смещение для пагинации",
                    },
                    "sort": {
                        "type": "array",
                        "description": "Параметры сортировки",
                    },
                    "filters": {
                        "type": "array",
                        "description": "Фильтры для поиска",
                    },
                    "facets": {
                        "type": "object",
                        "description": "Параметры фасетов для поиска",
                    },
                    "vector_field": {
                        "type": "string",
                        "description": "Поле с векторными эмбеддингами",
                    },
                    "es_url": {
                        "type": "string",
                        "description": "URL Elasticsearch",
                    },
                },
            },
        },
        "required": ["operation", "query", "index"],
    }

    def __init__(self, name: str = "search", description: str = ""):
        """
        Инициализирует инструмент поиска.

        Args:
            name: Имя инструмента
            description: Описание инструмента
        """
        if not description:
            description = (
                "Инструмент для выполнения поисковых операций. "
                "Поддерживает полнотекстовый, семантический и фасетный поиск."
            )

        super().__init__(name=name, description=description)
        self.client = None

    async def initialize(self) -> None:
        """
        Инициализирует инструмент.
        """
        logger.info("Инициализация инструмента поиска")
        self.client = httpx.AsyncClient(timeout=30.0)

    async def cleanup(self) -> None:
        """
        Освобождает ресурсы инструмента.
        """
        logger.info("Освобождение ресурсов инструмента поиска")
        if self.client:
            await self.client.aclose()

    async def execute(
        self,
        operation: str,
        query: str,
        index: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Выполняет поисковую операцию.

        Args:
            operation: Тип операции поиска
            query: Поисковый запрос
            index: Индекс для поиска
            params: Дополнительные параметры

        Returns:
            Dict[str, Any]: Результаты поиска

        Raises:
            ValueError: Если указаны некорректные параметры
        """
        if not query:
            raise ValueError("Поисковый запрос не может быть пустым")

        if not index:
            raise ValueError("Необходимо указать индекс для поиска")

        if not params:
            params = {}

        logger.info(
            f"Выполнение поиска: операция={operation}, "
            f"запрос='{query}', индекс={index}"
        )

        try:
            # Получаем стратегию поиска
            strategy = SearchStrategyFactory.get_strategy(operation)

            # Выполняем поиск с выбранной стратегией
            result = await strategy.search(
                query=query,
                index=index,
                params=params,
                client=self.client,
            )

            return result
        except ValueError as e:
            logger.error(f"Ошибка валидации: {str(e)}")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"Ошибка HTTP: {str(e)}")
            raise ValueError(f"Ошибка при выполнении запроса: {str(e)}")
        except Exception as e:
            logger.exception(f"Непредвиденная ошибка: {str(e)}")
            raise ValueError(f"Ошибка при выполнении поиска: {str(e)}")
