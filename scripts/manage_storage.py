#!/usr/bin/env python3
import os
import sys
import asyncio
import importlib.util
from pathlib import Path
from typing import List
import click
from elasticsearch import AsyncElasticsearch
import aioredis
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class StorageManager:
    def __init__(self):
        self.es = AsyncElasticsearch(
            [os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")]
        )
        self.redis = aioredis.from_url(
            os.getenv("REDIS_URL", "redis://redis:6379"),
            encoding="utf-8",
            decode_responses=True,
        )

    async def close(self):
        await self.es.close()
        await self.redis.close()

    async def check_connections(self) -> bool:
        """Проверка подключений к ES и Redis"""
        try:
            # Проверяем ES
            es_health = await self.es.cluster.health()
            logger.info(f"Elasticsearch status: {es_health['status']}")

            # Проверяем Redis
            redis_info = await self.redis.info()
            logger.info(f"Redis version: {redis_info['redis_version']}")

            return True
        except Exception as e:
            logger.error(f"Connection check failed: {str(e)}")
            return False

    async def get_migrations(self) -> List[str]:
        """Получение списка выполненных миграций"""
        try:
            result = await self.es.search(
                index=".migrations", body={"sort": [{"executed_at": "desc"}]}
            )
            return [hit["_id"] for hit in result["hits"]["hits"]]
        except:
            return []

    async def run_migration(self, migration_file: Path, direction: str = "up") -> bool:
        """Запуск миграции"""
        try:
            # Импортируем модуль миграции
            spec = importlib.util.spec_from_file_location(
                migration_file.stem, migration_file
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Выполняем миграцию
            if direction == "up":
                await module.migrate_up()
            else:
                await module.migrate_down()

            return True
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            return False

    async def clear_redis(self) -> None:
        """Очистка Redis"""
        await self.redis.flushall()
        logger.info("Redis cleared")


@click.group()
def cli():
    """Утилита для управления хранилищем данных"""
    pass


@cli.command()
def check():
    """Проверка подключений к ES и Redis"""

    async def run():
        manager = StorageManager()
        try:
            result = await manager.check_connections()
            if not result:
                sys.exit(1)
        finally:
            await manager.close()

    asyncio.run(run())


@cli.command()
@click.option("--direction", type=click.Choice(["up", "down"]), default="up")
def migrate(direction):
    """Запуск миграций"""

    async def run():
        manager = StorageManager()
        try:
            # Получаем список миграций
            migrations_dir = (
                Path(__file__).parent.parent / "migrations" / "elasticsearch"
            )
            migration_files = sorted(migrations_dir.glob("*.py"))

            if direction == "up":
                # Выполняем миграции вперед
                executed = await manager.get_migrations()
                for migration_file in migration_files:
                    if migration_file.stem not in executed:
                        logger.info(f"Running migration: {migration_file.name}")
                        if await manager.run_migration(migration_file, "up"):
                            logger.info("Migration successful")
                        else:
                            logger.error("Migration failed")
                            sys.exit(1)
            else:
                # Откатываем миграции
                for migration_file in reversed(migration_files):
                    logger.info(f"Rolling back migration: {migration_file.name}")
                    if await manager.run_migration(migration_file, "down"):
                        logger.info("Rollback successful")
                    else:
                        logger.error("Rollback failed")
                        sys.exit(1)

        finally:
            await manager.close()

    asyncio.run(run())


@cli.command()
def clear_cache():
    """Очистка кэша Redis"""

    async def run():
        manager = StorageManager()
        try:
            await manager.clear_redis()
        finally:
            await manager.close()

    asyncio.run(run())


if __name__ == "__main__":
    cli()
