"""
Тесты для проверки эндпоинтов MCP сервера.
"""

import json
from collections.abc import AsyncGenerator
from typing import Dict

import pytest
import websockets
from fastapi.testclient import TestClient
from httpx import AsyncClient
from websockets.client import WebSocketClientProtocol

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Фикстура для синхронного клиента FastAPI."""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Фикстура для асинхронного клиента FastAPI."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# REST API тесты
def test_health_check(client: TestClient) -> None:
    """Тест эндпоинта проверки здоровья."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_list_tools(client: TestClient) -> None:
    """Тест получения списка инструментов."""
    response = client.get("/tools")
    assert response.status_code == 200
    tools = response.json()["tools"]
    assert isinstance(tools, list)
    assert len(tools) > 0
    assert all(
        isinstance(tool, dict) and "name" in tool and "description" in tool
        for tool in tools
    )


def test_execute_file_operations_tool(client: TestClient) -> None:
    """Тест выполнения инструмента file_operations."""
    response = client.post(
        "/tools/file_operations",
        json={
            "operation": "list",
            "path": "app",
        },
    )
    assert response.status_code == 200
    result = response.json()
    assert "success" in result
    assert result["success"] is True
    assert "result" in result
    assert "content" in result["result"]


def test_execute_weather_tool(client: TestClient) -> None:
    """Тест выполнения инструмента weather."""
    response = client.post(
        "/tools/weather",
        json={
            "latitude": 40.7128,
            "longitude": -74.0060,
        },
    )
    assert response.status_code == 200
    result = response.json()
    assert "success" in result
    assert "result" in result
    assert "content" in result["result"]


# GraphQL тесты
def test_graphql_get_tools(client: TestClient) -> None:
    """Тест GraphQL запроса на получение инструментов."""
    query = """
    query {
        getTools {
            name
            description
            inputSchema
        }
    }
    """
    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "getTools" in data["data"]
    tools = data["data"]["getTools"]
    assert isinstance(tools, list)
    assert len(tools) > 0


def test_graphql_execute_tool(client: TestClient) -> None:
    """Тест GraphQL мутации для выполнения инструмента."""
    mutation = """
    mutation {
        executeTool(
            input: {
                name: "weather",
                parameters: {
                    latitude: 40.7128,
                    longitude: -74.0060
                }
            }
        ) {
            content {
                type
                text
            }
            is_error
        }
    }
    """
    response = client.post("/graphql", json={"query": mutation})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "executeTool" in data["data"]


# WebSocket тесты
@pytest.mark.asyncio
async def test_websocket_connection():
    """Тест WebSocket соединения."""
    async with websockets.connect("ws://localhost:8000/ws") as websocket:
        # Тест выполнения инструмента через WebSocket
        await test_websocket_execute_tool(websocket)


async def test_websocket_execute_tool(websocket: WebSocketClientProtocol):
    """Тест выполнения инструмента через WebSocket."""
    message = {
        "type": "execute_tool",
        "tool": "weather",
        "parameters": {
            "latitude": 40.7128,
            "longitude": -74.0060,
        },
    }
    await websocket.send(json.dumps(message))
    response = await websocket.recv()
    data = json.loads(response)
    assert isinstance(data, dict)
    assert "content" in data


# Тесты ошибок
def test_invalid_tool_name(client: TestClient) -> None:
    """Тест запроса к несуществующему инструменту."""
    response = client.post(
        "/tools/nonexistent_tool",
        json={
            "operation": "test",
        },
    )
    assert response.status_code == 404


def test_invalid_tool_parameters(client: TestClient) -> None:
    """Тест запроса с неверными параметрами."""
    response = client.post(
        "/tools/weather",
        json={
            "invalid_param": "test",
        },
    )
    assert response.status_code in (400, 422)  # Validation error


def test_graphql_invalid_query(client: TestClient) -> None:
    """Тест невалидного GraphQL запроса."""
    query = """
    query {
        invalidField {
            name
        }
    }
    """
    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    assert "errors" in data


# Интеграционные тесты
@pytest.mark.asyncio
async def test_tool_execution_flow(async_client: AsyncClient) -> None:
    """
    Интеграционный тест потока выполнения инструмента:
    1. Получение списка инструментов
    2. Выполнение инструмента
    3. Проверка результата
    """
    # 1. Получаем список инструментов
    response = await async_client.get("/tools")
    assert response.status_code == 200
    tools = response.json()["tools"]
    assert len(tools) > 0

    # 2. Выбираем инструмент weather
    weather_tool = next(
        (tool for tool in tools if tool["name"] == "weather"),
        None,
    )
    assert weather_tool is not None

    # 3. Выполняем инструмент
    response = await async_client.post(
        "/tools/weather",
        json={
            "latitude": 40.7128,
            "longitude": -74.0060,
        },
    )
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True


@pytest.mark.asyncio
async def test_multiple_concurrent_requests(async_client: AsyncClient) -> None:
    """Тест одновременного выполнения нескольких запросов."""
    import asyncio

    async def make_request() -> Dict:
        response = await async_client.get("/tools")
        return response.json()

    # Выполняем 10 одновременных запросов
    tasks = [make_request() for _ in range(10)]
    results = await asyncio.gather(*tasks)

    # Проверяем, что все запросы выполнились успешно
    assert len(results) == 10
    assert all("tools" in result for result in results)
