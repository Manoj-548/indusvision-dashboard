from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.db.models import Count, Avg, F
from .models_annotation import Workspace, Project, Image, Annotation, AnnotationTask
from django.utils import timezone
from datetime import timedelta
import json
import zipfile
import cv2
import numpy as np
from ultralytics import YOLO  # YOLOv8
from io import BytesIO

@login_required
def workspace_list(request):
    """View to list all workspaces for the logged-in user."""
    workspaces = Workspace.objects.filter(created_by=request.user)
    return render(request, 'annotation/workspace.html', {'workspaces': workspaces})
@login_required
@require_http_methods(["GET", "POST"])
def workspaces_api(request):
    """API to list or create workspaces."""
    if request.method == 'POST':
        data = json.loads(request.body)
        workspace = Workspace.objects.create(
            name=data['name'],
            description=data.get('description', ''),
            created_by=request.user
        )
        return JsonResponse({'workspace': {'id': workspace.id, 'name': workspace.name}})
    
    workspaces = Workspace.objects.filter(created_by=request.user).annotate(
        project_count=Count('projects'),
        total_images=Count('projects__images')
    )
    return JsonResponse({'workspaces': list(workspaces.values('id', 'name', 'description', 'project_count', 'total_images'))})

@login_required
@require_http_methods(["DELETE"])
def delete_workspace(request, workspace_id):
    workspace = get_object_or_404(Workspace, id=workspace_id, created_by=request.user)
    workspace.delete()
    return JsonResponse({'status': 'deleted'})
@login_required
@require_http_methods(["GET", "POST"])
def workspace_projects(request, workspace_id):
    """View to list projects in a workspace or create a new one."""
    workspace = get_object_or_404(Workspace, id=workspace_id, created_by=request.user)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        project = Project.objects.create(
            workspace=workspace,
            name=data['name'],
            project_type=data['project_type'],
            description=data.get('description', ''),
            classes=data.get('classes', [])
        )
        return JsonResponse({'project': {'id': project.id, 'name': project.name}})
    
    projects = workspace.projects.annotate(image_count=Count('images'))
    return JsonResponse({'projects': list(projects.values('id', 'name', 'project_type', 'image_count'))})

@login_required
@require_http_methods(["DELETE"])
def delete_project(request, workspace_id, project_id):
    project = get_object_or_404(Project, id=project_id, workspace_id=workspace_id, workspace__created_by=request.user)
    project.delete()
    return JsonResponse({'status': 'deleted'})

@login_required
def annotation_project(request, workspace_id, project_id):
    project = get_object_or_404(Project, id=project_id, workspace_id=workspace_id, workspace__created_by=request.user)
    return render(request, 'annotation/project.html', {'project': project, 'workspace': project.workspace})

@login_required
@require_http_methods(["POST"])
def upload_images(request, workspace_id, project_id):
    project = get_object_or_404(Project, id=project_id, workspace_id=workspace_id, workspace__created_by=request.user)
    
    if 'image_file' not in request.FILES:
        return JsonResponse({'error': 'No image file provided'}, status=400)
    
    image_file = request.FILES['image_file']
    
    # Get image dimensions
    try:
        img = cv2.imread(image_file.temporary_file_path())
        height, width = img.shape[:2]
    except:
        # Fallback dimensions if CV2 fails
        width, height = 640, 480
    
    image = Image.objects.create(
        project=project,
        filename=image_file.name,
        image_file=image_file,
        width=width,
        height=height
    )
    
    return JsonResponse({
        'message': f'Uploaded {image_file.name}',
        'image_id': image.id,
        'width': width,
        'height': height
    })

@login_required
@require_http_methods(["POST"])
def auto_annotate(request, workspace_id, project_id, image_id):
    image = get_object_or_404(Image, id=image_id, project_id=project_id, project__workspace_id=workspace_id)
    model = YOLO('yolov8n.pt') 
    results = model(image.image_file.path)
    
    annotations_created = 0
    for r in results:
        boxes = r.boxes
        if boxes is not None:
            for box in boxes:
                cls = int(box.cls)
                conf = float(box.conf)
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                Annotation.objects.create(
                    image=image,
                    class_name=model.names[cls],
                    annotation_type='bbox',
                    data={'x1': x1/image.width, 'y1': y1/image.height, 'x2': x2/image.width, 'y2': y2/image.height},
                    confidence=conf
                )
                annotations_created += 1
    
    return JsonResponse({'total_created': annotations_created})

@login_required
@require_http_methods(["POST"])
def export_dataset(request, workspace_id, project_id):
    project = get_object_or_404(Project, id=project_id, workspace_id=workspace_id)
    export_format = request.POST.get('format')
    
    if export_format == 'coco':
        data = generate_coco(project)
        response = HttpResponse(json.dumps(data, indent=2), content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="annotations_{project.id}.json"'
        return response
    elif export_format == 'yolo':
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            for img in project.images.all():
                anns = img.annotations.all()
                label_path = f"labels/{img.filename.rsplit('.', 1)[0]}.txt"
                label_content = ""
                for ann in anns:
                    if ann.annotation_type == 'bbox':
                        d = ann.data
                        try:
                            class_idx = project.classes.index(ann.class_name)
                            label_content += f"{class_idx} {d['x1']} {d['y1']} {d['x2']-d['x1']} {d['y2']-d['y1']}\n"
                        except ValueError:
                            continue
                zf.writestr(label_path, label_content)
                zf.write(img.image_file.path, f"images/{img.filename}")
        
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="dataset_{project.id}.zip"'
        return response
    
    return HttpResponse('Unsupported format', status=400)

def generate_coco(project):
    ann_id, img_id = 1, 1
    cats = [{'id': i+1, 'name': cls} for i, cls in enumerate(project.classes)]
    images, annotations = [], []
    
    for img in project.images.all():
        images.append({
            'id': img_id,
            'file_name': img.filename,
            'width': img.width,
            'height': img.height
        })
        for ann in img.annotations.all():
            if ann.annotation_type == 'bbox':
                d = ann.data
                bbox = [d['x1'] * img.width, d['y1'] * img.height, (d['x2'] - d['x1']) * img.width, (d['y2'] - d['y1']) * img.height]
                annotations.append({
                    'id': ann_id,
                    'image_id': img_id,
                    'category_id': project.classes.index(ann.class_name) + 1,
                    'bbox': bbox,
                    'area': bbox[2] * bbox[3],
                    'iscrowd': 0
                })
                ann_id += 1
        img_id += 1
    
    return {'categories': cats, 'images': images, 'annotations': annotations}

@login_required
@require_http_methods(["GET", "POST"])
def project_detail_api(request, workspace_id, project_id):
    project = get_object_or_404(Project, id=project_id, workspace_id=workspace_id, workspace__created_by=request.user)
    
    stats = project.images.aggregate(
        total_images=Count('id'),
        annotated_images=Count('annotations', distinct=True),
        total_annotations=Count('images__annotations'),
        auto_generated=Count('images__annotations', filter=F('images__annotations__confidence__gt') > 0.5)
    )
    
    return JsonResponse({
        'project': {
            'id': project.id,
            'name': project.name,
            'project_type': project.project_type,
            'image_count': stats['total_images']
        }
    })

@login_required
@require_http_methods(["GET"])
def project_images_api(request, workspace_id, project_id):
    project = get_object_or_404(Project, id=project_id, workspace_id=workspace_id, workspace__created_by=request.user)
    
    images = project.images.all().values('id', 'filename', 'image_file', 'width', 'height', 'status')
    return JsonResponse({'images': list(images)})

@login_required
@require_http_methods(["GET"])
def project_metrics_api(request, workspace_id, project_id):
    project = get_object_or_404(Project, id=project_id, workspace_id=workspace_id, workspace__created_by=request.user)
    
    stats = project.images.aggregate(
        total_images=Count('id'),
        annotated_images=Count('annotations', distinct=True),
        total_annotations=Count('images__annotations'),
        auto_generated=Count('images__annotations', filter=F('images__annotations__confidence__gt') > 0.5),
        approved=Count('images__annotations', filter=F('images__annotations__is_approved') == True)
    )
    
    return JsonResponse({
        'metrics': {
            'annotated_images': stats['annotated_images'] or 0,
            'auto_generated': stats['auto_generated'] or 0,
            'approved': stats['approved'] or 0
        }
    })

@login_required
@require_http_methods(["GET"])
def project_review_queue_api(request, workspace_id, project_id):
    project = get_object_or_404(Project, id=project_id, workspace_id=workspace_id, workspace__created_by=request.user)
    
    # Get images with pending annotations (not fully reviewed)
    review_queue = []
    for img in project.images.all():
        pending = img.annotations.filter(is_approved=False).count()
        if pending > 0:
            review_queue.append({
                'id': img.id,
                'filename': img.filename,
                'pending_annotations': pending,
                'status': 'pending_review'
            })
    
    return JsonResponse({'review_queue': review_queue})

@login_required
@require_http_methods(["GET", "POST"])
def image_annotations(request, workspace_id, project_id, image_id):
    image = get_object_or_404(Image, id=image_id, project_id=project_id, project__workspace_id=workspace_id)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        annotation = Annotation.objects.create(
            image=image,
            class_name=data['class_name'],
            annotation_type=data['annotation_type'],
            data=data['data'],
            confidence=data.get('confidence', 0.0)
        )
        return JsonResponse({'annotation': {'id': annotation.id}})
    
    annotations = image.annotations.all()
    return JsonResponse({'annotations': list(annotations.values('id', 'class_name', 'annotation_type', 'data', 'confidence'))})

@login_required
def annotate_image(request, workspace_id, project_id, image_id):
    """Display the annotation canvas for an image."""
    image = get_object_or_404(Image, id=image_id, project_id=project_id, project__workspace_id=workspace_id)
    project = image.project
    workspace = project.workspace
    
    # Check permission
    if workspace.created_by != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    return render(request, 'annotation/annotate.html', {
        'image': image,
        'project': project,
        'workspace': workspace
    })

@login_required
@require_http_methods(["POST"])
def auto_annotate_image(request, workspace_id, project_id, image_id):
    image = get_object_or_404(Image, id=image_id, project_id=project_id, project__workspace_id=workspace_id)
    # Call the existing auto_annotate function
    return auto_annotate(request, workspace_id, project_id, image_id)

def user_performance(request):
    # Fixed the F-expression for duration calculation
    tasks = AnnotationTask.objects.filter(completed_at__isnull=False).values('assigned_to').annotate(
        avg_time=Avg(F('completed_at') - F('assigned_at'))
    )
    return JsonResponse({'performance': list(tasks)})
