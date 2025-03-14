import json
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel

from app.models.graphql import graphql_router  # Импорт GraphQL маршрутизатора
from app.services.mcp_service import mcp_service

app = FastAPI(title="MCP Server", docs_url="/docs", redoc_url="/redoc")
Instrumentator().instrument(app).expose(app)


@app.on_event("startup")
async def startup_event():
    # Register example tools
    from app.tools.example_tool import register_tools

    await register_tools()

    print("MCP Server started with the following tools:")
    tools = await mcp_service.list_tools()
    for tool_name, tool in tools.items():
        print(f"- {tool_name}: {tool.description}")


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/")
async def root():
    return {"message": "Welcome to MCP Server"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Добавляем GraphQL маршрутизатор
app.include_router(graphql_router, prefix="/graphql")


# Resources API
@app.get("/resources")
async def list_resources():
    """Получить список всех ресурсов"""
    resources = await mcp_service.list_resources()
    return {"resources": resources}


@app.get("/resources/{uri}")
async def get_resource(uri: str):
    """Получить ресурс по URI"""
    resource = await mcp_service.get_resource(uri)
    if not resource:
        raise HTTPException(
            status_code=404,
            detail=f"Resource '{uri}' not found",
        )
    return resource


class ResourceCreate(BaseModel):
    """Модель для создания ресурса"""

    uri: str
    name: str
    description: Optional[str] = None
    mime_type: Optional[str] = None
    content: Optional[str] = None


@app.post("/resources")
async def create_resource(resource: ResourceCreate):
    """Создать новый ресурс"""
    from app.models.mcp import Resource as MCPResource

    new_resource = MCPResource(
        uri=resource.uri,
        name=resource.name,
        description=resource.description,
        mimeType=resource.mime_type,
    )
    await mcp_service.register_resource(new_resource)
    return {
        "message": f"Resource '{resource.uri}' created",
        "resource": new_resource,
    }


# Tools API
@app.get("/tools")
async def list_tools():
    tools = await mcp_service.list_tools()
    return {"tools": list(tools.values())}


class ToolParameters(BaseModel):
    # Общие параметры
    operation: Optional[str] = None
    path: Optional[str] = None
    content: Optional[str] = None

    # Параметры для text_analysis
    text: Optional[str] = None
    analysis_type: Optional[str] = None

    # Параметры для weather
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # Параметры для image_processing
    image_data: Optional[str] = None
    params: Optional[Dict[str, Any]] = None

    model_config = {"extra": "allow"}  # Разрешаем дополнительные поля


@app.post("/tools/{tool_name}")
async def execute_tool(tool_name: str, parameters: ToolParameters):
    try:
        # Convert to dict and remove None values
        params_dict = {
            k: v for k, v in parameters.model_dump().items() if v is not None
        }
        result = await mcp_service.execute_tool(tool_name, params_dict)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Prompts API
@app.get("/prompts")
async def list_prompts():
    """Получить список всех промптов"""
    prompts = await mcp_service.list_prompts()
    return {"prompts": prompts}


@app.get("/prompts/{name}")
async def get_prompt(name: str):
    """Получить промпт по имени"""
    prompt = await mcp_service.get_prompt(name)
    if not prompt:
        raise HTTPException(
            status_code=404,
            detail=f"Prompt '{name}' not found",
        )
    return prompt


class PromptArguments(BaseModel):
    """Модель для аргументов промпта"""

    model_config = {"extra": "allow"}  # Разрешаем дополнительные поля


@app.post("/prompts/{name}")
async def execute_prompt(name: str, arguments: PromptArguments):
    """Выполнить промпт"""
    try:
        # Преобразуем в словарь и удаляем значения None
        args_dict = {k: v for k, v in arguments.model_dump().items() if v is not None}
        messages = await mcp_service.execute_prompt(name, args_dict)
        return {"messages": messages}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Sampling API
class SamplingRequest(BaseModel):
    """Модель для запроса сэмплирования"""

    messages: List[Dict[str, Any]]
    model_preferences: Optional[Dict[str, Any]] = None
    system_prompt: Optional[str] = None
    include_context: Optional[str] = "none"
    temperature: Optional[float] = None
    max_tokens: Optional[int] = 1024
    stop_sequences: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


@app.post("/sampling")
async def create_sampling(request: SamplingRequest):
    """Создать запрос на сэмплирование LLM"""
    try:
        from app.models.mcp import SamplingRequest as MCPSamplingRequest

        # Преобразование запроса в формат MCP
        mcp_request = MCPSamplingRequest(
            messages=request.messages,
            modelPreferences=request.model_preferences,
            systemPrompt=request.system_prompt,
            includeContext=request.include_context,
            temperature=request.temperature,
            maxTokens=request.max_tokens or 1024,
            stopSequences=request.stop_sequences,
            metadata=request.metadata,
        )

        # Выполнение запроса сэмплирования
        result = await mcp_service.create_sampling(mcp_request)
        return result
    except NotImplementedError:
        raise HTTPException(
            status_code=501,
            detail="Sampling functionality is not implemented yet",
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                message_type = message.get("type")
                message_data = message.get("data", {})

                if message_type == "tool_request":
                    response = await mcp_service.execute_tool(
                        message_data.get("name", ""), message_data.get("parameters", {})
                    )
                    await websocket.send_json(
                        {"type": "tool_response", "data": response}
                    )
                elif message_type == "register_tool":
                    from app.models.mcp import Tool

                    tool = Tool(
                        name=message_data.get("name"),
                        description=message_data.get("description"),
                        input_schema=message_data.get("input_schema", {}),
                    )
                    await mcp_service.register_tool(tool)
                    await websocket.send_json(
                        {
                            "type": "registration_response",
                            "data": {
                                "status": "success",
                                "message": f"Tool '{tool.name}' registered",
                            },
                        }
                    )
                elif message_type == "resource_request":
                    resource_uri = message_data.get("uri")
                    resource = await mcp_service.get_resource(resource_uri)
                    if resource:
                        await websocket.send_json(
                            {
                                "type": "resource_response",
                                "data": {
                                    "resource": resource,
                                    "status": "success",
                                },
                            }
                        )
                    else:
                        await websocket.send_json(
                            {
                                "type": "resource_response",
                                "data": {
                                    "status": "error",
                                    "message": f"Resource '{resource_uri}' not found",
                                },
                            }
                        )
                elif message_type == "prompt_request":
                    prompt_name = message_data.get("name")
                    prompt_args = message_data.get("arguments", {})

                    messages = await mcp_service.execute_prompt(
                        prompt_name,
                        prompt_args,
                    )
                    await websocket.send_json(
                        {
                            "type": "prompt_response",
                            "data": {
                                "messages": messages,
                                "status": "success",
                            },
                        }
                    )
                elif message_type == "sampling_request":
                    # Преобразование запроса в формат MCP
                    from app.models.mcp import SamplingRequest as MCPSamplingRequest

                    try:
                        mcp_request = MCPSamplingRequest(
                            messages=message_data.get("messages", []),
                            modelPreferences=message_data.get("model_preferences"),
                            systemPrompt=message_data.get("system_prompt"),
                            includeContext=message_data.get("include_context", "none"),
                            temperature=message_data.get("temperature"),
                            maxTokens=message_data.get("max_tokens", 1024),
                            stopSequences=message_data.get("stop_sequences"),
                            metadata=message_data.get("metadata"),
                        )

                        result = await mcp_service.create_sampling(mcp_request)
                        await websocket.send_json(
                            {
                                "type": "sampling_response",
                                "data": {
                                    "result": result,
                                    "status": "success",
                                },
                            }
                        )
                    except NotImplementedError:
                        await websocket.send_json(
                            {
                                "type": "sampling_response",
                                "data": {
                                    "status": "error",
                                    "message": "Sampling functionality is not implemented yet",
                                },
                            }
                        )
                    except Exception as e:
                        await websocket.send_json(
                            {
                                "type": "sampling_response",
                                "data": {
                                    "status": "error",
                                    "message": str(e),
                                },
                            }
                        )
                else:
                    await websocket.send_json(
                        {"type": "error", "data": {"message": "Unknown message type"}}
                    )
            except json.JSONDecodeError:
                await websocket.send_json(
                    {"type": "error", "data": {"message": "Invalid JSON"}}
                )
            except Exception as e:
                await websocket.send_json(
                    {"type": "error", "data": {"message": str(e)}}
                )
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
