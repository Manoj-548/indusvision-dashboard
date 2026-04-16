from django.contrib import admin
from .models import LLMConfig, KnowledgeEntry, ChatHistory, RateLimitConfig

@admin.register(LLMConfig)
class LLMConfigAdmin(admin.ModelAdmin):
    list_display = ('user', 'model_name', 'base_url', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username', 'model_name')

@admin.register(KnowledgeEntry)
class KnowledgeEntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'knowledge_type', 'created_at')
    list_filter = ('knowledge_type', 'created_at')
    search_fields = ('title', 'content_preview')

@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'model_used', 'created_at')
    list_filter = ('model_used', 'created_at')
    search_fields = ('query', 'response', 'user__username')
    readonly_fields = ('created_at',)

@admin.register(RateLimitConfig)
class RateLimitConfigAdmin(admin.ModelAdmin):
    list_display = ('user', 'requests_per_minute', 'enabled')
    list_filter = ('enabled',)
