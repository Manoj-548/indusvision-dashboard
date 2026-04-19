from django.urls import path
from . import views

urlpatterns = [
    path("sensor/", views.api_sensor),
    path("annotation/", views.api_annotation),
    path("ai-suggest/", views.ai_suggest),
    path("knowledge/", views.api_knowledge),
]
