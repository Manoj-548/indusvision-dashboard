# Advanced Annotation System - Architecture & Workflow

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     ANNOTATION SYSTEM                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              FRONTEND (HTML/CSS/JS)                      │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │                                                            │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │  │
│  │  │ workspaces   │  │  project.    │  │ annotate.    │   │  │
│  │  │ .html        │  │ html         │  │ html         │   │  │
│  │  ├──────────────┤  ├──────────────┤  ├──────────────┤   │  │
│  │  │ • Create WS  │  │ • Dashboard  │  │ • Canvas     │   │  │
│  │  │ • List WS    │  │ • Upload Img │  │ • Tools      │   │  │
│  │  │ • Delete WS  │  │ • Gallery    │  │ • Undo/Redo  │   │  │
│  │  │              │  │ • Metrics    │  │ • Save Ann   │   │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │  │
│  │        ↓                   ↓                    ↓          │  │
│  │    Fetch WS           Upload/Load          Draw/Edit     │  │
│  │                                                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              REST API ENDPOINTS                          │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │                                                            │  │
│  │  /annotation/api/workspaces/               [GET/POST]     │  │
│  │  /annotation/<ws>/project/<proj>/          [GET/POST]     │  │
│  │  /annotation/<ws>/project/<proj>/images/   [GET/POST]     │  │
│  │  /annotation/<ws>/project/<proj>/metrics/  [GET]          │  │
│  │  /annotation/<ws>/project/<proj>/review-queue/ [GET]      │  │
│  │  /annotation/<ws>/project/<proj>/images/<img>/annotate/   │  │
│  │  /annotation/<ws>/project/<proj>/images/<img>/annotations/│  │
│  │  /annotation/<ws>/project/<proj>/images/<img>/auto-ann/   │  │
│  │                                                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         DJANGO BACKEND (views_annotation.py)            │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │                                                            │  │
│  │  ┌─────────────────┐  ┌─────────────────┐               │  │
│  │  │ Workspace Mgmt  │  │ Project Mgmt    │               │  │
│  │  ├─────────────────┤  ├─────────────────┤               │  │
│  │  │ • Create        │  │ • Create        │               │  │
│  │  │ • List          │  │ • List          │               │  │
│  │  │ • Delete        │  │ • Delete        │               │  │
│  │  │ • Auth Check    │  │ • Auth Check    │               │  │
│  │  └─────────────────┘  └─────────────────┘               │  │
│  │            ↓                      ↓                       │  │
│  │  ┌─────────────────┐  ┌─────────────────┐               │  │
│  │  │ Image Upload    │  │ Annotation Mgmt │               │  │
│  │  ├─────────────────┤  ├─────────────────┤               │  │
│  │  │ • CV2 resize    │  │ • Create        │               │  │
│  │  │ • Get dims      │  │ • Read          │               │  │
│  │  │ • Save to DB    │  │ • Update        │               │  │
│  │  │ • File handling │  │ • Delete        │               │  │
│  │  │                 │  │ • Export        │               │  │
│  │  └─────────────────┘  └─────────────────┘               │  │
│  │                                                            │  │
│  │  ┌────────────────────────────────────────┐             │  │
│  │  │ YOLO Auto-Annotation                  │             │  │
│  │  ├────────────────────────────────────────┤             │  │
│  │  │ • Load model (yolov8n.pt)              │             │  │
│  │  │ • Run inference                        │             │  │
│  │  │ • Extract boxes + confidence           │             │  │
│  │  │ • Store in DB with confidence scores   │             │  │
│  │  └────────────────────────────────────────┘             │  │
│  │                                                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │            DATABASE MODELS (ORM)                         │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │                                                            │  │
│  │  Workspace                Image                           │  │
│  │  ├─ id                     ├─ id                          │  │
│  │  ├─ name                   ├─ filename                    │  │
│  │  ├─ description            ├─ project_id (FK)            │  │
│  │  ├─ created_by (FK:User)   ├─ image_file                 │  │
│  │  ├─ created_at             ├─ width/height               │  │
│  │  └─ projects (Rel)         ├─ status                     │  │
│  │                            ├─ assigned_to (FK)           │  │
│  │  Project                   └─ annotations (Rel)          │  │
│  │  ├─ id                                                    │  │
│  │  ├─ workspace_id (FK)      Annotation                    │  │
│  │  ├─ name                   ├─ id                         │  │
│  │  ├─ project_type           ├─ image_id (FK)             │  │
│  │  ├─ description            ├─ user_id (FK)              │  │
│  │  ├─ classes (JSON)         ├─ class_name                │  │
│  │  ├─ created_at             ├─ annotation_type           │  │
│  │  └─ images (Rel)           ├─ data (JSON)               │  │
│  │                            ├─ confidence                │  │
│  │                            ├─ is_approved               │  │
│  │                            └─ created_at                │  │
│  │                                                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │            STORAGE LAYER                                 │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │                                                            │  │
│  │  SQLite (Local)           File System                     │  │
│  │  ├─ All models            ├─ media/annotation/images/    │  │
│  │  ├─ User data             ├─ JPEG/PNG files             │  │
│  │  ├─ Annotations           └─ Uploaded by users           │  │
│  │  └─ Metadata                                             │  │
│  │                                                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Flow Diagrams

### Upload Workflow
```
User browses folder
        ↓
File list displayed
        ↓
User confirms upload
        ↓
Frontend loops through files
        ↓
        ├─→ POST /annotation/<ws>/project/<proj>/images/
        │        with FormData (single file per request)
        │
        ├─→ Backend receives image_file
        │
        ├─→ Backend reads dimensions with CV2
        │
        ├─→ Backend creates Image model
        │   - filename
        │   - width/height (actual)
        │   - project_id
        │   - status='pending'
        │
        ├─→ Save to file system
        │   media/annotation/images/<filename>
        │
        └─→ Return JSON: {image_id, width, height}
        
Update progress bar on frontend
        ↓
Display in gallery (thumbnails)
        ↓
Ready for annotation
```

### Annotation Workflow
```
User clicks image in gallery
        ↓
GET /annotation/<ws>/project/<proj>/images/<img>/annotate/
        ↓
Backend renders annotate.html
  - Passes: image, project, workspace
  - Sets template variables for JS
        ↓
Frontend loads image file
        ↓
User selects tool (BBox/Polygon/Smart/Keypoint)
        ↓
User draws on canvas (mouse events)
        ↓
Frontend tracks:
  - Tool type
  - Coordinates
  - Class name
  - Color
        ↓
User clicks SAVE button
        ↓
For each annotation:
    ├─→ POST /annotation/<ws>/project/<proj>/images/<img>/annotations/
    │        with JSON: {class_name, annotation_type, data, confidence}
    │
    ├─→ Backend creates Annotation model
    │
    └─→ Returns annotation_id
        
Show progress bar: completed / total
        ↓
Database updated with all annotations
        ↓
User can continue annotating or export
```

### Auto-Annotation Workflow
```
User clicks "✨ Auto" button
        ↓
POST /annotation/<ws>/project/<proj>/images/<img>/auto-annotate/
        ↓
Backend:
  ├─→ Load YOLO model: 'yolov8n.pt'
  │
  ├─→ Run inference on image
  │        model = YOLO('yolov8n.pt')
  │        results = model(image_path)
  │
  ├─→ For each detection:
  │   ├─→ Extract:
  │   │   - class ID (cls)
  │   │   - confidence score (conf)
  │   │   - bounding box (x1, y1, x2, y2)
  │   │
  │   └─→ Create Annotation:
  │       - annotation_type = 'bbox'
  │       - data = {x1, y1, x2, y2} (normalized)
  │       - confidence = score
  │       - is_approved = False (manual review needed)
  │
  └─→ Return: {total_created: N}
        
Show alert: "Auto-annotated N objects"
        ↓
Reload annotation canvas
        ↓
Frontend displays auto boxes with confidence labels
        ↓
User can:
  ├─→ Approve (check is_approved = True)
  ├─→ Edit (delete + redraw)
  └─→ Reject (delete)
```

### Export Workflow
```
User selects export format (COCO/YOLO/VOC/etc)
        ↓
POST /annotation/<ws>/project/<proj>/export/
        with {format, include_auto_annotations}
        ↓
Backend aggregates data:
  ├─→ Get all images for project
  ├─→ Get all annotations per image
  └─→ Filter by format requirements
        ↓
Format-specific processing:
  │
  ├─ COCO JSON:
  │   ├─→ Build categories array
  │   ├─→ Build images array
  │   └─→ Build annotations with COCO structure
  │
  ├─ YOLO TXT:
  │   ├─→ Create labels/ directory
  │   ├─→ For each image:
  │   │   └─→ Write .txt file: class_id x_center y_center width height
  │   └─→ Create classes.txt
  │
  ├─ Pascal VOC:
  │   ├─→ Create Annotations/ directory
  │   └─→ For each image:
  │       └─→ Write .xml file: VOC format
  │
  └─ CSV:
      └─→ Create spreadsheet: image | class | bbox | confidence
        
Package into ZIP
        ↓
Return download URL
        ↓
User downloads dataset.zip
        ↓
Extract and use for training
```

---

## 🔐 Authentication & Authorization

```
User Login
    ↓
Django auth middleware
    ↓
@login_required decorator on all views
    ↓
Per-request checks:
    ├─→ Workspace.created_by == request.user
    ├─→ Project in user's workspace
    ├─→ Image in user's project
    └─→ Return 403 if unauthorized
    
This ensures:
  - Users only see their own workspaces
  - Users only edit their own projects
  - Users only view/annotate their images
  - No cross-user data access
```

---

## 📈 Database Query Patterns

### Efficient Queries Used

```python
# Aggregated metrics (single query instead of loops)
stats = project.images.aggregate(
    total_images=Count('id'),
    annotated_images=Count('annotations', distinct=True),
    auto_generated=Count('images__annotations',
                        filter=F('images__annotations__confidence__gt') > 0.5),
    approved=Count('images__annotations',
                   filter=F('images__annotations__is_approved') == True)
)

# Result: 1 query, all stats computed in DB
# Not: 4 separate queries

# Efficient filtering
review_queue = Image.objects.filter(
    project_id=project_id
).prefetch_related('annotations')

# Result: 2 queries (images + related annotations)
# Not: N+1 query problem
```

---

## 🎯 Request/Response Examples

### Create Annotation
```json
REQUEST POST /annotation/1/project/5/images/12/annotations/
{
    "class_name": "person",
    "annotation_type": "bbox",
    "data": {
        "x1": 0.1,
        "y1": 0.2,
        "x2": 0.5,
        "y2": 0.8
    },
    "confidence": 0.0
}

RESPONSE 200
{
    "annotation": {
        "id": 42
    }
}
```

### Get Metrics
```json
REQUEST GET /annotation/1/project/5/metrics/

RESPONSE 200
{
    "metrics": {
        "annotated_images": 45,
        "auto_generated": 180,
        "approved": 120
    }
}
```

### Upload Image
```json
REQUEST POST /annotation/1/project/5/images/
Content-Type: multipart/form-data
files[0]: image.jpg

RESPONSE 200
{
    "message": "Uploaded image.jpg",
    "image_id": 156,
    "width": 1920,
    "height": 1080
}
```

---

## ⚡ Performance Optimizations

1. **Aggregations Instead of Loops**
   - Metrics calculation: DB aggregation (1 query)
   - Review queue: Prefetch related (2 queries)

2. **Batch Operations**
   - Upload: Process each file individually
   - Save annotations: Client-side batching
   - Export: Streaming response (no memory spike)

3. **Frontend Caching**
   - Canvas state held in memory
   - History stack (not DB stored until save)
   - Image cached in browser

4. **Lazy Loading**
   - Image thumbnails load on demand
   - Annotation list updates only on save
   - Metrics fetched separately

---

## 🔄 Concurrency Handling

```
Scenario: Two users editing same image

User A: Opens image → Loads annotations into canvas
User B: Opens image → Loads annotations into canvas

User A: Draws box → Saves annotation
  └─→ Creates new Annotation record

User B: Draws different box → Saves annotation
  └─→ Creates new Annotation record (independent)

Result: Both annotations saved (no conflict)
        Both visible on next refresh

This design allows:
✅ Concurrent annotation (different objects)
❌ Prevents concurrent edits (same object)
   - Not an issue since each draws unique objects
```

---

## 🛡️ Error Handling

```
User uploads corrupted image:
    ↓
Backend tries CV2.imread()
    ↓
Exception caught
    ↓
Falls back to default dimensions (640x480)
    ↓
Image still uploads (degraded UX, no crash)
    ↓
Annotation proceeds normally

Network interruption during upload:
    ↓
Frontend retries failed file
    ↓
Shows file status (success/error/retry)
    ↓
User can download progress and resume later

DB write conflict:
    ↓
Django ORM handles via transaction
    ↓
Atomic write or rollback
    ↓
User sees success or "try again" error
```

---

## 📚 Key Files Reference

| File | Purpose | Key Functions |
|------|---------|----------------|
| annotate.html | Canvas UI | draw(), annotate(), save() |
| project.html | Manager UI | uploadFiles(), exportDataset() |
| views_annotation.py | API logic | upload_images(), image_annotations() |
| models_annotation.py | DB schema | Workspace, Project, Image, Annotation |
| urls.py | Routing | Path definitions |

---

**Architecture Version:** 1.0  
**Last Updated:** System Integration Complete  
**Status:** Production Ready ✅
