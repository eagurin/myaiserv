# FastAPI MCP Сервер: Ваше мощное AI-приложение 🚀

Этот проект демонстрирует передовой сервер FastAPI, использующий протокол Model Context Protocol (MCP) для бесшовной интеграции с большими языковыми моделями (LLM). Он разработан для скорости, масштабируемости и простоты использования, что делает его идеальной основой для вашего следующего AI-приложения.

## Ключевые особенности ✨

- **Исключительная производительность:** Создан на базе FastAPI для оптимальной скорости и эффективности.
- **Гибкое хранилище данных:** Использует Elasticsearch для мощного полнотекстового и векторного поиска, а также Redis для молниеносного кэширования.
- **Надежная реализация MCP:** Поддерживает все основные функции MCP: инструменты, ресурсы, подсказки и сэмплирование.
- **Интеграция с GraphQL:** Предоставляет гибкий API GraphQL для удобного доступа к данным.
- **Всесторонний мониторинг:** Включает метрики Prometheus и панели Grafana для мониторинга и оповещений в реальном времени.
- **Модульная архитектура:** Чистый, хорошо структурированный код для простого обслуживания и расширения.
- **Тщательное тестирование:** Включает модульные и интеграционные тесты для надежной работы.
- **Простое развертывание:** Dockerized для простого и согласованного развертывания.

## Начало работы 🛠️

1. **Клонирование репозитория:**

   ```bash
   git clone <repository-url>
   cd myaiserv
   ```

2. **Создание виртуального окружения:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. **Установка зависимостей:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Настройка переменных окружения:** Скопируйте `.env.example` в `.env` и настройте значения в соответствии с вашей средой.
5. **Запуск приложения:**

   ```bash
   uvicorn app.main:app --reload
   ```

6. **Доступ к API:**
   - Документация API: [http://localhost:8000/docs](http://localhost:8000/docs)
   - GraphQL Playground: [http://localhost:8000/graphql](http://localhost:8000/graphql)

## Примеры использования 💡

### REST API

```python
import httpx
import asyncio

async def main():
 async with httpx.AsyncClient() as client:
  # Получение списка инструментов
  response = await client.get("http://localhost:8000/tools")
  print(response.json())

  # Выполнение инструмента
  result = await client.post(
   "http://localhost:8000/tools/weather",
   json={"latitude": 37.7749, "longitude": -122.4194}
  )
  print(result.json())

asyncio.run(main())
```

### GraphQL

```graphql
query {
  listTools {
 name
 description
  }
}

mutation {
  executeTool(
 name: "weather"
 parameters: {
   latitude: 37.7749
   longitude: -122.4194
 }
  ) {
 content {
   text
 }
  }
}
```

### WebSocket

```python
import asyncio
import websockets
import json

async def main():
 async with websockets.connect("ws://localhost:8000/mcp") as websocket:
  await websocket.send(json.dumps({"jsonrpc": "2.0", "method": "initialize"}))
  response = await websocket.recv()
  print(response)

asyncio.run(main())
```

## Структура проекта 📁

```
myaiserv/
├── app/
│   ├── core/             # Основные компоненты MCP
│   ├── models/          # Модели Pydantic
│   ├── services/        # Бизнес-логика
│   ├── storage/         # Взаимодействие с базой данных
│   ├── tools/           # Инструменты MCP
│   └── main.py         # Приложение FastAPI
├── config/             # Файлы конфигурации
├── docs/               # Документация
├── migrations/         # Миграции базы данных
├── scripts/            # Служебные скрипты
├── tests/              # Тесты
└── requirements.txt   # Зависимости проекта
```

## Вклад 🤝

Мы приветствуем ваш вклад! Пожалуйста, ознакомьтесь с файлом [CONTRIBUTING.md](CONTRIBUTING.md) для получения дополнительной информации.

## Лицензия 📄

[MIT](LICENSE)
