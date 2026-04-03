@echo off
REM Apply all pending migrations for the dashboard
REM This script should be run from the indusvision-dashboard directory

echo Applying migrations for modelweights...
python manage.py migrate dashboard

echo.
echo Migrations applied successfully!
echo.
echo Starting Celery beat scheduler in background...
start /B celery -A indusvision beat --loglevel=info

echo.
echo Starting Celery worker in background...
start /B celery -A indusvision worker --loglevel=info

echo.
echo Dashboard services started. You can now access the dashboard.
echo Admin: http://localhost:8000/admin
echo API: http://localhost:8000/api/
echo Dashboard: http://localhost:8000/
