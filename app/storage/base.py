from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol


class StorageProtocol(Protocol):
    """Протокол для хранилища данных"""

    @abstractmethod
    async def initialize(self) -> None:
        """Инициализация хранилища"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Закрытие соединений"""
        pass


class BaseStorage(ABC):
    """Базовый класс для хранилища данных"""

    def __init__(self, es_storage, redis_storage):
        self.es = es_storage
        self.redis = redis_storage

    async def initialize(self) -> None:
        """Инициализация хранилища"""
        await self.es.initialize()

    async def close(self) -> None:
        """Закрытие соединений"""
        await self.es.close()
        await self.redis.close()

    # Методы для работы с промптами
    async def get_prompt(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """Получение промпта"""
        # Пробуем получить из кэша
        prompt = await self.redis.get_cached_prompt(prompt_id)
        if prompt:
            return prompt

        # Если нет в кэше, получаем из ES
        prompt = await self.es.get_prompt(prompt_id)
        if prompt:
            # Кэшируем результат
            await self.redis.cache_prompt(prompt_id, prompt)
        return prompt

    async def save_prompt(self, prompt_data: Dict[str, Any]) -> str:
        """Сохранение промпта"""
        # Сохраняем в ES
        prompt_id = await self.es.index_prompt(prompt_data)
        # Кэшируем
        await self.redis.cache_prompt(prompt_id, prompt_data)
        return prompt_id

    async def search_prompts(self, query: str, size: int = 10) -> List[Dict[str, Any]]:
        """Поиск промптов"""
        return await self.es.search_prompts(query, size)

    # Методы для работы с ресурсами
    async def get_resource(self, resource_uri: str) -> Optional[Dict[str, Any]]:
        """Получение ресурса"""
        # Пробуем получить из кэша
        resource = await self.redis.get_cached_resource(resource_uri)
        if resource:
            # Увеличиваем счетчик использования
            await self.redis.increment_resource_usage(resource_uri)
            return resource

        # Если нет в кэше, получаем из ES
        resource = await self.es.get_resource(resource_uri)
        if resource:
            # Кэшируем результат
            await self.redis.cache_resource(resource_uri, resource)
            # Увеличиваем счетчик использования
            await self.redis.increment_resource_usage(resource_uri)
        return resource

    async def save_resource(self, resource_data: Dict[str, Any]) -> str:
        """Сохранение ресурса"""
        # Сохраняем в ES
        resource_id = await self.es.index_resource(resource_data)
        # Кэшируем
        await self.redis.cache_resource(resource_data["uri"], resource_data)
        return resource_id

    async def search_resources(
        self, query: str, mime_type: Optional[str] = None, size: int = 10
    ) -> List[Dict[str, Any]]:
        """Поиск ресурсов"""
        return await self.es.search_resources(query, mime_type, size)

    async def delete_resource(self, resource_uri: str) -> bool:
        """Удаление ресурса"""
        # Удаляем из ES
        success = await self.es.delete_resource(resource_uri)
        if success:
            # Удаляем из кэша
            key = f"resource:{resource_uri}"
            await self.redis.delete(key)
        return success

    # Методы для работы с сессиями
    async def create_session(
        self, session_id: str, data: Dict[str, Any], ttl: int = 3600
    ) -> None:
        """Создание сессии"""
        await self.redis.create_session(session_id, data, ttl)

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Получение сессии"""
        return await self.redis.get_session(session_id)

    async def update_session(
        self, session_id: str, data: Dict[str, Any], ttl: int = 3600
    ) -> None:
        """Обновление сессии"""
        await self.redis.update_session(session_id, data, ttl)

    async def delete_session(self, session_id: str) -> None:
        """Удаление сессии"""
        await self.redis.delete_session(session_id)

    # Методы для аналитики
    async def get_popular_resources(self, limit: int = 10) -> List[str]:
        """Получение популярных ресурсов"""
        return await self.redis.get_popular_resources(limit)

    async def get_recent_prompts(self, limit: int = 10) -> List[str]:
        """Получение последних промптов"""
        return await self.redis.get_recent_prompts(limit)


# Создаем глобальный экземпляр хранилища
from .elasticsearch import es_storage
from .redis import redis_storage

storage = BaseStorage(es_storage, redis_storage)
