# Foodgram — Share Your Recipes

Веб-приложение для обмена рецептами. Позволяет пользователям публиковать рецепты, подписываться на авторов, добавлять рецепты в избранное и создавать список покупок с автоматическим расчётом ингредиентов.

---

## Автор

**Олег Роговенко**
- GitHub: [github.com/0legRogovenko](https://github.com/0legRogovenko)
- Email: [0808006oleg@gmail.com](mailto:0808006oleg@gmail.com)

---

## Технологический стек

### Backend
- **Django 4.2** — веб-фреймворк
- **Django REST Framework** — API
- **djoser** — аутентификация и управление пользователями
- **drf-extra-fields** — дополнительные поля для DRF
- **django-filter** — фильтрация данных
- **Gunicorn** — WSGI сервер
- **PostgreSQL** — база данных

### Frontend
- **React** — UI фреймворк
- **Node.js** — среда выполнения
- **npm** — управление пакетами

### DevOps
- **Docker & Docker Compose** — контейнеризация
- **Nginx** — веб-сервер и reverse proxy

---

## Развертывание с Docker

### Требования
- [Docker](https://www.docker.com/products/docker-desktop)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Шаг 1. Клонирование репозитория
```bash
git clone https://github.com/0legRogovenko/foodgram.git
cd foodgram
```

### Шаг 2. Создание .env файла
В корне проекта создайте файл `.env`:
```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.postgresql
DB_NAME=foodgram_db
DB_USER=foodgram_user
DB_PASSWORD=foodgram_password
DB_HOST=db
DB_PORT=5432
```

### Шаг 3. Развертывание контейнеров
```bash
cd infra
docker-compose up -d
```

Контейнер frontend автоматически подготовит статические файлы и завершит работу.

### Шаг 4. Инициализация базы данных
```bash
# Миграции
docker-compose exec backend python manage.py migrate

# Создание суперпользователя
docker-compose exec backend python manage.py createsuperuser

# Импорт тегов
docker-compose exec backend python manage.py loaddata tags.json

# Импорт ингредиентов (из data/ingredients.json)
docker-compose exec backend python manage.py loaddata ingredients.json
```

---

## Локальное развертывание без Docker

### Требования
- Python 3.9+
- PostgreSQL 12+
- pip и virtualenv

### Шаг 1. Подготовка окружения
```bash
# Клонирование
git clone https://github.com/0legRogovenko/foodgram.git
cd foodgram/backend

# Виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

### Шаг 2. Установка зависимостей
```bash
pip install -r requirements.txt
```

### Шаг 3. Конфигурация базы данных
Создайте `.env` в папке `backend/`:
```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_ENGINE=django.db.backends.postgresql
DB_NAME=foodgram_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

### Шаг 4. Миграции и инициализация
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata tags.json
python manage.py loaddata ingredients.json  # Из data/ingredients.json
```

### Шаг 5. Запуск сервера
```bash
python manage.py runserver
```

Сервер будет доступен на `http://127.0.0.1:8000`

---

## Команды запуска

### С Docker Compose
```bash
# Запуск всех сервисов
cd infra
docker-compose up -d

# Остановка
docker-compose down

# Просмотр логов
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f nginx
```

### Локально (без Docker)
```bash
cd backend

# Запуск Django development сервера
python manage.py runserver

# Запуск с gunicorn (production)
gunicorn foodgram.wsgi --bind 0.0.0.0:8000
```

---

## Доступы к приложению

### С Docker Compose

| Сервис | URL | Описание |
|--------|-----|---------|
| **Фронтенд** | [http://localhost](http://localhost) | Веб-приложение для пользователей |
| **API Docs** | [http://localhost/api/docs/](http://localhost/api/docs/) | Документация REST API (Swagger/ReDoc) |
| **Admin Panel** | [http://localhost/admin/](http://localhost/admin/) | Django Admin для управления данными |
| **API Server** | [http://localhost/api/](http://localhost/api/) | REST API endpoints |

### Локально (без Docker)

| Сервис | URL | Описание |
|--------|-----|---------|
| **API Server** | [http://127.0.0.1:8000](http://127.0.0.1:8000) | Django REST API |
| **API Docs** | [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/) | Документация API |
| **Admin Panel** | [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) | Django Admin |

### Учётные данные по умолчанию
- **Superuser**: создаётся вручную командой `createsuperuser`
- **API Token**: получается через [POST /api/auth/token/login/](http://localhost/api/docs/#/Пользователи/post_api_auth_token_login_)

---

## API Документация

REST API полностью описана в формате OpenAPI 3.0.2.

### Основные endpoints:

**Рецепты:**
- `GET /api/recipes/` — список всех рецептов (с фильтрацией)
- `POST /api/recipes/` — создать рецепт
- `GET /api/recipes/{id}/` — получить рецепт
- `PATCH /api/recipes/{id}/` — обновить рецепт
- `DELETE /api/recipes/{id}/` — удалить рецепт
- `POST /api/recipes/{id}/favorite/` — добавить в избранное
- `DELETE /api/recipes/{id}/favorite/` — удалить из избранного
- `POST /api/recipes/{id}/shopping_cart/` — добавить в корзину
- `DELETE /api/recipes/{id}/shopping_cart/` — удалить из корзины
- `GET /api/recipes/download_shopping_cart/` — скачать список покупок

**Пользователи:**
- `GET /api/users/` — список пользователей
- `POST /api/users/` — регистрация
- `GET /api/users/{id}/` — профиль пользователя
- `GET /api/users/me/` — текущий пользователь
- `POST /api/users/{id}/subscribe/` — подписаться
- `DELETE /api/users/{id}/subscribe/` — отписаться
- `GET /api/users/subscriptions/` — мои подписки

**Теги и ингредиенты:**
- `GET /api/tags/` — список тегов
- `GET /api/ingredients/` — поиск ингредиентов

Полная документация: [http://localhost/api/docs/](http://localhost/api/docs/)

---

## Структура проекта

```
foodgram/
├── infra/                    # Docker конфигурация
│   ├── docker-compose.yml
│   ├── nginx.conf
│   └── Dockerfile
├── backend/                  # Django приложение
│   ├── recipes/             # Основное приложение
│   │   ├── models.py        # Модели базы данных
│   │   ├── views.py         # ViewSets и endpoints
│   │   ├── serializers.py   # Сериализаторы
│   │   ├── urls.py          # Маршруты API
│   │   └── filters.py       # Фильтры для поиска
│   ├── foodgram/            # Конфигурация проекта
│   ├── manage.py
│   └── requirements.txt
├── frontend/                 # React приложение
│   ├── src/
│   ├── public/
│   └── package.json
├── data/                     # Фикстуры
│   ├── ingredients.json      # Ингредиенты
│   └── tags.json            # Теги (если есть)
└── README.md
```

---

## Аутентификация

API использует Token-based аутентификацию.

### Получение токена:
```bash
curl -X POST http://localhost/api/auth/token/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com", "password":"password123"}'
```

Ответ:
```json
{
  "auth_token": "f8b3d4e2c1f9a7e6b5c4d3a2f1b0e9d8"
}
```

### Использование токена:
```bash
curl -X GET http://localhost/api/recipes/ \
  -H "Authorization: Token f8b3d4e2c1f9a7e6b5c4d3a2f1b0e9d8"
```

---

## Решение проблем

### Django не находит базу данных
Убедитесь, что PostgreSQL запущен и учётные данные в `.env` верны.

### Frontend не загружается
```bash
docker-compose ps  # Проверьте статус контейнеров
docker-compose logs frontend
```

### Ошибка 502 Bad Gateway
Проверьте, что backend запущён:
```bash
docker-compose logs backend
```

---

## Поддержка

Для вопросов и предложений:
- [GitHub Issues](https://github.com/0legRogovenko/foodgram/issues)
- Email: 080806oleg@gmail.com
