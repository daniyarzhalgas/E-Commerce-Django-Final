FROM python:3.11

WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копируем оставшийся код проекта
COPY . /app

# Собираем статические файлы
ENV DJANGO_SETTINGS_MODULE=backend.settings
RUN python manage.py collectstatic --noinput

# Открываем порт
EXPOSE 8000

# Запуск Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend.wsgi:application"]
