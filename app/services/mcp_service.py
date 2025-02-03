import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, List, Optional

import jsonschema
from fastapi import HTTPException
from graphql import GraphQLSchema, graphql


from app.core.base_sampling import BaseSampler, KeywordSampler, MLSampler
from app.models.mcp import (ContentType, MCPError, Message, MessageContent,
                            MessageRole, ModelPreferences, Prompt, Resource,
                            SamplingRequest, SamplingResponse, Tool,
                            mcp_schema)
from app.utils.prompt_loader import prompt_loader


class MCPService:
    """Сервис для обработки MCP запросов

    Provides:
            - Resource management
            - Tool execution
            - Prompt handling
            - Sampling support
            - GraphQL API
    """

    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.resources: Dict[str, Resource] = {}
        self.prompts: Dict[str, Prompt] = {}
        self.subscriptions: Dict[str, List[AsyncGenerator]] = {}
        self.samplers: Dict[str, BaseSampler] = {}

    # Resource Management
    async def register_resource(self, resource: Resource) -> None:
        """Регистрация нового ресурса"""
        self.resources[resource.uri] = resource

    async def get_resource(self, uri: str) -> Optional[Resource]:
        """Получение ресурса по URI"""
        return self.resources.get(uri)

    async def list_resources(self) -> List[Resource]:
        """Список всех доступных ресурсов"""
        return list(self.resources.values())

    @asynccontextmanager
    async def subscribe_to_resource(self, uri: str):
        """Подписка на обновления ресурса"""
        if uri not in self.subscriptions:
            self.subscriptions[uri] = []

        queue = asyncio.Queue()
        self.subscriptions[uri].append(queue)
        try:
            yield queue
        finally:
            self.subscriptions[uri].remove(queue)

    # Tool Management
    async def register_tool(self, tool: Tool) -> None:
        """Регистрация нового инструмента"""
        self.tools[tool.name] = tool

    async def get_tool(self, name: str) -> Optional[Tool]:
        """Получение инструмента по имени"""
        return self.tools.get(name)

    async def list_tools(self) -> Dict[str, Tool]:
        """Список всех доступных инструментов"""
        return self.tools

    async def execute_tool(
        self, name: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Выполнение инструмента"""
        tool = await self.get_tool(name)
        if not tool:
            raise HTTPException(
                status_code=404, detail=f"Tool '{name}' not found"
            )

        # Validate parameters against schema
        try:
            jsonschema.validate(parameters, tool.input_schema)
        except jsonschema.exceptions.ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Execute tool logic
        try:
            result = await self._execute_tool_logic(tool, parameters)
            return {"content": [{"type": "text", "text": str(result)}]}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Prompt Management
    async def register_prompt(self, prompt: Prompt) -> None:
        """Регистрация нового промпта"""
        self.prompts[prompt.name] = prompt

    async def get_prompt(self, name: str) -> Optional[Prompt]:
        """Получение промпта по имени"""
        return self.prompts.get(name)

    async def list_prompts(self) -> List[Prompt]:
        """Список всех доступных промптов"""
        return list(self.prompts.values())

    async def execute_prompt(
        self, name: str, arguments: Dict[str, Any]
    ) -> List[Message]:
        """Выполнение промпта"""
        prompt = await self.get_prompt(name)
        if not prompt:
            raise HTTPException(
                status_code=404, detail=f"Prompt '{name}' not found"
            )

        # Validate required arguments
        if prompt.arguments:
            required = [arg.name for arg in prompt.arguments if arg.required]
            missing = [arg for arg in required if arg not in arguments]
            if missing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required arguments: {', '.join(missing)}",
                )

        # Generate messages
        return await self._generate_prompt_messages(prompt, arguments)

    # Sampling Support
    async def register_sampler(self, sampler: BaseSampler) -> None:
        """Регистрация нового сэмплера"""
        self.samplers[sampler.name] = sampler

    async def get_sampler(self, name: str) -> Optional[BaseSampler]:
        """Получение сэмплера по имени"""
        return self.samplers.get(name)

    async def list_samplers(self) -> List[BaseSampler]:
        """Список всех доступных сэмплеров"""
        return list(self.samplers.values())

    async def create_sampling(
        self, request: SamplingRequest
    ) -> SamplingResponse:
        """Создание сэмплинга для LLM"""
        sampler = await self.get_sampler("keyword_sampler")
        if not sampler:
            raise HTTPException(status_code=500, detail="No sampler available")

        prepared_request = await sampler.execute(request.dict())
        # Implement sampling logic here
        raise NotImplementedError("Sampling not implemented")

    # GraphQL API
    async def handle_graphql(
        self, query: str, variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Обработка GraphQL запроса"""
        from app.models.mcp import mcp_schema

        result = await graphql(
            mcp_schema, query, variable_values=variables
        )
        if result.errors:
            raise HTTPException(status_code=400, detail=str(result.errors[0]))
        return result.data

    # Private methods
    async def _execute_tool_logic(
        self, tool: Tool, parameters: Dict[str, Any]
    ) -> Any:
        """Execute tool logic"""
        try:
            result = await tool.execute(parameters)
            return result
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Tool execution failed: {str(e)}"
            )

    async def _generate_prompt_messages(
        self, prompt: Prompt, arguments: Dict[str, Any]
    ) -> List[Message]:
        """Генерация сообщений для промпта"""
        raise NotImplementedError(
            f"Prompt '{prompt.name}' generation not implemented"
        )

    async def _notify_resource_subscribers(
        self, uri: str, content: Any
    ) -> None:
        """Оповещение подписчиков об обновлении ресурса"""
        if uri in self.subscriptions:
            for queue in self.subscriptions[uri]:
                await queue.put(content)


# Создаем глобальный экземпляр сервиса
mcp_service = MCPService()


# Регистрируем сэмплеры
async def register_samplers():
    samplers = [KeywordSampler(), MLSampler()]

    for sampler in samplers:
        await sampler.initialize()
        await mcp_service.register_sampler(sampler)


# Запускаем регистрацию сэмплеров
asyncio.create_task(register_samplers())
