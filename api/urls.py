from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ModelWeightsViewSet, MetricRecordViewSet, SourceFileViewSet

router = DefaultRouter()
router.register(r'models', ModelWeightsViewSet, basename='model-weights')
router.register(r'metrics', MetricRecordViewSet, basename='metrics')
router.register(r'sources', SourceFileViewSet, basename='source-files')

urlpatterns = [
    path('', include(router.urls)),
]
