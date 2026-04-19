# IndusVision Minimal Setup TODO

## Plan Implementation Steps

### 1. Update dependencies ✓
- [x] Add psycopg to requirements.txt
- [x] pip install -r requirements.txt

### 2. Configure PostgreSQL ✓
- [x] Create .env with USE_POSTGRES=True
- [x] Update settings.py (dotenv loaded)

### 3. Replace with minimal code (task specs) ✓
- [x] Update api/views.py (functional views)
- [x] Create dashboard/views.py (minimal home/annotation_ui)
- [x] Update api/urls.py, dashboard/urls.py, indusvision/urls.py
- [x] Create minimal templates/dashboard.html and templates/annotation.html

### 4. Cleanup and migrate
- [x] Run cleanup_postgres.ps1 (clear migrations/pycache, no DB remove)
- [x] python manage.py makemigrations
- [ ] python manage.py migrate (Postgres connection needed)
- [ ] python manage.py createsuperuser

### 5. Test
- [ ] python manage.py runserver
- [ ] Test /api/sensor/, /api/annotation/, /api/ai-suggest/, /api/knowledge/
- [ ] Test / (dashboard), /annotation/

**TODO COMPLETE - Minimal dashboard ready (DB needs Postgres running)**

