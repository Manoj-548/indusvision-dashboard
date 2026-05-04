from django.db import models
from django.contrib.auth.models import User

# AI KNOWLEDGE + MEMORY MODELS (Projects Dashboard)

class SourceFile(models.Model):
    path = models.CharField(max_length=500)
    file_type = models.CharField(max_length=50)
    size_bytes = models.BigIntegerField(null=True, blank=True)
    is_dashboard_relevant = models.BooleanField(default=False)
    is_knowledge_relevant = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_updated']

class KnowledgeEntry(models.Model):
    KNOWLEDGE_TYPES = [
        ('doc', 'Documentation'),
        ('script', 'Script'),
        ('config', 'Configuration'),
    ]
    title = models.CharField(max_length=200)
    content_preview = models.TextField()
    knowledge_type = models.CharField(max_length=20, choices=KNOWLEDGE_TYPES, default='doc')
    source_file = models.ForeignKey(SourceFile, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class FeedbackMemory(models.Model):
    prompt = models.TextField()
    response = models.TextField()
    improved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class LLMConfig(models.Model):
    """Configuration for LLM models used in RAG engine"""
    name = models.CharField(max_length=100, default="ollama-default")
    model_name = models.CharField(max_length=100, default="llama3.2:1b")
    base_url = models.CharField(max_length=200, default="http://localhost:11434")
    request_timeout = models.FloatField(default=120.0)
    num_ctx = models.IntegerField(default=4096)
    num_predict = models.IntegerField(default=512)
    temperature = models.FloatField(default=0.7)
    is_active = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.name} ({self.model_name})"
