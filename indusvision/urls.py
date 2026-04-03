from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from .views import dashboard_view, login_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='login'),
    path('login/', login_view, name='login_page'),
    path('dashboard/', include('dashboard.urls')),
    path('api/', include('api.urls')),
]

