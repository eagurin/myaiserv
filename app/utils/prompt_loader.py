import json
import os
from functools import cache
from typing import Any, Dict, Optional


class PromptLoader:
    """Утилита для загрузки и управления промптами"""

    def __init__(self, prompts_dir: str = None):
        self.prompts_dir = prompts_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "prompts"
        )

    @cache
    def load_prompts(self, prompt_type: str) -> Dict[str, Any]:
        """Загрузка промптов из JSON файла

        Args:
                prompt_type: Тип промптов (system_prompts/user_prompts)

        Returns:
                Dict с промптами
        """
        file_path = os.path.join(self.prompts_dir, f"{prompt_type}.json")
        try:
            with open(file_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading prompts from {file_path}: {str(e)}")
            return {}

    def get_system_prompt(self, prompt_type: str) -> Optional[Dict[str, Any]]:
        """Получение системного промпта по типу"""
        prompts = self.load_prompts("system_prompts")
        return prompts.get(prompt_type)

    def get_user_prompt(self, prompt_name: str) -> Optional[Dict[str, Any]]:
        """Получение пользовательского промпта по имени"""
        prompts = self.load_prompts("user_prompts")
        return prompts.get(prompt_name)

    def format_system_prompt(self, prompt_type: str) -> str:
        """Форматирование системного промпта"""
        prompt = self.get_system_prompt(prompt_type)
        if not prompt:
            return ""

        content = prompt["content"]
        return f"""You are a {content['description']} with expertise in:
{chr(10).join(f'- {cap}' for cap in content['capabilities'])}

{content['instruction']}"""

    def format_user_prompt(
        self, prompt_name: str, **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Форматирование пользовательского промпта с аргументами"""
        prompt = self.get_user_prompt(prompt_name)
        if not prompt:
            return None

        # Проверяем обязательные аргументы
        required_args = {
            arg["name"] for arg in prompt["arguments"] if arg.get("required", False)
        }
        missing_args = required_args - set(kwargs.keys())
        if missing_args:
            raise ValueError(f"Missing required arguments: {', '.join(missing_args)}")

        return {
            "name": prompt["name"],
            "description": prompt["description"],
            "arguments": kwargs,
        }


# Создаем глобальный экземпляр загрузчика промптов
prompt_loader = PromptLoader()
