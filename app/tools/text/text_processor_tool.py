import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Optional, Protocol

from app.core.base_mcp import MCPError, MCPTool
from app.services.mcp_service import mcp_service

logger = logging.getLogger(__name__)


class TextOperation(Protocol):
    async def process(self, text: str, params: Dict[str, Any]) -> Dict[str, Any]:
        pass


class TextFormatter:
    async def process(self, text: str, params: Dict[str, Any]) -> Dict[str, Any]:
        format_type = params.get("format_type", "lowercase")
        result = text

        if format_type == "uppercase":
            result = text.upper()
        elif format_type == "lowercase":
            result = text.lower()
        elif format_type == "capitalize":
            result = text.capitalize()
        elif format_type == "title_case":
            result = text.title()

        return {
            "formatted_text": result,
            "format_type": format_type,
            "original_length": len(text),
            "formatted_length": len(result),
        }


class TextStatisticsCalculator:
    def __init__(self) -> None:
        self.executor = ThreadPoolExecutor(max_workers=2)

    async def process(self, text: str, params: Dict[str, Any]) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()
        stats_options = params.get("stats_options", ["word_count", "char_count"])

        def _stats_calc() -> Dict[str, Any]:
            words = text.split()
            sentences = [
                s.strip()
                for s in text.replace("!", ".").replace("?", ".").split(".")
                if s.strip()
            ]
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

            result: Dict[str, Any] = {
                "text_length": len(text),
            }

            if "char_count" in stats_options:
                result["char_count"] = len(text)

            if "word_count" in stats_options:
                result["word_count"] = len(words)

            if "sentence_count" in stats_options:
                result["sentence_count"] = len(sentences)

            if "paragraph_count" in stats_options:
                result["paragraph_count"] = len(paragraphs)

            if "avg_word_length" in stats_options and words:
                result["avg_word_length"] = sum(len(word) for word in words) / len(
                    words
                )

            if "avg_sentence_length" in stats_options and sentences:
                sentence_words = [len(s.split()) for s in sentences]
                result["avg_sentence_length"] = sum(sentence_words) / len(sentences)

            if "readability" in stats_options:
                if len(sentences) > 0 and len(words) > 0:
                    avg_sentence_len = len(words) / len(sentences)
                    avg_word_len = sum(len(word) for word in words) / len(words)
                    readability = 206.835 - (1.015 * avg_sentence_len)
                    readability = readability - (84.6 * avg_word_len)
                    result["readability_score"] = readability
                else:
                    result["readability_score"] = 0

            return result

        return await loop.run_in_executor(self.executor, _stats_calc)


class EntityExtractor:
    def __init__(self) -> None:
        self.executor = ThreadPoolExecutor(max_workers=2)

    async def process(self, text: str, params: Dict[str, Any]) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()
        entity_types = params.get("entity_types", ["person", "organization"])

        def _extract() -> Dict[str, Any]:
            entities = {
                "person": ["Иван Иванов", "Петр Петров"],
                "organization": ["ООО Рога и Копыта", "Компания"],
                "location": ["Москва", "Россия"],
                "date": ["10 января 2023", "вчера"],
                "time": ["10:00", "полдень"],
                "money": ["$100", "5000 рублей"],
                "percent": ["10%", "половина"],
            }

            result: Dict[str, Any] = {
                "entities": {},
                "entity_count": 0,
            }

            for entity_type in entity_types:
                if entity_type in entities:
                    found = [
                        e for e in entities[entity_type] if e.lower() in text.lower()
                    ]
                    if found:
                        result["entities"][entity_type] = found
                        result["entity_count"] += len(found)

            return result

        return await loop.run_in_executor(self.executor, _extract)


class TextSummarizer:
    def __init__(self) -> None:
        self.executor = ThreadPoolExecutor(max_workers=2)

    async def process(self, text: str, params: Dict[str, Any]) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()

        def _summarize() -> Dict[str, Any]:
            sentences = [
                s.strip()
                for s in text.replace("!", ".").replace("?", ".").split(".")
                if s.strip()
            ]

            summary = []
            if sentences:
                summary.append(sentences[0])

                if len(sentences) > 1:
                    num_sentences = max(1, int(len(sentences) * 0.15))
                    step = len(sentences) // num_sentences

                    for i in range(1, len(sentences), step):
                        limit = num_sentences + 1
                        if len(summary) < limit:
                            summary.append(sentences[i])

            summary_text = ". ".join(summary) + "." if summary else ""
            compression = (len(summary_text) / len(text)) * 100 if text else 0

            return {
                "summary": summary_text,
                "original_length": len(text),
                "summary_length": len(summary_text),
                "compression_ratio": compression,
            }

        return await loop.run_in_executor(self.executor, _summarize)


class KeywordFinder:
    def __init__(self) -> None:
        self.executor = ThreadPoolExecutor(max_workers=2)

    async def process(self, text: str, params: Dict[str, Any]) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()

        def _extract_keywords() -> Dict[str, Any]:
            words = text.lower().split()

            stop_words = {
                "и",
                "в",
                "на",
                "с",
                "по",
                "у",
                "к",
                "о",
                "из",
                "за",
                "под",
                "для",
                "то",
                "а",
                "но",
                "я",
                "ты",
                "он",
                "она",
                "оно",
                "мы",
                "вы",
                "они",
                "этот",
                "тот",
                "что",
                "как",
                "так",
                "где",
                "когда",
                "потому",
            }

            word_freq = {}
            for word in words:
                clean_word = "".join(c for c in word if c.isalnum())
                if clean_word and clean_word not in stop_words:
                    word_freq[clean_word] = word_freq.get(clean_word, 0) + 1

            sorted_words = sorted(
                word_freq.items(),
                key=lambda x: x[1],
                reverse=True,
            )

            top_keywords = sorted_words[:10] if sorted_words else []

            return {
                "keywords": [
                    {"word": word, "frequency": freq} for word, freq in top_keywords
                ],
                "total_words": len(words),
                "unique_words": len(word_freq),
            }

        return await loop.run_in_executor(self.executor, _extract_keywords)


class TextOperationFactory:
    operations = {
        "format": TextFormatter(),
        "statistics": TextStatisticsCalculator(),
        "extract_entities": EntityExtractor(),
        "summarize": TextSummarizer(),
        "find_keywords": KeywordFinder(),
    }

    @classmethod
    def get_operation(cls, operation_type: str) -> Optional[TextOperation]:
        return cls.operations.get(operation_type)


class TextProcessorTool(MCPTool):
    """
    Инструмент для обработки текста с различными функциями: форматирование,
    статистика, извлечение сущностей, сокращение и поиск ключевых слов.
    """

    def __init__(self):
        super().__init__()
        self.input_schema = {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": [
                        "format",
                        "statistics",
                        "extract_entities",
                        "summarize",
                        "find_keywords",
                    ],
                    "description": "Операция обработки текста для выполнения",
                },
                "text": {
                    "type": "string",
                    "description": "Текст для обработки",
                },
                "format_type": {
                    "type": "string",
                    "enum": ["uppercase", "lowercase", "capitalize", "title_case"],
                    "description": "Тип форматирования для операции format",
                },
                "stats_options": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "char_count",
                            "word_count",
                            "sentence_count",
                            "paragraph_count",
                            "avg_word_length",
                            "avg_sentence_length",
                            "readability",
                        ],
                    },
                    "description": "Статистические опции для операции statistics",
                },
                "entity_types": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "person",
                            "organization",
                            "location",
                            "date",
                            "time",
                            "money",
                            "percent",
                        ],
                    },
                    "description": "Типы сущностей для операции extract_entities",
                },
            },
            "required": ["operation", "text"],
        }
        self.name = "text_processor"
        self.description = (
            "Обработка текста: форматирование, статистика, "
            "извлечение сущностей, сокращение и ключевые слова"
        )

    async def initialize(self):
        """Инициализация инструмента обработки текста."""
        logger.info("Инициализация TextProcessorTool")
        return True

    async def cleanup(self):
        """Очистка ресурсов инструмента обработки текста."""
        logger.info("Очистка ресурсов TextProcessorTool")
        return True

    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Выполнение операции обработки текста.

        Args:
            parameters: Словарь с параметрами запроса
                - operation: Операция для выполнения
                - text: Текст для обработки
                - format_type: Тип форматирования (для операции format)
                - stats_options: Статистические опции (для операции statistics)
                - entity_types: Типы сущностей (для операции extract_entities)

        Returns:
            Dict[str, Any]: Результат операции обработки текста
        """
        operation = parameters.get("operation")
        text = parameters.get("text", "")

        if not text.strip():
            raise MCPError(
                "text_processor_error",
                "Текст не может быть пустым",
            )

        logger.info(f"Выполнение операции {operation} на тексте длиной {len(text)}")

        operation_processor = TextOperationFactory.get_operation(operation)
        if not operation_processor:
            raise MCPError(
                "invalid_operation",
                f"Неподдерживаемая операция: {operation}",
            )

        try:
            return await operation_processor.process(text, parameters)
        except Exception as e:
            logger.error(f"Ошибка при обработке текста: {str(e)}")
            raise MCPError(
                "processing_error",
                f"Ошибка при обработке текста: {str(e)}",
            )


async def register_text_processor():
    """Регистрация инструмента обработки текста"""
    text_processor = TextProcessorTool()
    await text_processor.initialize()

    # Регистрируем инструмент
    from app.models.mcp import Tool

    tool = Tool(
        name=text_processor.name,
        description=text_processor.description,
        input_schema=text_processor.input_schema,
    )

    await mcp_service.register_tool(tool, text_processor.execute)
