import asyncio
import json
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.models.mcp import (
    MCPError,
    Message,
    MessageContent,
    MessageRole,
    ModelPreferences,
    Prompt,
    Resource,
    Tool,
)

from app.services.mcp_service import mcp_service

app = FastAPI(title="MCP Server", docs_url="/docs", redoc_url="/redoc")

# Initialize Prometheus metrics
Instrumentator().instrument(app).expose(app)


@app.on_event("startup")
async def startup_event():
    # Tools are registered when imported
    print("MCP Server started with the following tools:")
    for tool_name, tool in mcp_service.list_tools().items():
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
    return {"tools": list(mcp_service.list_tools().values())}


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
                    response = await mcp_service.execute_tool(message_data)
                    await websocket.send_json({
                        "type": "tool_response",
                        "data": response
                    })
                elif message_type == "register_tool":
                    tool = Tool(**message_data)
                    mcp_service.register_tool(tool)
                    await websocket.send_json({
                        "type": "registration_response",
                        "data": {
                            "status": "success",
                            "message": f"Tool '{tool.name}' registered"
                        }
                    })
                else:
                    await websocket.send_json({
                        "type": "error",
                        "data": {"message": "Unknown message type"}
                    })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": "Invalid JSON"}
                })
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": str(e)}
                })
    except WebSocketDisconnect:
        manager.disconnect(websocket)
