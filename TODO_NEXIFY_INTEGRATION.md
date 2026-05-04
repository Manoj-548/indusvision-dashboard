# NEXIFY INTEGRATION TODO - Step by Step

## Phase 1: Dependencies
- [ ] Install albumentations in .venv
- [ ] Install pycocotools in .venv
- [ ] Update requirements.txt
- [ ] Verify installations

## Phase 2: Settings Update
- [ ] Add 'nexify' to INSTALLED_APPS
- [ ] Add MEDIA_URL and MEDIA_ROOT

## Phase 3: Create nexify App Files
- [ ] Create nexify/__init__.py
- [ ] Create nexify/apps.py
- [ ] Create nexify/models.py
- [ ] Create nexify/admin.py
- [ ] Create nexify/views.py
- [ ] Create nexify/urls.py
- [ ] Create nexify/migrations/__init__.py
- [ ] Create nexify/templates/nexify/index.html

## Phase 4: Integration
- [ ] Update indusvision/urls.py (include nexify + media)
- [ ] Update templates/base.html (sidebar link)

## Phase 5: Database
- [ ] Run makemigrations nexify (VERIFY OUTPUT)
- [ ] Run migrate (VERIFY OUTPUT)

## Phase 6: Verification
- [ ] Run server
- [ ] Test /nexify/ page
- [ ] Test API endpoints

