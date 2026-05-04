# TODO: Full Nexify Flow

- [x] Migrations fixed
- [ ] 1. Fix nexify/views.py workspace_view query: filter(..., user_id=request.user.pk)
- [ ] 2. templates/base.html: {% block sidebar %}{% if not nexify %}{% include 'sidebar.html' %}{% endif %}
- [ ] 3. Create augmentation.html, export.html (basic)
- [ ] 4. Update index.html with workspace/project tabs calling APIs
- [ ] 5. Add rate limits (django-ratelimit)
- [ ] 6. Test login -> workspace -> project -> upload -> annotate (SAM) -> export
