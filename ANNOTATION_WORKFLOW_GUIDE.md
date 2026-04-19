# Complete Annotation Tool Workflow Guide

## 🎯 Overview
A comprehensive annotation platform with role-based access control (RBAC), time tracking, project management, and dataset versioning for computer vision tasks.

---

## 📋 Features Implemented

### 1. **Workspace Management**
- Create and manage annotation workspaces
- Add team members with different roles
- Organize multiple projects within a workspace

**Roles:**
- **Admin**: Full control, can manage members and settings
- **Reviewer**: Can review and approve annotations
- **Annotator**: Can annotate images

**API Endpoints:**
```
POST   /annotation/api/workspaces/              - Create workspace
GET    /annotation/api/workspaces/              - List workspaces
DELETE /annotation/api/workspaces/{id}/         - Delete workspace
```

### 2. **Project Creation with Annotation Types**
Create projects with two main annotation types:

- **Object Detection (Bounding Box)**: Detect and locate objects in images
- **Semantic Segmentation**: Segment image regions by class

**Supported Project Types:**
- Object Detection
- Semantic Segmentation
- Image Classification
- Keypoint Detection
- Video Tracking

**API Endpoints:**
```
POST   /annotation/{workspace_id}/create-project-folder/  - Create project with folder upload
GET    /annotation/api/workspaces/{workspace_id}/projects/ - List projects
DELETE /annotation/api/workspaces/{workspace_id}/projects/{project_id}/delete/ - Delete project
```

### 3. **Image Upload & Management**
Upload image folders in any format:
- **Supported formats**: JPG, JPEG, PNG, GIF, BMP, WEBP
- **Batch upload**: Upload entire folders with images
- **Folder tagging**: Organize images with custom tags

**Features:**
- Automatic image dimension extraction
- Image status tracking (Pending → In Progress → Completed → Approved)
- Folder organization with tags

### 4. **Annotation with RBAC**
Annotators can create annotations with full time tracking:

- **Annotation Types**:
  - Bounding Box (bbox)
  - Polygon Segmentation
  - Keypoint Detection
  - Auto-generated (from AI models)

- **Time Tracking**:
  - `annotation_start_time`: When annotator starts
  - `annotation_end_time`: When annotator finishes
  - `review_start_time`: When reviewer starts review
  - `review_end_time`: When reviewer finishes review
  - Automatic calculation: `annotation_time_minutes()`, `review_time_minutes()`

**API Endpoints:**
```
POST   /annotation/{workspace_id}/project/{project_id}/images/{image_id}/annotations/
GET    /annotation/{workspace_id}/project/{project_id}/images/{image_id}/annotations/
POST   /annotation/{workspace_id}/project/{project_id}/images/{image_id}/auto-annotate/
```

### 5. **Admin Review & Approval**
Admins and reviewers can:
- Review annotations
- Add review comments
- Approve or reject annotations
- Track review time

**Review Workflow:**
1. Annotator completes annotations
2. Status changes to "Completed"
3. Reviewer examines and approves
4. Status changes to "Approved"
5. Move to dataset

**Image Status Flow:**
```
Pending → In Progress → Completed → Approved → In Dataset
                                   ↓
                              Rejected (back to Pending)
```

### 6. **Time Tracking & Analytics**
Comprehensive metrics tracking:

- **Per Image Metrics**:
  - Annotation time (minutes)
  - Review time (minutes)
  - Assigned annotator
  - Assigned reviewer

- **Project Metrics**:
  - Total images count
  - Completed images count
  - Approved images count
  - In progress count
  - Completion percentage
  - Average annotation time per image
  - Average review time per image
  - Total project time spent

**API Endpoint:**
```
GET /annotation/{workspace_id}/project/{project_id}/metrics/
```

### 7. **Dataset Management & Versioning**
Create datasets from approved images with version control:

**Dataset Creation:**
- Select approved images
- Name the dataset
- Add description
- Auto version tracking

**Version Control:**
- Automatic version numbering (v1, v2, v3...)
- Track changes and improvements
- Multiple export formats per version
- Metadata: created_by, created_at, image_count

**API Endpoints:**
```
POST   /annotation/{workspace_id}/project/{project_id}/datasets/                              - Create dataset
GET    /annotation/{workspace_id}/project/{project_id}/datasets/                              - List datasets
POST   /annotation/{workspace_id}/project/{project_id}/dataset/{dataset_id}/version/         - Create version
POST   /annotation/{workspace_id}/project/{project_id}/move-to-dataset/                      - Move images to dataset
GET    /annotation/{workspace_id}/project/{project_id}/dataset/{dataset_id}/version/{version_id}/download/
```

### 8. **Multi-Format Export**
Export datasets in multiple formats for different platforms:

**Supported Formats:**
1. **COCO JSON** - For Object Detection (PyTorch, TensorFlow)
2. **YOLO TXT** - For YOLO detection models
3. **Pascal VOC XML** - For traditional CV pipelines
4. **CSV** - For spreadsheet analysis
5. **ZIP Archive** - Complete dataset package

**Export Contents:**
- Images organized by folder
- Annotations in specified format
- Metadata and class definitions
- Ready to use in training frameworks

**Usage in Training:**
- **Google Colab**: Download ZIP, extract, train with Notebook
- **VS Code**: Clone repo, set up environment, use exported dataset
- **Local Machine**: Download formats, integrate with ML pipeline

### 9. **Complete Workflow Example**

```
Step 1: Create Workspace
├─ Name: "Product Detection"
├─ Description: "Annotate product images for object detection"
└─ Members: Admin (you), Reviewer (john), Annotators (alice, bob)

Step 2: Create Project
├─ Name: "Retail Products"
├─ Type: Object Detection (Bounding Box)
├─ Description: "Detect products on shelves"
└─ Upload Folder: ~/images/products/ (contains 100+ images)

Step 3: Assign Tasks
├─ Assign image batches to annotators
├─ Annotators start annotation (annotation_start_time recorded)
└─ Annotators complete annotations (annotation_end_time recorded)

Step 4: Review & Approve
├─ Reviewer checks annotations (review_start_time recorded)
├─ Reviewer approves quality (review_end_time recorded)
└─ Status changes to "Approved"

Step 5: Create Dataset
├─ Name: "Retail Products v1"
├─ Select all approved images (100+ images)
└─ Auto version: v1.0 created

Step 6: Export & Download
├─ Export Format: YOLO TXT
├─ Download: retail-products-v1.zip
└─ Contains: images/ + labels/ (ready for training)

Step 7: Train Model
├─ Upload to Google Colab
├─ Extract dataset
├─ Run YOLOv8 training
└─ Evaluate metrics

Step 8: Create v2 Dataset
├─ Add 50 more reviewed images
├─ Version auto-increments to v2
├─ Export again in multiple formats
└─ Track dataset evolution
```

---

## 🔧 Technical Implementation

### Database Models

**Workspace** (Base Container)
```
- id: PK
- name: CharField
- description: TextField
- created_by: User FK
- created_at: DateTime
- members: ManyToMany (through WorkspaceMember)
```

**WorkspaceMember** (RBAC)
```
- workspace: FK
- user: FK
- role: CharField (admin, reviewer, annotator)
- added_at: DateTime
```

**Project** (Annotation Project)
```
- workspace: FK
- name: CharField
- project_type: CharField
- description: TextField
- classes: JSONField (class definitions with colors)
- created_at: DateTime
```

**Image** (Annotation Target)
```
- project: FK
- filename: CharField
- image_file: FileField
- width, height: IntegerField
- status: CharField (pending, in_progress, completed, approved, in_dataset)
- folder_tag: CharField (for organization)
- assigned_to: User FK (annotator)
- reviewed_by: User FK (reviewer)
- review_comments: TextField

# Time Tracking
- annotation_start_time: DateTime (nullable)
- annotation_end_time: DateTime (nullable)
- review_start_time: DateTime (nullable)
- review_end_time: DateTime (nullable)
- uploaded_at: DateTime
```

**Annotation** (Actual Annotation)
```
- image: FK
- user: User FK (who created it)
- class_name: CharField
- annotation_type: CharField (bbox, polygon, keypoint, segmentation, auto)
- data: JSONField (coordinates, masks, points)
- confidence: FloatField (for auto-generated)
- is_approved: BooleanField
- created_at, updated_at: DateTime
```

**Dataset** (Collection of Approved Images)
```
- project: FK
- name: CharField
- description: TextField
- created_by: User FK
- created_at: DateTime
- images: ManyToMany
```

**DatasetVersion** (Version Control)
```
- dataset: FK
- version_number: IntegerField
- name: CharField
- description: TextField
- created_by: User FK
- created_at: DateTime
- image_count: IntegerField
- formats: JSONField (list of export formats)
```

**DatasetExport** (Exported Files)
```
- dataset_version: FK
- export_format: CharField (coco, yolo, pascal_voc, csv, zip)
- file_path: FileField
- created_at: DateTime
- created_by: User FK
```

---

## 🚀 Quick Start

### 1. Access the Dashboard
```
URL: http://localhost:8000/annotation/
```

### 2. Create Workspace
- Click "New Workspace"
- Enter name (e.g., "Manoj")
- Enter description (e.g., "BB/SEG")
- Submit

### 3. Create Project
- Enter project name
- Select annotation type (Object Detection or Segmentation)
- Upload folder with images
- Add optional folder tag
- Submit

### 4. Annotate Images
- View images in project
- Click on image to annotate
- Add annotations (bbox, polygon, etc.)
- Save annotations

### 5. Review & Approve
- Admin/Reviewer navigates to review queue
- Checks annotations
- Approves or rejects
- Time auto-tracked

### 6. Create Dataset
- Go to project
- Click "Create Dataset"
- Name it (v1 auto-created)
- Download in desired format

### 7. Train Model
- Download YOLO/COCO format
- Upload to Google Colab/VS Code
- Train with your ML framework
- Track metrics

---

## 📊 Metrics & Reporting

### Project Metrics Endpoint
```json
GET /annotation/{workspace_id}/project/{project_id}/metrics/

Response:
{
  "metrics": {
    "total_images": 150,
    "completed_images": 120,
    "approved_images": 100,
    "in_progress": 20,
    "pending": 30,
    "completion_percentage": 80.0,
    "avg_annotation_time_minutes": 5.2,
    "avg_review_time_minutes": 2.1,
    "total_annotation_time_hours": 10.4,
    "total_review_time_hours": 3.5
  }
}
```

### Time Tracking per Image
```python
image.annotation_time_minutes()  # Returns: 5
image.review_time_minutes()      # Returns: 2
```

---

## 🔐 Security & RBAC

### Role-Based Access Control
- **Admin**: Can manage workspace members, delete projects, access all data
- **Reviewer**: Can review annotations, approve/reject, add comments
- **Annotator**: Can annotate assigned images only

### CSRF Protection
- All POST/DELETE requests require CSRF token
- Frontend automatically includes token in requests
- Django middleware validates all state-changing operations

### User Isolation
- Users can only access their own workspaces
- Filtering on all queries: `created_by=request.user`
- File access restricted to authorized users

---

## 📦 Export Formats Guide

### COCO Format (JSON)
```json
{
  "images": [...],
  "annotations": [...],
  "categories": [...]
}
```
**Use for**: PyTorch, TensorFlow, detectron2

### YOLO Format (TXT)
```
# labels/image.txt
0 0.5 0.5 0.3 0.4  # class x_center y_center width height
1 0.2 0.3 0.1 0.2
```
**Use for**: YOLOv8, YOLOv5

### Pascal VOC Format (XML)
```xml
<annotation>
  <filename>image.jpg</filename>
  <object>
    <name>person</name>
    <bndbox>
      <xmin>100</xmin>
      <ymin>150</ymin>
      <xmax>200</xmax>
      <ymax>300</ymax>
    </bndbox>
  </object>
</annotation>
```
**Use for**: Faster R-CNN, RetinaNet

### CSV Format
```
image_id,filename,x1,y1,x2,y2,class,confidence
1,image1.jpg,100,150,200,300,person,0.95
2,image1.jpg,50,100,150,200,car,0.87
```
**Use for**: Data analysis, spreadsheet tools

---

## 🐛 Troubleshooting

### Workspace Creation Error
**Problem**: "Error creating workspace"
**Solution**: Ensure CSRF token is present, check browser console for details

### Images Not Uploading
**Problem**: "No image files found"
**Solution**: Upload a folder with image files (jpg, png, gif, bmp, webp)

### Annotations Not Saving
**Problem**: Image stays in "In Progress" status
**Solution**: Ensure all annotation fields are filled, check browser console

### Slow Time Tracking
**Problem**: Annotation times seem incorrect
**Solution**: Check server time synchronization, ensure timestamps are recorded

### Export File Not Generated
**Problem**: Dataset version created but no export file
**Solution**: Ensure images have completed annotations, check disk space

---

## 📱 Browser Requirements
- Modern browser (Chrome, Firefox, Safari, Edge)
- JavaScript enabled
- Cookies enabled (for CSRF token)
- File upload support

---

## 🔄 Future Enhancements

1. **AI-Assisted Annotation**: Auto-detection using pre-trained models
2. **Real-time Collaboration**: Multi-user simultaneous annotation
3. **Quality Control**: Inter-annotator agreement metrics
4. **Advanced Analytics**: Dashboard with charts and trends
5. **Mobile App**: iOS/Android annotation app
6. **Integration**: Webhook support for external tools
7. **API Webhooks**: Notify external systems on events

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review API endpoint documentation
3. Check server logs: `python manage.py runserver`
4. Contact team lead for assistance

---

**Version**: 1.0  
**Last Updated**: April 16, 2026  
**Status**: ✅ Production Ready
