import hashlib
import json
from datetime import datetime
from typing import Any, Dict, List

import torch
from sentence_transformers import SentenceTransformer

from app.storage.elasticsearch import es_storage
from app.storage.redis import redis_storage


class EmbeddingsManager:
    """Менеджер для работы с эмбеддингами"""

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        self.vector_dim = 384
        self.cache_ttl = 3600 * 24  # 24 часа

    def _get_cache_key(self, text: str) -> str:
        """Получение ключа кэша для текста"""
        return f"embedding:{hashlib.md5(text.encode()).hexdigest()}"

    async def get_embedding(self, text: str) -> List[float]:
        """Получение эмбеддинга для текста"""
        # Проверяем кэш Redis
        cache_key = self._get_cache_key(text)
        cached = await redis_storage.get(cache_key)
        if cached:
            return json.loads(cached)

        # Проверяем кэш Elasticsearch
        try:
            result = await es_storage.search(
                index="mcp_vectors",
                body={"query": {"term": {"vector_id.keyword": cache_key}}},
            )
            if result["hits"]["hits"]:
                vector = result["hits"]["hits"][0]["_source"]["vector"]
                # Кэшируем в Redis
                await redis_storage.set(
                    cache_key, json.dumps(vector), ex=self.cache_ttl
                )
                return vector
        except Exception as e:
            # Логируем ошибку и продолжаем выполнение
            print(f"Error searching Elasticsearch: {e}")

        # Генерируем новый эмбеддинг
        with torch.no_grad():
            embedding = self.model.encode(
                text, convert_to_tensor=True, device=self.device
            )
            vector = embedding.cpu().numpy().tolist()

        # Сохраняем в Redis
        await redis_storage.set(cache_key, json.dumps(vector), ex=self.cache_ttl)

        # Сохраняем в Elasticsearch
        await es_storage.index(
            index="mcp_vectors",
            document={
                "vector_id": cache_key,
                "vector": vector,
                "source": "text",
                "created_at": datetime.utcnow().isoformat(),
                "metadata": {"text_length": len(text), "language": "auto"},
            },
        )

        return vector

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Получение эмбеддингов для списка текстов"""
        embeddings = []
        for text in texts:
            embedding = await self.get_embedding(text)
            embeddings.append(embedding)
        return embeddings

    async def search_similar(
        self,
        query_vector: List[float],
        index: str,
        field: str = "embedding",
        size: int = 10,
        min_score: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """Поиск похожих документов по вектору"""
        body = {
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": f"cosineSimilarity(params.query_vector, '{field}') + 1.0",
                        "params": {"query_vector": query_vector},
                    },
                }
            },
            "min_score": min_score,
            "size": size,
        }

        result = await es_storage.search(index=index, body=body)
        return [hit["_source"] for hit in result["hits"]["hits"]]

    async def chunk_and_embed_text(
        self, text: str, chunk_size: int = 512, overlap: int = 128
    ) -> List[Dict[str, Any]]:
        """Разбиение текста на чанки и получение эмбеддингов"""
        # Простое разбиение по предложениям
        sentences = text.split(". ")
        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence)
            if current_length + sentence_length > chunk_size:
                # Сохраняем текущий чанк
                chunk_text = ". ".join(current_chunk)
                chunks.append(chunk_text)

                # Начинаем новый чанк с перекрытием
                overlap_size = max(0, len(current_chunk) - overlap)
                current_chunk = current_chunk[overlap_size:]
                current_length = sum(len(s) for s in current_chunk)

            current_chunk.append(sentence)
            current_length += sentence_length

        # Добавляем последний чанк
        if current_chunk:
            chunks.append(". ".join(current_chunk))

        # Получаем эмбеддинги для чанков
        chunk_embeddings = []
        for i, chunk in enumerate(chunks):
            embedding = await self.get_embedding(chunk)
            chunk_embeddings.append(
                {"content": chunk, "embedding": embedding, "position": i}
            )

        return chunk_embeddings


# Создаем глобальный экземпляр
embeddings_manager = EmbeddingsManager()
