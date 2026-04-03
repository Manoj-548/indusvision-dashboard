from django.db import models

MODULE_CHOICES = [
    ('annotation', 'Annotation'),
    ('automation', 'Automation'),
    ('sandbox', 'Sandbox'),
    ('spider', 'Spider'),
    ('wrangling', 'Data Wrangling'),
    ('sensor', 'Sensor'),
    ('camera', 'Live Camera'),
]


class MetricRecord(models.Model):
    module = models.CharField(max_length=32, choices=MODULE_CHOICES)
    value = models.IntegerField(default=0)
    status = models.CharField(max_length=128, default='idle')
    info = models.JSONField(default=dict, blank=True)
    collected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-collected_at']

    def __str__(self):
        return f"[{self.collected_at}] {self.module} -> {self.value} ({self.status})"


SOURCE_TYPE_CHOICES = [
    ('py', 'Python'),
    ('html', 'HTML'),
    ('index', 'Index'),
    ('other', 'Other'),
]


class SourceFile(models.Model):
    path = models.CharField(max_length=512, unique=True)
    file_type = models.CharField(max_length=16, choices=SOURCE_TYPE_CHOICES)
    components = models.CharField(max_length=128, blank=True)
    line_count = models.IntegerField(default=0)
    last_updated = models.DateTimeField(null=True, blank=True)
    size_bytes = models.BigIntegerField(default=0)
    is_dashboard_relevant = models.BooleanField(default=True)

    class Meta:
        ordering = ['-last_updated', 'path']

    def __str__(self):
        return f"{self.path} ({self.file_type})"


class ModelWeights(models.Model):
    name = models.CharField(max_length=128, unique=True)
    path = models.CharField(max_length=512)
    model_type = models.CharField(max_length=64, default='yolo')  # yolo, custom, etc.
    num_classes = models.IntegerField(default=0)
    trained_at = models.DateTimeField(null=True, blank=True)
    accuracy = models.FloatField(default=0.0)
    status = models.CharField(max_length=32, default='available')  # available, training, error
    last_used = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-last_used', '-trained_at']

    def __str__(self):
        return f"{self.name} ({self.model_type}) - {self.status}"
