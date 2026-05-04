from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth.views import LogoutView
from project_core import views as project_core_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", lambda request: redirect("login"), name="home"),
    path("login/", indusvision_views.login_view, name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
    path("dashboard/", include(("dashboard.urls", "dashboard"), namespace="dashboard")),
    
    # path("dashboard/", indusvision_views.dashboard_view, name="dashboard"),  # commented to avoid conflict with namespaced dashboard
    

    path("api/", include("api.urls")),
path("annotation/", include(("nexify.urls", "nexify"), namespace="annotation_app")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
