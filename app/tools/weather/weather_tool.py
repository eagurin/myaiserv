"""
Инструмент для получения информации о погоде.
"""

from typing import Any, Dict

import httpx

from app.core.base.tool import MCPTool


class WeatherTool(MCPTool):
    """Инструмент для получения информации о погоде."""

    def __init__(self) -> None:
        super().__init__()
        self.name = "weather"
        self.description = "Get weather information for a location"
        self.input_schema = {
            "type": "object",
            "properties": {
                "latitude": {
                    "type": "number",
                    "description": "Latitude of the location",
                },
                "longitude": {
                    "type": "number",
                    "description": "Longitude of the location",
                },
            },
            "required": ["latitude", "longitude"],
        }

    async def initialize(self) -> bool:
        return True

    async def cleanup(self) -> bool:
        return True

    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        lat = parameters["latitude"]
        lon = parameters["longitude"]

        try:
            # Используем NOAA Weather API для получения данных
            api_url = f"https://api.weather.gov/points/{lat},{lon}"

            async with httpx.AsyncClient() as client:
                # Первый запрос для получения ссылок на прогноз
                response = await client.get(api_url)

                # Проверка статуса ответа
                if response.status_code != 200:
                    error_msg = f"API error: {response.status_code} - {response.text}"
                    return {
                        "content": [{"type": "text", "text": error_msg}],
                        "isError": True,
                    }

                data = response.json()

                # Проверка наличия нужных данных
                if "properties" not in data or "forecast" not in data["properties"]:
                    return {
                        "content": [
                            {"type": "text", "text": "Invalid API response format"}
                        ],
                        "isError": True,
                    }

                # Получаем URL для прогноза
                forecast_url = data["properties"]["forecast"]

                # Второй запрос для получения прогноза
                forecast_response = await client.get(forecast_url)

                if forecast_response.status_code != 200:
                    error_msg = (
                        f"Forecast API error: {forecast_response.status_code} - "
                        f"{forecast_response.text}"
                    )
                    return {
                        "content": [{"type": "text", "text": error_msg}],
                        "isError": True,
                    }

                forecast_data = forecast_response.json()

                if (
                    "properties" not in forecast_data
                    or "periods" not in forecast_data["properties"]
                ):
                    return {
                        "content": [
                            {"type": "text", "text": "Invalid forecast response format"}
                        ],
                        "isError": True,
                    }

                periods = forecast_data["properties"]["periods"]

                # Формируем результат
                location_props = data["properties"].get("relativeLocation", {})
                location_name = location_props.get("properties", {}).get(
                    "city", "Unknown"
                )

                result = f"Weather for {location_name} ({lat}, {lon}):\n\n"

                for period in periods[:3]:  # Берем только первые 3 периода
                    name = period.get("name", "Unknown")
                    temperature = period.get("temperature", "N/A")
                    temp_unit = period.get("temperatureUnit", "F")
                    wind_speed = period.get("windSpeed", "N/A")
                    wind_dir = period.get("windDirection", "N/A")
                    forecast = period.get("shortForecast", "N/A")

                    result += (
                        f"{name}: {temperature}°{temp_unit}, "
                        f"Wind: {wind_speed} {wind_dir}, {forecast}\n"
                    )

                return {"content": [{"type": "text", "text": result}]}

        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"Error: {str(e)}"}],
                "isError": True,
            }
