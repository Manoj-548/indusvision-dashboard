from django.urls import path
from django.shortcuts import redirect, render
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),

    path("models/", lambda r: render(r, "models.html"), name="models"),
    path("unified/", lambda r: render(r, "unified.html"), name="unified"),

    path("annotation/", lambda r: redirect("nexify:workspace"), name="annotation"),

    path("rag/", views.agent, name="rag"),
    path("projects/", views.projects_list, name="projects_list"),
    path("projects/<int:project_id>/", views.project_detail, name="project_detail"),

    path("knowledge/", views.knowledge, name="knowledge"),
    path("agent/", views.agent, name="agent"),
    path("tensorboard/", views.tensorboard, name="tensorboard"),
    path("sync/", views.sync, name="sync"),
]