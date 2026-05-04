from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

# Optional role decorator (future use)
def require_nexify_role(role=None):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# =========================
# UI VIEWS
# =========================

@login_required
def workspace_view(request):
    return render(request, "nexify/workspace.html")

@login_required
def project_detail(request, pk):
    return render(request, "nexify/project_detail.html", {"pk": pk})

@login_required
def annotation_tool(request, pk):
    return render(request, "nexify/annotation.html", {"pk": pk})

@login_required
def dataset_view(request):
    return render(request, "nexify/dataset.html")

@login_required
def export_view(request, pk):
    return render(request, "nexify/export.html", {"pk": pk})

@login_required
def augment_image(request, pk):
    return render(request, "nexify/augmentation.html", {"pk": pk})

# =========================
# API VIEWS
# =========================

@login_required
def upload_image(request):
    return JsonResponse({"status": "single image uploaded"})

@login_required
def upload_folder(request):
    return JsonResponse({"status": "folder uploaded"})

@login_required
def annotate(request):
    return JsonResponse({"status": "annotation saved"})

@login_required
def sam_auto_annotate(request):
    return JsonResponse({"status": "SAM auto annotation triggered"})

@login_required
def assign_task(request):
    return JsonResponse({"status": "task assigned"})

@login_required
def list_annotations(request, pk):
    return JsonResponse({"annotations": [], "project_id": pk})
