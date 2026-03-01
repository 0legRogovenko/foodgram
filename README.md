# Foodgram — Share Your Recipes

Веб-приложение для публикации рецептов.
Пользователи могут создавать рецепты, подписываться на авторов, добавлять рецепты в избранное и формировать список покупок.

## Автор

**Олег Роговенко**
- GitHub: [0legRogovenko](https://github.com/0legRogovenko)
- Email: [0808006oleg@gmail.com](mailto:0808006oleg@gmail.com)

## Технологии

### Backend
- [Django 3.2.3](https://www.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Djoser](https://djoser.readthedocs.io/)
- [django-filter](https://django-filter.readthedocs.io/)
- [drf-extra-fields](https://github.com/Hipo/drf-extra-fields)
- [Gunicorn](https://gunicorn.org/)
- [PostgreSQL](https://www.postgresql.org/)

### Frontend
- [React](https://react.dev/)

### Инфраструктура
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Nginx](https://nginx.org/)

## Запуск в Docker

### 1. Клонирование

```bash
git clone https://github.com/0legRogovenko/foodgram.git
cd foodgram
```

### 2. Настройка `.env`

Создайте файл `.env` в корне проекта:

```env
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost, 127.0.0.1

POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_HOST=db
DB_PORT=5432
```

### 3. Поднять контейнеры

```bash
docker compose up -d
```

### 4. Инициализация backend

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py load_tags
docker compose exec backend python manage.py load_ingredients
```

## Локальный запуск (без Docker)

### 1. Подготовка

```bash
git clone https://github.com/0legRogovenko/foodgram.git
cd foodgram/backend

python -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate    # Windows
```

### 2. Зависимости

```bash
pip install -r requirements.txt
```

### 3. Настройка `.env`

Создайте файл `backend/.env`:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1, localhost

POSTGRES_DB=foodgram
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

### 4. Миграции и загрузка данных

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py load_tags --file ../data/tags.json
python manage.py load_ingredients --file ../data/ingredients.json
```

### 5. Запуск

```bash
python manage.py runserver
```

## Основные команды

### Docker

```bash
docker compose up -d
docker compose down
docker compose logs -f backend
docker compose logs -f gateway
```

### Локально

```bash
cd backend
python manage.py runserver
gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
```

## Доступ к сервисам

### Docker
- Приложение: [http://localhost:9090/](http://localhost:9090/)
- API: [http://localhost:9090/api/](http://localhost:9090/api/)
- Админка: [http://localhost:9090/admin/](http://localhost:9090/admin/)

### Локально
- API: [http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/)
- Админка: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

## API

Ключевые эндпоинты:

- `POST /api/auth/token/login/` — получить токен
- `POST /api/auth/token/logout/` — удалить токен
- `GET /api/users/` — список пользователей
- `GET /api/users/me/` — текущий пользователь
- `POST /api/users/{id}/subscribe/` — подписаться на автора
- `DELETE /api/users/{id}/subscribe/` — отписаться
- `GET /api/users/subscriptions/` — подписки пользователя
- `GET /api/tags/` — список тегов
- `GET /api/ingredients/` — список ингредиентов
- `GET /api/recipes/` — список рецептов
- `POST /api/recipes/` — создать рецепт
- `POST /api/recipes/{id}/favorite/` — добавить в избранное
- `DELETE /api/recipes/{id}/favorite/` — удалить из избранного
- `POST /api/recipes/{id}/shopping_cart/` — добавить в корзину
- `DELETE /api/recipes/{id}/shopping_cart/` — удалить из корзины
- `GET /api/recipes/download_shopping_cart/` — скачать список покупок
- `GET /api/recipes/{id}/get_link/` — получить короткую ссылку

## Структура проекта

```text
foodgram/
├── backend/
│   ├── api/
│   ├── foodgram/
│   ├── recipes/
│   ├── manage.py
│   └── requirements.txt
├── data/
├── frontend/
├── infra/
├── docker-compose.yml
├── docker-compose.production.yml
└── README.md
```

## Поддержка

- Issues: [GitHub Issues](https://github.com/0legRogovenko/foodgram/issues)
- Email: [0808006oleg@gmail.com](mailto:0808006oleg@gmail.com)
