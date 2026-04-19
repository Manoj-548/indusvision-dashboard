from django.db import models
from django.contrib.auth.models import User

# =========================
# WORKSPACE + RBAC
# =========================

class Workspace(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class WorkspaceMember(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('reviewer', 'Reviewer'),
        ('annotator', 'Annotator'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

# =========================
# PROJECT
# =========================

class Project(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    project_type = models.CharField(max_length=50)
    classes = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

# =========================
# IMAGE + ANNOTATION
# =========================

class Image(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    file = models.ImageField(upload_to='images/')
    status = models.CharField(max_length=50, default='pending')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Annotation(models.Model):
    TYPE_CHOICES = [
        ('bbox', 'Bounding Box'),
        ('polygon', 'Polygon'),
        ('smart_polygon', 'Smart Polygon'),
    ]
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    annotation_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    data = models.JSONField()  # stores bbox or polygon
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

# =========================
# DATASET EXPORT
# =========================

class Dataset(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    version = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

# =========================
# AI KNOWLEDGE + MEMORY
# =========================

class SourceFile(models.Model):
    path = models.CharField(max_length=500)
    file_type = models.CharField(max_length=50)

class KnowledgeEntry(models.Model):
    title = models.CharField(max_length=200)
    content_preview = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class FeedbackMemory(models.Model):
    prompt = models.TextField()
    response = models.TextField()
    improved = models.BooleanField(default=False)