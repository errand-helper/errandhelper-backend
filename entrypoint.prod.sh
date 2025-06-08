#!/usr/bin/env bash
SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL:-"michaelodras@gmail.com"}
SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD:-"admin123"}

python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py createsuperuser --email $SUPERUSER_EMAIL --noinput || true
echo "from django.contrib.auth import get_user_model; User = get_user_model(); user = User.objects.filter(email='$SUPERUSER_EMAIL').first(); user.set_password('$SUPERUSER_PASSWORD') if user else None; user.save() if user else None" | python manage.py shell || true
python -m gunicorn --bind 0.0.0.0:8000 --workers 3 configs.wsgi:application