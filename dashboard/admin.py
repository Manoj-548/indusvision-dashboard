from django.contrib import admin
from django.utils.html import format_html
from .models import MetricRecord, SourceFile, ModelWeights, KnowledgeEntry


@admin.register(MetricRecord)
class MetricRecordAdmin(admin.ModelAdmin):
    list_display = ('module', 'value', 'status', 'collected_at')
    list_filter = ('module', 'status')
    search_fields = ('module',)
    ordering = ('-collected_at',)
    readonly_fields = ('collected_at',)


@admin.register(SourceFile)
class SourceFileAdmin(admin.ModelAdmin):
    list_display = ('short_path', 'file_type', 'line_count', 'size_mb', 'is_knowledge_relevant', 'last_updated')
    list_filter = ('file_type', 'is_dashboard_relevant', 'is_knowledge_relevant')
    search_fields = ('path',)
    ordering = ('-last_updated',)
    readonly_fields = ('path', 'last_updated')
    date_hierarchy = 'last_updated'
    list_per_page = 20

    def short_path(self, obj):
        return obj.path[:50] + '...' if len(obj.path) > 50 else obj.path
    short_path.short_description = 'Path'

    def size_mb(self, obj):
        return f"{obj.size_bytes / (1024*1024):.1f} MB"
    size_mb.short_description = 'Size'


@admin.register(ModelWeights)
class ModelWeightsAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_type', 'status', 'num_classes', 'last_used', 'path', 'accuracy')
    list_filter = ('model_type', 'status')
    search_fields = ('name',)
    ordering = ('-last_used',)
    readonly_fields = ('metadata',)
    date_hierarchy = 'last_used'


@admin.register(KnowledgeEntry)
class KnowledgeEntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'knowledge_type', 'source_file_short', 'consolidated_at')
    list_filter = ('knowledge_type',)
    search_fields = ('title',)
    readonly_fields = ('source_file', 'consolidated_at', 'extracted_data')
    ordering = ('-consolidated_at',)
    date_hierarchy = 'consolidated_at'
    list_per_page = 20

    def source_file_short(self, obj):
        return obj.source_file.path[:50] + '...' if len(obj.source_file.path) > 50 else obj.source_file.path
    source_file_short.short_description = 'Source'

