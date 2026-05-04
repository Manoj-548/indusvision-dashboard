from django.contrib import admin
from django.urls import path
from nexify import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.dashboard, name='dashboard'),
    path('annotation/', views.annotation, name='annotation'),

    path('upload/', views.upload_image, name='upload_image'),
    path('save-annotation/', views.save_annotation, name='save_annotation'),
    path('export/', views.export_dataset, name='export_dataset'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)