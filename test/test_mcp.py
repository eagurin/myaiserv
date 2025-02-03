import pytest
from fastapi.testclient import TestClient
import json
from datetime import datetime

from app.main import app
from app.services.mcp_service import mcp_service
from app.models.mcp import Tool, Resource, Prompt, Message

client = TestClient(app)

# Фикстуры
@pytest.fixture
def test_tool():
	return Tool(
		name="test-tool",
		description="Test tool",
		inputSchema={
			"type": "object",
			"properties": {
				"param": {"type": "string"}
			},
			"required": ["param"]
		}
	)

@pytest.fixture
def test_resource():
	return Resource(
		uri="test://resource",
		name="Test Resource",
		description="Test resource",
		mimeType="text/plain"
	)

@pytest.fixture
def test_prompt():
	return Prompt(
		name="test-prompt",
		description="Test prompt",
		arguments=[
			{
				"name": "test_arg",
				"description": "Test argument",
				"required": True
			}
		]
	)

# Тесты инструментов
@pytest.mark.asyncio
async def test_list_tools():
	response = client.get("/tools")
	assert response.status_code == 200
	assert "tools" in response.json()

@pytest.mark.asyncio
async def test_execute_tool(test_tool):
	await mcp_service.register_tool(test_tool)
	
	response = client.post(
		f"/tools/{test_tool.name}",
		json={"param": "test"}
	)
	assert response.status_code == 200

# Тесты ресурсов
@pytest.mark.asyncio
async def test_list_resources():
	response = client.get("/resources")
	assert response.status_code == 200
	assert "resources" in response.json()

@pytest.mark.asyncio
async def test_get_resource(test_resource):
	await mcp_service.register_resource(test_resource)
	
	response = client.get(f"/resources/{test_resource.uri}")
	assert response.status_code == 200

# Тесты промптов
@pytest.mark.asyncio
async def test_list_prompts():
	response = client.get("/prompts")
	assert response.status_code == 200
	assert "prompts" in response.json()

@pytest.mark.asyncio
async def test_execute_prompt(test_prompt):
	await mcp_service.register_prompt(test_prompt)
	
	response = client.post(
		f"/prompts/{test_prompt.name}",
		json={"test_arg": "test"}
	)
	assert response.status_code == 200

# Тесты GraphQL
@pytest.mark.asyncio
async def test_graphql_tools_query():
	query = """
	query {
		listTools {
			name
			description
		}
	}
	"""
	response = client.post(
		"/graphql",
		json={"query": query}
	)
	assert response.status_code == 200
	data = response.json()
	assert "data" in data
	assert "listTools" in data["data"]

# Тесты WebSocket
@pytest.mark.asyncio
async def test_websocket_connection():
	with client.websocket_connect("/mcp") as websocket:
		# Тест инициализации
		websocket.send_json({
			"jsonrpc": "2.0",
			"method": "initialize"
		})
		response = websocket.receive_json()
		assert "result" in response
		assert "capabilities" in response["result"]

# Тесты ошибок
@pytest.mark.asyncio
async def test_tool_not_found():
	response = client.post(
		"/tools/nonexistent",
		json={"param": "test"}
	)
	assert response.status_code == 404

@pytest.mark.asyncio
async def test_invalid_tool_parameters(test_tool):
	await mcp_service.register_tool(test_tool)
	
	response = client.post(
		f"/tools/{test_tool.name}",
		json={"invalid_param": "test"}
	)
	assert response.status_code == 400

# Тесты безопасности
@pytest.mark.asyncio
async def test_cors():
	response = client.options(
		"/tools",
		headers={"Origin": "http://testserver"}
	)
	assert response.status_code == 200
	assert "access-control-allow-origin" in response.headers

@pytest.mark.asyncio
async def test_rate_limiting():
	# Отправляем множество запросов
	responses = [
		client.get("/tools")
		for _ in range(100)
	]
	# Проверяем, что некоторые запросы были ограничены
	assert any(r.status_code == 429 for r in responses)

# Тесты производительности
@pytest.mark.asyncio
async def test_tools_response_time():
	import time
	start = time.time()
	response = client.get("/tools")
	end = time.time()
	
	assert end - start < 0.5  # Ответ должен быть получен менее чем за 500мс
	assert response.status_code == 200

# Тесты интеграции
@pytest.mark.asyncio
async def test_full_workflow(test_tool, test_resource, test_prompt):
	# Регистрируем компоненты
	await mcp_service.register_tool(test_tool)
	await mcp_service.register_resource(test_resource)
	await mcp_service.register_prompt(test_prompt)
	
	# Проверяем инструмент
	tool_response = client.post(
		f"/tools/{test_tool.name}",
		json={"param": "test"}
	)
	assert tool_response.status_code == 200
	
	# Проверяем ресурс
	resource_response = client.get(f"/resources/{test_resource.uri}")
	assert resource_response.status_code == 200
	
	# Проверяем промпт
	prompt_response = client.post(
		f"/prompts/{test_prompt.name}",
		json={"test_arg": "test"}
	)
	assert prompt_response.status_code == 200