from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Q
from .models import MetricRecord, SourceFile, ModelWeights, KnowledgeEntry
from .tasks import sync_source_files, consolidate_knowledge_task
import time
import numpy as np

@login_required
def home(request):
    latest_metrics = MetricRecord.objects.order_by('-collected_at')[:14]
    knowledge_docs = KnowledgeEntry.objects.filter(knowledge_type='doc').order_by('-consolidated_at')[:10]
    scripts = SourceFile.objects.filter(file_type='script').order_by('-last_updated')[:10]
    knowledge_stats = KnowledgeEntry.objects.aggregate(
        total=Count('id'),
        docs=Count('id', filter=Q(knowledge_type='doc')),
        scripts=Count('id', filter=Q(knowledge_type='script'))
    ) or {'total': 0, 'docs': 0, 'scripts': 0}
    file_type_counts = SourceFile.objects.values('file_type').annotate(count=Count('id'))
    total_files = SourceFile.objects.count()
    model_weights = ModelWeights.objects.all()[:10]
    
    return render(request, 'dashboard.html', {
        'metrics': latest_metrics,
        'knowledge_docs': knowledge_docs,
        'scripts': scripts,
        'knowledge_stats': knowledge_stats,
        'file_type_counts': file_type_counts,
        'total_files': total_files,
        'model_weights': model_weights,
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

