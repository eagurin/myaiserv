"""MCP Service module."""

from asyncio import Queue
from typing import Any, Optional

from app.core.errors import MCPError
from app.models.mcp import (
    Message,
    MessageRole,
    ModelPreferences,
    SamplingRequest,
    SamplingResponse,
)
from app.models.mcp.tool import Tool
from app.storage.base import BaseStorage
from app.storage.elasticsearch import ElasticsearchStorage
from app.storage.redis import RedisStorage


class MCPRegistry:
    """Registry for MCP components."""

    def __init__(self) -> None:
        """Initialize the registry."""
        self.tools: dict[str, Tool] = {}
        self.resources: dict[str, Any] = {}
        self.prompts: dict[str, Any] = {}
        self.samplers: dict[str, Any] = {}
        self.observers: dict[str, set[Queue]] = {}

    def register_tool(self, tool: Tool) -> None:
        """Register a tool."""
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> Tool:
        """Get a tool by name."""
        return self.tools[name]

    def register_resource(self, name: str, resource: Any) -> None:
        """Register a resource."""
        self.resources[name] = resource

    def get_resource(self, name: str) -> Any:
        """Get a resource by name."""
        return self.resources[name]

    def register_prompt(self, name: str, prompt: Any) -> None:
        """Register a prompt."""
        self.prompts[name] = prompt

    def get_prompt(self, name: str) -> Any:
        """Get a prompt by name."""
        return self.prompts[name]

    def register_sampler(self, name: str, sampler: Any) -> None:
        """Register a sampler."""
        self.samplers[name] = sampler

    def get_sampler(self, name: str) -> Any:
        """Get a sampler by name."""
        return self.samplers[name]

    def subscribe_to_resource(self, name: str, queue: Queue) -> None:
        """Subscribe to resource updates."""
        if name not in self.observers:
            self.observers[name] = set()
        self.observers[name].add(queue)

    def unsubscribe_from_resource(self, name: str, queue: Queue) -> None:
        """Unsubscribe from resource updates."""
        if name in self.observers and queue in self.observers[name]:
            self.observers[name].remove(queue)


class MCPService:
    """Service for managing MCP components."""

    def __init__(
        self,
        registry: MCPRegistry,
        storage: Optional[BaseStorage] = None,
    ) -> None:
        """Initialize the service."""
        self.registry = registry
        self.storage = storage or ElasticsearchStorage()
        self.redis = RedisStorage()

    async def initialize(self) -> None:
        """Initialize the service."""
        await self.storage.initialize()

    async def index_prompt(self, prompt: dict) -> dict:
        """Index a prompt in storage."""
        return await self.storage.index_prompt(prompt)

    async def get_prompt(self, prompt_id: str) -> dict:
        """Get a prompt from storage."""
        return await self.storage.get_prompt(prompt_id)

    async def search_prompts(self, query: str) -> list[dict]:
        """Search prompts in storage."""
        return await self.storage.search_prompts(query)

    async def index_resource(self, resource: dict) -> dict:
        """Index a resource in storage."""
        return await self.storage.index_resource(resource)

    async def get_resource(self, resource_id: str) -> dict:
        """Get a resource from storage."""
        return await self.storage.get_resource(resource_id)

    async def search_resources(self, query: str) -> list[dict]:
        """Search resources in storage."""
        results = await self.storage.search_resources(query)
        return [
            {
                "id": result["id"],
                "name": result["name"],
                "type": result["type"],
                "content": result["content"],
            }
            for result in results
        ]

    async def delete_resource(self, resource_id: str) -> None:
        """Delete a resource from storage."""
        await self.storage.delete_resource(resource_id)

    async def execute_tool(self, tool_name: str, params: dict) -> dict:
        """Execute a tool."""
        try:
            tool = self.registry.get_tool(tool_name)
            result = await tool.execute(params)
            return {"success": True, "result": result}
        except MCPError as err:
            raise MCPError(f"Tool execution failed: {err}") from err

    async def process_message(
        self,
        message: Message,
        preferences: Optional[ModelPreferences] = None,
    ) -> dict:
        """Process a message."""
        try:
            if message.role == MessageRole.USER:
                # Process user message
                response = await self._process_user_message(message, preferences)
            elif message.role == MessageRole.ASSISTANT:
                # Process assistant message
                response = await self._process_assistant_message(message)
            else:
                response = {"error": f"Unsupported message role: {message.role}"}

            return response
        except MCPError as err:
            raise MCPError(f"Message processing failed: {err}") from err

    async def _process_user_message(
        self,
        message: Message,
        preferences: Optional[ModelPreferences] = None,
    ) -> dict:
        """Process a user message."""
        try:
            # Extract content and prepare request
            content = message.content[0].content if message.content else ""
            response = await self._generate_response(content, preferences)
            return response
        except MCPError as err:
            raise MCPError(f"User message processing failed: {err}") from err

    async def _process_assistant_message(self, message: Message) -> dict:
        """Process an assistant message."""
        try:
            # Extract content and prepare response
            content = message.content[0].content if message.content else ""
            return {"response": content}
        except MCPError as err:
            raise MCPError(f"Assistant message processing failed: {err}") from err

    async def _generate_response(
        self,
        content: str,
        preferences: Optional[ModelPreferences] = None,
    ) -> dict:
        """Generate a response using sampling."""
        try:
            # Prepare sampling request
            request = SamplingRequest(
                prompt=content,
                preferences=preferences or ModelPreferences(),
            )

            # Get sampler and generate response
            sampler = self.registry.get_sampler("default")
            response = await sampler.sample(request)

            return {"response": response.text}
        except MCPError as err:
            raise MCPError(f"Response generation failed: {err}") from err

    async def process_sampling_request(
        self,
        request: SamplingRequest,
    ) -> SamplingResponse:
        """Process a sampling request."""
        try:
            sampler = self.registry.get_sampler(request.sampler or "default")
            response = await sampler.sample(request)
            return response
        except MCPError as err:
            raise MCPError(f"Sampling request failed: {err}") from err

    async def execute_graphql(self, query: str, variables: dict) -> dict:
        """Execute a GraphQL query."""
        try:
            # Execute query and return result
            result = await self._execute_graphql_query(query, variables)
            return result
        except MCPError as err:
            raise MCPError(f"GraphQL execution failed: {err}") from err

    async def _execute_graphql_query(self, query: str, variables: dict) -> dict:
        """Execute a GraphQL query internally."""
        try:
            # Execute query using schema
            result = {"data": {}}  # Placeholder for actual GraphQL execution
            return result
        except Exception as err:
            raise MCPError(f"GraphQL query execution failed: {err}") from err

    async def register_tool(self, tool: Tool) -> None:
        """Регистрация инструмента в сервисе."""
        self.registry.register_tool(tool)

    async def list_tools(self) -> dict:
        """Получение списка всех инструментов."""
        return self.registry.tools

    async def list_prompts(self) -> list:
        """Получение списка всех промптов."""
        return list(self.registry.prompts.values())

    async def list_resources(self) -> list:
        """Получение списка всех ресурсов."""
        return list(self.registry.resources.values())


# Создаем глобальный экземпляр MCPRegistry
mcp_registry = MCPRegistry()

# Создаем глобальный экземпляр MCPService
mcp_service = MCPService(registry=mcp_registry)
