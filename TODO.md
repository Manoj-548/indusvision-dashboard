# IndusVision Dashboard Consolidation TODO
## Status: 🚀 In Progress

1. [x] **Add KnowledgeEntry model** to dashboard/models.py + makemigrations/migrate

3. [ ] **New consolidate_knowledge_task** in tasks.py calling updated consolidate_knowledge.py
4. [ ] **Update consolidate_knowledge.py** to target new_folder_destination + expose function
5. [ ] **Add knowledge_view** to dashboard/views.py
6. [ ] **Create templates/knowledge.html** + update dashboard.html/base.html (tabs/sections)
7. [ ] **Update urls** (dashboard/urls.py, indusvision/urls.py)
8. [ ] **Add KnowledgeViewSet/ScriptViewSet** to api/views.py
9. [ ] **Update settings.py** CELERY_BEAT_SCHEDULE
10. [ ] **Update startup.sh** to run consolidation
11. [ ] **Test**: migrate, startup.sh, runserver+celery, verify /dashboard/ shows knowledge/scripts from new_folder_destination
12. [ ] **Final**: attempt_completion
