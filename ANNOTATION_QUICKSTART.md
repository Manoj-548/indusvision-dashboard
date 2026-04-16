# 🎯 Advanced Annotation System - Quick Start Guide

## Getting Started

### 1. Launch the Annotation Tool
```bash
# Start Django server if not running
python manage.py runserver
```

### 2. Navigate to Annotation Dashboard
```
http://localhost:8000/annotation/
```

### 3. Create Your First Workspace
- Click "Create Workspace"
- Enter workspace name (e.g., "Object Detection Project")
- Click Create

### 4. Create a Project
- Select your workspace
- Click "New Project"
- Choose project type:
  - **Object Detection** - Bounding boxes
  - **Semantic Segmentation** - Polygons
  - **Keypoint Detection** - Points
  - **Classification** - Image-level
  - **Video Tracking** - Sequence annotation

### 5. Upload Images
**Option A: Drag & Drop**
- Open project → Images tab
- Drag folder/images onto upload zone
- Watch progress bar

**Option B: Click to Browse**
- Click upload zone
- Select files or folder
- System will process all images

### 6. Start Annotating
- Click image in gallery
- Choose annotation tool (top toolbar)
- Pick class and color
- Draw annotation
- Repeat for all objects

---

## 🛠️ Annotation Tools

### Bounding Box (📦 BBox)
```
1. Click "BBox" button
2. Click and drag on image
3. Release to create rectangle
4. Class auto-selected from dropdown
```

### Polygon (🔷 Polygon)
```
1. Click "Polygon" button
2. Click to add points around object
3. Double-click to finish shape
4. System closes polygon automatically
```

### Smart Polygon (🧠 Smart)
```
1. Click "Smart" button
2. Click starting point
3. Click intermediate points along boundary
4. Double-click to auto-complete
5. AI refines the boundary (optional)
```

### Keypoint (🎯 Keypoint)
```
1. Click "Keypoint" button
2. Click to place keypoints
3. Each click creates a numbered point
4. Update class for keypoint type
```

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl + Z` | Undo last annotation |
| `Ctrl + Y` | Redo annotation |
| `Mouse Wheel ↑` | Zoom in |
| `Mouse Wheel ↓` | Zoom out |
| `Middle Click + Drag` | Pan image |
| `Space + Drag` | Pan (alternative) |

---

## 📊 Working with Annotations

### Editing
- **Delete**: Click × button next to annotation in right panel
- **Clear All**: Click "Clear" button in toolbar
- **Modify**: Delete and redraw (undo if mistake)

### Saving
- Click **"💾 Save"** button (green)
- All annotations upload to database
- Progress bar shows completion

### Auto-Annotation
- Click **"✨ Auto"** button
- YOLO model runs inference
- Auto-generated boxes appear with confidence scores
- Review and manually verify

### Reviewing
- Go to "Review Queue" tab
- See all images with pending annotations
- Click "Review" to edit
- Approve when satisfied

---

## 📤 Exporting Data

### Export Formats
1. **COCO JSON** - For detection/instance segmentation
2. **YOLO TXT** - For YOLOv8 training
3. **Pascal VOC** - For VOC format tools
4. **Darknet** - For Darknet training
5. **CSV** - Spreadsheet format

### Export Process
1. Go to "Export" tab
2. Click desired format
3. Select options:
   - Include auto-annotations
   - Include unapproved
   - Training/validation split
4. Download ZIP file

### Using Exported Data
```bash
# YOLO format
yolo detect train data=dataset.yaml

# COCO format
python scripts/train_coco.py --annotations coco.json

# Pascal VOC
python train.py --dataset VOC --year 2024
```

---

## 🎨 Canvas Controls

### Right Panel Sections

**Image Info**
- Current image details
- Zoom level
- Upload status

**Annotations List**
- All annotations for this image
- Quick delete buttons
- Export button

**Statistics**
- Manual annotations count
- Auto-generated count
- Approved count
- Progress bar

**Version History**
- Previous saves
- Rollback capability (coming soon)

---

## 🔄 Team Workflow

### Typical Annotation Workflow:

```
1. Create Project
   ↓
2. Upload bulk images
   ↓
3. Assign images to annotators
   ↓
4. Each annotator: Open image → Annotate → Save
   ↓
5. Review Queue: Manager reviews annotations
   ↓
6. Approve/Reject annotations
   ↓
7. Export final dataset
   ↓
8. Train model
```

### Best Practices:
- One person per image (avoid conflicts)
- Review high-confidence annotations first
- Create consistent class definitions
- Document special cases
- Regular exports as backup

---

## 🐛 Troubleshooting

### Issue: Image won't load
- Check file format (JPEG, PNG, WebP, GIF)
- Verify file size < 50MB
- Ensure no special characters in filename

### Issue: Zoom too slow
- Check image resolution
- Reduce canvas zoom range
- Close other browser tabs

### Issue: Undo not working
- Refresh page if history corrupts
- Changes are auto-saved after each annotation

### Issue: Upload fails
- Check internet connection
- Upload smaller batches
- Clear browser cache

---

## 💾 Data Management

### Database Storage
- Images: `media/annotation/images/`
- Metadata: SQLite database
- Auto-backup recommended

### Backup Process
```bash
# Export all annotations
python manage.py dumpdata dashboard.Annotation > backup.json

# Export images
cp -r media/annotation/images backup_images/

# Export metadata
cp db.sqlite3 backup_db.sqlite3
```

### Import Backed-up Data
```bash
# Restore database
python manage.py loaddata backup.json

# Restore images
cp backup_images/* media/annotation/images/
```

---

## 🚀 Performance Tips

1. **Batch Uploads**
   - Upload 50-100 images at a time
   - System more efficient with bigger batches

2. **Annotation Speed**
   - Use keyboard shortcuts for faster workflow
   - Zoom to minimum to see full image
   - Use consistent class names

3. **Export Optimization**
   - Export at end of day
   - Don't keep too many versions
   - Archive old projects

---

## 📞 Support

### Common Questions

**Q: Can multiple people annotate same image?**
A: Yes, but last save wins. Recommend assigning different images.

**Q: How do I set confidence threshold?**
A: Settings tab → Confidence Threshold → Save

**Q: Can I undo all changes?**
A: Use Ctrl+Z repeatedly or refresh to discard unsaved changes.

**Q: How large can images be?**
A: Max 50MB recommended. System handles up to 100MB but may be slow.

**Q: Can I annotate videos?**
A: Yes! Create project type "Video Tracking". Frame-by-frame interface.

---

## 🎓 Training Tips

### Object Detection Best Practices:
1. **Tight bounding boxes** - Don't include background
2. **Complete objects** - Include partially visible objects
3. **Consistent sizes** - Similar objects have similar box sizes
4. **Label everything** - All objects of target class

### Segmentation Best Practices:
1. **Precise boundaries** - Follow object edges closely
2. **Consistency** - Same object type, same drawing style
3. **No gaps** - Fully outline object
4. **Clean edges** - Zoom in for accuracy

---

## 📚 Advanced Features (Coming Soon)

- Smart polygon with AI boundary detection
- Auto-class suggestion
- Batch annotation templates
- Multi-person collaboration frame
- Version control and rollback
- Annotation validation rules
- Model-guided suggestions

---

**Ready to annotate?** Start at `/annotation/` 🎉

For detailed API documentation, see `ANNOTATION_SYSTEM_UPDATE.md`
