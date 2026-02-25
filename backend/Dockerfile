FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev gcc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir

COPY . .

RUN mkdir -p /app/collected_static

RUN python manage.py collectstatic --noinput

CMD sh -c "python manage.py migrate --noinput && gunicorn --bind 0.0.0.0:8000 foodgram.wsgi"
