"""
Стратегия фасетного поиска.
"""

from typing import Any, Dict

import httpx


class FacetedSearchStrategy:
    """
    Стратегия фасетного поиска с агрегацией результатов.

    Выполняет поиск с фильтрацией по заданным критериям и
    возвращает агрегированные фасеты для результатов поиска.
    """

    async def search(
        self,
        query: str,
        index: str,
        params: Dict[str, Any],
        client: httpx.AsyncClient,
    ) -> Dict[str, Any]:
        """
        Выполняет фасетный поиск в Elasticsearch.

        Args:
            query: Поисковый запрос
            index: Индекс Elasticsearch для поиска
            params: Дополнительные параметры поиска
            client: HTTP клиент для запросов к Elasticsearch

        Returns:
            Dict[str, Any]: Результаты поиска с агрегациями
        """
        size = params.get("size", 10)
        from_ = params.get("from_", 0)
        fields = params.get("fields", ["content", "title"])
        facets = params.get("facets", {})

        # Формируем базовый запрос
        es_query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": fields,
                                "type": "best_fields",
                                "operator": "and",
                            }
                        }
                    ]
                }
            },
            "size": size,
            "from": from_,
            "aggs": self._build_aggregations(facets),
        }

        # Добавляем фильтры, если они указаны
        if "filters" in params and params["filters"]:
            es_query["query"]["bool"]["filter"] = params["filters"]

        # Добавляем сортировку, если указана
        if "sort" in params and params["sort"]:
            es_query["sort"] = params["sort"]

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

    def _build_aggregations(
        self,
        facets: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Создает агрегации для фасетного поиска.

        Args:
            facets: Словарь с описанием фасетов

        Returns:
            Dict[str, Dict[str, Any]]: Словарь агрегаций для Elasticsearch
        """
        aggregations = {}

        for facet_name, facet_config in facets.items():
            facet_type = facet_config.get("type", "terms")

            if facet_type == "terms":
                aggregations[facet_name] = {
                    "terms": {
                        "field": facet_config["field"],
                        "size": facet_config.get("size", 10),
                    }
                }
            elif facet_type == "date_histogram":
                aggregations[facet_name] = {
                    "date_histogram": {
                        "field": facet_config["field"],
                        "calendar_interval": facet_config.get(
                            "interval",
                            "month",
                        ),
                        "format": facet_config.get("format", "yyyy-MM-dd"),
                    }
                }
            elif facet_type == "range":
                aggregations[facet_name] = {
                    "range": {
                        "field": facet_config["field"],
                        "ranges": facet_config.get("ranges", []),
                    }
                }

        return aggregations
