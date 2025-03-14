"""
Промпты MCP.

Этот пакет содержит промпты, которые могут быть использованы
для генерации сообщений для LLM.
"""

from app.prompts.registry import register_prompts

__all__ = ["register_prompts"]
