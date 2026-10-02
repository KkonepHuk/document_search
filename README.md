# Document Search

Сервис для поиска документов по тексту.

Сервис использует:

- FastAPI — HTTP API;
- PostgreSQL — хранение документов;
- Elasticsearch — полнотекстовый поиск;
- Docker Compose — запуск всех компонентов проекта;
- SQL migrations — создание структуры базы данных.

## Требования

Для запуска проекта необходимы:

- Docker;
- Docker Compose.

Устанавливать Python, PostgreSQL или Elasticsearch локально не требуется.

## Запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/KkonepHuk/document_search.git
cd document_search
```

### 2. Настройка переменных окружения

Создайте файл `.env` на основе [`.env.example`](.env.example):

```bash
touch .env
cp .env.example .env
```

### 3. Запуск проекта

```bash
make build
```

При запуске выполняются следующие действия:

1) Запускается PostgreSQL
2) Выполняются SQL-миграции
3) Тестовые документы импортируются из CSV в PostgreSQL
4) Документы индексируются в Elasticsearch
5) Запускается FastAPI-приложение

После запуска API доступен по адресу:

```
http://localhost:8000
```

Swagger UI:

```
http://localhost:8000/docs
```
## Остановка
Остановить контейнеры:

```
make down
```
Для удаления контейнеров вместе с данными PostgreSQL и Elasticsearch:

```
make down-hard
```

## Тесты
Для запуска тестов необходимо:

```
make test-run
```