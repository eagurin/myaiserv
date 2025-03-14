"""
Стратегия текстового поиска.
"""

from typing import Any, Dict

import httpx


class TextSearchStrategy:
    """
    Стратегия полнотекстового поиска.

    Выполняет поиск по текстовому содержимому с использованием
    Elasticsearch multi_match запроса.
    """

    async def search(
        self,
        query: str,
        index: str,
        params: Dict[str, Any],
        client: httpx.AsyncClient,
    ) -> Dict[str, Any]:
        """
        Выполняет полнотекстовый поиск в Elasticsearch.

        Args:
            query: Поисковый запрос
            index: Индекс Elasticsearch для поиска
            params: Дополнительные параметры поиска
            client: HTTP клиент для запросов к Elasticsearch

        Returns:
            Dict[str, Any]: Результаты поиска
        """
        fields = params.get("fields", ["content", "title"])
        size = params.get("size", 10)
        from_ = params.get("from_", 0)
        sort = params.get("sort", [{"_score": {"order": "desc"}}])

        # Формируем запрос для полнотекстового поиска
        es_query = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": fields,
                    "type": "best_fields",
                    "operator": "and",
                    "fuzziness": "AUTO",
                },
            },
            "size": size,
            "from": from_,
            "sort": sort,
        }

        # Добавляем фильтры, если они указаны
        if "filters" in params and params["filters"]:
            es_query["query"] = {
                "bool": {
                    "must": es_query["query"],
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
