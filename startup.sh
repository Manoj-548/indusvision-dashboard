#!/bin/bash
echo "=== IndusVision Dashboard Startup ==="
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python consolidate_knowledge.py
echo "Server ready: python manage.py runserver"
echo "Visit http://localhost:8000/dashboard/"

