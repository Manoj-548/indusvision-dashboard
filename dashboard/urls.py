from django.urls import path
from django.shortcuts import render
from django.contrib.auth import views as auth_views
from . import views
from . import views_annotation

urlpatterns = [
    path('', views.home, name='dashboard_home'),
    
    # Workspace & Project Management
    # Renamed from annotation_workspace to workspace_list to match views
    path('annotation/', views_annotation.workspace_list, name='annotation_workspace'),
    path('annotation/api/workspaces/', views_annotation.workspaces_api, name='workspaces_api'),
    path('annotation/api/workspaces/<int:workspace_id>/', views_annotation.delete_workspace, name='delete_workspace'),
    path('annotation/<int:workspace_id>/', views_annotation.workspace_projects, name='workspace_projects'),
    path('annotation/<int:workspace_id>/project/<int:project_id>/', views_annotation.annotation_project, name='annotation_project'),
    
    # API & Route to annotate page
    path('annotation/<int:workspace_id>/project/<int:project_id>/images/', views_annotation.upload_images, name='upload_images'),
    path('annotation/<int:workspace_id>/project/<int:project_id>/images/', views_annotation.project_images_api, name='project_images_api'),
    path('annotation/<int:workspace_id>/project/<int:project_id>/', views_annotation.project_detail_api, name='project_detail_api'),
    path('annotation/<int:workspace_id>/project/<int:project_id>/metrics/', views_annotation.project_metrics_api, name='project_metrics_api'),
    path('annotation/<int:workspace_id>/project/<int:project_id>/review-queue/', views_annotation.project_review_queue_api, name='project_review_queue_api'),
    path('annotation/<int:workspace_id>/project/<int:project_id>/images/<int:image_id>/annotate/', views_annotation.annotate_image, name='annotate_image'),
    path('annotation/<int:workspace_id>/project/<int:project_id>/images/<int:image_id>/annotations/', views_annotation.image_annotations, name='image_annotations'),
    path('annotation/<int:workspace_id>/project/<int:project_id>/images/<int:image_id>/auto-annotate/', views_annotation.auto_annotate_image, name='auto_annotate_image'),
    path('annotation/auto/<int:workspace_id>/<int:project_id>/<int:image_id>/', views_annotation.auto_annotate, name='auto_annotate'),
    path('annotation/export/<int:workspace_id>/<int:project_id>/', views_annotation.export_dataset, name='export_dataset'),
    path('annotation/api/workspaces/<int:workspace_id>/projects/', views_annotation.workspace_projects, name='annotation_api_projects'),
    path('annotation/api/workspaces/<int:workspace_id>/projects/<int:project_id>/', views_annotation.delete_project, name='annotation_api_delete_project'),

    # Project Management
    path('projects/', views.projects_list, name='projects_list'),
    path('projects/new/', views.project_create, name='project_create'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/edit/', views.project_update, name='project_update'),
    path('projects/<int:project_id>/delete/', views.project_delete, name='project_delete'),

    # Other Tools
    path('models/', lambda r: render(r, 'model_management.html'), name='model_management'),
    path('unified/', views.unified, name='unified'),
    path('sync/', views.sync, name='sync'),
    path('knowledge/', views.knowledge, name='knowledge'),
    path('agent/', views.agent, name='agent'),
    path('annotations/', views.annotations, name='annotations'),
    path('tensorboard/', views.tensorboard, name='tensorboard'),
    path('start-tensorboard/', views.start_tensorboard_view, name='start_tensorboard'),
    path('api/live/', views.live_updates, name='live_updates'),

    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]