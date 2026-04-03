from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from .views import ModelWeightsViewSet, MetricRecordViewSet, SourceFileViewSet

router = DefaultRouter()
router.register(r'models', ModelWeightsViewSet)
router.register(r'metrics', MetricRecordViewSet)
router.register(r'sources', SourceFileViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('sensor/', lambda r: JsonResponse({'status': 'ok', 'data': {'sensor1': 42, 'sensor2': 75}})),
    path('annotation/', lambda r: JsonResponse({'classes': ['person', 'car', 'truck']})),
    path('camera/', lambda r: JsonResponse({'stream': 'active', 'fps': 30})),
    path('automation/', lambda r: JsonResponse({'status': 'idle', 'tasks': 5})),
    path('sandbox/', lambda r: JsonResponse({'status': 'ready', 'projects': 12})),
    path('sync/', lambda r: JsonResponse({'synced': True, 'files': 1500})),
]
