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
        self.base_dir = "/app"  # Update base directory for Docker container
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
                        "description": "File or directory path (relative to project root)",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write (for write operation)",
                    },
                },
                "required": ["operation", "path"],
            },
        )

    def _validate_path(self, path: str) -> str:
        """Validate and normalize path to ensure it's within allowed directory"""
        # Convert to absolute path
        if os.path.isabs(path):
            full_path = path
        else:
            full_path = os.path.join(self.base_dir, path)
        
        # Resolve to absolute path, removing any .. or . components
        full_path = os.path.abspath(full_path)
        
        # Ensure path is within base directory
        if not full_path.startswith(self.base_dir):
            raise ValueError(f"Access denied: Path must be within {self.base_dir}")
            
        return full_path


    async def initialize(self) -> None:
        """Initialize the tool"""
        await self.log_event("initialize", {"status": "success"})

    async def cleanup(self) -> None:
        """Cleanup any resources used by the tool"""
        await self.log_event("cleanup", {"status": "success"})

    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        try:
            operation = parameters["operation"]
            path = self._validate_path(parameters["path"])

            # Debug logging
            await self.log_event("debug", {
                "operation": operation,
                "path": path,
                "exists": os.path.exists(path),
                "is_dir": os.path.isdir(path),
                "abs_path": os.path.abspath(path)
            })

            if operation == "read":
                result = await self._read_file(path)
            elif operation == "write":
                result = await self._write_file(path, parameters.get("content", ""))
            elif operation == "list":
                result = await self._list_directory(path)
            elif operation == "delete":
                result = await self._delete_file(path)
            else:
                raise ValueError(f"Unknown operation: {operation}")

            return {"content": [{"type": "text", "text": result}]}
        except Exception as e:
            await self.handle_error(e)
            error_msg = f"Error: {str(e)}\nPath: {path}\nExists: {os.path.exists(path)}\nIs Dir: {os.path.isdir(path)}"
            return {"content": [{"type": "text", "text": error_msg}], "isError": True}


    async def _read_file(self, path: str) -> str:
        try:
            if not os.path.exists(path):
                raise FileNotFoundError(f"File not found: {path}")
            if not os.path.isfile(path):
                raise IsADirectoryError(f"Path is a directory: {path}")
            with open(path, "r") as f:
                return f.read()
        except Exception as e:
            await self.log_event("error", {"operation": "read", "path": path, "error": str(e)})
            raise

    async def _write_file(self, path: str, content: str) -> str:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            return "File written successfully"
        except Exception as e:
            await self.log_event("error", {"operation": "write", "path": path, "error": str(e)})
            raise

    async def _list_directory(self, path: str) -> str:
        """List contents of a directory"""
        try:
            # Debug logging
            await self.log_event("debug", {
                "operation": "list",
                "path": path,
                "exists": os.path.exists(path),
                "is_dir": os.path.isdir(path),
                "abs_path": os.path.abspath(path)
            })

            if not os.path.exists(path):
                raise FileNotFoundError(f"Directory not found: {path}")
            if not os.path.isdir(path):
                raise NotADirectoryError(f"Not a directory: {path}")
            
            contents = []
            for item in sorted(os.listdir(path)):
                item_path = os.path.join(path, item)
                item_type = "directory" if os.path.isdir(item_path) else "file"
                contents.append(f"{item} ({item_type})")
            
            if not contents:
                return "Directory is empty"
                
            return "\n".join(contents)
        except Exception as e:
            await self.log_event("error", {
                "operation": "list",
                "path": path,
                "error": str(e),
                "exists": os.path.exists(path),
                "is_dir": os.path.isdir(path)
            })
            raise

    async def _delete_file(self, path: str) -> str:
        try:
            if not os.path.exists(path):
                raise FileNotFoundError(f"File not found: {path}")
            if os.path.isdir(path):
                raise IsADirectoryError(f"Cannot delete directory: {path}")
            os.remove(path)
            return "File deleted successfully"
        except Exception as e:
            await self.log_event("error", {"operation": "delete", "path": path, "error": str(e)})
            raise


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

    async def initialize(self) -> None:
        """Initialize the tool"""
        await self.log_event("initialize", {"status": "success"})

    async def cleanup(self) -> None:
        """Cleanup any resources used by the tool"""
        await self.log_event("cleanup", {"status": "success"})


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


async def register_tools():
    tools = [FileSystemTool(), WeatherTool()]
    for tool in tools:
        await tool.initialize()
        await mcp_service.register_tool(tool)

# Export register_tools function

__all__ = ["register_tools"]

