 # Phase 1: Stabilize + Clean IndusVision Dashboard
## Approved Plan Steps

### 1. ✅ Create this TODO.md file

### 2. ✅ Enhance indusvision/settings.py (security, logging, tests)

### 3. ✅ Clean dashboard/models.py (remove annotation models: Workspace*, Project/Image/Annotation/Dataset - kept Knowledge/SourceFile)

### 4. ✅ Delete dashboard/views_fixed.py and dashboard/migrations/

### 5. ✅ Update dashboard/views.py (projects via Knowledge/SourceFile, knowledge/agent, no ann)

### 6. ✅ Update dashboard/urls.py (projects/, knowledge/, no annotation/)

### 7. ✅ Clean api/views.py & urls.py (remove annotation/)

### 8. ☐ Remove templates/annotation/* and repurpose projects/* for knowledge

### 9. ☐ python manage.py makemigrations dashboard && migrate

### 10. ☐ Add basic tests in dashboard/tests.py & api/tests.py

### 11. ☐ Test: python manage.py runserver → /dashboard/ shows projects main

### 12. ☐ Clean old workspace/ duplicates

**Post-completion:** Ready for Phase 2 (Nexify integration).

Current progress: 1/12

