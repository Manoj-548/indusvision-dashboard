from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    PLAN_CHOICES = [
        ('basic', 'Basic'),
        ('admin', 'Admin'),
        ('licensed', 'Licensed'),
        ('host', 'Host'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='nexify_profile')
    nexify_plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='basic')
    is_host = models.BooleanField(default=False)
    email_approved = models.BooleanField(default=False)
    rate_limit_annotations_per_hour = models.PositiveIntegerField(default=10)
    rate_limit_uploads_per_hour = models.PositiveIntegerField(default=5)
    rate_limit_projects_per_day = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"Profile for {self.user.username} ({self.nexify_plan})"

    def get_limits(self):
        limits = {
            'basic': {'annotations': 10, 'uploads': 5, 'projects': 1},
            'admin': {'annotations': 50, 'uploads': 20, 'projects': 5},
            'licensed': {'annotations': 200, 'uploads': 100, 'projects': 20},
            'host': {'annotations': 999999, 'uploads': 999999, 'projects': 999999},
        }
        return limits.get(self.nexify_plan, limits['basic'])


class NexifyWorkspace(models.Model):
    PLAN_CHOICES = [
        ("free", "Free"),
        ("basic", "Basic"),
        ("pro", "Pro"),
        ("enterprise", "Enterprise"),
    ]

    name = models.CharField(max_length=100, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="workspaces")
    description = models.TextField(blank=True)

    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default="free")

    max_projects = models.PositiveIntegerField(default=1)
    max_images = models.PositiveIntegerField(default=100)
    max_storage_mb = models.PositiveIntegerField(default=500)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['owner', 'created_at']),
        ]

    def __str__(self):
        return self.name

    __repr__ = lambda self: f"<NexifyWorkspace id={self.id} name='{self.name}'>"


class NexifyProject(models.Model):
    name = models.CharField(max_length=200)
    workspace = models.ForeignKey(NexifyWorkspace, on_delete=models.CASCADE, related_name="projects")
    description = models.TextField(blank=True)
    classes = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['workspace', 'created_at']),
        ]

    def __str__(self):
        return self.name

    __repr__ = lambda self: f"<NexifyProject id={self.id} name='{self.name}'>"


class NexifyFolder(models.Model):
    name = models.CharField(max_length=100)
    project = models.ForeignKey(NexifyProject, on_delete=models.CASCADE, related_name="folders")

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['project', 'name']),
        ]

    def __str__(self):
        return f"{self.name} ({self.project.name})"

    __repr__ = lambda self: f"<NexifyFolder id={self.id} name='{self.name}'>"


class NexifyImage(models.Model):
    file = models.ImageField(upload_to="nexify/images/")
    folder = models.ForeignKey(NexifyFolder, on_delete=models.CASCADE, related_name="images")

    name = models.CharField(max_length=255, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['folder', 'uploaded_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.name and self.file:
            self.name = self.file.name

        super().save(*args, **kwargs)

        if self.file and (not self.width or not self.height):
            try:
                from PIL import Image
                img = Image.open(self.file.path)
                self.width, self.height = img.size
                super().save(update_fields=["width", "height"])
            except:
                pass

    def __str__(self):
        return self.name

    __repr__ = lambda self: f"<NexifyImage id={self.id} name='{self.name}'>"


class NexifyVideo(models.Model):
    file = models.FileField(upload_to="nexify/videos/")
    folder = models.ForeignKey(NexifyFolder, on_delete=models.CASCADE, related_name="videos")

    name = models.CharField(max_length=255, blank=True)
    duration_sec = models.IntegerField(default=0)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or f"Video-{self.id}"

    __repr__ = lambda self: f"<NexifyVideo id={self.id}>"


class NexifyLabelClass(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default="#00FF00")

    project = models.ForeignKey(NexifyProject, on_delete=models.CASCADE, related_name="label_classes")

    class Meta:
        indexes = [
            models.Index(fields=['project', 'name']),
        ]

    def __str__(self):
        return self.name

    __repr__ = lambda self: f"<NexifyLabelClass id={self.id} name='{self.name}'>"


class NexifyAnnotation(models.Model):
    TYPE_CHOICES = [
        ("bbox", "Bounding Box"),
        ("polygon", "Polygon"),
        ("keypoint", "Keypoint"),
    ]

    image = models.ForeignKey(NexifyImage, on_delete=models.CASCADE, related_name="annotations")
    annotator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="annotations")
    label_class = models.ForeignKey(NexifyLabelClass, on_delete=models.CASCADE)
    reviewed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="reviewed_annotations")

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    data = models.JSONField()
    confidence = models.FloatField(default=1.0)

    is_approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['image', 'created_at']),
            models.Index(fields=['is_approved']),
        ]

    def __str__(self):
        return f"{self.type} - {self.image.name}"

    __repr__ = lambda self: f"<NexifyAnnotation id={self.id} type='{self.type}'>"


class NexifyAssignment(models.Model):
    ROLE_CHOICES = [
        ("annotator", "Annotator"),
        ("reviewer", "Reviewer"),
        ("admin", "Admin"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(NexifyProject, on_delete=models.CASCADE)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    assigned_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['project', 'status']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.project.name}"

    __repr__ = lambda self: f"<NexifyAssignment id={self.id}>"


class NexifyAugmentedImage(models.Model):
    original = models.ForeignKey(NexifyImage, on_delete=models.CASCADE, related_name="augmented")

    file = models.ImageField(upload_to="nexify/augmented/")
    transform_metadata = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    __repr__ = lambda self: f"<NexifyAugmentedImage id={self.id}>"


class NexifyDatasetVersion(models.Model):
    EXPORT_FORMATS = [
        ("yolo", "YOLO"),
        ("coco", "COCO"),
        ("voc", "VOC"),
        ("csv", "CSV"),
        ("tensorflow", "TensorFlow"),
        ("pytorch", "PyTorch"),
        ("roboflow", "Roboflow"),
        ("labelme", "LabelMe"),
        ("kitti", "KITTI"),
        ("json", "JSON"),
        ("yaml", "YAML"),
    ]

    project = models.ForeignKey(NexifyProject, on_delete=models.CASCADE)

    version = models.CharField(max_length=20)
    format = models.CharField(max_length=30, choices=EXPORT_FORMATS)

    export_file = models.FileField(upload_to="nexify/exports/", null=True, blank=True)
    zip_file = models.FileField(upload_to="nexify/exports/zips/", null=True, blank=True)

    image_count = models.IntegerField(default=0)
    annotation_count = models.IntegerField(default=0)

    train_count = models.IntegerField(default=0)
    val_count = models.IntegerField(default=0)
    test_count = models.IntegerField(default=0)

    export_settings = models.JSONField(default=dict, blank=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("completed", "Completed"),
        ],
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=['project', 'status']),
        ]

    def __str__(self):
        return f"{self.project.name} - v{self.version}"

    __repr__ = lambda self: f"<NexifyDatasetVersion id={self.id}>"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        profile = UserProfile.objects.get(user=instance)
        profile.save()
    except UserProfile.DoesNotExist:
        pass

