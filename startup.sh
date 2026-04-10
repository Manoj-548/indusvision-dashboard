#!/bin/bash
echo "=== IndusVision Dashboard Startup ==="
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py collectstatic --noinput
python consolidate_knowledge.py
echo "Starting Celery worker & beat..."
start /B celery -A indusvision worker --loglevel=info
start /B celery -A indusvision beat --loglevel=info
echo "Server ready: python manage.py runserver 0.0.0.0:8000"
echo "Visit http://localhost:8000/dashboard/"

