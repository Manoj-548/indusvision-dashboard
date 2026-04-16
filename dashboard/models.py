from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class SourceFile(models.Model):
    path = models.CharField(max_length=500, unique=True)
    file_type = models.CharField(max_length=20, default='other')
    line_count = models.IntegerField(default=0)
    last_updated = models.DateTimeField(null=True, blank=True)
    size_bytes = models.BigIntegerField(default=0)
    is_dashboard_relevant = models.BooleanField(default=False)
    is_knowledge_relevant = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.path

class KnowledgeEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    source_file = models.ForeignKey(SourceFile, on_delete=models.CASCADE, null=True, blank=True)
    knowledge_type = models.CharField(max_length=50, default='code')
    title = models.CharField(max_length=200)
    content_preview = models.TextField(blank=True)
    extracted_data = models.JSONField(default=dict)
    vector_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class LLMConfig(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    model_name = models.CharField(max_length=100, default='qwen2.5-coder:3b')
    base_url = models.CharField(max_length=200, default='http://localhost:11434')
    request_timeout = models.IntegerField(default=120)
    num_ctx = models.IntegerField(default=4096)
    num_predict = models.IntegerField(default=512)
    temperature = models.FloatField(default=0.7)
    top_p = models.FloatField(default=0.9)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.model_name}"

class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.TextField()
    response = models.TextField()
    model_used = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.query[:50]}..."

class RateLimitConfig(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    requests_per_minute = models.IntegerField(default=60)
    requests_per_hour = models.IntegerField(default=1000)
    concurrent_requests = models.IntegerField(default=5)
    enabled = models.BooleanField(default=False)

    def __str__(self):
        return f"RateLimit: {self.user.username}"
