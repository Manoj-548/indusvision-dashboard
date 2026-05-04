from django.contrib import admin
from .models import SourceFile, KnowledgeEntry, FeedbackMemory

@admin.register(SourceFile)
class SourceFileAdmin(admin.ModelAdmin):
    list_display = ("path", "file_type", "is_knowledge_relevant", "last_updated")
    list_filter = ("file_type", "is_knowledge_relevant")
    search_fields = ("path",)

@admin.register(KnowledgeEntry)
class KnowledgeEntryAdmin(admin.ModelAdmin):
    list_display = ("title", "knowledge_type", "created_at")
    list_filter = ("knowledge_type",)
    search_fields = ("title", "content_preview")

@admin.register(FeedbackMemory)
class FeedbackMemoryAdmin(admin.ModelAdmin):
    list_display = ("prompt", "improved", "created_at")
    list_filter = ("improved",)
    search_fields = ("prompt", "response")

