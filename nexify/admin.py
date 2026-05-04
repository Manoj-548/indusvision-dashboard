from django.contrib import admin
from .models import (
    NexifyWorkspace,
    NexifyProject,
    NexifyFolder,
    NexifyImage,
    NexifyLabelClass,
    NexifyAnnotation,
    NexifyDatasetVersion,
    NexifyAssignment,
    NexifyAugmentedImage,
)


@admin.register(NexifyWorkspace)
class NexifyWorkspaceAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name", "description")


@admin.register(NexifyProject)
class NexifyProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "workspace", "created_at")
    list_filter = ("workspace",)
    search_fields = ("name", "description")


@admin.register(NexifyFolder)
class NexifyFolderAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "created_at")
    list_filter = ("project",)


@admin.register(NexifyImage)
class NexifyImageAdmin(admin.ModelAdmin):
    list_display = ("name", "folder", "width", "height", "uploaded_at")
    list_filter = ("folder__project", "uploaded_at")


@admin.register(NexifyLabelClass)
class NexifyLabelClassAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "project")
    list_filter = ("project",)


@admin.register(NexifyAnnotation)
class NexifyAnnotationAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "image", "annotator", "label_class", "is_approved", "created_at")
    list_filter = ("type", "is_approved", "created_at")
    search_fields = ("annotator__username",)


@admin.register(NexifyDatasetVersion)
class NexifyDatasetVersionAdmin(admin.ModelAdmin):
    list_display = ("version", "project", "format", "annotation_count", "image_count", "created_at")
    list_filter = ("format", "project")


@admin.register(NexifyAssignment)
class NexifyAssignmentAdmin(admin.ModelAdmin):
    list_display = ("user", "project", "role", "status", "assigned_at")
    list_filter = ("role", "status", "project")


@admin.register(NexifyAugmentedImage)
class NexifyAugmentedImageAdmin(admin.ModelAdmin):
    list_display = ("original", "created_at")
