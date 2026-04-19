@echo off
cd /d %~dp0
set USE_POSTGRES=False
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
pause
