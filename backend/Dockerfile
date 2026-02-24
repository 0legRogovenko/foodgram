FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir

COPY . .

RUN mkdir -p /backend_static

CMD sh -c "python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:8000 foodgram.wsgi"
