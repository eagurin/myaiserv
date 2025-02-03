from elasticsearch import AsyncElasticsearch
import os
import asyncio
from datetime import datetime


async def migrate_up():
    """Добавление поддержки векторного поиска"""
    es = AsyncElasticsearch(
        [os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")]
    )

    try:
        # Обновляем маппинг для промптов
        await es.indices.put_mapping(
            index="mcp_prompts",
            body={
                "properties": {
                    "embedding": {
                        "type": "dense_vector",
                        "dims": 384,
                        "index": True,
                        "similarity": "cosine",
                    },
                    "text_chunks": {
                        "type": "nested",
                        "properties": {
                            "content": {"type": "text"},
                            "embedding": {
                                "type": "dense_vector",
                                "dims": 384,
                                "index": True,
                                "similarity": "cosine",
                            },
                        },
                    },
                }
            },
        )
        print("Updated mcp_prompts mapping")

        # Обновляем маппинг для ресурсов
        await es.indices.put_mapping(
            index="mcp_resources",
            body={
                "properties": {
                    "embedding": {
                        "type": "dense_vector",
                        "dims": 384,
                        "index": True,
                        "similarity": "cosine",
                    },
                    "text_chunks": {
                        "type": "nested",
                        "properties": {
                            "content": {"type": "text"},
                            "embedding": {
                                "type": "dense_vector",
                                "dims": 384,
                                "index": True,
                                "similarity": "cosine",
                            },
                        },
                    },
                    "metadata": {
                        "properties": {
                            "tags": {"type": "keyword"},
                            "category": {"type": "keyword"},
                            "embedding": {
                                "type": "dense_vector",
                                "dims": 384,
                                "index": True,
                                "similarity": "cosine",
                            },
                        }
                    },
                }
            },
        )
        print("Updated mcp_resources mapping")

        # Создаем индекс для кэширования векторов
        if not await es.indices.exists(index="mcp_vectors"):
            await es.indices.create(
                index="mcp_vectors",
                body={
                    "settings": {"number_of_shards": 1, "number_of_replicas": 0},
                    "mappings": {
                        "properties": {
                            "vector_id": {"type": "keyword"},
                            "vector": {
                                "type": "dense_vector",
                                "dims": 384,
                                "index": True,
                                "similarity": "cosine",
                            },
                            "source": {"type": "keyword"},
                            "created_at": {"type": "date"},
                            "metadata": {"type": "object"},
                        }
                    },
                },
            )
            print("Created mcp_vectors index")

        # Создаем метаданные миграции
        await es.index(
            index=".migrations",
            id="002_vector_search",
            document={
                "name": "002_vector_search",
                "executed_at": datetime.utcnow().isoformat(),
            },
        )

    finally:
        await es.close()


async def migrate_down():
    """Удаление поддержки векторного поиска"""
    es = AsyncElasticsearch(
        [os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")]
    )

    try:
        # Удаляем индекс векторов
        if await es.indices.exists(index="mcp_vectors"):
            await es.indices.delete(index="mcp_vectors")
            print("Deleted mcp_vectors index")

        # Обновляем маппинги, удаляя поля векторов
        await es.indices.put_mapping(
            index="mcp_prompts",
            body={"properties": {"embedding": None, "text_chunks": None}},
        )
        print("Removed vector fields from mcp_prompts")

        await es.indices.put_mapping(
            index="mcp_resources",
            body={
                "properties": {
                    "embedding": None,
                    "text_chunks": None,
                    "metadata": {"properties": {"embedding": None}},
                }
            },
        )
        print("Removed vector fields from mcp_resources")

        # Удаляем метаданные миграции
        await es.delete(index=".migrations", id="002_vector_search", ignore=[404])

    finally:
        await es.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2 or sys.argv[1] not in ["up", "down"]:
        print("Usage: python 002_vector_search.py [up|down]")
        sys.exit(1)

    command = sys.argv[1]
    asyncio.run(migrate_up() if command == "up" else migrate_down())
