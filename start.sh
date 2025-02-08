#!/bin/bash
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn ig_prj.asgi:application --bind 0.0.0.0:10000
