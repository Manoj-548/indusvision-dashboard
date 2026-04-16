from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from datetime import datetime

class Workspace(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workspaces')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Project(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200)
    project_type = models.CharField(max_length=50, choices=[
        ('object', 'Object Detection'),
        ('segmentation', 'Semantic Segmentation'),
        ('classification', 'Image Classification'),
        ('keypoint', 'Keypoint Detection'),
        ('video', 'Video Tracking'),
    ])
    description = models.TextField(blank=True)
    classes = models.JSONField(default=list)  # [{'name': 'person', 'color': '#ff0000'}]
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.project_type})"

class Image(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')
    filename = models.CharField(max_length=500)
    image_file = models.FileField(upload_to='annotation/images/')
    width = models.IntegerField()
    height = models.IntegerField()
    status = models.CharField(max_length=50, default='pending', choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ])
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.filename

class Annotation(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='annotations')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    class_name = models.CharField(max_length=100)
    annotation_type = models.CharField(max_length=50, choices=[
        ('bbox', 'Bounding Box'),
        ('polygon', 'Polygon'),
        ('keypoint', 'Keypoint'),
        ('auto', 'Auto-generated'),
    ])
    data = models.JSONField()  # {'x1':0.1, 'y1':0.2, 'x2':0.3, 'y2':0.4} or polygon points
    confidence = models.FloatField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.class_name} - {self.image.filename}"

class AnnotationTask(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, default='assigned')
