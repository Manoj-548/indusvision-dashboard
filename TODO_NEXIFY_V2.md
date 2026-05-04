 # Nexify V2 — Comprehensive Annotation Platform

## Phase 1: Foundation Fixes
- [x] Fix login.html (remove add_class filter)
- [x] Fix nexify template (add endblock)
- [x] Wire nexify URLs in indusvision/urls.py
- [ ] Make all indusvision dashboard tabs work (projects, knowledge, agent, tensorboard, sync)
- [ ] Fix base.html navigation links to match actual URL routes

## Phase 2: Models & Roles
- [ ] Add is_nexify_admin field to User profile (or use is_staff)
- [ ] Add email field to assignments
- [ ] Create NexifyTask model for task assignment with email
- [ ] Add keypoint type to annotation TYPE_CHOICES
- [ ] Migration for new fields

## Phase 3: Views & Permissions
- [ ] Add admin_required decorator for nexify admin views
- [ ] Create folder_upload view (multi-file / zip)
- [ ] Create dataset view (admin only)
- [ ] Create admin review view for annotations
- [ ] Create task assignment view (email-based)
- [ ] Update annotate view to support keypoint type
- [ ] Add cursor tracking endpoint (optional, do client-side)

## Phase 4: Templates & UI
- [ ] Rewrite nexify/index.html — big workspace, full-size images
- [ ] Add XY cursor coordinate tracker
- [ ] Add polygon drawing tool
- [ ] Add keypoint placement tool
- [ ] Add folder upload UI
- [ ] Add admin dataset review page
- [ ] Add task assignment UI
- [ ] Add role-based UI (hide admin features from annotators)

## Phase 5: URL Routing
- [ ] Add routes for new views
- [ ] Add media serving for uploaded images

## Phase 6: Testing
- [ ] Verify login works
- [ ] Verify annotation tools work
- [ ] Verify folder upload
- [ ] Verify admin dataset view

