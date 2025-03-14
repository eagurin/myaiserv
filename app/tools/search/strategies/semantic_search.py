"""
Стратегия семантического поиска.
"""

from typing import Any, Dict, List

import httpx
import numpy as np

from app.utils.embeddings import get_embedding


class SemanticSearchStrategy:
    """
    Стратегия семантического поиска с использованием векторных эмбеддингов.

    Выполняет поиск по семантической близости с использованием
    векторных представлений текста.
    """

    async def search(
        self,
        query: str,
        index: str,
        params: Dict[str, Any],
        client: httpx.AsyncClient,
    ) -> Dict[str, Any]:
        """
        Выполняет семантический поиск в Elasticsearch.

        Args:
            query: Поисковый запрос
            index: Индекс Elasticsearch для поиска
            params: Дополнительные параметры поиска
            client: HTTP клиент для запросов к Elasticsearch

        Returns:
            Dict[str, Any]: Результаты поиска
        """
        size = params.get("size", 10)
        from_ = params.get("from_", 0)
        vector_field = params.get("vector_field", "embedding")

        # Получаем векторное представление запроса
        query_vector = await self._get_embedding(query)

        # Формируем запрос для семантического поиска
        script_source = f"cosineSimilarity(params.query_vector, '{vector_field}') + 1.0"

        es_query = {
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": script_source,
                        "params": {"query_vector": query_vector},
                    },
                },
            },
            "size": size,
            "from": from_,
        }

        # Добавляем фильтры, если они указаны
        if "filters" in params and params["filters"]:
            es_query["query"]["script_score"]["query"] = {
                "bool": {
                    "filter": params["filters"],
                }
            }

        # Выполняем запрос к Elasticsearch
        es_url = f"{params.get('es_url', 'http://localhost:9200')}/{index}/_search"
        response = await client.post(
            es_url,
            json=es_query,
            headers={"Content-Type": "application/json"},
        )

        # Проверяем статус ответа
        response.raise_for_status()

        # Возвращаем результаты
        return response.json()

    async def _get_embedding(self, text: str) -> List[float]:
        """
        Получает векторное представление текста.

        Args:
            text: Текст для векторизации

        Returns:
            List[float]: Векторное представление текста
        """
        # Используем утилиту для получения эмбеддингов
        embedding = await get_embedding(text)

        # Нормализуем вектор для косинусного сходства
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = [float(x / norm) for x in embedding]

        return embedding
