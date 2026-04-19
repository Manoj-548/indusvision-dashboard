
from django.contrib import admin
from django.urls import path, include
from indusvision import views as indusvision_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", indusvision_views.login_view, name="login"),
    path("dashboard/", indusvision_views.dashboard_view, name="dashboard"),
    path("", include("dashboard.urls")),
    path("api/", include("api.urls")),
]
