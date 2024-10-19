#!/bin/bash
if [[ "$DJANGO_ENV" == 'prod' ]]; then
    python manage.py migrate
    python manage.py collectstatic --noinput
    celery -A server worker -l info&
    celery -A server beat -l info&
    gunicorn server.wsgi:application -w 4 -k gthread -b 0.0.0.0:8000 --timeout 30 --graceful-timeout 120

    else
    python manage.py makemigrations
    python manage.py migrate
    celery -A server worker -l info&
    celery -A server beat -l info&
#    python manage.py runserver 0.0.0.0:8000
    gunicorn server.wsgi:application -w 1 -k gthread -b 0.0.0.0:8000 --timeout 30 --graceful-timeout 120
fi
