#!/usr/bin/env bash

SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL:-"michaelodras@gmail.com"}

# cd /app/

python manage.py migrate --noinput

python manage.py createsuperuser --email $SUPERUSER_EMAIL --noinput || true