"""
URL configuration for indusvision project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from .views import dashboard_view, api_sensor, login_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('models/', lambda r: render(r, 'model_management.html'), name='models'),
    path('', login_view, name='login'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('api/sensor/', api_sensor, name='api_sensor'),
    path('api/annotation/', api_sensor, name='api_annotation'),
    path('api/camera/', api_sensor, name='api_camera'),
    path('api/automation/', api_sensor, name='api_automation'),
    path('api/sandbox/', api_sensor, name='api_sandbox'),
]
