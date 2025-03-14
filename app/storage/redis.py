import json
import os
from typing import Any, Dict, List, Optional

import redis.asyncio as redis


class RedisStorage:
    """Класс для работы с Redis"""

    def __init__(self):
        self.redis = redis.from_url(
            os.getenv("REDIS_URL", "redis://redis:6379"),
            encoding="utf-8",
            decode_responses=True,
        )
        self.default_ttl = 3600  # 1 час

    async def close(self):
        """Закрытие соединения"""
        await self.redis.close()

    # Методы для работы с промптами
    async def cache_prompt(
        self, prompt_id: str, data: Dict[str, Any], ttl: int = None
    ) -> None:
        """Кэширование промпта"""
        key = f"prompt:{prompt_id}"
        await self.redis.set(key, json.dumps(data), ex=ttl or self.default_ttl)
        # Добавляем в список последних промптов
        await self.redis.lpush("prompt:recent", prompt_id)
        await self.redis.ltrim("prompt:recent", 0, 99)  # Храним только 100 последних

    async def get_cached_prompt(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """Получение промпта из кэша"""
        key = f"prompt:{prompt_id}"
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def get_recent_prompts(self, limit: int = 10) -> List[str]:
        """Получение списка последних промптов"""
        return await self.redis.lrange("prompt:recent", 0, limit - 1)

    # Методы для работы с ресурсами
    async def cache_resource(
        self, uri: str, data: Dict[str, Any], ttl: int = None
    ) -> None:
        """Кэширование ресурса"""
        key = f"resource:{uri}"
        await self.redis.set(key, json.dumps(data), ex=ttl or self.default_ttl)

    async def get_cached_resource(self, uri: str) -> Optional[Dict[str, Any]]:
        """Получение ресурса из кэша"""
        key = f"resource:{uri}"
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def increment_resource_usage(self, uri: str) -> int:
        """Увеличение счетчика использования ресурса"""
        key = f"resource:usage:{uri}"
        count = await self.redis.incr(key)
        # Добавляем в сортированное множество популярных ресурсов
        await self.redis.zadd("resource:popular", {uri: count})
        return count

    async def get_popular_resources(self, limit: int = 10) -> List[str]:
        """Получение списка популярных ресурсов"""
        return await self.redis.zrevrange("resource:popular", 0, limit - 1)

    # Методы для работы с сессиями
    async def create_session(
        self, session_id: str, data: Dict[str, Any], ttl: int = 3600
    ) -> None:
        """Создание сессии"""
        key = f"session:{session_id}"
        await self.redis.set(key, json.dumps(data), ex=ttl)

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Получение сессии"""
        key = f"session:{session_id}"
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def update_session(
        self, session_id: str, data: Dict[str, Any], ttl: int = 3600
    ) -> None:
        """Обновление сессии"""
        await self.create_session(session_id, data, ttl)

    async def delete_session(self, session_id: str) -> None:
        """Удаление сессии"""
        key = f"session:{session_id}"
        await self.redis.delete(key)

    # Методы для работы с rate limiting
    async def check_rate_limit(self, key: str, limit: int, window: int) -> bool:
        """Проверка rate limit

        Args:
                key: Ключ для rate limit (например, "ip:123.123.123.123")
                limit: Максимальное количество запросов
                window: Временное окно в секундах
        """
        current = await self.redis.get(f"ratelimit:{key}")
        if not current:
            await self.redis.set(f"ratelimit:{key}", 1, ex=window)
            return True

        count = int(current)
        if count >= limit:
            return False

        await self.redis.incr(f"ratelimit:{key}")
        return True


# Создаем глобальный экземпляр
redis_storage = RedisStorage()
