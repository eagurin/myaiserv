import json
import os
from datetime import datetime
from typing import Any, Dict

import httpx

from app.core.base_mcp import MCPTool
from app.services.mcp_service import mcp_service


class FileSystemTool(MCPTool):
    """Инструмент для работы с файловой системой"""

    def __init__(self):
        super().__init__(
            name="file_operations",
            description="Perform basic file system operations",
            input_schema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["read", "write", "list", "delete"],
                        "description": "Operation to perform",
                    },
                    "path": {
                        "type": "string",
                        "description": "File or directory path",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write (for write operation)",
                    },
                },
                "required": ["operation", "path"],
            },
        )

    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        operation = parameters["operation"]
        path = parameters["path"]

        await self.log_event("execute", {"operation": operation, "path": path})

        try:
            if operation == "read":
                result = await self._read_file(path)
            elif operation == "write":
                result = await self._write_file(
                    path, parameters.get("content", "")
                )
            elif operation == "list":
                result = await self._list_directory(path)
            elif operation == "delete":
                result = await self._delete_file(path)
            else:
                raise ValueError(f"Unknown operation: {operation}")

            return {"content": [{"type": "text", "text": result}]}

        except Exception as e:
            await self.handle_error(e)
            return {
                "content": [{"type": "text", "text": str(e)}],
                "isError": True,
            }

    async def _read_file(self, path: str) -> str:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        with open(path, "r") as f:
            return f.read()

    async def _write_file(self, path: str, content: str) -> str:
        with open(path, "w") as f:
            f.write(content)
        return "File written successfully"

    async def _list_directory(self, path: str) -> str:
        if not os.path.isdir(path):
            raise NotADirectoryError(f"Not a directory: {path}")
        return "\n".join(os.listdir(path))

    async def _delete_file(self, path: str) -> str:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        os.remove(path)
        return "File deleted successfully"


class WeatherTool(MCPTool):
    """Инструмент для получения погодных данных"""

    def __init__(self):
        super().__init__(
            name="weather",
            description="Get weather information for a location",
            input_schema={
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "Location latitude",
                    },
                    "longitude": {
                        "type": "number",
                        "description": "Location longitude",
                    },
                },
                "required": ["latitude", "longitude"],
            },
        )

    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        lat = parameters["latitude"]
        lon = parameters["longitude"]

        await self.log_event("execute", {"latitude": lat, "longitude": lon})

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.weather.gov/points/{lat},{lon}"
                )
                if response.status_code == 200:
                    data = response.json()
                    forecast_url = data["properties"]["forecast"]
                    forecast_response = await client.get(forecast_url)
                    if forecast_response.status_code == 200:
                        forecast_data = forecast_response.json()
                        result = json.dumps(
                            forecast_data["properties"]["periods"][0], indent=2
                        )
                        return {"content": [{"type": "text", "text": result}]}

            return {
                "content": [
                    {"type": "text", "text": "Failed to fetch weather data"}
                ],
                "isError": True,
            }

        except Exception as e:
            await self.handle_error(e)
            return {
                "content": [{"type": "text", "text": str(e)}],
                "isError": True,
            }


# Создаем и регистрируем инструменты
async def register_tools():
    tools = [FileSystemTool(), WeatherTool()]

    for tool in tools:
        await tool.initialize()
        await mcp_service.register_tool(tool)

    async def tool_execution_wrapper(
        name: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        tool = next((t for t in tools if t.name == name), None)
        if tool:
            return await tool.execute(parameters)
        return {
            "content": [{"type": "text", "text": f"Tool not found: {name}"}],
            "isError": True,
        }

    # Устанавливаем обработчик выполнения инструментов
    mcp_service._execute_tool_logic = tool_execution_wrapper


# Регистрируем инструменты при импорте
import asyncio

asyncio.create_task(register_tools())
