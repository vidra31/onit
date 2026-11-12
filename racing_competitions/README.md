# Лабораторные №1 и №2 — Учёт гоночных соревнований

**Один проект для двух лабораторных.** Python 3.12, FastAPI, SQLAlchemy 2, PostgreSQL 16, Alembic, pytest, Docker Compose.

## Предметная область

- `Team` — команда (`id`, `name`, `country`)
- `Driver` — пилот (`id`, `name`, `number`, `team_id`)
- `Race` — гонка (`id`, `name`, `circuit`, `laps`)
- `Result` — результат (`id`, `race_id`, `driver_id`, `position`, `points`)

Связи: Team 1:N Driver, Driver 1:N Result, Race 1:N Result.

**Бизнес-правила:** в одной гонке пилот может иметь только один результат; одну финишную позицию нельзя назначить двум пилотам; команда с пилотами не удаляется. Позиция положительна, очки от 0 до 1000. Ограничения дублируются на уровне БД, чтобы исключить нарушения при параллельных запросах.

## ЛР №1 — backend, миграции, тесты

Установите Python 3.12 и PostgreSQL. Создайте базу и пользователя, указанные в `DATABASE_URL`.

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env  # в Windows можно скопировать вручную
# В .env укажите адрес локальной PostgreSQL (localhost вместо db)
alembic upgrade head
uvicorn app.main:app --reload
```

Документация API: http://localhost:8000/docs. Создание таблиц рабочей PostgreSQL производится **только через Alembic**. Тесты используют отдельную SQLite in-memory БД для изоляции и не изменяют рабочую базу.

```bash
pytest -q
```

## ЛР №2 — контейнеризация

Нужны Docker Engine и Docker Compose v2.

```bash
cp .env.example .env
# При необходимости поменяйте пароль в .env
docker compose up --build -d
docker compose ps
docker compose logs backend
docker compose down
```

`compose.yaml` поднимает `db` и `backend` в общей сети `lab_net`. PostgreSQL хранит данные в именованном томе `postgres_data`. `backend` ждёт успешного healthcheck БД, выполняет `alembic upgrade head` и запускает Uvicorn. Для тестов на хосте: `pip install -r requirements.txt -r requirements-dev.txt && pytest -q`.

**Проверка сохранности:** создайте команду через Swagger UI; выполните `docker compose down`, затем `docker compose up -d`; GET `/teams` должен вернуть созданную команду. Не используйте `docker compose down -v` — это удалит том.

## API (22 endpoints + health)

| Метод | Адрес | Назначение |
|---|---|---|
| GET/POST | `/teams` | Список / создание команд |
| GET/PATCH/DELETE | `/teams/{item_id}` | Команда по ID / изменение / удаление |
| GET | `/teams/{team_id}/drivers` | Пилоты команды |
| GET/POST | `/drivers` | Список / создание пилотов |
| GET/PATCH/DELETE | `/drivers/{item_id}` | Пилот по ID / изменение / удаление |
| GET/POST | `/races` | Список / создание гонок |
| GET/PATCH/DELETE | `/races/{item_id}` | Гонка по ID / изменение / удаление |
| GET | `/races/{race_id}/results` | Результаты гонки |
| GET/POST | `/results` | Список / добавление результатов |
| GET/PATCH/DELETE | `/results/{item_id}` | Результат по ID / изменение / удаление |
| GET | `/health` | Проверка доступности |

## Пример демонстрации

1. `POST /teams`: `{"name":"Scuderia Red","country":"Italy"}`
2. `POST /drivers`: `{"name":"Marco Rossi","number":16,"team_id":1}`
3. `POST /races`: `{"name":"Italian Grand Prix","circuit":"Monza","laps":53}`
4. `POST /results`: `{"race_id":1,"driver_id":1,"position":1,"points":25}`
5. Повторите `POST /results` с тем же пилотом и гонкой — ожидается **409 Conflict**.
6. Проверьте `GET /races/1/results`, затем сохранность после перезапуска Docker.

## Структура

- `app/` — ORM-модели, схемы валидации, бизнес-правила, маршруты API
- `alembic/versions/` — начальная миграция PostgreSQL
- `tests/test_rules.py` — unit-тесты
- `tests/test_integration.py` — интеграционные тесты через TestClient
- `Dockerfile`, `.dockerignore`, `compose.yaml` — инфраструктура
- `.env.example` — пример настроек (не публикуйте настоящий `.env`)

## Git

```bash
git init
git add .
git commit -m "Racing competitions API: labs 1 and 2"
```

Публикация в удалённый репозиторий выполняется отдельно. Для защиты проверьте Docker на своём компьютере.
