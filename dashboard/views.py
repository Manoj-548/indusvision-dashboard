from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import render
from django.http import JsonResponse
from .models import MetricRecord, SourceFile, ModelWeights


@login_required
def home(request):
    latest_metrics = MetricRecord.objects.order_by('-collected_at')[:14]
    source_files = SourceFile.objects.order_by('-last_updated')[:25]
    model_weights = ModelWeights.objects.order_by('-last_used')[:10]

    module_summary = []
    for module in ['annotation', 'automation', 'sandbox', 'spider', 'wrangling', 'sensor', 'camera']:
        metric = MetricRecord.objects.filter(module=module).order_by('-collected_at').first()
        if metric:
            module_summary.append(metric)

    total_files = SourceFile.objects.count()
    file_type_counts = SourceFile.objects.values('file_type').order_by().annotate(count=models.Count('id'))
    return render(request, 'dashboard_home.html', {
        'metrics': latest_metrics,
        'summary': module_summary,
        'source_files': source_files,
        'model_weights': model_weights,
        'total_files': total_files,
        'file_type_counts': file_type_counts,
    })


@login_required
def model_management(request):
    """View for managing models and running detections."""
    models_list = ModelWeights.objects.order_by('-last_used')
    stats = {
        'total': ModelWeights.objects.count(),
        'available': ModelWeights.objects.filter(status='available').count(),
    }
    
    return render(request, 'model_management.html', {
        'models': models_list,
        'stats': stats,
    })


def api_health(request):
    records = MetricRecord.objects.order_by('-collected_at')[:25]
    data = [
        {
            'module': r.module,
            'value': r.value,
            'status': r.status,
            'info': r.info,
            'collected_at': r.collected_at.isoformat(),
        }
        for r in records
    ]
    return JsonResponse({'data': data})
