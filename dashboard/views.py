from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Project, Image, Annotation

@login_required
def home(request):
    projects = Project.objects.all().order_by("-created_at")

    stats = {
        "projects": Project.objects.count(),
        "images": Image.objects.count(),
        "annotations": Annotation.objects.count(),
    }

    return render(request, "dashboard.html", {
        "projects": projects,
        "stats": stats
    })


@login_required
def annotation_ui(request):
    return render(request, "annotation.html")
