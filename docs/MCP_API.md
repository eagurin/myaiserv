# MCP API - Документация

## Обзор

MCP (Model Context Protocol) - это протокол для стандартизации взаимодействия между LLM-моделями и приложениями, предоставляющими контекст и инструменты для этих моделей. Данная документация описывает API-интерфейсы сервера MCP и способы их использования.

## Основные концепции

MCP оперирует следующими основными концепциями:

1. **Ресурсы (Resources)** - источники данных, доступные для LLM-моделей
2. **Инструменты (Tools)** - функции, которые могут быть вызваны LLM-моделями
3. **Промпты (Prompts)** - шаблоны для формирования запросов к моделям
4. **Сэмплирование (Sampling)** - процесс генерации контента моделью

## API Endpoints

### RESTful API

#### Инструменты (Tools)

- `GET /tools` - Получить список всех доступных инструментов
- `GET /tools/{name}` - Получить информацию о конкретном инструменте
- `POST /tools/{name}` - Выполнить инструмент с заданными параметрами

Пример запроса для выполнения инструмента:
```bash
curl -X POST "http://localhost:8000/tools/text_processor" \
     -H "Content-Type: application/json" \
     -d '{
           "operation": "statistics",
           "text": "Это пример текста для анализа. Он содержит несколько предложений. Статистика будет рассчитана для этого текста.",
           "stat_options": ["chars", "words", "sentences", "readability"]
         }'
```

#### Ресурсы (Resources)

- `GET /resources` - Получить список всех доступных ресурсов
- `GET /resources/{uri}` - Получить ресурс по URI
- `POST /resources` - Создать новый ресурс

Пример создания ресурса:
```bash
curl -X POST "http://localhost:8000/resources" \
     -H "Content-Type: application/json" \
     -d '{
           "uri": "example://document1",
           "name": "Пример документа",
           "description": "Документ для тестирования API ресурсов",
           "mime_type": "text/plain",
           "content": "Это содержимое тестового документа"
         }'
```

#### Промпты (Prompts)

- `GET /prompts` - Получить список всех доступных промптов
- `GET /prompts/{name}` - Получить информацию о конкретном промпте
- `POST /prompts/{name}` - Выполнить промпт с заданными аргументами

Пример выполнения промпта:
```bash
curl -X POST "http://localhost:8000/prompts/code_review" \
     -H "Content-Type: application/json" \
     -d '{
           "language": "python",
           "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)"
         }'
```

#### Сэмплирование (Sampling)

- `POST /sampling` - Выполнить сэмплирование с заданными параметрами

Пример запроса сэмплирования:
```bash
curl -X POST "http://localhost:8000/sampling" \
     -H "Content-Type: application/json" \
     -d '{
           "messages": [
             {
               "role": "user",
               "content": {"type": "text", "text": "Что такое MCP?"}
             }
           ],
           "max_tokens": 100,
           "temperature": 0.7
         }'
```

### GraphQL API

Доступ к GraphQL API осуществляется через эндпоинт `/graphql`. API предоставляет возможность выполнять запросы и мутации.

#### Запросы (Queries)

- `getTools` - Получить список всех инструментов
- `getTool(name: String!)` - Получить информацию о конкретном инструменте
- `getResources` - Получить список всех ресурсов
- `getResource(uri: String!)` - Получить ресурс по URI
- `getPrompts` - Получить список всех промптов
- `getPrompt(name: String!)` - Получить информацию о конкретном промпте

Пример GraphQL запроса:
```graphql
query {
  getTools {
    name
    description
    input_schema
  }
}
```

#### Мутации (Mutations)

- `executeTool(input: ToolInput!)` - Выполнить инструмент
- `executePrompt(input: PromptInput!)` - Выполнить промпт
- `createResource(input: ResourceInput!)` - Создать ресурс

Пример GraphQL мутации:
```graphql
mutation {
  executeTool(input: {
    name: "text_processor",
    parameters: {
      operation: "find_keywords",
      text: "MCP является стандартным протоколом для взаимодействия между LLM-моделями и приложениями, предоставляющими контекст и инструменты для этих моделей."
    }
  }) {
    content {
      type
      text
    }
    is_error
  }
}
```

### WebSocket API

Для реализации двусторонней связи и поддержки потоковой передачи данных, MCP предоставляет WebSocket API через эндпоинт `/ws`.

#### Сообщения WebSocket

1. **Инициализация соединения**
   ```json
   {"type": "initialize", "id": "unique-request-id"}
   ```

2. **Выполнение инструмента**
   ```json
   {
     "type": "tool_request",
     "id": "unique-request-id",
     "data": {
       "name": "text_processor",
       "parameters": {
         "operation": "summarize",
         "text": "Длинный текст для суммаризации..."
       }
     }
   }
   ```

3. **Запрос ресурса**
   ```json
   {
     "type": "resource_request",
     "id": "unique-request-id",
     "data": {
       "uri": "example://document1"
     }
   }
   ```

4. **Выполнение промпта**
   ```json
   {
     "type": "prompt_request",
     "id": "unique-request-id",
     "data": {
       "name": "code_review",
       "arguments": {
         "language": "python",
         "code": "def example():\n    pass"
       }
     }
   }
   ```

5. **Сэмплирование**
   ```json
   {
     "type": "sampling_request",
     "id": "unique-request-id",
     "data": {
       "messages": [
         {
           "role": "user",
           "content": {"type": "text", "text": "Что такое MCP?"}
         }
       ],
       "max_tokens": 100,
       "temperature": 0.7
     }
   }
   ```

## Примеры использования инструментов

### Text Processor

Инструмент `text_processor` предоставляет различные операции для обработки текста:

#### Статистика текста

```bash
curl -X POST "http://localhost:8000/tools/text_processor" \
     -H "Content-Type: application/json" \
     -d '{
           "operation": "statistics",
           "text": "Пример текста для анализа. Этот текст содержит несколько предложений. Мы используем его для демонстрации функций инструмента.",
           "stat_options": ["chars", "words", "sentences", "paragraphs", "readability"]
         }'
```

#### Извлечение сущностей

```bash
curl -X POST "http://localhost:8000/tools/text_processor" \
     -H "Content-Type: application/json" \
     -d '{
           "operation": "extract_entities",
           "text": "Свяжитесь с нами по email: example@email.com или посетите наш сайт https://example.com. Вы также можете позвонить по телефону +7 (123) 456-7890.",
           "entity_types": ["emails", "urls", "phone_numbers"]
         }'
```

#### Суммаризация текста

```bash
curl -X POST "http://localhost:8000/tools/text_processor" \
     -H "Content-Type: application/json" \
     -d '{
           "operation": "summarize",
           "text": "Длинный текст, который требуется суммаризировать..."
         }'
```

## Модели данных

### Tool (Инструмент)

```json
{
  "name": "text_processor",
  "description": "Обработка и анализ текста: форматирование, подсчет статистики и другие операции",
  "input_schema": {
    "type": "object",
    "properties": {
      "operation": {
        "type": "string",
        "enum": ["format", "statistics", "extract_entities", "summarize", "find_keywords"],
        "description": "Операция для выполнения"
      },
      "text": {
        "type": "string",
        "description": "Текст для обработки"
      },
      "...": "..."
    },
    "required": ["operation", "text"]
  }
}
```

### Resource (Ресурс)

```json
{
  "uri": "example://document1",
  "name": "Пример документа",
  "description": "Документ для тестирования API ресурсов",
  "mimeType": "text/plain"
}
```

### Message (Сообщение)

```json
{
  "role": "user",
  "content": {
    "type": "text",
    "text": "Что такое MCP?"
  }
}
```

## Коды ошибок

- `400 Bad Request` - Некорректные параметры запроса
- `404 Not Found` - Ресурс, инструмент или промпт не найден
- `500 Internal Server Error` - Внутренняя ошибка сервера
- WebSocket коды ошибок:
  - `-32000` - Общая ошибка
  - `-32601` - Метод не найден

## Требования к безопасности

- Все запросы к API должны проходить валидацию параметров
- При необходимости следует использовать аутентификацию и авторизацию
- Инструменты, требующие пользовательского подтверждения (requires_user_approval = true), должны быть явно подтверждены перед выполнением
- Доступ к файловой системе через инструменты должен быть ограничен безопасными директориями

## Версионирование API

Текущая версия API: 1.0.0
При обновлении API следует придерживаться семантического версионирования (SemVer):
- Увеличение первого номера (MAJOR) при несовместимых изменениях API
- Увеличение второго номера (MINOR) при добавлении функциональности с обратной совместимостью
- Увеличение третьего номера (PATCH) при исправлении ошибок с обратной совместимостью
