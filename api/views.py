from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_http_methods
import json
import numpy as np

try:
    from dashboard.models import SourceFile, KnowledgeEntry
except ImportError:
    SourceFile = None
    KnowledgeEntry = None


@require_http_methods(["GET"])
def api_sensor(request):
    return JsonResponse({
        "sensor1": float(np.random.rand()*100),
        "sensor2": float(np.random.rand()*100)
    })


@require_http_methods(["GET"])
def api_projects(request):
    from dashboard.models import KnowledgeEntry
    projects = KnowledgeEntry.objects.filter(knowledge_type='doc').values('id', 'title', 'created_at', 'content_preview')[:10]
    return JsonResponse({'projects': list(projects)})


@require_http_methods(["POST"])
def ai_suggest(request):
    body = json.loads(request.body or "{}")

    # Dummy AI suggestion (replace later)
    return JsonResponse({
        "type": "polygon",
        "points": [[100,100],[200,100],[200,200],[100,200]],
        "confidence": 0.9
    })


@require_http_methods(["GET"])
def api_knowledge(request):
    data = list(KnowledgeEntry.objects.values()[:10])
    return JsonResponse({"data": data})
