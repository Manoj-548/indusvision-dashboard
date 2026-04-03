from django.contrib import admin
from .models import MetricRecord, SourceFile, ModelWeights


@admin.register(MetricRecord)
class MetricRecordAdmin(admin.ModelAdmin):
    list_display = ('module', 'value', 'status', 'collected_at')
    list_filter = ('module', 'status')
    search_fields = ('module', 'status')
    ordering = ('-collected_at',)


@admin.register(SourceFile)
class SourceFileAdmin(admin.ModelAdmin):
    list_display = ('path', 'file_type', 'line_count', 'last_updated', 'size_bytes', 'is_dashboard_relevant')
    list_filter = ('file_type', 'is_dashboard_relevant')
    search_fields = ('path', 'components')
    ordering = ('-last_updated',)


@admin.register(ModelWeights)
class ModelWeightsAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_type', 'num_classes', 'accuracy', 'status', 'last_used')
    list_filter = ('model_type', 'status')
    search_fields = ('name', 'path')
    ordering = ('-last_used',)
