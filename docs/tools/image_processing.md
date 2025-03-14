# Инструмент Image Processing

Инструмент `image_processing` предназначен для выполнения базовых операций обработки изображений, таких как изменение размера, обрезка, преобразование в оттенки серого и другие.

## Основные возможности

- Изменение размера изображения (resize)
- Обрезка изображения (crop)
- Преобразование в оттенки серого (grayscale)
- Поворот изображения (rotate)
- Отражение изображения (flip)

## Параметры

### Общие параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `image_data` | string | Да | Base64-кодированное изображение. Может содержать префикс data URI (например, `data:image/jpeg;base64,`) |
| `operation` | string | Да | Операция для выполнения. Допустимые значения: `resize`, `crop`, `grayscale`, `rotate`, `flip` |
| `params` | object | Нет | Дополнительные параметры для конкретной операции |

### Параметры для операции `resize`

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `width` | number | Нет* | Ширина результирующего изображения в пикселях |
| `height` | number | Нет* | Высота результирующего изображения в пикселях |

> \* Необходимо указать хотя бы один из параметров: `width` или `height`. Если указан только один параметр, другой будет вычислен автоматически с сохранением пропорций изображения.

### Параметры для операции `crop`

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|-------------|----------|
| `left` | number | 0 | Левая координата прямоугольника обрезки |
| `top` | number | 0 | Верхняя координата прямоугольника обрезки |
| `right` | number | width | Правая координата прямоугольника обрезки |
| `bottom` | number | height | Нижняя координата прямоугольника обрезки |

### Параметры для операции `rotate`

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|-------------|----------|
| `angle` | number | 90 | Угол поворота в градусах (по часовой стрелке) |

### Параметры для операции `flip`

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|-------------|----------|
| `direction` | string | "horizontal" | Направление отражения. Допустимые значения: `horizontal`, `vertical` |

## Примеры использования

### Изменение размера изображения

```bash
curl -X POST "http://localhost:8000/tools/image_processing" \
  -H "Content-Type: application/json" \
  -d '{
    "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABA...",
    "operation": "resize",
    "params": {
      "width": 800,
      "height": 600
    }
  }'
```

### Преобразование в оттенки серого

```bash
curl -X POST "http://localhost:8000/tools/image_processing" \
  -H "Content-Type: application/json" \
  -d '{
    "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABA...",
    "operation": "grayscale"
  }'
```

### Обрезка изображения

```bash
curl -X POST "http://localhost:8000/tools/image_processing" \
  -H "Content-Type: application/json" \
  -d '{
    "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABA...",
    "operation": "crop",
    "params": {
      "left": 100,
      "top": 100,
      "right": 500,
      "bottom": 400
    }
  }'
```

### Поворот изображения

```bash
curl -X POST "http://localhost:8000/tools/image_processing" \
  -H "Content-Type: application/json" \
  -d '{
    "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABA...",
    "operation": "rotate",
    "params": {
      "angle": 45
    }
  }'
```

### Отражение изображения

```bash
curl -X POST "http://localhost:8000/tools/image_processing" \
  -H "Content-Type: application/json" \
  -d '{
    "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABA...",
    "operation": "flip",
    "params": {
      "direction": "vertical"
    }
  }'
```

## Формат ответа

```json
{
  "content": [
    {
      "type": "text",
      "text": "Изображение обработано: {\"width\": 800, \"height\": 600, \"format\": \"JPEG\", \"mode\": \"RGB\"}"
    }
  ]
}
```

## Обработка ошибок

В случае ошибки инструмент вернет ответ с флагом `isError: true` и описанием ошибки:

```json
{
  "content": [
    {
      "type": "text",
      "text": "Ошибка обработки изображения: Требуется указать width и/или height"
    }
  ],
  "isError": true
}
```

## Ограничения

- Максимальный размер изображения ограничен настройками сервера
- Поддерживаются форматы изображений, совместимые с библиотекой Pillow (JPEG, PNG, GIF, BMP и др.)
- При работе с большими изображениями может потребоваться больше времени на обработку

## Зависимости

Для работы инструмента необходима библиотека Pillow:

```bash
pip install Pillow
```
