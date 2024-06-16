#!/bin/bash
if [[ "$DJANGO_ENV" == 'prod' ]]; then
    python manage.py migrate
    python manage.py collectstatic --noinput
    gunicorn server.wsgi:application -w 4 -k gthread -b 0.0.0.0:8000

    else
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver 0.0.0.0:8000
fi
