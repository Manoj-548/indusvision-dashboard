from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
import cv2
from .tasks import sync_source_files, consolidate_knowledge_task
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Q
from .models import SourceFile, KnowledgeEntry
from dashboard.models_annotation import Workspace, Project, Image, Annotation, AnnotationTask
# from .tasks import sync_source_files, consolidate_knowledge_task  # Use dashboard sync btn
import subprocess
import socket
import os
import signal
import time
import numpy as np
import urllib.request
import urllib.error

def is_port_open(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def start_tensorboard_process():
    pid_file = 'tb.pid'
    log_dir = 'tensorboard_logs'
    port = 6006
    if is_port_open(port):
        return {'status': 'already_running'}
    if os.path.exists(pid_file):
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)  # check if alive
        except (ValueValue, OSError):
            os.remove(pid_file)
        else:
            return {'status': 'already_running'}
    
    tb_exe = 'tensorboard'
    if os.name == 'nt':
        tb_exe = '"C:\\Users\\manoj\\AppData\\Roaming\\Python\\Python314\\Scripts\\tensorboard.exe"'
    
    cmd = [tb_exe, '--logdir=' + log_dir, '--port=' + str(port), '--host=0.0.0.0']
    
    p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)  # wait start
    
    with open(pid_file, 'w') as f:
        f.write(str(p.pid))
    
    return {'status': 'started', 'pid': p.pid}

@login_required
@require_http_methods(["POST"])
def start_tensorboard_view(request):
    result = start_tensorboard_process()
    return JsonResponse(result)


def get_ai_status():
    status = {'llm': 'Ollama', 'available': False, 'detail': 'unknown'}
    try:
        resp = urllib.request.urlopen('http://localhost:11434/api/tags', timeout=3)
        if resp.status == 200:
            status['available'] = True
            status['detail'] = 'Local Ollama instance reachable'
        else:
            status['detail'] = f'HTTP {resp.status}'
    except urllib.error.HTTPError as e:
        status['detail'] = f'HTTPError {e.code}'
    except urllib.error.URLError as e:
        status['detail'] = f'Unavailable: {e.reason}'
    except Exception as e:
        status['detail'] = str(e)
    return status

@login_required
def home(request):
    latest_metrics = []  # MetricRecord not defined
    knowledge_docs = KnowledgeEntry.objects.filter(knowledge_type='doc').order_by('-created_at')[:10]
    scripts = SourceFile.objects.filter(file_type='script').order_by('-last_updated')[:10]
    knowledge_stats = KnowledgeEntry.objects.aggregate(
        total=Count('id'),
        docs=Count('id', filter=Q(knowledge_type='doc')),
        scripts=Count('id', filter=Q(knowledge_type='script'))
    ) or {'total': 0, 'docs': 0, 'scripts': 0}
    file_type_counts = SourceFile.objects.values('file_type').annotate(count=Count('id'))
    total_files = SourceFile.objects.count()
    model_weights = []  # ModelWeights not available
    projects = Project.objects.order_by('-created_at')[:6]
    project_count = Project.objects.count()
    
    source_files_total = SourceFile.objects.count()
    knowledge_total = KnowledgeEntry.objects.count()
    knowledge_sources = SourceFile.objects.filter(is_knowledge_relevant=True).order_by('-last_updated')[:8]
    ai_status = get_ai_status()

    return render(request, 'dashboard.html', {
        'metrics': latest_metrics,
        'knowledge_docs': knowledge_docs,
        'scripts': scripts,
        'knowledge_stats': knowledge_stats,
        'file_type_counts': file_type_counts,
        'total_files': total_files,
        'model_weights': model_weights,
        'projects': projects,
        'project_count': project_count,
        'is_admin': is_admin(request.user),
        'source_files_total': source_files_total,
        'knowledge_total': knowledge_total,
        'knowledge_sources': knowledge_sources,
        'ai_status': ai_status,
    })

@login_required
def unified(request):
    return render(request, 'unified.html')

@require_http_methods(["POST"])
def sync(request):
    sync_source_files()
    consolidate_knowledge_task()
    return JsonResponse({'status': 'synced'})

@require_http_methods(["GET"])
def api_sensor(request):
    return JsonResponse({'sensor1': np.random.rand()*100, 'sensor2': np.random.rand()*100})

@require_http_methods(["GET"])
def api_camera(request):
    def generate_frames():
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret: break
            ret, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        cap.release()
    return StreamingHttpResponse(generate_frames(), content_type='multipart/x-mixed-replace; boundary=frame')

@require_http_methods(["GET", "POST"])
def api_annotation(request):
    if request.method == 'POST':
        return JsonResponse({'status': 'saved'})
    return JsonResponse({'classes': ['person', 'car', 'truck']})

@require_http_methods(["GET", "POST"])
def api_automation(request):
    if request.method == 'POST':
        return JsonResponse({'status': 'running'})
    return JsonResponse({'automation_status': 'idle'})


@login_required
def knowledge(request):
    from django.db.models import Count, Q
    query = request.GET.get('q', '')
    knowledge_entries = KnowledgeEntry.objects.all()
    if query:
        knowledge_entries = knowledge_entries.filter(
            Q(title__icontains=query) | Q(source_file__path__icontains=query) | Q(content_preview__icontains=query)
        )
    knowledge_entries = knowledge_entries.order_by('-created_at')[:50]
    stats = KnowledgeEntry.objects.aggregate(
        total=Count('id'),
        docs=Count('id', filter=Q(knowledge_type='doc')),
        scripts=Count('id', filter=Q(knowledge_type='script'))
    )
    sources = SourceFile.objects.filter(is_knowledge_relevant=True).order_by('-last_updated')[:20]
    context = {
        'knowledge_entries': knowledge_entries,
        'stats': stats,
        'sources': sources,
        'query': query,
    }
    return render(request, 'knowledge.html', context)

from .rag import rag_agent

import json
import time
from django.http import StreamingHttpResponse
# from .models import MetricRecord

@login_required
@require_http_methods(["GET", "POST"])
def agent(request):
    if request.method == 'POST':
        return rag_agent(request)
    return render(request, 'agent.html')

@login_required
def annotations(request):
    return render(request, 'annotations.html')

@login_required
def tensorboard(request):
    return render(request, 'tensorboard.html')

@login_required
def live_updates(request):
    def event_stream():
        while True:
            latest = MetricRecord.objects.order_by('-collected_at').first()
            if latest:
                data = {
                    'value': latest.value,
                    'module': latest.module,
                    'status': latest.status,
                    'timestamp': latest.collected_at.isoformat()
                }
            else:
                data = {'value': 0, 'module': 'idle', 'status': 'waiting', 'timestamp': 'now'}
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(5)
    
    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['Access-Control-Allow-Origin'] = '*'
    return response


# ========== PROJECT MANAGEMENT VIEWS ==========

def is_admin(user):
    """Check if user is admin"""
    return user.is_staff or user.is_superuser


@login_required
def projects_list(request):
    """List all projects (accessible to all logged-in users)"""
    projects = Project.objects.all().annotate(
        image_count=Count('images'),
        annotation_count=Count('images__annotations')
    ).order_by('-created_at')
    
    context = {
        'projects': projects,
        'is_admin': is_admin(request.user),
    }
    return render(request, 'projects/list.html', context)


@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def project_create(request):
    """Create a new project (admin only)"""
    if request.method == 'POST':
        name = request.POST.get('name')
        project_type = request.POST.get('project_type', 'object')
        description = request.POST.get('description', '')
        classes = request.POST.get('classes', '').split(',')
        
        # Validate
        if not name:
            return JsonResponse({'error': 'Project name is required'}, status=400)
        
        # Create workspace if needed
        workspace_name = request.POST.get('workspace_name', 'Default')
        workspace, _ = Workspace.objects.get_or_create(
            name=workspace_name,
            defaults={'created_by': request.user}
        )
        
        project = Project.objects.create(
            workspace=workspace,
            name=name,
            project_type=project_type,
            description=description,
            classes=[c.strip() for c in classes if c.strip()]
        )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'id': project.id,
                'name': project.name,
                'url': f'/dashboard/projects/{project.id}/'
            })
        
        return redirect('project_detail', project_id=project.id)
    
    context = {
        'project_types': [
            ('object', 'Object Detection'),
            ('segmentation', 'Semantic Segmentation'),
            ('classification', 'Image Classification'),
            ('keypoint', 'Keypoint Detection'),
            ('video', 'Video Tracking'),
        ]
    }
    return render(request, 'projects/create.html', context)


@login_required
@user_passes_test(is_admin)
def project_detail(request, project_id):
    """View/edit project details (admin only)"""
    project = get_object_or_404(Project, id=project_id)
    images = project.images.all().order_by('-uploaded_at')[:50]
    
    stats = {
        'total_images': project.images.count(),
        'annotated_images': project.images.filter(annotations__isnull=False).distinct().count(),
        'total_annotations': Annotation.objects.filter(image__project=project).count(),
        'approved_annotations': Annotation.objects.filter(image__project=project, is_approved=True).count(),
    }
    
    context = {
        'project': project,
        'images': images,
        'stats': stats,
        'workspace': project.workspace,
    }
    return render(request, 'projects/detail.html', context)


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def project_delete(request, project_id):
    """Delete a project (admin only)"""
    project = get_object_or_404(Project, id=project_id)
    project_name = project.name
    project.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'message': f'Project "{project_name}" deleted'})
    
    return redirect('projects_list')


@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def project_update(request, project_id):
    """Update project details (admin only)"""
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'GET':
        context = {'project': project}
        return render(request, 'projects/edit.html', context)

    project.name = request.POST.get('name', project.name)
    project.description = request.POST.get('description', project.description)

    classes_str = request.POST.get('classes', '')
    if classes_str:
        project.classes = [c.strip() for c in classes_str.split(',') if c.strip()]

    project.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'message': 'Project updated successfully'})

    return redirect('project_detail', project_id=project.id)

