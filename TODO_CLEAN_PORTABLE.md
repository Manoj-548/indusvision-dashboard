# Clean and Portable Dashboard Project
Status: In Progress ✅

## Approved Plan Steps

### 1. [ ] Update Documentation and Scripts (Strings only)
- cleanup_venvs.bat: IndusVision_WorkBook -> WorkBook
- .vscode/settings.json: IndusVision_WorkBook -> WorkBook
- All TODO*.md: IndusVision -> Dashboard, Nexify -> Annotation Platform
- MODEL_INTEGRATION_REPORT.md, rag.py docstring
- Bat/ps1 files echoes

### 2. [ ] Core Config String Updates (no breaking)
- indusvision/settings.py: POSTGRES_DB='project_db', SSL generic, comments
- config/settings.py: INSTALLED_APPS reorder/fix
- config/urls.py: nexify -> annotation_app namespace (if rename) or strings

### 3. [ ] App Name Replacements (code-safe)
- Replace 'indusvision' -> 'project_core' in DJANGO_SETTINGS_MODULE, ROOT_URLCONF, WSGI
- 'nexify' -> 'annotation_app' in INSTALLED_APPS, includes, imports (targeted)
- dashboard/views.py: nexify imports -> annotation_app

### 4. [ ] Templates
- Title blocks: IndusVision -> Dashboard, Nexify -> Annotation Platform
- URLs/hrefs if namespaced

### 5. [ ] Workbook Env
- Symlink indusvision_workbook -> workbook
- Update any refs

### 6. [ ] Git and Push
- git checkout -b blackboxai/cleaned-portable
- git add . && git commit -m \"Cleaned for portability: renamed indusvision/nexify\"
- git push -u origin blackboxai/cleaned-portable

### 7. [ ] Workspace Cleanup
- Check duplicates in ConsolidatedProjects
- Push other dirs or create monorepo

### 8. [ ] Test
- python manage.py check
- migrate
- runserver

Post-completion: Ready to clone/use at new company. DB reset ok.
