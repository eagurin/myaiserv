import os
import platform
from datetime import datetime

import psutil

from app.core.base_resources import FileResource, JSONResource, MemoryResource
from app.services.mcp_service import mcp_service


class SystemInfoResource(MemoryResource):
    """Ресурс с системной информацией"""

    async def initialize(self) -> None:
        await super().initialize()
        # Обновляем системную информацию при инициализации
        await self.update_system_info()

    async def update_system_info(self) -> None:
        """Обновление системной информации"""
        info = {
            "os": platform.system(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "disk_usage": psutil.disk_usage("/").percent,
            "timestamp": datetime.now().isoformat(),
        }
        await self.write(info)


class ApplicationLogsResource(FileResource):
    """Ресурс с логами приложения"""

    async def initialize(self) -> None:
        """Создаем директорию для логов при необходимости"""
        await super().initialize()
        if not os.path.exists(self.path):
            await self.write("Log file initialized")


class APIDocsResource(JSONResource):
    """Ресурс с OpenAPI документацией"""

    async def initialize(self) -> None:
        await super().initialize()
        # Инициализируем базовую OpenAPI документацию
        api_docs = {
            "openapi": "3.0.0",
            "info": {"title": "MCP Server API", "version": "1.0.0"},
            "paths": {
                "/tools": {
                    "get": {
                        "summary": "List available tools",
                        "responses": {"200": {"description": "List of tools"}},
                    }
                }
            },
        }
        await self.write(api_docs)


class DBSchemaResource(JSONResource):
    """Ресурс со схемой базы данных"""

    async def initialize(self) -> None:
        await super().initialize()
        # Инициализируем базовую схему
        schema = {
            "tables": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "id", "type": "integer", "primary_key": True},
                        {"name": "username", "type": "varchar(255)"},
                        {"name": "email", "type": "varchar(255)"},
                    ],
                }
            ]
        }
        await self.write(schema)


async def register_resources():
    """Регистрация всех ресурсов"""
    # Создаем экземпляры ресурсов
    resources = [
        SystemInfoResource(name="System Information", mime_type="application/json"),
        ApplicationLogsResource(
            name="Application Logs",
            path=os.path.join(os.getcwd(), "logs", "app.log"),
            mime_type="text/plain",
        ),
        APIDocsResource(
            name="API Documentation",
            path=os.path.join(os.getcwd(), "docs", "api.json"),
        ),
        DBSchemaResource(
            name="Database Schema",
            path=os.path.join(os.getcwd(), "docs", "schema.json"),
        ),
    ]

    # Инициализируем и регистрируем ресурсы
    for resource in resources:
        await resource.initialize()
        await mcp_service.register_resource(resource)

    # Регистрируем обработчик чтения ресурсов
    async def resource_reader(uri: str) -> dict:
        """Обработчик чтения ресурсов"""
        resource = next((r for r in resources if r.uri == uri), None)

        if not resource:
            return {
                "uri": uri,
                "error": "Resource not found",
                "timestamp": datetime.now().isoformat(),
            }

        try:
            content = await resource.read()
            return {
                "uri": uri,
                "content": content,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "uri": uri,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    # Устанавливаем обработчик чтения ресурсов
    mcp_service._read_resource = resource_reader


# Регистрируем ресурсы при импорте

import asyncio

asyncio.create_task(register_resources())
