from django.urls import path
from . import views

urlpatterns = [
    path("", views.home),
    path("annotation/", views.annotation_ui),
]
