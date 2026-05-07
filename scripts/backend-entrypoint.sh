#!/bin/sh
set -e

cd /app/backend

python manage.py makemigrations users activities tasks gamification --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py seed_predefined_activities

gunicorn config.wsgi:application --bind 0.0.0.0:8000
