from elasticsearch import AsyncElasticsearch
import os
import asyncio
from datetime import datetime


async def migrate_up():
    """Создание начальных индексов"""
    es = AsyncElasticsearch(
        [os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")]
    )

    try:
        # Создаем индекс для промптов
        if not await es.indices.exists(index="mcp_prompts"):
            await es.indices.create(
                index="mcp_prompts",
                body={
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 0,
                        "analysis": {
                            "analyzer": {
                                "default": {
                                    "type": "custom",
                                    "tokenizer": "standard",
                                    "filter": [
                                        "lowercase",
                                        "asciifolding",
                                        "word_delimiter",
                                        "snowball",
                                    ],
                                }
                            }
                        },
                    },
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
                    },
                },
            )
            print("Created mcp_prompts index")

        # Создаем индекс для ресурсов
        if not await es.indices.exists(index="mcp_resources"):
            await es.indices.create(
                index="mcp_resources",
                body={
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 0,
                        "analysis": {
                            "analyzer": {
                                "default": {
                                    "type": "custom",
                                    "tokenizer": "standard",
                                    "filter": [
                                        "lowercase",
                                        "asciifolding",
                                        "word_delimiter",
                                        "snowball",
                                    ],
                                }
                            }
                        },
                    },
                    "mappings": {
                        "properties": {
                            "uri": {"type": "keyword"},
                            "name": {"type": "text"},
                            "content": {"type": "text"},
                            "mime_type": {"type": "keyword"},
                            "vector": {"type": "dense_vector", "dims": 384},
                            "metadata": {"type": "object"},
                        }
                    },
                },
            )
            print("Created mcp_resources index")

        # Создаем алиасы для версионирования
        await es.indices.put_alias(index="mcp_prompts", name="prompts_v1")
        await es.indices.put_alias(index="mcp_resources", name="resources_v1")

        # Создаем метаданные миграции
        await es.index(
            index=".migrations",
            id="001_initial_indices",
            document={
                "name": "001_initial_indices",
                "executed_at": datetime.utcnow().isoformat(),
            },
        )

    finally:
        await es.close()


async def migrate_down():
    """Удаление индексов"""
    es = AsyncElasticsearch(
        [os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")]
    )

    try:
        # Удаляем алиасы
        await es.indices.delete_alias(index="mcp_prompts", name="prompts_v1")
        await es.indices.delete_alias(index="mcp_resources", name="resources_v1")

        # Удаляем индексы
        if await es.indices.exists(index="mcp_prompts"):
            await es.indices.delete(index="mcp_prompts")
            print("Deleted mcp_prompts index")

        if await es.indices.exists(index="mcp_resources"):
            await es.indices.delete(index="mcp_resources")
            print("Deleted mcp_resources index")

        # Удаляем метаданные миграции
        await es.delete(index=".migrations", id="001_initial_indices", ignore=[404])

    finally:
        await es.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2 or sys.argv[1] not in ["up", "down"]:
        print("Usage: python 001_initial_indices.py [up|down]")
        sys.exit(1)

    command = sys.argv[1]
    asyncio.run(migrate_up() if command == "up" else migrate_down())
