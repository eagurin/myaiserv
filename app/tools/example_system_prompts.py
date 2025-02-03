from typing import Any, Dict

from app.services.mcp_service import mcp_service
from app.utils.prompt_loader import prompt_loader


async def register_system_prompts():
    """Регистрация системных промптов для сэмплинга"""

    async def sampling_handler(request: Dict[str, Any]) -> Dict[str, Any]:
        """Обработчик запросов на сэмплинг"""
        # Определяем тип задачи на основе контекста
        task_type = determine_task_type(request)

        # Добавляем системный промпт
        system_content = prompt_loader.format_system_prompt(task_type)
        if system_content:
            request["systemPrompt"] = system_content

        return request

    def determine_task_type(request: Dict[str, Any]) -> str:
        """Определение типа задачи на основе контекста запроса"""
        # Анализируем сообщения для определения типа задачи
        messages = request.get("messages", [])
        content = " ".join(
            msg.get("content", {}).get("text", "").lower() for msg in messages
        )

        # Определяем тип задачи по ключевым словам
        keywords = {
            "code_assistant": ["code", "programming", "function", "class"],
            "data_analyst": ["data", "analysis", "statistics", "dataset"],
            "documentation_writer": [
                "documentation",
                "docs",
                "guide",
                "manual",
            ],
            "sql_expert": ["sql", "query", "database", "table"],
            "security_analyst": [
                "security",
                "vulnerability",
                "secure",
                "threat",
            ],
        }

        for prompt_type, words in keywords.items():
            if any(word in content for word in words):
                return prompt_type

        # По умолчанию используем code_assistant
        return "code_assistant"

    # Регистрируем обработчик сэмплинга
    mcp_service.create_sampling = sampling_handler


# Регистрируем системные промпты при импорте

# Move import to top
import asyncio

asyncio.create_task(register_system_prompts())
