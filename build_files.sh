#!/bin/bash
uv pip install -r requirements.txt --system
python manage.py collectstatic --noinput
python manage.py migrate --noinput
