import asyncio

from app.models.mcp import Prompt, PromptArgument
from app.services.mcp_service import mcp_service
from app.utils.prompt_loader import prompt_loader


async def register_prompts():
    """Регистрация всех промптов в сервисе"""
    # Загружаем промпты из JSON
    user_prompts = prompt_loader.load_prompts("user_prompts")

    # Конвертируем в модели Pydantic
    prompts = []
    for prompt_data in user_prompts.values():
        arguments = [
            PromptArgument(
                name=arg["name"],
                description=arg["description"],
                required=arg.get("required", False),
            )
            for arg in prompt_data.get("arguments", [])
        ]

        prompt = Prompt(
            name=prompt_data["name"],
            description=prompt_data["description"],
            arguments=arguments,
        )
        prompts.append(prompt)

    # Регистрируем промпты
    for prompt in prompts:
        await mcp_service.register_prompt(prompt)

    # Реализация генерации сообщений для промптов
    async def generate_prompt_messages(prompt: Prompt, arguments: dict) -> list:
        """Генерация сообщений для промпта с использованием системных промптов"""
        # Определяем тип системного промпта на основе имени пользовательского промпта
        system_prompt_type = determine_system_prompt_type(prompt.name)

        # Получаем системный промпт
        system_content = prompt_loader.format_system_prompt(system_prompt_type)

        # Форматируем пользовательский промпт
        user_content = prompt_loader.format_user_prompt(prompt.name, **arguments)

        if not user_content:
            return []

        return [
            {
                "role": "system",
                "content": {"type": "text", "text": system_content},
            },
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": format_user_message(prompt.name, arguments),
                },
            },
        ]

    def determine_system_prompt_type(prompt_name: str) -> str:
        """Определение типа системного промпта на основе имени пользовательского промпта"""
        if "code" in prompt_name:
            return "code_assistant"
        elif "data" in prompt_name:
            return "data_analyst"
        elif "doc" in prompt_name:
            return "documentation_writer"
        elif "sql" in prompt_name:
            return "sql_expert"
        return "code_assistant"

    def format_user_message(prompt_name: str, arguments: dict) -> str:
        """Форматирование пользовательского сообщения"""
        if prompt_name == "analyze-code":
            return f"Please analyze this {arguments['language']} code focusing on {arguments.get('focus', 'general improvements')}:\n\n{arguments['code']}"
        elif prompt_name == "analyze-data":
            return f"Please perform a {arguments['analysis_type']} analysis on this data:\n\n{arguments['data']}"
        elif prompt_name == "generate-docs":
            return f"Please generate {arguments.get('format', 'markdown')} documentation for:\n\n{arguments['content']}"
        elif prompt_name == "generate-sql":
            return f"Generate a {arguments.get('dialect', 'postgresql')} SQL query for: {arguments['description']}"
        return ""

    # Регистрация обработчика генерации сообщений
    mcp_service._generate_prompt_messages = generate_prompt_messages


# Регистрируем промпты при импорте

asyncio.create_task(register_prompts())
