import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from elasticsearch import AsyncElasticsearch, NotFoundError


class ElasticsearchStorage:
    """Класс для работы с Elasticsearch"""

    def __init__(self):
        self.es = AsyncElasticsearch(
            [os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")]
        )
        self.indices = {"prompts": "mcp_prompts", "resources": "mcp_resources"}

    async def initialize(self):
        """Инициализация индексов"""
        # Маппинг для промптов
        prompt_mapping = {
            "mappings": {
                "properties": {
                    "name": {"type": "keyword"},
                    "description": {"type": "text"},
                    "content": {"type": "text"},
                    "arguments": {"type": "nested"},
                    "vector": {"type": "dense_vector", "dims": 384},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                }
            }
        }

        # Маппинг для ресурсов
        resource_mapping = {
            "mappings": {
                "properties": {
                    "uri": {"type": "keyword"},
                    "name": {"type": "text"},
                    "content": {"type": "text"},
                    "mime_type": {"type": "keyword"},
                    "vector": {"type": "dense_vector", "dims": 384},
                    "metadata": {"type": "object"},
                }
            }
        }

        # Создаем индексы если их нет
        for index_name in self.indices.values():
            if not await self.es.indices.exists(index=index_name):
                mapping = (
                    prompt_mapping if "prompts" in index_name else resource_mapping
                )
                await self.es.indices.create(index=index_name, body=mapping)

    async def close(self):
        """Закрытие соединения"""
        await self.es.close()

    # Методы для работы с промптами
    async def index_prompt(self, prompt_data: Dict[str, Any]) -> str:
        """Индексация промпта"""
        prompt_data["created_at"] = datetime.utcnow()
        prompt_data["updated_at"] = datetime.utcnow()

        result = await self.es.index(
            index=self.indices["prompts"], document=prompt_data
        )
        return result["_id"]

    async def get_prompt(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """Получение промпта по ID"""
        try:
            result = await self.es.get(index=self.indices["prompts"], id=prompt_id)
            return result["_source"]
        except NotFoundError:
            return None
        except Exception as e:
            print(f"Error getting prompt {prompt_id}: {e}")
            return None

    async def search_prompts(self, query: str, size: int = 10) -> List[Dict[str, Any]]:
        """Поиск промптов"""
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["name^2", "description", "content"],
                }
            },
            "size": size,
        }

        result = await self.es.search(index=self.indices["prompts"], body=body)
        return [hit["_source"] for hit in result["hits"]["hits"]]

    # Методы для работы с ресурсами
    async def index_resource(self, resource_data: Dict[str, Any]) -> str:
        """Индексация ресурса"""
        result = await self.es.index(
            index=self.indices["resources"], document=resource_data
        )
        return result["_id"]

    async def get_resource(self, resource_uri: str) -> Optional[Dict[str, Any]]:
        """Получение ресурса по URI"""
        try:
            result = await self.es.search(
                index=self.indices["resources"],
                body={"query": {"term": {"uri.keyword": resource_uri}}},
            )
            hits = result["hits"]["hits"]
            return hits[0]["_source"] if hits else None
        except Exception as e:
            print(f"Error getting resource {resource_uri}: {e}")
            return None

    async def search_resources(
        self, query: str, mime_type: Optional[str] = None, size: int = 10
    ) -> List[Dict[str, Any]]:
        """Поиск ресурсов"""
        should_queries = [
            {"multi_match": {"query": query, "fields": ["name^2", "content"]}}
        ]

        if mime_type:
            should_queries.append({"term": {"mime_type.keyword": mime_type}})

        body = {
            "query": {"bool": {"should": should_queries, "minimum_should_match": 1}},
            "size": size,
        }

        result = await self.es.search(index=self.indices["resources"], body=body)
        return [hit["_source"] for hit in result["hits"]["hits"]]

    async def delete_resource(self, resource_uri: str) -> bool:
        """Удаление ресурса"""
        try:
            await self.es.delete_by_query(
                index=self.indices["resources"],
                body={"query": {"term": {"uri.keyword": resource_uri}}},
            )
            return True
        except Exception as e:
            print(f"Error deleting resource {resource_uri}: {e}")
            return False


# Создаем глобальный экземпляр
es_storage = ElasticsearchStorage()
