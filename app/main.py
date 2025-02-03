import asyncio
import json
from typing import Any, Dict, List, Optional, Union

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.models.mcp import (
    MCPError, Message, MessageContent, MessageRole,
    ModelPreferences, Prompt, Resource, Tool,
)
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


@app.get("/tools")
async def list_tools():
    tools = await mcp_service.list_tools()
    return {"tools": list(tools.values())}


class ToolParameters(BaseModel):
    operation: str
    path: str
    content: Optional[str] = None

    model_config = {
        "extra": "allow"  # Allow additional fields
    }

@app.post("/tools/{tool_name}")
async def execute_tool(tool_name: str, parameters: ToolParameters):
    try:
        # Convert to dict and remove None values
        params_dict = {k: v for k, v in parameters.model_dump().items() if v is not None}
        result = await mcp_service.execute_tool(tool_name, params_dict)
        return result
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
                        message_data.get("name", ""),
                        message_data.get("parameters", {})
                    )
                    await websocket.send_json(
                        {"type": "tool_response", "data": response}
                    )
                elif message_type == "register_tool":
                    tool = Tool(**message_data)
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
