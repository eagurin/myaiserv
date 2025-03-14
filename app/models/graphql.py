from typing import List, Optional

import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.scalars import JSON


@strawberry.type
class Tool:
    name: str
    description: str
    input_schema: JSON


@strawberry.type
class Resource:
    uri: str
    name: str
    description: Optional[str] = None
    mime_type: Optional[str] = None


@strawberry.type
class PromptArgument:
    name: str
    description: Optional[str] = None
    required: bool = False


@strawberry.type
class Prompt:
    name: str
    description: Optional[str] = None
    arguments: Optional[List[PromptArgument]] = None


@strawberry.type
class MessageContent:
    type: str
    text: Optional[str] = None
    data: Optional[str] = None
    mime_type: Optional[str] = None
    resource: Optional[Resource] = None


@strawberry.type
class Message:
    role: str
    content: MessageContent


@strawberry.type
class ToolResult:
    content: List[MessageContent]
    is_error: bool = False


@strawberry.type
class PromptResult:
    messages: List[Message]


@strawberry.input
class ToolInput:
    name: str
    parameters: JSON


@strawberry.input
class PromptInput:
    name: str
    arguments: JSON


@strawberry.input
class ResourceInput:
    uri: str
    name: str
    description: Optional[str] = None
    mime_type: Optional[str] = None
    content: Optional[str] = None


@strawberry.type
class Query:
    @strawberry.field
    async def get_tools(self) -> List[Tool]:
        from app.services.mcp_service import mcp_service

        tools = await mcp_service.list_tools()
        return [
            Tool(
                name=tool.name,
                description=tool.description,
                input_schema=tool.input_schema,
            )
            for tool in tools.values()
        ]

    @strawberry.field
    async def get_tool(self, name: str) -> Optional[Tool]:
        from app.services.mcp_service import mcp_service

        tool = await mcp_service.get_tool(name)
        if not tool:
            return None
        return Tool(
            name=tool.name,
            description=tool.description,
            input_schema=tool.input_schema,
        )

    @strawberry.field
    async def get_resources(self) -> List[Resource]:
        from app.services.mcp_service import mcp_service

        resources = await mcp_service.list_resources()
        return [
            Resource(
                uri=resource.uri,
                name=resource.name,
                description=resource.description,
                mime_type=resource.mimeType,
            )
            for resource in resources
        ]

    @strawberry.field
    async def get_resource(self, uri: str) -> Optional[Resource]:
        from app.services.mcp_service import mcp_service

        resource = await mcp_service.get_resource(uri)
        if not resource:
            return None
        return Resource(
            uri=resource.uri,
            name=resource.name,
            description=resource.description,
            mime_type=resource.mimeType,
        )

    @strawberry.field
    async def get_prompts(self) -> List[Prompt]:
        from app.services.mcp_service import mcp_service

        prompts = await mcp_service.list_prompts()
        return [
            Prompt(
                name=prompt.name,
                description=prompt.description,
                arguments=[
                    PromptArgument(
                        name=arg.name,
                        description=arg.description,
                        required=arg.required,
                    )
                    for arg in (prompt.arguments or [])
                ],
            )
            for prompt in prompts
        ]

    @strawberry.field
    async def get_prompt(self, name: str) -> Optional[Prompt]:
        from app.services.mcp_service import mcp_service

        prompt = await mcp_service.get_prompt(name)
        if not prompt:
            return None
        return Prompt(
            name=prompt.name,
            description=prompt.description,
            arguments=[
                PromptArgument(
                    name=arg.name,
                    description=arg.description,
                    required=arg.required,
                )
                for arg in (prompt.arguments or [])
            ],
        )


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def execute_tool(self, input: ToolInput) -> ToolResult:
        from app.services.mcp_service import mcp_service

        try:
            result = await mcp_service.execute_tool(input.name, input.parameters)
            content = [
                MessageContent(
                    type=item.get("type", "text"),
                    text=item.get("text"),
                    data=item.get("data"),
                    mime_type=item.get("mime_type"),
                )
                for item in result.get("content", [])
            ]
            return ToolResult(
                content=content,
                is_error=result.get("isError", False),
            )
        except Exception as e:
            return ToolResult(
                content=[MessageContent(type="text", text=str(e))],
                is_error=True,
            )

    @strawberry.mutation
    async def execute_prompt(self, input: PromptInput) -> PromptResult:
        from app.services.mcp_service import mcp_service

        try:
            messages = await mcp_service.execute_prompt(
                input.name,
                input.arguments,
            )
            return PromptResult(messages=messages)
        except Exception as e:
            # Создаем сообщение об ошибке
            error_message = Message(
                role="system",
                content=MessageContent(
                    type="text",
                    text=f"Error executing prompt: {str(e)}",
                ),
            )
            return PromptResult(messages=[error_message])

    @strawberry.mutation
    async def create_resource(self, input: ResourceInput) -> Resource:
        from app.models.mcp import Resource as MCPResource
        from app.services.mcp_service import mcp_service

        resource = MCPResource(
            uri=input.uri,
            name=input.name,
            description=input.description,
            mimeType=input.mime_type,
        )
        await mcp_service.register_resource(resource)
        return Resource(
            uri=resource.uri,
            name=resource.name,
            description=resource.description,
            mime_type=resource.mimeType,
        )


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_router = GraphQLRouter(schema)
