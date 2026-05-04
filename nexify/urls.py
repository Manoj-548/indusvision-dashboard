from django.urls import path
from . import views

app_name = "nexify"

urlpatterns = [
    path("", views.workspace_view, name="workspace"),
    path("project/<int:pk>/", views.project_detail, name="project_detail"),
    path("annotate/<int:pk>/", views.annotation_tool, name="annotation_tool"),
    path("dataset/", views.dataset_view, name="dataset_view"),
    path("export/<int:pk>/", views.export_view, name="export_view"),
    path("augment/<int:pk>/", views.augment_image, name="augment_image"),
    # APIs
    path("upload/", views.upload_image, name="upload_image"),
    path("upload-folder/", views.upload_folder, name="upload_folder"),
    path("annotate-api/", views.annotate, name="annotate_api"),
    path("sam/", views.sam_auto_annotate, name="sam_auto"),
    path("assign/", views.assign_task, name="assign_task"),
    path("annotations/<int:pk>/", views.list_annotations, name="list_annotations"),
]
