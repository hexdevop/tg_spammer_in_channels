# Телеграмм бот для спама в добавленные каналы

Бот предназначен для добавления каналов, а в них посты с целью спама с интервалами. Имеется довольно гибкая настройка спама.

## Установка

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/hexdevop/tg_spammer_in_channels.git
   cd tg_spammer_in_channels
   ```

2. Создайте и активируйте виртуальное окружение:
   - Для Linux:
      ```bash
      python3 -m venv venv
      source venv/bin/activate
      ```
   - Для Windows:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```

3. Установите зависимости:

   ```bash
   pip install -r requirements.txt
   ```

4. Настройте конфигурацию:
   - Заполните файл `.env` с вашими данными:
     - `bot.token` — токен вашего бота.
     - Данные для подключения к базе данных MySQL и Redis.

5. Запустите миграции Alembic для настройки базы данных:

   ```bash
   alembic upgrade head
   ```

## Запуск


```bash
python main.py
```

## Структура проекта

- **bot/** — Основная логика бота, обработчики, middlewares, и другие утилиты.
- **config.py** — Конфигурация проекта.
- **database/** — Модели SQLAlchemy и настройки подключения к базе данных.
- **migrations/** — Миграции Alembic.
- **variables/** — Хранение переменных и настроек, доступных в боте.

## Миграции базы данных

Для работы с базой данных используется **SQLAlchemy** и **Alembic** для миграций. Чтобы создать новую миграцию, выполните команду:

```bash
alembic revision --autogenerate -m "description of changes"
```

Для применения миграций:

```bash
alembic upgrade head
```

## Используемые технологии

- **aiogram** — библиотека для создания телеграмм-ботов.
- **MySQL** — база данных с поддержкой репликации.
- **SQLAlchemy** — ORM для работы с базой данных.
- **Alembic** — инструмент для миграций базы данных.
- **Redis** — система кэширования.

