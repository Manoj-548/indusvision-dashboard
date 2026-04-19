from django.contrib import admin
from .models import Workspace, WorkspaceMember, Project, Image, Annotation, Dataset, SourceFile, KnowledgeEntry, FeedbackMemory

@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
	list_display = ("name", "created_by", "created_at")
	search_fields = ("name",)

@admin.register(WorkspaceMember)
class WorkspaceMemberAdmin(admin.ModelAdmin):
	list_display = ("user", "workspace", "role")
	list_filter = ("role",)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
	list_display = ("name", "workspace", "project_type", "created_at")
	search_fields = ("name",)

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
	list_display = ("project", "file", "status", "uploaded_at")
	list_filter = ("status",)

@admin.register(Annotation)
class AnnotationAdmin(admin.ModelAdmin):
	list_display = ("image", "user", "annotation_type", "created_at", "is_approved")
	list_filter = ("annotation_type", "is_approved")

@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
	list_display = ("project", "version", "created_at")

@admin.register(SourceFile)
class SourceFileAdmin(admin.ModelAdmin):
	list_display = ("path", "file_type")

@admin.register(KnowledgeEntry)
class KnowledgeEntryAdmin(admin.ModelAdmin):
	list_display = ("title", "created_at")

@admin.register(FeedbackMemory)
class FeedbackMemoryAdmin(admin.ModelAdmin):
	list_display = ("prompt", "improved")
