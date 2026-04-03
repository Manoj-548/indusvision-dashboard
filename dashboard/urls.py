from django.urls import path
from django.shortcuts import render
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='dashboard_home'),
    path('models/', lambda r: render(r, 'model_management.html'), name='model_management'),
    path('unified/', views.unified, name='unified'),
    path('sync/', views.sync, name='sync'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
