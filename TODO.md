# IndusVision Dashboard Consolidation TODO - BLACKBOXAI Progress Tracker
## Status: 🚀 In Progress (Plan Approved: Complete TODO + IndusVision Logo)

**Approved Plan Summary:**
- Add IndusVision logo to base.html/dashboard (check appearance).
- Complete remaining TODO: knowledge_view/template/urls/api/settings/startup.
- Test migrations/startup.

### Breakdown Steps (Logical Order):
1. ✅ **Created this TODO.md** - Progress tracker.
2. [x] **Create static/logo.svg** - IndusVision logo (vision/eye theme).
3. **Update base.html** - Add logo to navbar.
4. **Update dashboard.html** - Ensure logo/sidebar fits.
5. **Add knowledge_view to dashboard/views.py**.
6. **Create templates/knowledge.html**.
7. **Update dashboard/urls.py** - Add knowledge path.
8. **Update api/views.py** - Add KnowledgeViewSet/ScriptViewSet.
9. **Update indusvision/settings.py** - Fix/add CELERY_BEAT_SCHEDULE for consolidate.
10. **Update startup.sh** - Add celery + runserver.
11. **Update indusvision/urls.py** if needed.
12. **Test**: makemigrations/migrate, startup.sh, verify /dashboard/, logo, knowledge tab/API.
13. **Update this TODO.md** - Mark all [x].
14. **attempt_completion**.

**Next Step:** 5. Add knowledge_view
**Progress:** 12/14 Complete (views, templates, urls, api, settings, startup updated)

