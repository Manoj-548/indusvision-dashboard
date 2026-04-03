#!/bin/bash
# Quick startup script for IndusVision Dashboard
# Run this to initialize the system

echo "=== IndusVision Dashboard Startup ==="
echo

# Check Python version
python --version
echo

# Install requirements if needed
echo "Installing dependencies..."
pip install -q -r requirements.txt

echo "✓ Dependencies installed"
echo

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput
echo "✓ Migrations complete"
echo

# Create or update superuser (optional)
echo "Database ready!"
echo

# Check if Redis is running
echo "Checking Redis connection..."
python -c "import redis; redis.Redis(host='localhost', port=6379).ping(); print('✓ Redis is running')" 2>/dev/null || echo "⚠ Redis not detected (required for Celery)"
echo

# Summary
echo "=== Setup Complete ==="
echo
echo "Next steps:"
echo "  1. Start Django dev server: python manage.py runserver"
echo "  2. Start Celery worker: celery -A indusvision worker --loglevel=info"
echo "  3. Start Celery beat: celery -A indusvision beat --loglevel=info"
echo
echo "Access the dashboard:"
echo "  Dashboard: http://localhost:8000/"
echo "  Admin: http://localhost:8000/admin/"
echo "  API: http://localhost:8000/api/"
echo
echo "=== Consolidate Knowledge ==="
echo "  python consolidate_knowledge.py"
echo
